from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests

#TODO: this is very slack
import warnings
warnings.filterwarnings("ignore")

def xero_file_listing(resource_owner_key, resource_owner_secret):
	url = 'https://api.xero.com/files.xro/1.0/Files'
	auth = OAuth1(XERO_CLIENT_KEY, 
					client_secret=XERO_CLIENT_SECRET, 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)
	result = requests.get(url, auth=auth)

	return result.content

def xero_folder_listing(resource_owner_key, resource_owner_secret):
	url = 'https://api.xero.com/files.xro/1.0/Folders'
	auth = OAuth1(XERO_CLIENT_KEY, 
					client_secret=XERO_CLIENT_SECRET, 
					resource_owner_key=resource_owner_key, 
					resource_owner_secret=resource_owner_secret)
	result = requests.get(url, auth=auth)

	return result.content	