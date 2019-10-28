import os
from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/listeningdata"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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

db.create_all()
