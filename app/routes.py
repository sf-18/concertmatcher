import os
import requests
import base64
from app import app
from flask import render_template, request, redirect
# from flask_login import login_required, current_user
try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
user_access_token, user_refresh_token = None, None

@app.route('/')
@app.route('/index')
def index():
    print(user_access_token)
    if user_access_token:
        user = {'token': user_access_token}
        return render_template('index.html', title='Home', user=user)
    else:
        return redirect("/login")

@app.route('/login')
def login():
    return render_template('login.html', cid=client_id)

@app.route('/logout')
def logout():
    user_access_token, user_refresh_token = None, None
    return render_template('login.html', cid=client_id)

@app.route('/callback/')
def callback():
    url = request.url
    # Converts url into a query object and extracts auth code
    query = parse_qs(urlparse(url).query)
    if 'code' in query:
        global user_access_token, user_refresh_token
        code = query['code']
        # Construct post request to retrieve access token
        data = {'grant_type':'authorization_code',
                'code': code,
                'redirect_uri': request.base_url,
                'client_id': client_id,
                'client_secret': client_secret}

        response = requests.post('https://accounts.spotify.com/api/token', data=data)
        response = response.json()
        user_access_token, user_refresh_token = response["access_token"], response["refresh_token"]

        return redirect('/index')
    else:
        return 'Error in authorization'
