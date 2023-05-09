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
    'observations',
    Field('observed_on_string'),
    Field('observed_on', 'datetime'),
    Field('time_observed_at', 'datetime'),
    Field('time_zone'),
    Field('user_id', 'integer'),
    Field('user_login'),
    Field('user_name'),
    Field('created_at', 'datetime'),
    Field('updated_at', 'datetime'),
    Field('quality_grade'),
    Field('license'),
    Field('url'),
    Field('image_url'),
    Field('tag_list'),
    Field('description'),
    Field('num_identification_agreements', 'integer'),
    Field('num_identification_disagreements', 'integer'),
    Field('captive_cultivated', 'boolean'),
    Field('oauth_application_id', 'integer'),
    Field('place_guess'),
    Field('latitude', 'double'),
    Field('longitude', 'double'),
    Field('positional_accuracy', 'integer'),
    Field('public_positional_accuracy', 'integer'),
    Field('geoprivacy'),
    Field('taxon_geoprivacy'),
    Field('coordinates_obscured', 'boolean'),
    Field('positioning_method'),
    Field('positioning_device'),
    Field('place_town_name'),
    Field('place_county_name'),
    Field('place_state_name'),
    Field('place_country_name'),
    Field('species_guess'),
    Field('scientific_name'),
    Field('common_name'),
    Field('iconic_taxon_name'),
    Field('taxon_id', 'integer'),
)
db.define_table(
    'interests',
    Field('user_email', default=get_user_email),
)

db.interests.user_email.readable = db.interests.user_email.writable = False

db.commit()
