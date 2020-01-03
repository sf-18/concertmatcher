from app import app, db
import os
import requests
import base64
from flask import render_template, request, redirect, session
from flask_session import Session
from dateutil.parser import parse

from concertlogic import *
from tempfile import mkdtemp
# Sets environment variables
import config

# Avoids broken pipe error 
try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False

Session(app)

user = None 

user_info = {
    'access_token': None,
    'refresh_token': None,
    'id': None
}


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)

@app.route('/')
@app.route('/index')
def index():
    if user_info['access_token'] and user:
        # Find concerts 
        concerts = find_concerts(user)
        return render_template('index.html', concerts=concerts)
    else:
        return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html', cid=SPOTIFY_CLIENT_ID, ac=user_info['access_token'], message="Welcome! Please log in.")

@app.route('/logout')
def logout():
    global user, user_info
    user = None 
    user_info = user_info.fromkeys(user_info, None)
    return render_template('login.html', cid=SPOTIFY_CLIENT_ID, ac=user_info['access_token'], message="You have been logged out.")

@app.route('/callback/')
def callback():
    url = request.url
    # Converts url into a query object and extracts auth code
    query = parse_qs(urlparse(url).query)
    if 'code' in query:
        global user_access_token, user
        code = query['code']
        # Construct post request to retrieve access token
        data = {'grant_type':'authorization_code',
                'code': code,
                'redirect_uri': request.base_url,
                'client_id': SPOTIFY_CLIENT_ID,
                'client_secret': SPOTIFY_CLIENT_SECRET}
        
        get_tokens(data)

        user_info['id'] = get_user_obj(user_info['access_token'])['id']

        # ADD USER TO DB
        if not SpotifyUser.query.filter_by(spotify_user_id=user_info['id']).count():
            db.session.add(SpotifyUser(spotify_user_id=user_info['id'], spotify_access_token=user_info['access_token']))
            db.session.commit()

        user = SpotifyUser.query.filter_by(spotify_user_id=user_info['id']).first()
        # Checks if current access token in database is expired
        valid_token(user.spotify_access_token, user)

        try:
            update_relations(user)
        # If concertlogic.py raises a key error, use refresh token to generate new access token
        except KeyError:
            valid_token(user.spotify_access_token)
        else:  
            return redirect('/index')

    else:
        return redirect('/login')

# Gets all info on the current user
def get_user_obj(token):
    response = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': 'Bearer ' + token})
    response = response.json()
    return response

# Checks if access token is still valid 
def valid_token(token, user):
    # No valid endpoint on spotify api for checking expiration; send "test" request to check
    response = get_user_obj(token)

    if 'error' in response:
        print("updating access token...")

        data = {
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': user_info['refresh_token']
        }

        get_tokens(data)
        user.spotify_access_token = user_info['access_token']
        db.session.commit()

# Updates access and refresh tokens, if any provided
def get_tokens(data):
    response = requests.post('https://accounts.spotify.com/api/token', data=data)
    response = response.json()

    print(response)

    user_info['access_token'] = response["access_token"]

    if 'refresh_token' in response:
        user_info['refresh_token'] = response["refresh_token"]