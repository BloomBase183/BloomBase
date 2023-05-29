"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'observations_na',
    Field('observed_on', 'date'),
    Field('url'),
    Field('image_url'),
    Field('latitude', 'double'),
    Field('longitude', 'double'),
    Field('species_guess'),
    Field('scientific_name'),
    Field('common_name'),
    Field('iconic_taxon_name'),
    Field('taxon_id', 'integer')
)

db.define_table(
    'users',
    Field('user_email', default=get_user_email),
    Field('first_name', 'string', default=None, requires=IS_NOT_EMPTY()),
    Field('last_name', 'string', default=None, requires=IS_NOT_EMPTY()),
)

db.define_table(
    'interests',
    Field('user_id'),
    # gives the option for more filtering types later
    Field('interest_category', requires=IS_IN_SET(['Species'])),
    # should be a search bar of species we have available, currently takes whatever
    Field('interest_name'),
    # the weight impacts which interests are highest priority
    Field('interest_weight', 'integer', requires=IS_INT_IN_RANGE(1, 11)),
)


db.interests.user_id.readable = db.interests.user_id.writable = False
db.users.user_email.readable = db.users.user_email.writable = False
db.users.id.readable = db.users.id.writable = False
#db.interests.user_email.readable = db.interests.user_email.writable = False

db.commit()
