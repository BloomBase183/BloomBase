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
from .common import db, session, T, cache, auth, signed_url

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db, session, url_signer)
# @action.uses('index.html', db, auth.user)
def index():
    return dict(
    url_signer = url_signer
    )

@action('profile')
@action.uses('profile.html', db, auth.user, url_signer.verify(), session)
def profile():
    interests = db(db.interests.user_email == get_user_email()).select()
    return dict(
    interests = interests,
    url_signer = url_signer
    )

@action('edit_profile', method=["GET", "POST"])
@action.uses('edit_profile.html', db, auth.user, url_signer.verify(), session)
def edit_contact(contact_id=None):
    #ensure an id was given
    assert contact_id is not None
    profile = db.users[contact_id]
    if contact is None or contact.created_by != auth.current_user.get('id'):
        #contact not found, or invalid user accessing
        redirect(URL('index'))
    else:
        #contact exists
        return dict(rows = db(db.phone.contact_id == contact_id).select(), url_signer = url_signer, contact = contact)