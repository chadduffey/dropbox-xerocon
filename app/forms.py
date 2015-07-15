from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from wtforms import ValidationError

class TokenForm(Form):
	token = StringField('Token', validators=[Required()])
	submit = SubmitField('Authorize')