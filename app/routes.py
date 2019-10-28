import os
import requests
import base64
from app import app
from flask import render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
# Ignores broken pipe warning

from helpers import apology, login_required
from models import SpotifyUser, Artist
from models import db
from concertlogic import *
from tempfile import mkdtemp
import config

# from flask_login import login_required, current_user
try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

app.config["SECRET_KEY"] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False

SEATGEEK_CLIENT_ID = os.environ['SEATGEEK_CLIENT_ID']
SEATGEEK_SECRET = os.environ['SEATGEEK_SECRET']
SEATGEEK_URL = os.environ['SEATGEEK_URL']

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_SECRET']
SPOTIFY_URL = os.environ['SPOTIFY_API_URL']

Session(app)

user_access_token = None
user = None

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)

@app.route('/')
@app.route('/index')
def index():
    if user_access_token and user:
        # Find concerts
        # events = concerts(user)
        return render_template('index.html')
    else:
        return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html', cid=SPOTIFY_CLIENT_ID, ac=user_access_token, message="Welcome! Please log in.")

@app.route('/logout')
def logout():
    user_access_token = None
    # session.clear()
    return render_template('login.html', cid=SPOTIFY_CLIENT_ID, ac=user_access_token, message="You have been logged out.")

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

        response = requests.post('https://accounts.spotify.com/api/token', data=data)
        response = response.json()
        # print(response)

        user = get_user_obj(response["access_token"])

        user_access_token = user['id']

        # ADD USER TO DB
        print('begin')
        spotify_user_id = user['id']
        spotify_access_token = response["access_token"]
        # facebook_user_id = request.args.get('facebook_user_id')
        print(SpotifyUser.query.filter_by(spotify_user_id=spotify_user_id).count())
        if not SpotifyUser.query.filter_by(spotify_user_id=spotify_user_id).count():
            db.session.add(SpotifyUser(spotify_user_id=spotify_user_id, spotify_access_token=spotify_access_token))
            db.session.commit()
        user = SpotifyUser.query.filter_by(spotify_user_id=spotify_user_id).first()
        update_relations(user)

        return redirect('/index')

    else:
        return apology('Error in authorization', 403)

def get_user_obj(token):
    response = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': 'Bearer ' + token})
    response = response.json()

    return response
