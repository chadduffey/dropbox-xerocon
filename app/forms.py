from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import Required
from wtforms import ValidationError

class XeroAuthForm(Form):
	verification_code = StringField('2. Enter the Xero verification code here:', validators=[Required()])
	submit = SubmitField('Authorize')

class SettingsForm(Form):
	save_invoices = BooleanField('Save a PDF copy of every Xero invoice to Dropbox', validators=[Required()])
	sync_files = BooleanField('Sync files between Xero Files and Dropbox', validators=[Required()])
	submit = SubmitField('Save')