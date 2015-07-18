import requests

#TODO: Dropbox app variables. Move this to env variables on heroku later.
DROPBOX_APP_KEY = "nyc0pnugsh7ix0v"
DROPBOX_APP_SECRET = "u2i1rvdkmztmv7g"
OAUTH_REDIRECT_URI = None #!#

# Given a CSRF token (for session validation), return the URL to send the user to authorize
def dropbox_obtain_authorization_url(csrf_token):
	url = "https://www.dropbox.com/1/oauth2/authorize?"
	url += "client_id=" + DROPBOX_APP_KEY
	url += "&response_type=code&redirect_uri=" + OAUTH_REDIRECT_URI
	url += "&state=" + csrf_token

# Given the auth code from a call to /authorize, returns the Dropbox UID and matching auth token
def dropbox_get_auth_token(auth_code):
	url = "https://api.dropbox.com/1/oauth2/token?"
	url += "code=" + auth_code
	url += "grant_type=" + "authorization_code"
	url += "redirect_uri=" + OAUTH_REDIRECT_URI
	url += "client_id=" + DROPBOX_APP_KEY
	url += "client_secret=" + DROPBOX_APP_SECRET
	
	r = requests.post(url=url)
	response = r.json()
	return response['uid'], response['access_token']

def dropbox_process_webhook(request):
	if request.method == 'GET':
		# Respond to the webhook verification (GET request) by echoing back the challenge parameter
		return HttpResponse(request.GET["challenge"])

	print "Dropbox webhook received: " + str(datetime.now())