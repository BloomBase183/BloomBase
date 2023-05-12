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

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db)
def index():
    # Section is for the searchBar component
    userinput = request.params.userinput
    results = db(db.observations_na.species_guess.contains(userinput, all=True)).select(limitby=(0,10))
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
    drop_old_observations()
    redirect("admin")
    return dict()


@action('drop_observations')
@action.uses('admin.html', db)
def drop_observations():
    drop_old_observations()
    redirect('admin')
    return dict()


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
    print("Database Updated!")


def drop_old_observations():
    # Count the number of rows that match the condition
    count = db.executesql("SELECT COUNT(*) FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-10 days')")[0][0]

    # Ask for confirmation before deleting
    answer = input(f"Are you sure you want to delete {count} rows? (y/n)")

    # If the user confirms, delete the rows
    if answer.lower() == "y":
        db.executesql("DELETE FROM observations_na WHERE DATE(observed_on) <= DATE('now', '-10 days')")
        print(f"{count} rows deleted.")
    else:
        print("Operation cancelled.")
