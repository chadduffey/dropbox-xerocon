from app import app
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests

def xero_file_listing(oauth):
	url = 'https://api.xero.com/files.xro/1.0/Files'
	result = requests.get(url, auth=auth)

	return result.content

def xero_folder_listing(oauth):
	url = 'https://api.xero.com/files.xro/1.0/Folders'
	result = requests.get(url, auth=auth)

	return result.content