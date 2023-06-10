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
from .models import get_user_email, get_userID
from .common import db, session, T, cache, auth, signed_url, Field
from .settings import APP_FOLDER
import os
import json
import datetime
JSON_FILE = os.path.join(APP_FOLDER, "private", "keys.json")
import requests

from .email_auth import EmailAuth

url_signer = URLSigner(session)


# auth = EmailAuth(session, url_signer)
f = open(JSON_FILE)

rows = json.load(f)
mapkey = rows[0].get('maps')

@action('index')
@action.uses('index.html', db, session, url_signer, auth)
def index():
    # Section is for the searchBar component

    user_input = request.params.get('user_input')
    if user_input == "" or user_input is None:
        results = db(db.observations_na).select(limitby=(0,10))
    else:
        results = db((db.observations_na.species_guess.contains(user_input, all=True)) |
                (db.observations_na.scientific_name.contains(user_input, all=True)) |
                (db.observations_na.common_name.contains(user_input, all=True)) |
                (db.observations_na.iconic_taxon_name.contains(user_input, all=True))).select(limitby=(0,10))
    return dict(
        observations_url=URL('grab_observations'),
        search_url=URL('search'),
        add_interest_url=URL('add_interest'),
        url_signer = url_signer,
        auth = auth,
        results=results,
        MAPS_API_KEY=mapkey,
        getfieldnotes_url=URL('get_fieldNotes'),
        field_notes_url=URL('fnote'),
        interest_url=URL('interest_list'),
        drop_interest_url=URL('drop_interest'),
        post_note_url=URL('add_note', signer=url_signer),
    )

@action('search')
@action.uses(db)
def search():
    user_input = request.params.get('q')
    search_results = db((db.observations_na.species_guess.contains(user_input, all=True)) |
                    (db.observations_na.scientific_name.contains(user_input, all=True)) |
                    (db.observations_na.common_name.contains(user_input, all=True)) |
                    (db.observations_na.iconic_taxon_name.contains(user_input, all=True))).select(limitby=(0, 10))

    return dict(search_results=search_results.as_list())




## MAKE SURE TO MAKE IT SO ONLY ADMINS CAN ACCESS THIS ##
@action('admin')
@action.uses('admin.html', db, auth.enforce(), url_signer.verify(), session)
def admin():
    return dict(
        url_signer=url_signer,
        auth=auth
        )


@action('fieldNotes')
@action.uses('fieldNotes.html', db, url_signer, auth)
def fieldNotes():
    # access all field notes associated with the current user email
    field_notes = db(db.field_notes.user_email == get_user_email()).select()
    return dict(field_notes=field_notes)


@action('get_fieldNotes')
@action.uses(db, url_signer, auth)
def fieldNotes():
    # access all field notes associated with the current user email
    print("gettinfnote")
    field_notes = db(db.field_notes.user_email == get_user_email()).select()
    
    return dict(field_notes=field_notes)

@action('add_note', method=["GET", "POST"])
@action.uses('add_note.html', db, auth.enforce(), url_signer.verify(), session)
def add_note():
    content = request.params.get('noteContent')
    iNat_url = request.params.get('iNat_url')
    long = request.params.get('long')
    lat = request.params.get('lat')
    title = request.params.get('title')
    #print(content, iNat_url, long, lat)
    db.field_notes.insert(notes=content, iNat_url=iNat_url, longitude=long, latitude=lat, title=title)
    return "Added note!"
    # if get_userID() is None: #if the user isnt logged in.
    #     redirect(URL('index'))
    # insert form, no record in database
    # form = Form(db.field_notes, formstyle=FormStyleBulma)
    # if form.accepted:
    #     redirect(URL('profile', signer=url_signer))
    # if this is a get request, or a post but not accepted = with error
    # return dict(
    #     form=form,
    #     url_signer=url_signer,
    #     auth=auth,
    # )




