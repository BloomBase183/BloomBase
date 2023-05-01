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

<<<<<<< HEAD
=======

##CHANGE THIS ####################################
db.define_table(
    'observations',
    Field('user_email', default=get_user_email),
)
db.define_table(
    'interests',
    Field('user_email', default=get_user_email),
)
db.observations.user_email.readable = db.observations.user_email.writable = False
db.interests.user_email.readable = db.interests.user_email.writable = False
db.commit()
>>>>>>> b78aaf6da7af0757c9d9388702713fa2e804bb1f
