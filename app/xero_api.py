from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests

#this is very slack
import warnings
warnings.filterwarnings("ignore")

#Move this to env variables on heroku later.
client_key = 'ADATDGXMOMVM1ASRTQTXDOHRUQNNO7'
client_secret = 'F4EEJL5ZLPHAC5JJJ5IVI1IHXJHADO'

def xero_file_listing(resource_owner_key, resource_owner_secret):
	url = 'https://api.xero.com/files.xro/1.0/Files'
	auth = OAuth1(client_key, 
					client_secret=client_secret, 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)
	result = requests.get(url, auth=auth)

	return result.content

def xero_folder_listing(resource_owner_key, resource_owner_secret):
	url = 'https://api.xero.com/files.xro/1.0/Folders'
	auth = OAuth1(client_key, 
					client_secret=client_secret, 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)
	result = requests.get(url, auth=auth)

	return result.content	