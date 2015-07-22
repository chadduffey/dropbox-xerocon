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
	base_folder_path = db.Column(db.Text)

	last_sync = db.Column(db.DateTime)
	dropbox_cursor = db.Column(db.Text)

	def __init__(self, id, email, auth_token):
		self.id = id
		self.email = email
		self.auth_token = auth_token

	def __repr__(self):
	    return '<User %r>' % self.email


	def xero_is_logged_in(self):
		if self.xero_auth:
			if self.xero_auth.expires > datetime.datetime.now():
				print "Xero login still valid: %s" % self.xero_auth #!#
				return True
			else:
				print "Xero login expired; deleting: %s" % self.xero_auth #!#
				db.session.delete(self.xero_auth)
				db.session.commit()

	# return time remaining in Xero session, in seconds
	def xero_session_time_remaining(self):
		return (self.xero_auth.expires - datetime.datetime.now()).seconds

	def xero_login(self, resource_owner_key, resource_owner_secret):
	    auth = XeroAuth(resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret)
	    db.session.add(auth)
	    self.xero_auth = auth
	    db.session.commit()



class XeroAuth(db.Model):
	__tablename__ = 'xero_auth'

	id = db.Column(db.Integer, primary_key=True)
	resource_owner_key = db.Column(db.Text)
	resource_owner_secret = db.Column(db.Text)
	created = db.Column(db.DateTime)
	expires = db.Column(db.DateTime)

	def __init__(self, resource_owner_key, resource_owner_secret):
		self.resource_owner_key = resource_owner_key
		self.resource_owner_secret = resource_owner_secret

		creation_time = datetime.datetime.now()
		self.created = creation_time
		self.expires = creation_time + datetime.timedelta(minutes=app.config['XERO_AUTH_DURATION_MIN'])

	def __repr__(self):
		return '<XeroAuth %r (created %r)>' % (self.resource_owner_key, self.created)
