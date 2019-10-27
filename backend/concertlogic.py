import os 
import requests
import config
import urllib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#TODO - figure out exactly what the database URI should be
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/listeningdata"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']

""" Bidirectional, so you can access all Users interested in a certain artist and all 
	the Artists a certain User is interested in.""" 

association = db.Table('association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	spotify_user_id = db.Column(db.String, unique = True, nullable=False)
	spotify_access_token = db.Column(db.String, unique=True)
	facebook_user_id = db.Column(db.String, unique = True)

	relevant_artists = db.relationship('Artist', secondary=association, backref = db.backref('users', lazy=True))

class Artist(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key = True)
	artist_id = db.Column(db.String, unique=True)
	artist_name = db.Column(db.String, unique=True)
	
	interested_users = db.relationship('User', secondary=association, backref = db.backref('artists', lazy=True))


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
	return r.json()["items"]

def related_artists(artist_id, user):
	""" Returns related artists given a certain artist_id. """
	query = SPOTIFY_URL + '/artists/' + artist_id + '/related-artists' + '?access_token=' + user.spotify_access_token
	return r.json()["artists"]


def friends(concert):
	""" Returns the Users to go with for a given
		concert. Concert is the json data returned by the SeatGeek API."""
	artists = [performer["name"] for performer in concert["performers"]]
	users = [] 
	for artist in artists:
		artist_obj = Artist.query.filter_by(name=artist) # each name should be unique
		users.append(artist_obj.users) # append or concatenate - TODO: check behavior
	return users

@app.route('/add_user', methods=['POST'])
def add_user():
    
    if request.method == 'POST':
        spotify_user_id = request.args.get('spotify_user_id')
        spotify_access_token = request.args.get('spotify_access_token')
        facebook_user_id = request.args.get('facebook_user_id')

        if not db.session.query(User).filter(User.spotify_user_id == spotify_user_id).count(): # find better way
            db.session.add(User(spotify_user_id=spotify_user_id, spotify_access_token=spotify_access_token, facebook_user_id=facebook_user_id))
            db.session.commit()
        
        update_users_top_artists(user)
    user = User.query.filter_by(spotify_user_id=spotify_user_id)
    update_top_artists(user)


def update_relations(user):
    top_artists = top_artists(user)
    for artist in top_artists:
        artist_name = artist["name"]
        artist_id = artist["id"]
        if not db.session.query(Artist).filter(Artist.name==artist_name).count(): # find better way
            db.session.add(Artist(artist_id=artist_id, artist_name=artist_name))
        artist = Artist.query.filter_by(artist_id = artist_id)
        """ Check if it's not already there?""" 
        user.relevantartists.append(artist)
        artist.interested_users.append(relevantartists)

