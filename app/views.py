from app import app
from flask import url_for, render_template, request, redirect, abort, session
from flask_bootstrap import Bootstrap

from xero_auth import obtain_authorization_url, authorize 
from xero_api import xero_file_listing, xero_folder_listing
from forms import TokenForm

app.secret_key = 'fix_this'

Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():   
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
