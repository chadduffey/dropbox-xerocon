from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

# Flask secret key, for securing sessions
app.secret_key = app.config['FLASK_SECRET_KEY']

db = SQLAlchemy(app)

from app import views, models