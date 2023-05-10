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
import csv

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .common import db, session, T, cache, auth, signed_url
from .settings import APP_FOLDER
import os

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db)
def index():

    return dict()


##MAKE SURE TO MAKE IT SO ONLY ADMINS CAN ACCESS THIS##
@action('admin')
@action.uses('admin.html', db)
def admin():

    return dict()


@action('upload_csv')
@action.uses('admin.html', db)
def upload_csv():
    my_csv_file = os.path.join(APP_FOLDER, "observations.csv")
    insert_csv_to_database(my_csv_file)


def insert_csv_to_database(filename):  #filename = "observations.csv"   ### observations is in my root directory
    print(f"Parsing file: {filename}")  # Debug statement
    with open(filename, encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(f"Parsing row: {row}")  # Debug statement
            db.observations.insert(
                observed_on_string=row['observed_on_string'],
                observed_on=row['observed_on'],
                time_observed_at=row['time_observed_at'],
                time_zone=row['time_zone'],
                user_id=row['user_id'],
                user_login=row['user_login'],
                user_name=row['user_name'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                quality_grade=row['quality_grade'],
                license=row['license'],
                url=row['url'],
                image_url=row['image_url'],
                tag_list=row['tag_list'],
                description=row['description'],
                num_identification_agreements=row['num_identification_agreements'],
                num_identification_disagreements=row['num_identification_disagreements'],
                captive_cultivated=row['captive_cultivated'],
                oauth_application_id=row['oauth_application_id'],
                place_guess=row['place_guess'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                positional_accuracy=row['positional_accuracy'],
                public_positional_accuracy=row['public_positional_accuracy'],
                geoprivacy=row['geoprivacy'],
                taxon_geoprivacy=row['taxon_geoprivacy'],
                coordinates_obscured=row['coordinates_obscured'],
                positioning_method=row['positioning_method'],
                positioning_device=row['positioning_device'],
                place_town_name=row['place_town_name'],
                place_county_name=row['place_county_name'],
                place_state_name=row['place_state_name'],
                place_country_name=row['place_country_name'],
                species_guess=row['species_guess'],
                scientific_name=row['scientific_name'],
                common_name=row['common_name'],
                iconic_taxon_name=row['iconic_taxon_name'],
                taxon_id=row['taxon_id']
            )
    print("Database Updated!")
    redirect("admin.html")
