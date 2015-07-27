from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import Required
from wtforms import ValidationError

class XeroAuthForm(Form):
	verification_code = StringField('2. Enter the Xero verification code here:', validators=[Required()])
	submit = SubmitField('Authorize')

class SaveInvoicesForm(Form):
	submit = SubmitField('Save New Invoices')

class ResetInvoicesForm(Form):
	submit = SubmitField('Reset Invoice Sync Status')

class SyncFilesForm(Form):
	submit = SubmitField('Sync Files')

class ResetFilesForm(Form):
	submit = SubmitField('Reset File Sync Status')