from app import app, db
from models import DropboxUser, XeroAuth
import os
import binascii # for generating CSRF
from flask import url_for, render_template, request, redirect, abort, session
from forms import TokenForm

import dropbox
import dropbox_auth

from xero_auth import obtain_authorization_url, authorize 
from xero_api import xero_file_listing, xero_folder_listing

DROPBOX_UID_KEY = 'dropbox_uid'

@app.route('/', methods=['GET', 'POST'])
def index():
    user = None
    if DROPBOX_UID_KEY in session:
        user = DropboxUser.query.get(session[DROPBOX_UID_KEY])

    # If the user is an authorized Dropbox user
    if user:
        form = TokenForm()
        if form.validate_on_submit():
            token=form.token.data.strip()
            rok = session['rok']
            ros = session['ros']
            resource_owner_key, resource_owner_secret = authorize(token, rok, ros)
            data = xero_folder_listing(resource_owner_key, resource_owner_secret)
            return render_template("temp_data.html", data=data)
        else:
            authorization_url, rok, ros = obtain_authorization_url()
            session['rok'] = rok
            session['ros'] = ros

        return render_template("main.html", form=form, authorization_url = authorization_url)

    else:
        session['dropbox_csrf'] = binascii.hexlify(os.urandom(40))
        return redirect(dropbox_auth.authorization_url(session['dropbox_csrf']))

@app.route('/dropbox_auth_redirect', methods=['GET', 'POST'])
def process_dropbox_auth_redirect():
    if request.args['state'] == session['dropbox_csrf'] and request.args['code']:
        (dropbox_uid, access_token) = dropbox_auth.get_access_token(request.args['code'])

        # get users account info for their email - also validates the access token
        dbx = dropbox.Dropbox(access_token)
        dbx_account = dbx.users_get_current_account()

        user = DropboxUser.query.get(session[DROPBOX_UID_KEY])
        # if user already exists, just update the auth token and email
        if user:
            user.email = dbx_account.email
            user.access_token = access_token
        else:
            user = DropboxUser(id=dropbox_uid, email=dbx_account.email, auth_token=access_token)
            db.session.add(user)
        
        db.session.commit()
        session[DROPBOX_UID_KEY] = dropbox_uid

        return redirect(url_for('index'))

    abort(401)
