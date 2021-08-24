from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(25), nullable=True)
    last_name = db.Column(db.String(25), nullable=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return f'user_id={self.user_id} username={self.username}'


class Game(db.Model):

    __tablename__ = 'video_games'

    video_game_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    cover_pic = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'video_game_id={self.video_game_id} name={self.name}'


class Wishlist(db.Model):

    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    video_game_id = db.Column(
        db.Integer, db.ForeignKey('video_games.video_game_id'))

    game = db.relationship('Game', backref=db.backref('wishlist', order_by=id))

    def __repr__(self):
        return f'video_game_id={self.video_game_id} name={self.game.name}'


class Library(db.Model):

    __tablename__ = 'library'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    video_game_id = db.Column(
        db.Integer, db.ForeignKey('video_games.video_game_id'))
    played = db.Column(db.Boolean, nullable=True)

    game = db.relationship('Game', backref=db.backref('library', order_by=id))


# def connect_db(app):
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://owcwrsvbjlrnri:6dfd1b7bbb6ca7a12448a27b00c9bbd1f6027a635773b9a89acbb6412c5b85a4@ec2-35-153-114-74.compute-1.amazonaws.com:5432/dfnb0bbojq31d0'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.app = app
#     db.init_app(app)
