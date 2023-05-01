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
<<<<<<< HEAD

from .models import get_user_email
from . common import db, session, T, cache, auth, signed_url

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db)
def index():
        ### You have to modify the code here as well.
        return dict()
=======
from .models import get_user_email
from .common import db, session, T, cache, auth, signed_url

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db)
# @action.uses('index.html', db, auth.user)
def index():
    return dict()
>>>>>>> b78aaf6da7af0757c9d9388702713fa2e804bb1f