@action('view_note/<field_note_id:int>', method=["GET", "POST"])
@action.uses('view_note.html', db, auth.enforce(), url_signer.verify(), session)
def view_note(field_note_id=None):
    assert field_note_id is not None
    f = db.field_notes[field_note_id]
    if f is None:
        # Nothing found to be edited!
        redirect(URL('profile', signer=url_signer))
    form = Form(db.field_notes, record=f, deletable=False, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('profile', signer=url_signer))
    # if this is a get request, or a post but not accepted = with error
    return dict(
        form=form,
        url_signer=url_signer,
        auth=auth,
    )


@action('add_interest', method=["POST"])
@action.uses(db, auth, url_signer)
def add_interest():
    # Grabbing neccessary info 
    species_id = request.params.get('species_id')
    species_name = request.params.get('species_name')
    species_image = request.params.get('species_image')
    species_scientific_name = request.params.get('scientific_name')
    print(species_image)
    # Checking if species is in database
    species_exist = db(db.observations_na.id == species_id).select().first()
    # Checking if species is already added as an interest from user
    in_interest = db((db.interests.user_email == get_user_email()) &
                     # (db.interests.species_id == species_id) &
                     (db.interests.species_name == species_name)).select().first()

    # Species already in interest or not in updated db
    if species_exist is None:
        print("species doesn't exist")
        return 'false'
    if in_interest is not None:
        print("already added")
        return 'false'

    # Adding interest into users table
    db.interests.insert(user_email=get_user_email(), species_id=species_id, species_name=species_name, scientific_name=species_scientific_name, image=species_image)
    print("added interest")
    return 'true'

@action('drop_interest', method=["POST"])
@action.uses(db, auth, url_signer)
def drop_interest():
    interest_id = request.params.get('interest_id')
    interest_email = request.params.get('user_email')
    assert interest_id is not None
    assert interest_email is not None
    db((db.interests.id == interest_id) & (db.interests.user_email == interest_email)).delete()
    print("successfully deleted interest entry")
    return "deleted interest entry"


@action('profile')
@action.uses('profile.html', db, auth, auth.enforce(), url_signer.verify(), session)
def profile():
    if len(db(db.users.user_email == get_user_email()).select()) > 0:
        # checks if the user exists in the database. If so then take their entry for the user field, otherwise just take their email
        user = db(db.users.user_email == get_user_email()).select()
    else:
        user = [session.get("_user_email")]
    if user is None:
        redirect(URL('index'))
    # interests = db(db.interests.user_id == auth.current_user.get('id')).select()
    field_notes = db(db.field_notes.user_email == get_user_email()).select()
    return dict(
        current_user=user,
        field_notes=field_notes,
        # interests are empty for now
        interests=[],
        url_signer=url_signer,
        auth=auth,
        MAPS_API_KEY=mapkey,
        getfieldnotes_url=URL('get_fieldNotes'),
    )


