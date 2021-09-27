from flask import Flask, render_template, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from model import db, User, Game, Wishlist, Library
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from igdb.wrapper import IGDBWrapper

import json
import config
import requests
import calendar

engine = create_engine(
    f'postgresql://{config.psql_username}:{config.psql_password}@{config.psql_host}/{config.psql_db}')

Session = sessionmaker(engine)

db = SQLAlchemy()
app = Flask(__name__)

app.secret_key = "secret-key"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config.psql_username}:{config.psql_password}@{config.psql_host}/{config.psql_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.app = app
db.init_app(app)

wrapper = IGDBWrapper(config.client_id,
                      config.access_token)


@app.route('/', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        if 'register_username' in request.form:
            user = User(first_name=request.form['first_name'], last_name=request.form['last_name'],
                        username=request.form['register_username'], password=request.form['password'])

            db.session.add(user)
            db.session.commit()

            flash(f'User registered')
            return redirect('/')

        elif 'login_username' in request.form:
            username = request.form['login_username']
            password = request.form['password']
            user = User.query.filter_by(username=f'{username}').first()

            if not user:
                flash('User does not exist')
                return redirect('/')
            elif password == user.password:
                session['logged_in'] = user.user_id
                flash('Logged in!')
                return redirect('/')
            else:
                flash('Incorrect password')
                return redirect('/')

    date = datetime(datetime.today().year, datetime.today().month, 1).date()
    last_day = calendar.monthrange(
        datetime.today().year, datetime.today().month)[1]
    date_last = datetime(datetime.today().year,
                         datetime.today().month, last_day).date()
    utc_timestamp = int(datetime(datetime.today().year, datetime.today(
    ).month, 1).replace(tzinfo=timezone.utc).timestamp())
    utc_timestamp_last = int(datetime(datetime.today().year, datetime.today(
    ).month, last_day).replace(tzinfo=timezone.utc).timestamp())
    current_month = date.strftime('%B')
    current_year = date.strftime('%Y')

    response = requests.get(
        f"https://api.rawg.io/api/games?dates={date},{date_last}&key={config.key}&platforms=18,1,7,187,186,3,21&genres=51&page_size=50&page=1&ordering=released")

    results_rawg = response.json()

    byte_array = wrapper.api_request(
        'games', f'fields name, summary, cover.url, videos.video_id, release_dates.human, genres.name, platforms.name; where first_release_date < {utc_timestamp} &release_dates.date >= {utc_timestamp} & release_dates.date <= {utc_timestamp_last} & genres = (32) & platforms= (130); limit 60;')

    results = json.loads(byte_array)

    with Session() as dbsession:

        wishlist = dbsession.query(Wishlist).filter_by(
            user_id=session.get('logged_in')).all()

        wishlist_games = []

        for i in wishlist:
            wishlist_games.append(i.game.name)

        library = dbsession.query(Library).filter_by(
            user_id=session.get('logged_in')).all()

        library_games = []

        for i in library:
            library_games.append(i.game.name)

    return render_template('homepage.html', results=results, results_rawg=results_rawg['results'], wishlist=wishlist_games, library=library_games, current_month=current_month, current_year=current_year)


@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash('Logged out')
    return redirect('/')


@app.route('/wishlist/<int:id>')
def add_wishlist_item(id):

    with Session() as dbsession:

        response = requests.get(
            f"https://api.rawg.io/api/games/{id}?key={config.key}")
        results = response.json()
        name = results.get('name')
        cover_pic = results.get('background_image')

        video_game = dbsession.query(Game).filter_by(name=f'{name}').first()

        if not video_game:

            video_game = Game(name=name,
                              url=f'https://rawg.io/games/{id}', cover_pic=cover_pic)

            dbsession.add(video_game)
            dbsession.commit()

        wishlist_item = Wishlist(user_id=session.get(
            'logged_in'), video_game_id=video_game.video_game_id)

        dbsession.add(wishlist_item)
        dbsession.commit()

        return redirect('/')


@app.route('/library/<int:id>')
def add_library_item(id):

    response = requests.get(
        f"https://api.rawg.io/api/games/{id}?key={config.key}")
    results = response.json()
    name = results.get('name')
    cover_pic = results.get('background_image')

    video_game = Game.query.filter_by(name=f'{name}').first()

    if not video_game:

        video_game = Game(name=name,
                          url=f'https://rawg.io/games/{id}', cover_pic=cover_pic)

        db.session.add(video_game)
        db.session.commit()

    library_item = Library(user_id=session.get(
        'logged_in'), video_game_id=video_game.video_game_id, played=False)

    db.session.add(library_item)
    db.session.commit()

    return redirect('/')


@app.route('/wishlist/port/<int:id>')
def add_port_wishlist(id):

    byte_array = wrapper.api_request(
        'games', f'fields name, slug; where id={id};')

    results = json.loads(byte_array)
    name = results[0].get('name')
    slug = results[0].get('slug')

    with Session() as dbsession:

        video_game = dbsession.query(Game).filter_by(name=name).first()

        if not video_game:

            video_game = Game(name=name,
                              url=f'https://www.igdb.com/games/{slug}')

            dbsession.add(video_game)
            dbsession.commit()

        wishlist_item = Wishlist(user_id=session.get(
            'logged_in'), video_game_id=video_game.video_game_id)

        dbsession.add(wishlist_item)
        dbsession.commit()

    return redirect('/')


@app.route('/library/port/<int:id>')
def add_port_library(id):

    byte_array = wrapper.api_request(
        'games', f'fields name, slug; where id={id};')

    results = json.loads(byte_array)
    name = results[0].get('name')
    slug = results[0].get('slug')

    with Session() as dbsession:

        video_game = dbsession.query(Game).filter_by(name=name).first()

        if not video_game:

            video_game = Game(name=name,
                              url=f'https://www.igdb.com/games/{slug}')

            dbsession.add(video_game)
            dbsession.commit()

        library_item = Library(user_id=session.get(
            'logged_in'), video_game_id=video_game.video_game_id, played=False)

        dbsession.add(library_item)
        dbsession.commit()

    return redirect('/')


@app.route('/wishlist/show')
def show_wishlist():

    with Session() as dbsession:

        wishlist = dbsession.query(Wishlist).filter_by(
            user_id=session.get('logged_in')).all()

        return render_template('wishlist.html', wishlist=wishlist)


@app.route('/library/show')
def show_library():

    with Session() as dbsession:

        library = dbsession.query(Library).filter_by(
            user_id=session.get('logged_in')).all()

        return render_template('library.html', library=library)


@app.route('/library/played/<int:user_id>,<int:video_game_id>')
def mark_played(user_id, video_game_id):
    video_game = Library.query.filter_by(
        user_id=user_id, video_game_id=video_game_id).first()

    video_game.played = True
    db.session.merge(video_game)
    db.session.commit()

    return redirect('/library/show')


@app.route('/library/played/remove/<int:user_id>,<int:video_game_id>')
def remove_played(user_id, video_game_id):

    with Session() as session:
        video_game = session.query(Library).filter_by(
            user_id=user_id, video_game_id=video_game_id).first()

        video_game.played = False
        session.commit()

    return redirect('/library/show')


@app.route('/library/remove/<int:user_id>,<int:video_game_id>')
def remove_game_library(user_id, video_game_id):

    with Session() as session:

        video_game = session.query(Library).filter_by(
            user_id=user_id, video_game_id=video_game_id).first()

        session.delete(video_game)
        session.commit()

        return redirect('/library/show')


@app.route('/wishlist/remove/<int:user_id>,<int:video_game_id>')
def remove_game_wishlist(user_id, video_game_id):

    with Session() as session:

        video_game = session.query(Wishlist).filter_by(
            user_id=user_id, video_game_id=video_game_id).first()

        session.delete(video_game)
        session.commit()

        return redirect('/wishlist/show')


@app.route('/wishlist/move/<int:id>,<int:user_id>,<int:video_game_id>')
def move_game_library(id, user_id, video_game_id):

    with Session() as session:

        video_game = session.query(Wishlist).filter_by(id=id).first()
        session.delete(video_game)

        move_game = Library(
            user_id=user_id, video_game_id=video_game_id, played=False)
        session.add(move_game)
        session.commit()

    return redirect('/wishlist/show')


# if __name__ == '__main__':
#     app.run(debug=True)
