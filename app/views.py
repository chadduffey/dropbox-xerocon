from app import app, db
from models import User
import os
import binascii # for generating CSRF
from flask import url_for, render_template, request, redirect, abort, session, flash, g
import forms
from datetime import datetime

import dropbox
import dropbox_auth

from xero import Xero, utils # PyXero
import xero_auth 

USER_ID_KEY = 'uid'

# Set up the user object
@app.before_request
def before_request():
    g.user = None
    if USER_ID_KEY in session:
        g.user = User.query.get(session[USER_ID_KEY])
    if not g.user: # if the user hasn't been set up yet, or isn't in the database
        g.user = User()
        db.session.add(g.user)
        db.session.commit()
        session[USER_ID_KEY] = g.user.id
        session.permanent = True

# Make the user object available in all templates
@app.context_processor
def inject_user():
    return dict(user=g.user)

@app.route('/', methods=['GET', 'POST'])
def index():
    dropbox_auth_url = None
    if not g.user.is_logged_in_to_dropbox():
        session['dropbox_csrf'] = binascii.hexlify(os.urandom(40))
        dropbox_auth_url = dropbox_auth.authorization_url(session['dropbox_csrf'])

    xero_auth_url = None
    xero_auth_form = forms.XeroAuthForm()
    if not g.user.is_logged_in_to_xero():
        # if user is authorizing for Xero
        if xero_auth_form.validate_on_submit():
            verification_code=xero_auth_form.verification_code.data.strip()
            process_xero_auth(verification_code=verification_code)
            return redirect(url_for('index')) # redirect in order to clear the POST variables
        else:
            xero_auth_url, rok, ros = xero_auth.obtain_authorization_url()
            session['rok'] = rok
            session['ros'] = ros

    return render_template("main.html", dropbox_auth_url=dropbox_auth_url, 
        xero_auth_url=xero_auth_url, xero_auth_form=xero_auth_form,
        save_invoices_form=forms.SaveInvoicesForm(), reset_invoices_form=forms.ResetInvoicesForm(),
         sync_files_form=forms.SyncFilesForm(), reset_files_form=forms.ResetFilesForm())


@app.route('/dropbox/auth_redirect')
def process_dropbox_auth_redirect():
    if request.args['state'] == session['dropbox_csrf'] and request.args['code']:
        (dropbox_uid, access_token) = dropbox_auth.get_access_token(request.args['code'])

        # get users account info for their email - also validates the access token
        dbx = dropbox.Dropbox(access_token)
        dbx_account = dbx.users_get_current_account()

        g.user.dropbox_login(dropbox_uid, dbx_account.email, access_token)
        return redirect(url_for('index'))

    abort(401)


def process_xero_auth(verification_code):
    rok = session['rok']
    ros = session['ros']
    (org_id, token, secret, seconds_valid, error, error_details) = xero_auth.authorize(verification_code, rok, ros)
    if error:
        flash('Error %s: %s' % (error, error_details))
    else:
        # get org info for the name - also validates that we have access
        xero = Xero(xero_auth.XeroCredentials(token, secret))
        org_name = xero.organisations.all()[0]["Name"]

        g.user.xero_login(org_id, org_name, token, secret, seconds_valid)


@app.route('/save_invoices', methods=['POST'])
def save_invoices():
    xero = Xero(g.user.xero_credentials())
    dbx = dropbox.Dropbox(g.user.dropbox_credentials())
    base_path = g.user.invoices_folder_path
    ensure_dbx_folder_exists(dbx=dbx, path=base_path)

    if g.user.last_invoices_sync:
        # get only invoices modified since our last sync
        invoices = xero.invoices.filter(since=g.user.last_invoices_sync)
    else:
        # get all invoices
        invoices = xero.invoices.all()

    for invoice in invoices:
        # if there's a contact name, organize by contact
        if invoice['Contact']['Name']:
            folder_path = base_path+'/'+invoice['Contact']['Name']
            ensure_dbx_folder_exists(dbx=dbx, path=folder_path)
        else:
            folder_path = base_path

        # format as date + InvoiceNumber
        date_str = utils.parse_date(invoice['Date']).strftime('%Y-%m-%d')
        file_path = folder_path+'/'+date_str+' '+invoice['InvoiceNumber']+'.pdf'
        invoice_pdf = xero.invoices.get(invoice['InvoiceID'], headers={'Accept': 'application/pdf'})

        dbx.files_upload(f=invoice_pdf, path=file_path, mode=dropbox.files.WriteMode.overwrite, 
            autorename=True, client_modified=utils.parse_date(invoice['UpdatedDateUTC']), mute=False)

        print "Saved invoice: %s" % file_path #!#

    g.user.mark_invoices_synced()
    flash("Invoices saved!")
    return redirect(url_for('index'))


@app.route('/reset_invoices', methods=['POST'])
def reset_invoices():
    g.user.mark_invoices_synced(time=None)
    return redirect(url_for('index'))


