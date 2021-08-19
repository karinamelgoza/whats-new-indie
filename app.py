from flask import Flask, render_template, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy

from model import db, User

from igdb.wrapper import IGDBWrapper

import json
import config
import requests

app = Flask(__name__)

app.secret_key = "secret-key"

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config.psql_username}:{config.psql_password}@{config.psql_host}/{config.psql_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
                session['logged_in'] = user.username
                flash('Logged in!')
                return redirect('/')
            else:
                flash('Incorrect password')
                return redirect('/')

    response = requests.get(
        f"https://api.rawg.io/api/games?dates=2021-08-01,2021-08-31&key={config.key}&platforms=18,1,7,187,186,3,21&genres=51&page_size=50&page=1&ordering=released")

    results_rawg = response.json()

    byte_array = wrapper.api_request(
        'games', 'fields name, cover.url, videos.video_id, release_dates.human; where first_release_date < 1627776000 &release_dates.date > 1627776000 & release_dates.date < 1630454400 & genres = (32) & platforms= (130); limit 60;')

    results = json.loads(byte_array)

    return render_template('homepage.html', results=results, results_rawg=results_rawg['results'])


@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash('Logged out')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
