import os
from app import app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

association = db.Table('association',
    db.Column('association_key', db.Integer, unique=True, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('spotifyuser.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'))
)

class SpotifyUser(db.Model):
    __tablename__='spotifyuser'
    id = db.Column(db.Integer, primary_key = True)
    spotify_user_id = db.Column(db.String, unique = True, nullable=False)
    spotify_access_token = db.Column(db.String, unique=True)
    relevant_artists = db.relationship('Artist', secondary=association, backref = db.backref('spotifyusers', lazy=True))

class Artist(db.Model):
    __tablename__='artist'
    id = db.Column(db.Integer, unique=True, primary_key = True)
    artist_id = db.Column(db.String, unique=True)
    artist_name = db.Column(db.String, unique=True)
    interested_users = db.relationship('SpotifyUser', secondary=association, backref = db.backref('artists', lazy=True))

if __name__ ==  '__main__':
    manager.run()
