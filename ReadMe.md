# Bloombase
## Project Preview
![Bloombasegif(1) (online-video-cutter com) (1)](https://github.com/BloomBase183/BloomBase/assets/70651849/bd74acb4-d46f-40de-9035-95613b505c83)
## Project Goal
The goal of this project is to create a way for users to interact with and leave notes on observations grabbed from the iNaturalist database of plant observations. The available user features include being able to rate observations based on bloom density, to leave field notes on blooms which can be viewed by other users, and add interests which allow users to filter which points are displayed on the map at that time.
## Utilized tools
The project is created, with a mysql database and a py4web backend. The front end is done in Vue.js, with bulmacss and custom css styling. The project also uses the Google maps API to create dynamic maps with points that lead to data that users can interact with and create, as well as the iNaturalist API to fetch data points (observations).


To run the project, run py4web, and navigate to Bloombase/index.


## Database layout
The project uses 6 tables. One for the observations, field notes, users, liked, interests, and observation densities. Of these tables, all tables except users refer to observations in some way, with likes and densities being dropped when old observations are dropped. However, the interests and field notes tables persist, as those are user data that should persist even as observations exit the database.


## Maps API usage
The project uses 4 separate maps instances.

The first instance is the main observation map with the marker clusterer. This map displays all observations and thus has a performance constraint for loading all points on a map. Thus, this map utilizes a listener on a map resize event to query only points in the database within the constraints of each resize. Additionally, this map can have a filter to only interests applied, which allows users to filter based on their interests only. This map also prompts for user location on init to set initial bounds.
An additional map is used to display field notes on a user. This map, since it has a smaller number of points loads all points on initialization, and does not employ a clusterer to reduce usage latency when users are scrolling their field notes. This map also prompts for user location on init to set initial bounds.


There are finally two more smaller maps that are in modal components for observations and species. Both these maps do not prompt for user location as they display a much more zoomed out view, and do not utilize re querying for each resize event, since they either only display one, or a small subset of observations. These maps intialize on click events from a modal, since the maps api is not able to initialize a map that is hidden from a user and leave it hidden.


## Authentication
Authentication is done by associating user accounts solely with an email. When a user seeks to sign in to an account, they are prompted to provide a valid email address. A link for them to follow is then generated, and in actual implementation would be sent to the provided email, allowing them to log in by clicking the provided link. In the current version, however, for the sake of demo purposes the link is instead printed to the console. Once a user follows that link they are signed in, without the need for an additional password.

## iNaturalist API

The observations are pulled from the iNaturalist API, 

## UI work
[Figma](https://www.figma.com/)
### UI Design for Main Page
<img src="https://github.com/BloomBase183/BloomBase/assets/70651849/35d2bfc7-d86d-488d-8b50-107cf7d8eb4f" width="650" height="360">

## Pages used
### Main page (index)


The main index page of the site contains the primary map in which all observations are listed, as well as the list of user interests, and the search bar for searching species to add to interests.
The layout of this page consists of index.js and index.html, and is done using mostly Bulma css framework, with some custom css to manage resizing of map elements.


#### Observation popup modal
This popup displays the image, location, and density of the given observation. Of these fields, the users can add new field notes, or review field notes from other users, which is done through the javascript and adds these fields notes to the database tables. Additionally, the users can review the density of the observation, and see the overall rating for the density of the observation, which is the mean of all ratings for that observation. Additionally, this popup displays a map of the location of the observation, since a user could access this from the search view, which does not display location per observation. These density ratings are a separate database table tied to the observations table. This popup is accessed by an onclick either on the main map, or from a species in search.


#### Interest search field
This field queries the database for the species names that show up in observations that are currently in the table. The search checks for the user field in both the common and scientific name of species, and shows a list of those names without duplicates for repeated observations of the same species. The image used in the search list is fetched from current observations. The add interests dialog on the search allows a user to add a species to their interest via the search bar.




#### Interest search popup modal
This popup is opened on a click event from the interest search field and displays an aggrated view of all observations for that species. The popup displays a smaller map with all observations for that specific species, which can be clicked to open the abovementioned observation popup model. There are no user editable popups in this field, as it displays observations from the api and thus can't be added or removed.



#### Observation Map
This map makes up the most loaded map in the site, and contains all of the observations from the iNaturalist API. On init, this map either prompt the user for location data, and selects to a set zoom level outside that point, loading in the observations for that default view.  Due to the high number of observations that need to be displayed as points, this map uses an event listener for the google maps resize event, and on each map resize event, queries the database for points within it's current bounds to display. After this, the map uses the markercluster library to group observations based on location to reduce visual clutter on further zoomed out view.


### Profile page
This page contains the information for a single user, which is the username and the field notes created by that user.


#### Profile page map
This map displays all field notes created by a user. This map loads all points on init, since the amount of field note points is much less than the amount on the observations map.


#### Username change
Users can additionally change their display names from this page as well.


## Admin page
This page allows site admins (currently everyone on the project), to update observation tables from the API. This page is for testing and loading purposes until an asynchronous script to pull observations is set up.


## Current issues
There is currently not an asynchronous job set up to pull the observations from the api every day, so that is a task that needs to be performed manually by the admin users.

There is currently not a paid mail service set up with the login, thus the login must be accessed from the command line.