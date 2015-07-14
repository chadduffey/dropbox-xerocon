from app import app
from flask import url_for, render_template, request, redirect, abort, session

@app.route('/')
def index():
    return "Hello, World!"