import os
from app import app
from flask import render_template

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'ethan'}
    return render_template('index.html', title='Home', user=user)
