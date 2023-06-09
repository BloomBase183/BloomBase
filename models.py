"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None
def get_userID():
    return auth.current_user.get('id') if auth.current_user else None

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
    'field_notes',
    Field('title'),
    Field('iNat_url'),
    Field('notes', 'text'),
    Field('location', 'text'),
    Field('latitude', 'double'),
    Field('longitude', 'double'),
    Field('user_email', default=get_user_email),
    Field('created_on', 'datetime', default=get_time),
    Field('like_count', 'integer', default = 0),
    Field('dislike_count', 'integer', default = 0),
)


db.define_table(
    'interests',
    Field('user_id'),
    Field('user_email', default=get_user_email),
    # gives the option for more filtering types later
    Field('interest_category', requires=IS_IN_SET(['Species'])),
    # should be a search bar of species we have available, currently takes whatever
    Field('interest_name'),
    Field('species_id', 'integer'),
    Field('species_name'),
    Field('scientific_name'),
    Field('image'),
    # the weight impacts which interests are highest priority
    Field('interest_weight', 'integer', requires=IS_INT_IN_RANGE(1, 11)),
)

db.define_table(
    'fnote_likes',
    Field('user_email', default=get_user_email),
    Field('field_note_id'),
    Field('is_liked', 'boolean', default=False, migrate=True),
    
)

db.field_notes.user_email.readable = db.field_notes.user_email.writable = False
db.field_notes.id.readable = db.field_notes.id.writable = False
db.field_notes.created_on.writable = False
db.interests.user_id.readable = db.interests.user_id.writable = False
db.interests.id.readable = db.interests.id.writable = False
db.users.user_email.readable = db.users.user_email.writable = False
db.users.id.readable = db.users.id.writable = False
db.interests.user_email.readable = db.interests.user_email.writable = False
db.fnote_likes.user_email.readable = db.fnote_likes.user_email.writable = False
db.fnote_likes.id.readable = db.fnote_likes.id.writable = False



db.commit()


# create a function that makes test field_notes

# def make_test_field_notes(num_field_notes):
#     print("Adding", num_field_notes, "field notes.")
#     for i in range(num_field_notes):
#         note = dict(
#             iNat_url='https://www.inaturalist.org/observations/12345678',
#             notes='This is a test note.',
#             location='This is a test location.',
#         )
#         auth.register(note, send=False)
#     db.commit()
#
#
# make_test_field_notes(5)


