from app import app
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
from urlparse import parse_qs
import requests

def obtain_authorization_url():
	request_token_url = 'https://api.xero.com/oauth/RequestToken'
	oauth = OAuth1(app.config['XERO_CLIENT_KEY'], client_secret=app.config['XERO_CLIENT_SECRET'])
	r = requests.post(url=request_token_url, auth=oauth)
	credentials = parse_qs(r.content)
	resource_owner_key = credentials.get('oauth_token')[0]
	resource_owner_secret = credentials.get('oauth_token_secret')[0]
	base_authorization_url = 'https://api.xero.com/oauth/Authorize'
	authorize_url = base_authorization_url + '?oauth_token='
	authorize_url = authorize_url + resource_owner_key

	return authorize_url, resource_owner_key, resource_owner_secret

def authorize(verifier, resource_owner_key, resource_owner_secret):
	access_token_url = 'https://api.xero.com/oauth/AccessToken'
	oauth = OAuth1(app.config['XERO_CLIENT_KEY'],
	                   client_secret=app.config['XERO_CLIENT_SECRET'],
	                   resource_owner_key=resource_owner_key,
	                   resource_owner_secret=resource_owner_secret,
	                   verifier=verifier)
	r = requests.post(url=access_token_url, auth=oauth)
	credentials = parse_qs(r.content)
	org_id = token = secret = seconds_valid = error = error_details = None
	try:
		org_id = credentials.get('xero_org_muid')[0]
		token = credentials.get('oauth_token')[0]
		secret = credentials.get('oauth_token_secret')[0]
		seconds_valid = credentials.get('oauth_expires_in')[0]
	except:
		error = credentials.get('oauth_problem')[0]
		error_details = credentials.get('oauth_problem_advice')[0]	

	return org_id, token, secret, seconds_valid, error, error_details

def oauth(resource_owner_key, resource_owner_secret):
	return OAuth1(app.config['XERO_CLIENT_KEY'], 
					client_secret=app.config['XERO_CLIENT_SECRET'], 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)

# Wrapper class for use with PyXero
class XeroCredentials():
	def __init__(self, token, secret):
		self.oauth = oauth(token, secret)
		self.base_url = app.config['XERO_BASE_URL']