@app.route('/sync_files', methods=['POST'])
def sync_files():
    xero = Xero(g.user.xero_credentials())
    dbx = dropbox.Dropbox(g.user.dropbox_credentials())
    base_path = g.user.files_folder_path
    ensure_dbx_folder_exists(dbx=dbx, path=base_path)

    folders = {}
    xero_inbox_folder_id = None
    xero_folders = xero.filesAPI.folders.all()
    for folder in xero_folders:
        if folder['IsInbox']:
            xero_inbox_folder_id = folder['Id'] # treat the Xero inbox folder as the base Dropbox folder
        else:
            # add any folders that don't exist on Dropbox
            ensure_dbx_folder_exists(dbx=dbx, path=base_path+'/'+folder['Name'])

    #!# TODO: add support for Xero pagination
    #!# TODO: no support for cursors since Xero doesn't have support
    xero_files = xero.filesAPI.files.all()['Items']
    dbx_result = dbx.files_list_folder(path=base_path) #!# recursive = True not available?

    # cycle through and gather all Dropbox entries in the base dir
    dbx_entries = dbx_result.entries
    while dbx_result.has_more:
        dbx_result = dbx.files_list_folder_continue(cursor=dbx_result.cursor)
        dbx_entries.append(dbx_result.entries)

    print "Dropbox entries: %s" % dbx_entries #!#

    subfolder_entries = []

    # process folder and deleted contents
    for entry in dbx_entries:
        # add any folders that don't exist on Xero
        if isinstance(entry, dropbox.files.FolderMetadata):
            if not get_xero_obj_by_name(xero_folders, entry.name):
                xero.filesAPI.folders.create({"name": entry.name})
                print "Created folder on Xero: %s" % entry.name #!#
            # get subfolder entries (since apparently recursive isn't working)
            subfolder_result = dbx.files_list_folder(path=entry.path_lower)
            subfolder_entries.append(subfolder_result.entries)
            while subfolder_result.has_more:
                subfolder_result = dbx.files_list_folder_continue(cursor=subfolder_result.cursor)
                subfolder_entries.append(subfolder_result.entries)

        # ignore deleted files / folders for now
        if isinstance(entry, dropbox.files.DeletedMetadata):
            xero_file = get_xero_obj_by_name(xero_files, entry.name)

    # filter to just files
    dbx_files = [entry for entry in dbx_entries if isinstance(entry, dropbox.files.FileMetadata)]
    subfolder_files = [entry for entry in subfolder_entries if isinstance(entry, dropbox.files.FileMetadata)]
    dbx_files.append(subfolder_files)

    # write Xero files to Dropbox
    for xero_file in xero_files:
        if xero_file['FolderId'] == xero_inbox_folder_id:
            folder_path = base_path
        else: # if this is in a folder other than the inbox, add the folder name to the path
            folder_path = base_path+'/'+get_xero_obj_by_id(xero_folders,xero_file['FolderId'])['Name']
        file_path = folder_path+'/'+xero_file['Name']

        matching_dropbox_file = dropbox_entry_for_path(dbx_entries=dbx_files, path=file_path)
        # if it doesn't exist on Dropbox, or if the Xero file is newer, create it
        if not matching_dropbox_file or matching_dropbox_file.client_modified < datetime_from_utc(xero_file['UpdatedDateUtc']):
            file_content = xero.filesAPI.files.get_content(xero_file['Id'])

            dbx.files_upload(f=file_content, path=file_path, mode=dropbox.files.WriteMode.overwrite, 
                autorename=True, client_modified=datetime_from_utc(xero_file['UpdatedDateUtc']), mute=False)

            print "Created file on Dropbox: %s" % file_path #!#

    # write Dropbox files to Xero
    for entry in dbx_files:
        matching_xero_file = get_xero_obj_by_name(xero_files, entry.name)

        # if it doesn't exist in Xero, or if the Dropbox file is newer, create it
        if not matching_xero_file or datetime_from_utc(matching_xero_file['UpdatedDateUtc']) < entry.client_modified:
            path_elems = entry.path_lower.split('/')
            folder_name = path_elems[len(path_elems) - 2]
#!# TODO: FIX THIS!
#            xero_folder_id = get_xero_obj_by_name(xero_folders,folder_name)['Id']
#
#            (metadata, response) = dbx.files_download(entry.path_lower)
#            xero.filesAPI.files.upload_file(entry.name, response.content, xero_folder_id)

#            print "Created file on Xero: %s" % entry.name #!#

    # save the cursor
    g.user.dropbox_file_cursor = dbx_result.cursor
    g.user.mark_files_synced() # also calls db.session.commit()

    flash("Synced files!")
    return redirect(url_for('index'))


@app.route('/reset_files', methods=['POST'])
def reset_files():
    g.user.mark_files_synced(time=None)
    return redirect(url_for('index'))


# make sure that we have a valid Dropbox folder to write into
# will return a conflict if already exists, but that's fine
def ensure_dbx_folder_exists(dbx, path):
    try:
        dbx.files_create_folder(path=path)
    except dropbox.exceptions.ApiError as err:
        if not err.reason.is_conflict_folder():
            print "Dropbox API error: %s" % err
            abort(500)
    print "Created folder on Dropbox: %s" % path #!#


def dropbox_entry_for_path(dbx_entries, path):
    for entry in dbx_entries:
        if entry.path_lower == path.lower():
            return entry
    return None


# given an array of Xero objects, find the right object by ID
def get_xero_obj_by_id(objects, Id):
    for obj in objects:
        if obj['Id'] == Id:
            return obj
    return None


# given an array of Xero objects, find the right object by name
def get_xero_obj_by_name(objects, name):
    for obj in objects:
        if obj['Name'].lower() == name.lower():
            return obj
    return None


def datetime_from_utc(utc_time):
    return datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S.%f0")


@app.route('/dropbox/webhook')
def process_webhook(request): #!#
    if request.method == 'GET':
        # Respond to the webhook verification (GET request) by echoing back the challenge parameter
        return HttpResponse(request.GET["challenge"])

    print "Dropbox webhook received: " + str(datetime.now())


@app.route('/dropbox/logout')
def dropbox_logout():
    g.user.dropbox_logout()
    return redirect(url_for('index'))

@app.route('/xero/logout')
def xero_logout():
    g.user.xero_logout()
    return redirect(url_for('index'))

