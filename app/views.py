from app import app, db
from models import User
import os
import binascii # for generating CSRF
from flask import url_for, render_template, request, redirect, abort, session, flash, g
from forms import XeroAuthForm, SettingsForm

import dropbox
import dropbox_auth

from xero import Xero
import xero_auth 

USER_ID_KEY = 'uid'

# Set up the user object
@app.before_request
def before_request():
    g.user = None
    if USER_ID_KEY in session:
        g.user = User.query.get(session[USER_ID_KEY])
    if not g.user: # if the user hasn't been set up yet, or isn't in the database
        g.user = User()
        db.session.add(g.user)
        db.session.commit()
        session[USER_ID_KEY] = g.user.id
        session.permanent = True

# Make the user object available in all templates
@app.context_processor
def inject_user():
    return dict(user=g.user)


@app.route('/', methods=['GET', 'POST'])
def index():
    dropbox_auth_url = None
    if not g.user.is_logged_in_to_dropbox():
        session['dropbox_csrf'] = binascii.hexlify(os.urandom(40))
        dropbox_auth_url = dropbox_auth.authorization_url(session['dropbox_csrf'])

    xero_auth_url = None
    xero_auth_form = XeroAuthForm()
    if not g.user.is_logged_in_to_xero():
        # if user is authorizing for Xero
        if xero_auth_form.validate_on_submit():
            verification_code=xero_auth_form.verification_code.data.strip()
            rok = session['rok']
            ros = session['ros']
            (org_id, token, secret, seconds_valid, error, error_details) = xero_auth.authorize(verification_code, rok, ros)
            if error:
                flash('Error %s: %s' % (error, error_details))
            else:
                # get org info for the name - also validates that we have access
                xero = Xero(xero_auth.XeroCredentials(token, secret))
                org_name = xero.organisations.all()[0]["Name"]

                g.user.xero_login(org_id, org_name, token, secret, seconds_valid)

                return redirect(url_for('index')) # redirect in order to clear the POST variables
        else:
            xero_auth_url, rok, ros = xero_auth.obtain_authorization_url()
            session['rok'] = rok
            session['ros'] = ros

    return render_template("main.html", dropbox_auth_url=dropbox_auth_url, 
        xero_auth_url=xero_auth_url, xero_auth_form=xero_auth_form)


@app.route('/dropbox_auth_redirect')
def process_dropbox_auth_redirect():
    if request.args['state'] == session['dropbox_csrf'] and request.args['code']:
        (dropbox_uid, access_token) = dropbox_auth.get_access_token(request.args['code'])

        # get users account info for their email - also validates the access token
        dbx = dropbox.Dropbox(access_token)
        dbx_account = dbx.users_get_current_account()

        g.user.dropbox_login(dropbox_uid, dbx_account.email, access_token)
        return redirect(url_for('index'))

    abort(401)


@app.route('/dropbox-logout')
def dropbox_logout():
    g.user.dropbox_logout()
    return redirect(url_for('index'))

@app.route('/xero-logout')
def xero_logout():
    g.user.xero_logout()
    return redirect(url_for('index'))

