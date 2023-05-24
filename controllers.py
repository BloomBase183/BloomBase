"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .common import db, session, T, cache, auth, signed_url, Field

from .email_auth import EmailAuth
url_signer = URLSigner(session)
# auth = EmailAuth(session, url_signer)

@action('index')
@action.uses('index.html', auth, db, session, url_signer, auth)
# @action.uses('index.html', db, auth.user)
def index():
    return dict(
    url_signer = url_signer,
    auth = auth
    )

@action('profile')
@action.uses('profile.html', db, auth, auth.enforce(), url_signer.verify(), session)
def profile():
    if  len(db(db.users.user_email == get_user_email()).select()) > 0:
        #checks if the user exists in the database. If so then take their entry for the user field, otherwise just take their email
        user = db(db.users.user_email == get_user_email()).select()
    else:
        user = [session.get("_user_email")]
    if user is None:
        redirect(URL('index'))
    #interests = db(db.interests.user_id == auth.current_user.get('id')).select()
    return dict(
        current_user = user,
        #interests are empty for now
        interests = [],
        url_signer = url_signer,
        auth = auth
    )


@action('create_profile', method=["GET", "POST"])
@action.uses('create_profile.html', db, auth.enforce(), url_signer.verify(), session)
def create_profile():
    #creates an entry into the database, currently only associated with the name fields
    user = db(db.users.user_email == get_user_email()).select()
    if len(user) < 1:
        #don't have an account associated with the email
        form = Form([Field('first_name'), Field('last_name')], csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            db.users.insert(first_name=form.vars["first_name"], last_name=form.vars["last_name"])
            redirect(URL('profile', signer=url_signer))
        return dict(form=form, url_signer = url_signer, auth = auth)
    else:
        #The user already has an existing profile
        redirect(URL('index'))


@action('edit_profile', method=["GET", "POST"])
@action.uses('edit_profile.html', db, auth.enforce(), url_signer.verify(), session)
def edit_profile():
    #currently only works with the name fields
    user = db(db.users.user_email == get_user_email()).select()
    if len(user) < 1:
        #user not found, so we instead make a new database entry for them
        redirect(URL('create_profile', signer=url_signer))
    else:
        form = Form(db.users, record=user[0], deletable=False, csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            redirect(URL('profile', signer=url_signer))
        return dict(form=form, url_signer = url_signer, auth = auth)

# unfinished for now
# @action('add_interest/<user_id:int>', method=["GET", "POST"])
# @action.uses('add_interest.html', db, auth.enforce(), url_signer.verify(), session)
# def add_interest(user_id = None):
#     assert user_id is not None
#     form = Form([Field('interest_category'), Field('Name'), Field('Weight')], csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#       db.interests.insert(interest_category=form.vars["interest_category"], interest_name=form.vars["Name"], weight=form.vars["Weight"], user_id = user_id)
#       redirect(URL('index'))
#     return dict(form=form)
# #def add_interest(user_id = None):
# #    form = Form(db.interests, creator = user_id, csrf_session=session, formstyle=FormStyleBulma)
# #    if form.accepted:
# #      redirect(URL('index'))
# #    return dict(form=form)
#
# @action('delete_interest/<user_id:int>')
# @action.uses(db, auth.enforce(), url_signer.verify())
# def delete_contact(contact_id=None):
#     assert contact_id is not None
#     db(db.interests.id == contact_id).delete()
#     redirect(URL('index'))