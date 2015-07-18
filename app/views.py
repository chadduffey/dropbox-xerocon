from app import app
from flask import url_for, render_template, request, redirect, abort, session
from flask_bootstrap import Bootstrap
from forms import TokenForm
import dropbox
from xero_functions import obtain_authorization_url, authorize, api_query

# Flask secret key, for securing sessions
app.secret_key = '\x0c\xb5UK\xa8\xc4\xc7\xf1\x03\xe9+\xa3\xac:~Ys\x8aW`+ -\x00'

Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():   
    form = TokenForm()
    if form.validate_on_submit():
        token=form.token.data.strip()
        rok = session['rok']
        ros = session['ros']
        resource_owner_key, resource_owner_secret = authorize(token, rok, ros)
        data = api_query(resource_owner_key, resource_owner_secret)
        return render_template("temp_data.html", data=data)
    else:
        authorization_url, rok, ros = obtain_authorization_url()
        session['rok'] = rok
        session['ros'] = ros

    return render_template("main.html", form=form, authorization_url = authorization_url)