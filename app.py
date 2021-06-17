# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys
from datetime import datetime

import dateutil.parser
import logging
from logging import Formatter, FileHandler
import os

import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import Form
from forms import ArtistForm, ShowForm, VenueForm

from config import SQLALCHEMY_DATABASE_URI as DB_URI
from models import db, Venue, Artist, Show
from utils.mock_data_helpers import AppHelper

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__, template_folder="./templates")
moment = Moment(app)
app.config.from_object("config")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

app_helper = AppHelper()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route("/venues")
def venues():
    upcoming_shows = app_helper.get_shows("future")
    data = [
        {
            "city": venue.city,
            "state": venue.state,
            "venues": [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": [show.venue_id for show in upcoming_shows].count(venue.id)
                    # venues is a list of dicts that iterates over each venue in a city
                } for venue in Venue.query.filter(Venue.city == venue.city)
            ]
        }
        # data is a list of dicts that iterates over every venue in every distinct city
        for venue in Venue.query.distinct(Venue.city).order_by(Venue.city).all()
    ]
    if request.headers.get("api"):
        return jsonify(data)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    pattern = request.form.get("search_term", default="")
    results = app_helper.search(entity="venues", pattern=pattern)

    response = {
        "count": len(results),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(app_helper.get_shows_for_venue(venue.id, "future"))
        } for venue in results]
    }
    if request.headers.get("api"):
        return jsonify(response)
    return render_template("pages/search_venues.html", results=response, search_term=pattern)


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    if not app_helper.validate_entity("venues", venue_id):
        abort(404)

    venue = Venue.query.get(venue_id)
    past_venue_shows = app_helper.get_shows_for_venue(venue_id, "past")
    upcoming_venue_shows = app_helper.get_shows_for_venue(venue_id, "future")

    past_shows = [{
        "artist_id": show.artist_id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": str(show.start_time)
    } for show in past_venue_shows]

    upcoming_shows = [{
        "artist_id": show.artist_id,
        "artist_name": show.artists.name,
        "artist_image_link": show.artists.image_link,
        "start_time": str(show.start_time)
    } for show in upcoming_venue_shows]

    print(past_shows, file=sys.stderr)
    print(upcoming_shows, file=sys.stderr)
    data = {"id": venue.id,
            'name': venue.name,
            'genres': venue.genres,
            'address': venue.address,
            'city': venue.city,
            'state': venue.state,
            'phone': venue.phone,
            'website': venue.website,
            'facebook_link': venue.facebook_link,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'image_link': venue.image_link,
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
            }

    if request.headers.get("api"):
        return jsonify(data)
    return render_template("pages/show_venue.html", venue=data)


# ----------------------------------------------------------------------------#
#  Create Venue
# ----------------------------------------------------------------------------#

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: [insert] insert form data as a new Venue record in the db, instead
    # TODO: [insert] modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash(f"Venue {request.form['name']} was successfully listed!")
    # TODO: [insert] on unsuccessful db insert, flash an error instead.
    # e.g., flash("An error occurred. Venue " + data.name + " could not be listed.")
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: [delete] Complete this endpoint for taking a venue_id, and using SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


# ----------------------------------------------------------------------------#
#  Artists
# ----------------------------------------------------------------------------#
@app.route("/artists")
def artists():
    data = [{"id": artist.id, "name": artist.name} for artist in Artist.query.all()]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    pattern = request.form.get("search_term", default="")
    results = app_helper.search(entity="artists", pattern=pattern)

    response = {
        "count": len(results),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": app_helper.get_shows_for_artist(artist.id, "future"),
        } for artist in results]
    }
    return render_template("pages/search_artists.html", results=response, search_term=pattern)


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist_past_shows = app_helper.get_shows_for_artist(artist_id, "past")
    artist_upcoming_shows = app_helper.get_shows_for_artist(artist_id, "future")

    past_shows = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": str(show.start_time),
    } for show in artist_past_shows]

    upcoming_shows = [{
        "venue_id": show.venue_id,
        "venue_name": show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": str(show.start_time),
    } for show in artist_upcoming_shows]

    try:
        artist = Artist.query.get(artist_id)
        data = {"id": artist.id,
                "name": artist.name,
                "genres": artist.genres,
                "city": artist.city,
                "state": artist.state,
                "phone": artist.phone,
                "website": artist.website,
                "facebook_link": artist.facebook_link,
                "seeking_venue": artist.seeking_venue,
                "seeking_description": artist.seeking_description,
                "image_link": artist.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                }
        return render_template("pages/show_artist.html", artist=data)
    except AttributeError as e:
        return not_found_error(e)


# ----------------------------------------------------------------------------#
#  Update
# ----------------------------------------------------------------------------#
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    data = {"id": artist.id,
            "name": artist.name}
    return render_template("forms/edit_artist.html", form=form, artist=data)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: [update] take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    data = {"id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link}
    return render_template("forms/edit_venue.html", form=form, venue=data)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: [update] take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


# ----------------------------------------------------------------------------#
#  Create Artist
# ----------------------------------------------------------------------------#

@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: [insert] insert form data as a new Venue record in the db, instead
    # TODO: [insert] modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash(f"Artist {request.form['name']} was successfully listed!")
    # TODO: [insert] on unsuccessful db insert, flash an error instead.
    # e.g., flash("An error occurred. Artist " + data.name + " could not be listed.")
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#

@app.route("/shows")
def shows():
    # displays list of shows at /shows
    shows_data = [
        {"venue_id": show.venue_id,
         "venue_name": show.venues.name,
         "artist_id": show.artists.id,
         "artist_name": show.artists.name,
         "artist_image_link": show.artists.image_link,
         "start_time": str(show.start_time)}
        for show in Show.query.all()
    ]
    return render_template("pages/shows.html", shows=shows_data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: [insert] insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: [insert] on unsuccessful db insert, flash an error instead.
    # e.g., flash("An error occurred. Show could not be listed.")
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == "__main__":
    # Get Flask port from env or use 5000
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
