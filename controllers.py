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
    return dict(
        #results=results, 
        observations_url=URL('grab_observations'),
        search_url=URL('search'),
        add_interest_url=URL('add_interest'),
        )

@action('search')
@action.uses(db)
def search():
    user_input = request.params.get('q')
    search_results = db((db.observations_na.species_guess.contains(user_input, all=True)) |
                    (db.observations_na.scientific_name.contains(user_input, all=True)) |
                    (db.observations_na.common_name.contains(user_input, all=True)) |
                    (db.observations_na.iconic_taxon_name.contains(user_input, all=True))).select(limitby=(0, 10))
    return dict(search_results=search_results)


##MAKE SURE TO MAKE IT SO ONLY ADMINS CAN ACCESS THIS##
@action('admin')
@action.uses('admin.html', db)
def admin():
    first_ten = db(db.observations_na).select(limitby=(0, 10))
    return dict(first_ten=first_ten)


@action('fieldNotes')
@action.uses('fieldNotes.html', db)
def fieldNotes():
    # access all field notes associated with the current user email
    field_notes = db(db.field_notes.user_email == get_user_email()).select()
    return dict(field_notes=field_notes)


@action('addNote', method=["GET", "POST"])
@action.uses('addNote.html', db)
def addNote():
    # insert form, no record in database
    form=Form(db.field_notes, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('fieldNotes'))
    # if this is a get request, or a post but not accepted = with error
    return dict(form=form)


@action('viewNote/<field_note_id:int>', method=["GET", "POST"])
@action.uses('viewNote.html', db)
def viewNote(field_note_id=None):
    assert field_note_id is not None
    f = db.field_notes[field_note_id]
    if f is None:
        # Nothing found to be edited!
        redirect(URL('fieldNotes'))
    form = Form(db.field_notes, record=f, deletable=False, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('fieldNotes'))
    # if this is a get request, or a post but not accepted = with error
    return dict(form=form)

@action('add_interest', method=["POST"])
@action.uses(db)
def add_interest():
    # Grabbing neccessary info 
    user_email = get_user_email()
    species_id = request.params.get('species_id')
    species_name = request.params.get('species_name')

    # Checking if species is in database
    species_exist = db(db.observations_na.id == species_id).select().first()
    # Checking if species is already added as an interest from user
    in_interest = db((db.interests.user_email == user_email) and 
                     (db.interests.id == species_id) and
                     (db.interests.species_name == species_name)).select().first()
    
    # Species already in interest or not in updated db
    if not species_exist or in_interest is not None:
        print("already added")
        return 'false'
    
    # Adding interest into users table
    db.interests.insert(user_email=user_email, species_id=species_id, species_name=species_name)
    print("added interest")
    return 'true'


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


# This is the function that would be called everyday
@action('update_database')
def update_database():
    get_observations()  # Grab todays observations
    drop_old_observations(10)  # Remove 10 day old observations
    print("Database Updated")


@action('grab_observations')
@action.uses(db)
def grab_observations():
    a = db(db.observations_na).select().as_list()
    # a = a[0:200]
    print("grabbing url got")
    # print("a is" + str(a))
    print("got the value in db")
    return dict(
        observations=a
    )


def drop_old_observations(days):
    db.executesql(f"DELETE FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-{days} days')")
    # Debug
    # Count the number of rows that match the condition
    # count = db.executesql(f"SELECT COUNT(*) FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-{days} days')")[0][
    #     0]
    # answer = input(f"Are you sure you want to delete {count} rows? (y/n)")
    #
    #
    # if answer.lower() == "y":
    #     db.executesql("DELETE FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-10 days')")
    #     print(f"{count} rows deleted.")
    # else:
    #     print("Operation cancelled.")


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
