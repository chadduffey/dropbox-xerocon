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

class UploadFilesForm(Form):
	create_folder = SubmitField('Create Folder in Dropbox')
	upload_files = SubmitField('Upload Files from Dropbox')

class ResetUploadFilesForm(Form):
	submit = SubmitField('Reset File Upload Status')

class SaveFilesForm(Form):
	submit = SubmitField('Save New Files')

class ResetSaveFilesForm(Form):
	submit = SubmitField('Reset File Save Status')