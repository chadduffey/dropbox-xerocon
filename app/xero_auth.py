from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
from urlparse import parse_qs
import requests

#TODO: this is very slack
import warnings
warnings.filterwarnings("ignore")

def obtain_authorization_url():
	request_token_url = 'https://api.xero.com/oauth/RequestToken'
	oauth = OAuth1(config['XERO_CLIENT_KEY'], client_secret=config['XERO_CLIENT_SECRET'])
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
	oauth = OAuth1(config['XERO_CLIENT_KEY'],
	                   client_secret=config['XERO_CLIENT_SECRET'],
	                   resource_owner_key=resource_owner_key,
	                   resource_owner_secret=resource_owner_secret,
	                   verifier=verifier)
	r = requests.post(url=access_token_url, auth=oauth)
	credentials = parse_qs(r.content)
	try:
		resource_owner_key = credentials.get('oauth_token')[0]
		resource_owner_secret = credentials.get('oauth_token_secret')[0]
	except:
		resource_owner_key = credentials.get('oauth_problem')[0]
		resource_owner_secret = credentials.get('oauth_problem_advice')[0]	

	return resource_owner_key, resource_owner_secret
