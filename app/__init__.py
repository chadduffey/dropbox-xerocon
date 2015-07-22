from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

# Flask secret key, for securing sessions
app.secret_key = app.config['FLASK_SECRET_KEY']

db = SQLAlchemy(app)
Bootstrap(app)

from app import views, models