import os
import requests
import urllib
from flask import redirect
from app import app, db
from models import SpotifyUser, Artist
import socket

import config
# Avoids broken pipe error 
try:
    # Python 3
    from urllib.parse import quote
except ImportError:
    # Python 2
    from urllib import quote

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']

artist_qlimit = 50
rel_artists_qlimit = 1

def find_concerts(user):
	"""Returns concerts for a given user."""
	artists = top_artists(user)
	including_relevant = artists[:]

	# Expands artist lists by including related artists
	for artist in artists:
		artist_id = artist['id']
		relevant_artist = related_artists(artist_id, user)
		including_relevant.append(relevant_artist)

	# Searches venue by performer name
	concerts = []
	event_query = SEATGEEK_URL + 'events?geoip=true&performers.slug='

	for artist in including_relevant:
		modified_name = artist['name'].replace(' & ', quote('&')).replace(' ', '-').lower()
		response = requests.get(event_query + modified_name + '&client_id=' + SEATGEEK_CLIENT_ID).json()
		if response['events']:
			event = response['events'][0]
			print(friends(event))
			rec = {
				'title': event['title'],
				'url': event['url'],
				'datetime_local': event['datetime_local'],
				'image': event['performers'][0]['image'],
				'location': event['venue']['display_location'],
				'friends': friends(event)
			}
			concerts.append(rec)
	return concerts

def top_artists(user):
	""" Returns artists that the user is interested in."""
	query = SPOTIFY_URL + '/me/top/artists?limit=' + str(artist_qlimit)
	r = requests.get(query, headers={'Authorization': 'Bearer ' + user.spotify_access_token})
	# Will error if access token expires
	try:
		return r.json()["items"]
	except:
		raise KeyError 

def related_artists(artist_id, user):
	""" Returns related artists given a certain artist_id. """
	query = SPOTIFY_URL + '/artists/' + artist_id + '/related-artists'
	r = requests.get(query, headers={'Authorization': 'Bearer ' + user.spotify_access_token})
	# As of now, only takes the first entry or else the program will run too long
	return r.json()["artists"][0]

def friends(concert):
	""" Returns the Users to go with for a given
		concert. Concert is the json data returned by the SeatGeek API."""
	artists = [performer["name"] for performer in concert["performers"]]
	users = []
	for artist in artists:
		artist_obj = Artist.query.filter_by(artist_name=artist).first() # each name should be unique
		if artist_obj:
			users.append(artist_obj.spotifyusers) # append or concatenate - TODO: check behavior
	return users

def update_relations(user):
	print("Being called.")
	artists = top_artists(user)
	for artist in artists:
		artist_name = artist["name"]
		artist_id = artist["id"]
		if not db.session.query(Artist).filter(Artist.artist_name==artist_name).count(): # find better way
			db.session.add(Artist(artist_id=artist_id, artist_name=artist_name))
			db.session.commit()
		artist = Artist.query.filter_by(artist_id = artist_id).first()
		""" Check if it's not already there?"""
		user.relevant_artists.append(artist)
		artist.interested_users.append(user)
