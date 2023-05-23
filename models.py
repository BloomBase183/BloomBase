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
db.define_table(
    'field_notes',
    Field('iNat_url'),
    Field('notes', 'text'),
    Field('location', 'text'),
    Field('user_email', default=get_user_email),
    Field('created_on', 'datetime', default=get_time),
)


db.interests.user_email.readable = db.interests.user_email.writable = False
db.interests.id.readable = db.interests.id.writable = False
db.field_notes.user_email.readable = db.field_notes.user_email.writable = False
db.field_notes.id.readable = db.field_notes.id.writable = False
db.field_notes.created_on.writable = False

db.commit()


# create a function that makes test field_notes
def make_test_field_notes(num_field_notes):
    print("Adding", num_field_notes, "field notes.")
    for i in range(num_field_notes):
        note = dict(
            iNat_url='https://www.inaturalist.org/observations/12345678',
            notes='This is a test note.',
            location='This is a test location.',
        )
        auth.register(note, send=False)
    db.commit()


make_test_field_notes(5)

