from app import app, db
import datetime

class DropboxAccount(db.Model):
	__tablename__ = 'dropbox_account'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.Text)
	access_token = db.Column(db.Text)

	# assume email is fixed (even though it could technically change)
	def __init__(self, id, email):
		self.id = id
		self.email = email

	def __repr__(self):
	    return '<DropboxAccount %r (%r)>' % (self.id, self.email)

	def login(self, access_token):
		self.access_token = access_token
    	db.session.commit()

	def logout(self):
		self.access_token = None
		db.session.commit()

	def is_logged_in(self):
		return self.access_token is not None


class XeroOrg(db.Model):
	__tablename__ = 'xero_org'

	id = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text)
	token = db.Column(db.Text)
	secret = db.Column(db.Text)
	expires = db.Column(db.DateTime)

	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __repr__(self):
		return '<XeroOrg %r (%r)>' % (self.id, self.name)

	def login(self, token, secret, seconds_valid):
		self.token = token
		self.secret = secret
		self.expires = datetime.datetime.now() + datetime.timedelta(seconds=int(seconds_valid))
    	db.session.commit()

	def logout(self):
		self.resource_owner_key = None
		self.resource_owner_secret = None
		expires = datetime.datetime.now() - 1
		db.session.commit()

	def is_logged_in(self):
		if self.expires > datetime.datetime.now():
			return True

	# return time remaining in Xero session, in seconds
	def session_time_remaining(self):
		return (self.expires - datetime.datetime.now()).seconds


class User(db.Model):
	__tablename__ = 'app_user'

	id = db.Column(db.Integer, primary_key=True)
	dropbox_account_id = db.Column(db.Integer, db.ForeignKey('dropbox_account.id'))
	dropbox_account = db.relationship('DropboxAccount', backref=db.backref('user', lazy='dynamic'))
	xero_org_id = db.Column(db.Text, db.ForeignKey('xero_org.id'))
	xero_org = db.relationship('XeroOrg', backref=db.backref('user', lazy='dynamic'))

	last_invoices_sync = db.Column(db.DateTime)
	last_files_sync = db.Column(db.DateTime)	
	dropbox_file_cursor = db.Column(db.Text)

	def __repr__(self):
		return '<User %r>' % self.id

	def is_logged_in_to_dropbox(self):
		if self.dropbox_account:
			return self.dropbox_account.is_logged_in()
		return False

	def is_logged_in_to_xero(self):
		if self.xero_org:
			return self.xero_org.is_logged_in()
		return False

	def dropbox_login(self, id, email, access_token):
		if self.dropbox_account and (self.dropbox_account.id != id or self.dropbox_account.email != email):
			db.session.delete(self.dropbox_account)
			db.session.commit()
		if not self.dropbox_account:
			self.dropbox_account = DropboxAccount(id=id, email=email)
			db.session.add(self.dropbox_account)

		self.dropbox_account.login(access_token)
		db.session.commit()

	def dropbox_logout(self):
		if self.dropbox_account:
			db.session.delete(self.dropbox_account)
			db.session.commit()

	def xero_login(self, id, name, token, secret, seconds_valid):
		if self.xero_org and (self.xero_org.id != id or self.xero_org.name != name):
			db.session.delete(self.xero_org)
			db.session.commit()
		if not self.xero_org:
			self.xero_org = XeroOrg(id=id, name=name)
			db.session.add(self.xero_org)

		self.xero_org.login(token, secret, seconds_valid)
		db.session.commit()

	def xero_logout(self):
		if self.xero_org:
			db.session.delete(self.xero_org)
			db.session.commit()

