from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests

#<Really slack> 
#(Getting rid of insecure warning for this hack up)
import warnings
warnings.filterwarnings("ignore")
#</Really slack>

client_key = 'ADATDGXMOMVM1ASRTQTXDOHRUQNNO7'
client_secret = 'F4EEJL5ZLPHAC5JJJ5IVI1IHXJHADO'

request_token_url = 'https://api.xero.com/oauth/RequestToken'
oauth = OAuth1(client_key, client_secret=client_secret)
r = requests.post(url=request_token_url, auth=oauth)

from urlparse import parse_qs
credentials = parse_qs(r.content)
resource_owner_key = credentials.get('oauth_token')[0]
resource_owner_secret = credentials.get('oauth_token_secret')[0]

base_authorization_url = 'https://api.xero.com/oauth/Authorize'
authorize_url = base_authorization_url + '?oauth_token='
authorize_url = authorize_url + resource_owner_key

print 'Please go here to authorize: ' 
print authorize_url
verifier = raw_input('Please input the verifier: ')

#3
access_token_url = 'https://api.xero.com/oauth/AccessToken'

oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

r = requests.post(url=access_token_url, auth=oauth)

credentials = parse_qs(r.content)
resource_owner_key = credentials.get('oauth_token')[0]
resource_owner_secret = credentials.get('oauth_token_secret')[0]

#url = 'https://api.xero.com/api.xro/2.0/Contacts'
url = raw_input('Please enter the Xero API endpoint you want (or "quit"): ')

while url != "quit":
	auth = OAuth1(client_key, 
					client_secret=client_secret, 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)
	result = requests.get(url, auth=auth)

	print result.content
	url = raw_input('Please enter the Xero API endpoint you want (or "quit"): ')
