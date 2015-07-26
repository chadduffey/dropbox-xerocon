from app import app
from flask import url_for
import requests

def oauth_redirect_url():
	return url_for('process_dropbox_auth_redirect', _external=True)

# Given a CSRF token (for session validation), return the URL to send the user to authorize
def authorization_url(csrf_token):
	url = "https://www.dropbox.com/1/oauth2/authorize?"
	url += "client_id=" + app.config['DROPBOX_APP_KEY']
	url += "&response_type=code&redirect_uri=" + oauth_redirect_url()
	url += "&state=" + csrf_token
	return url

# Given the auth code from a call to /authorize, returns the Dropbox UID and matching access token
def get_access_token(auth_code):
	url = "https://api.dropbox.com/1/oauth2/token?"
	url += "code=" + auth_code
	url += "&grant_type=" + "authorization_code"
	url += "&redirect_uri=" + oauth_redirect_url()
	url += "&client_id=" + app.config['DROPBOX_APP_KEY']
	url += "&client_secret=" + app.config['DROPBOX_APP_SECRET']
	
	r = requests.post(url=url)
	response = r.json()
	return response['uid'], response['access_token']
	