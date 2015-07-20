from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

# Flask secret key, for securing sessions
app.secret_key = FLASK_SECRET_KEY

from app import views