@action('create_profile', method=["GET", "POST"])
@action.uses('create_profile.html', db, auth.enforce(), url_signer.verify(), session)
def create_profile():
    # creates an entry into the database, currently only associated with the name fields
    user = db(db.users.user_email == get_user_email()).select()
    if len(user) < 1:
        # don't have an account associated with the email
        form = Form([Field('first_name'), Field('last_name')], csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            db.users.insert(first_name=form.vars["first_name"], last_name=form.vars["last_name"])
            redirect(URL('profile', signer=url_signer))
        return dict(form=form, url_signer=url_signer, auth=auth)
    else:
        # The user already has an existing profile
        redirect(URL('index'))


@action('edit_profile', method=["GET", "POST"])
@action.uses('edit_profile.html', db, auth.enforce(), url_signer.verify(), session)
def edit_profile():
    # currently only works with the name fields
    user = db(db.users.user_email == get_user_email()).select()
    if len(user) < 1:
        # user not found, so we instead make a new database entry for them
        redirect(URL('create_profile', signer=url_signer))
    else:
        form = Form(db.users, record=user[0], deletable=False, csrf_session=session, formstyle=FormStyleBulma)
        if form.accepted:
            redirect(URL('profile', signer=url_signer))
        return dict(form=form, url_signer=url_signer, auth=auth)


@action('add_interest/<user_id:int>', method=["GET", "POST"])
@action.uses('add_interest.html', db, auth.enforce(), url_signer.verify(), session)
def add_interest(user_id=None):
    assert user_id is not None
    form = Form([Field('interest_category'), Field('Name'), Field('Weight')], csrf_session=session,
                formstyle=FormStyleBulma)
    if form.accepted:
        db.interests.insert(interest_category=form.vars["interest_category"], interest_name=form.vars["Name"],
                            weight=form.vars["Weight"], user_id=user_id)
        redirect(URL('index'))
    return dict(form=form)

# Func returns a list a field notes for the 
# corresponding observation
@action('fnote', method=["POST"])
@action.uses(db, url_signer, auth)
def fnote():
    observation = request.params.get("observation")
    observation_url = observation.get("url")
    
    
    print("we are in here")
    species_exist = db(db.observations_na.id == observation.get("id")).select().first()
    if species_exist is None:
        print("species is not in the database")
        return []

    field_notes = db(db.field_notes.iNat_url == observation_url).select(limitby=(0,15), orderby=~db.field_notes.created_on)

    for note in field_notes:
        note.created_on = format_timestamp(note.created_on)

    return dict(field_notes=field_notes)

@action('interest_list', method=["GET"])
@action.uses(db, url_signer, auth)
def interest_list():
    interests = db(get_user_email() == db.interests.user_email).select()
    return dict(interests=interests)


@action('delete_interest/<user_id:int>')
@action.uses(db, auth.enforce(), url_signer.verify())
def delete_contact(contact_id=None):
    assert contact_id is not None
    db(db.interests.id == contact_id).delete()
    redirect(URL('index'))


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


@action('upload_csv')
@action.uses('admin.html', db, auth.enforce(), url_signer.verify(), session)
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
@action.uses('admin.html', db, url_signer.verify())
def update_database():
    get_observations()  # Grab todays observations
    drop_old_observations(10)  # Remove 10 day old observations
    print("Database Updated")
    redirect(URL('admin', signer=url_signer))


@action('grab_observations')
@action.uses(db, url_signer, auth)
def grab_observations():
    latmax = request.params.get('lat_max')
    longmax = request.params.get('lng_max')
    latmin = request.params.get('lat_min')
    longmin = request.params.get('lng_min')
    filterok = request.params.get('filter')
    uid = get_userID()
    if(filterok == "true"):
        ints = db(db.interests.user_id == uid).select()
        ints = [x.get('species_name') for x in ints]
        ints.append('Prostrate Capeweed')
    
    #print(longmax, longmin, latmax, latmin)
    query = (db.observations_na.longitude <= longmax) & (db.observations_na.longitude >= longmin) & (db.observations_na.latitude >= latmin) & (db.observations_na.latitude <= latmax)
    a = db(query).select().as_list()
    if(filterok == "true"):
        a = [z for z in a if (z.get('common_name') in ints)]
    # a = a[0:200]
    print("grabbing url got")
    # print("a is" + str(a))
    print("got the value in db")
    #print(a)
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

# format created_on field fnotes
def format_timestamp(timestamp):

    current_time = datetime.datetime.utcnow()
    time_difference = current_time - timestamp

    minutes = time_difference.seconds // 60
    hours = minutes // 60
    days = time_difference.days

    if days > 0:
        formatted_time = timestamp.strftime("%Y-%m-%d")
    else:
        if hours == 1:
            formatted_time = f"{hours} hour ago" 
        elif hours > 0:
            formatted_time = f"{hours} hours ago"
        elif minutes == 1:
            formatted_time = f"{minutes} minute ago"
        elif minutes > 0:
            formatted_time = f"{minutes} minutes ago"
        else:
            formatted_time = "Just now"

    return formatted_time
