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
import datetime
import requests

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db)
def index():
    return dict()


##MAKE SURE TO MAKE IT SO ONLY ADMINS CAN ACCESS THIS##
@action('admin')
@action.uses('admin.html', db)
def admin():
    first_ten = db(db.observations_na).select(limitby=(0, 10))
    return dict(first_ten=first_ten)


@action('get_observations')
@action.uses('admin.html', db)
def get_observations():
    today = datetime.date.today().strftime('%Y-%m-%d')
    if not db(db.observations_na.observed_on == today).select().first():
        url = 'https://api.inaturalist.org/v1/observations'
        query_params = {
            'has[]': 'photos',
            'quality_grade': 'research',
            'identifications': 'most_agree',
            'captive': 'False',
            'geoprivacy': 'open',
            'taxon_geoprivacy': 'open',
            'iconic_taxa[]': 'Plantae',
            'place_id': '97394',
            'per_page': '200',
            'date': f"{datetime.date.today().strftime('%Y-%m-%d')}",
            'fields': 'observed_on,uri,photos.geojson.coordinates,photos.url,species_guess,taxon.id,taxon.name,'
                      'taxon.preferred_common_name,taxon.iconic_taxon_name',
        }  # 'date': f"{datetime.date.today().strftime('%Y-%m-%d')}"
        response = requests.get(url, params=query_params)
        observations = response.json()['results']
        error = False
        for observation in observations:
            try:
                db.observations_na.insert(
                    observed_on=observation['observed_on'],
                    url=observation['uri'],
                    image_url=observation['photos'][0]['url'] if observation['photos'] else None,
                    latitude=observation['geojson']['coordinates'][1] if observation['geojson'] else None,
                    longitude=observation['geojson']['coordinates'][0] if observation['geojson'] else None,
                    species_guess=observation['species_guess'],
                    scientific_name=observation['taxon']['name'],
                    common_name=observation['taxon']['preferred_common_name'] if 'preferred_common_name' in observation[
                        'taxon'] else None,
                    iconic_taxon_name=observation['taxon']['iconic_taxon_name'],
                    taxon_id=observation['taxon']['id']
                )
            except:
                error = True
        if error:
            print("Error in API Request")  # Maybe print to a log?
        else:
            print("Succesful API Request")
        # print({  #for debugging
        #     'observed_on': observation['observed_on'],
        #     'url': observation['uri'],
        #     'image_url': observation['photos'][0]['url'],
        #     'latitude': observation['geojson']['coordinates'][1],
        #     'longitude': observation['geojson']['coordinates'][0],
        #     'species_guess': observation['species_guess'],
        #     'scientific_name': observation['taxon']['name'],
        #     'common_name': observation['taxon']['preferred_common_name'],
        #     'iconic_taxon_name': observation['taxon']['iconic_taxon_name'],
        #     'taxon_id': observation['taxon']['id']
        # })
    else:
        print("Already added those observations")
    redirect('admin')


@action('upload_csv')
@action.uses('admin.html', db)
def upload_csv():
    my_csv_file = os.path.join(APP_FOLDER, "observations.csv")
    insert_csv_to_database(my_csv_file)
    redirect('admin')


@action('drop_observations')
@action.uses('admin.html', db)
def drop_observations():
    drop_old_observations(10)
    redirect('admin')


def drop_old_observations(days):
    # Count the number of rows that match the condition
    count = db.executesql(f"SELECT COUNT(*) FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-{days} days')")[0][
        0]
    # Debug
    # answer = input(f"Are you sure you want to delete {count} rows? (y/n)")
    #
    #
    # if answer.lower() == "y":
    #     db.executesql("DELETE FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-10 days')")
    #     print(f"{count} rows deleted.")
    # else:
    #     print("Operation cancelled.")


# @action('update_database')
# def update_database():
#     my_csv_file = os.path.join(APP_FOLDER, "observations.csv")
#     insert_csv_to_database(my_csv_file)
#     drop_old_observations()
#     print("Database Updated")

def insert_csv_to_database(filename):
    # print(f"Parsing file: {filename}")  # Debug statement
    with open(filename, encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(f"Parsing row: {row}")  # Debug statement
            db.observations_na.insert(
                observed_on=row['observed_on'],
                url=row['url'],
                image_url=row['image_url'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                species_guess=row['species_guess'],
                scientific_name=row['scientific_name'],
                common_name=row['common_name'],
                iconic_taxon_name=row['iconic_taxon_name'],
                taxon_id=row['taxon_id']
            )
    print("Succesfully Added CSV to database")



