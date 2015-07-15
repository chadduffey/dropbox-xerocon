from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from wtforms import ValidationError

class TokenForm(Form):
	token = StringField('2. Enter the XERO token here:', validators=[Required()])
	submit = SubmitField('Authorize')