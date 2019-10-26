import os 
import requests
import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = """ URL OF THE DATABASE """
db = SQLAlchemy(app)

CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SECRET = os.environ['SEATGEEK_SECRET']
URL = os.environ['SEATGEEK_URL']

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	spotify_user_id = db.Column(db.String, unique = True, nullable=False)

def concerts(user):
	"""Returns concerts for a given user.""" 
	artists = top_artists(user)
	artists = [artist.replace(" ", "+") for artist in artists]
	query_strings = [ URL + "events?q=" + artist + "&client_id=" + CLIENT_ID for artist in artists]
	concerts = [] 
	for query in query_strings:
		r = requests.get(query)
		concerts.append(r.json())
	return concerts

def top_artists(user):
	""" Returns artists that the user is interested in."""
	return ["Young the Giant"]

def friends(concert):
	""" Returns the user_ids of friends to go with for a given
		concert."""

