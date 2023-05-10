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


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


##CHANGE THIS ####################################
db.define_table(
    'observations',
    Field('user_email', default=get_user_email),
)
db.define_table(
    'interests',
    Field('user_email', default=get_user_email),
    Field('interest_category', requires=IS_IN_SET(['Kingdom', 'Class', 'Family', 'Species'])),
    Field('interest_name'),
    Field('interest_weight', 'integer', requires=IS_INT_IN_RANGE(1,10)),
)
db.define_table(
    'users',
    Field('user_email', default=get_user_email),
    Field('first_name', 'string', default = None, requires=IS_NOT_EMPTY()),
    Field('last_name', 'string', default = None, requires=IS_NOT_EMPTY()),
)
db.observations.user_email.readable = db.observations.user_email.writable = False
db.interests.user_email.readable = db.interests.user_email.writable = False
db.users.readable = db.users.writable = False
db.commit()
