from app import app, db
import datetime

#TODO: create an actual schema!
class DropboxUser(db.Model):
	__tablename__ = 'dropbox_user'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80), unique=True)
	auth_token = db.Column(db.Text)

	xero_auth_id = db.Column(db.Integer, db.ForeignKey('xero_auth.id'))
	xero_auth = db.relationship('XeroAuth', backref=db.backref('dropboxuser', lazy='dynamic'), uselist=False)

	save_invoices = db.Column(db.Boolean)
	sync_files = db.Column(db.Boolean)
	last_sync = db.Column(db.DateTime)
	dropbox_cursor = db.Column(db.Text)

	def __init__(self, id, email, auth_token):
		self.id = id
		self.email = email
		self.auth_token = auth_token

	def __repr__(self):
	    return '<User %r>' % self.email


class XeroAuth(db.Model):
	__tablename__ = 'xero_auth'

	id = db.Column(db.Integer, primary_key=True)
	resource_owner_key = db.Column(db.Text)
	resource_owner_secret = db.Column(db.Text)
	created = db.Column(db.DateTime)
	expires = db.Column(db.DateTime)

	def __init__(self, resource_owner_key, resource_owner_secret, creation_time=None):
		self.dropboxuser_id = dropboxuser_id
		self.resource_owner_key = resource_owner_key
		self.resource_owner_secret = resource_owner_secret

		if not creation_time:
			creation_time = datetime.datetime.now()

		self.created = creation_time
		self.expires = creation_time + timedelta(minutes=app.config['XERO_AUTH_DURATION_MIN'])

	def __repr__(self):
		return '<XeroAuth %r (created %r)>' % (self.resource_owner_key, self.created)
