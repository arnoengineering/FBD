# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
from PyQt5.QtCore import QSettings
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import pandas as pd

# Internal imports
#from db import init_db_command
# from user import User

# Configuration
settings = QSettings('Claassens Software', 'Users')
settings.beginGroup('key')



GOOGLE_CLIENT_ID = settings.value('client_id')# os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = settings.value('client_secret')
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

users = []
active_user = None
# # Naive database setup
# try:
#     init_db_command()
# except sqlite3.OperationalError:
#     # Assume it's already been created
#     pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@app.route("/")
def index():
    print('index')
    if active_user is not None:
        print('user exists')
        if active_user['Activated']:
            print('is active')
            return (
                "<p>Hello, {}! You're logged in! Email: {}</p>"
                "<div><p>Google Profile Picture:</p>"
                '<img src="{}" alt="Google profile pic"></img></div>'
                '<a class="button" href="/logout">Logout</a>'.format(
                    active_user['given_name'], active_user['email'], active_user['picture']
                )
            )
        else:
            print('not activ')
    else:
        print('no user exists')
    return '<a class="button" href="/login">Google Login</a>'


def get_google_provider_cfg():
    print('google config')
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    print('login')
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    print(request_uri)
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    print('calback')
    global active_user
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    print('tockens')
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    print('parse')
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    print('email to verif')
    if userinfo_response.json().get("email_verified"):
        print('email yes verif')
        user_d = {'Activated': True}
        for i in ["sub", "email", "picture", "given_name"]:
            user_d[i] = userinfo_response.json()[i]
        users.append(user_d)
        active_user = user_d
    else:
        print('email not verified')
        return "User email not available or not verified by Google.", 400

    # Begin user session by logging the user in
    # Begin user session by logging the user in
    # login()
    # login_user(user)

    # Send user back to homepage
    print('redirect to index')
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    print('logout')
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc")