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
    'interests',
    Field('user_email', default=get_user_email),
)

db.interests.user_email.readable = db.interests.user_email.writable = False

db.commit()
