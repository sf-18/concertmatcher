import os 
import requests
import config
import urllib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = """ URL OF THE DATABASE """
db = SQLAlchemy(app)

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']
GENERIC_SPOTIFY_ACCESS_TOKEN = os.environ['GENERIC_SPOTIFY_ACCESS_TOKEN']

REDIRECT_URI = 'http://localhost:8888' # temporary

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	spotify_user_id = db.Column(db.String, unique = True, nullable=False)
	spotify_access_token = db.Column(db.String, unique=True)

def concerts(user):
	"""Returns concerts for a given user.""" 
	artists = top_artists(user)
	artists = [artist.replace(" ", "+") for artist in artists]
	query_strings = [ SEATGEEK_URL + "events?q=" + artist + "&client_id=" + SEATGEEK_CLIENT_ID for artist in artists]
	concerts = [] 
	for query in query_strings:
		r = requests.get(query)
		concerts.append(r.json())
	return concerts

def top_artists(user):
	""" Returns artists that the user is interested in."""
	query = SPOTIFY_URL + '/me/top/artists' + '?access_token=' + user.spotify_access_token
	r = requests.get(query)
	return r.json() 

def related_artists(artist_id):
	""" Returns related artists given a certain artist_id. """
	query = SPOTIFY_URL + '/artists/' + artist_id + '/related-artists' + '?access_token=' + GENERIC_SPOTIFY_ACCESS_TOKEN
	return r.json()


def friends(concert):
	""" Returns the user_ids of friends to go with for a given
		concert."""

