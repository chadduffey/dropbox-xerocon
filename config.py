from app import app
import os, pwd

APP_NAME = 'dropbox-xerocon'
FLASK_SECRET_KEY = '\x0c\xb5UK\xa8\xc4\xc7\xf1\x03\xe9+\xa3\xac:~Ys\x8aW`+ -\x00'

# Allow Heroku to set database URL via environment variable
if os.environ.get('DATABASE_URL') is None:
	current_user = pwd.getpwuid(os.getuid())[0]
	SQLALCHEMY_DATABASE_URI = 'postgres:///' + APP_NAME
else:
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Dropbox API variables
DROPBOX_APP_KEY = 'nyc0pnugsh7ix0v'
DROPBOX_APP_SECRET = 'u2i1rvdkmztmv7g'

# Xero API variables
XERO_CLIENT_KEY = 'ADATDGXMOMVM1ASRTQTXDOHRUQNNO7'
XERO_CLIENT_SECRET = 'F4EEJL5ZLPHAC5JJJ5IVI1IHXJHADO'
XERO_AUTH_DURATION_MIN = 30

# Set up log to write to stdout
import logging
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)
app.logger.info(APP_NAME)