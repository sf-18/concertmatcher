import os
import requests
import config
import urllib
from flask import redirect
from app import app
from models import db, SpotifyUser, Artist
import socket

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']

q_limit = 50

def concerts(user):
	"""Returns concerts for a given user."""
	artists = top_artists(user)
	concerts = []
	mile_range = '12mi'
	# print(artists)
	# artists = [artist.replace(" ", "+") for artist in artists]
	ip = socket.gethostbyname(socket.gethostname())
	print(ip)
	query = SEATGEEK_URL + 'events?geoip=' + str(ip) + '&range=' + mile_range + '&client_id=' + SEATGEEK_CLIENT_ID
	response = requests.get(query)
	print(response)
	events = response.json()['meta']

	for event in events:
		for artist in artists:
			if event['title'].includes(artist['name']) or event['name'] == artist['name']:
				concerts.append(rec)
	return concerts

def top_artists(user):
	""" Returns artists that the user is interested in."""
	query = SPOTIFY_URL + '/me/top/artists?limit=' + str(q_limit)
	r = requests.get(query, headers={'Authorization': 'Bearer ' + user.spotify_access_token})
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
		artist_obj = Artist.query.filter_by(name=artist).first() # each name should be unique
		users.append(artist_obj.users) # append or concatenate - TODO: check behavior
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
