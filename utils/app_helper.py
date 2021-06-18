import sys
from datetime import datetime

from flask import request, flash
from sqlalchemy import func

from models import Artist, Show, Venue, db
from forms import ArtistForm, ShowForm, VenueForm


class AppHelper:
    """
    Assorted helper methods for the Fyyur app
    """

    def get_shows(self, interval="all"):
        """
        Get a list of all Show objects
        :param interval: (optional) get only past or future shows
        :return: list of Show objects
        """
        all_shows = Show.query.all()
        if interval == "past":
            return filter(lambda x: x.start_time < datetime.now(), all_shows)
        elif interval == "future":
            return filter(lambda x: x.start_time > datetime.now(), all_shows)
        return all_shows

    def get_shows_for_artist(self, artist_id, interval="all"):
        """
        Returns a list of Show objects for a given Artist
        :param artist_id: the id of the artist
        :param interval: past, future, or all
        :return: list of Show objects for `artist_id`
        """
        shows = filter(lambda x: x.artists.id == artist_id, self.get_shows(interval))
        return shows

    def get_shows_for_venue(self, venue_id, interval="all"):
        """
        Returns a list of Show objects for a given venue
        :param venue_id: the id of the venue
        :param interval: past, future, or all
        :return: list of Show objects for `venue_id`
        """
        shows = filter(lambda x: x.venues.id == venue_id, self.get_shows(interval))
        return list(shows)

    def validate_entity(self, entity, entity_id):
        """
        Ensures that valid ids are passed in for Artist, Show, and Venue. Checks to see if `entity_id` exists
        in valid_entities[entity]:
        :param entity: one of Artist, Show, Venue
        :param entity_id: the id of the entity, i.e. artist_id 1
        :return: boolean indicating whether the entity_id is valid, i.e. whether that id exists in that table
        """
        valid_entities = {
            "artists": [obj.id for obj in Artist.query.all()],
            "shows": [obj.id for obj in Show.query.all()],
            "venues": [obj.id for obj in Venue.query.all()],
        }
        return entity_id in valid_entities[entity]

    def max_value(self, db, entity):
        """
        Gets the max is for a given model/table. This is used as a sanity check to protect against integrity violations
        on PK contraints. For example, if the database is seeded with the sql files in /sql, then subsequent insertions
        will fail if we don't first check for extant rows.
        :param db: sqlalchemy db object
        :param entity: one of artists, shows, venues
        :return: integer representing the max(id) in the given table
        """
        max_values = {
            "artists": db.session.query(func.max(Artist.id)).scalar(),
            "shows": db.session.query(func.max(Show.id)).scalar(),
            "venues": db.session.query(func.max(Venue.id)).scalar()
        }
        return max_values[entity]

    @staticmethod
    def search(entity, pattern):
        """
        Implements search functionality for artists and venues. This works by doing a select ilike(%pattern%) against
        the given table. It returns a list of matching db.Model objects, which are parsed downstream
        :param entity:
        :param pattern:
        :return: list of `entity` objects
        """
        results = {
            "artists": Artist.query.filter(Artist.name.ilike(f"%{pattern}%")).all(),
            "venues": Venue.query.filter(Venue.name.ilike(f"%{pattern}%")).all(),
        }
        return results[entity]

    def handle_submission(self, obj, operation="insert", entity_id=None):
        """
        Custom handler for submissions. Parses form data to either create new or update existing entities
        :param obj: an instance of either Artist, Show, or Venue
        :param operation: CRUD operation, either insert or update
        :param entity_id: the id attribute of the Artist, Show, or Venue object
        :return: None
        """
        cls_name = obj.__class__.__name__
        entity = obj.__tablename__
        verb = "updated" if operation == "update" else "listed"
        entity_form = {
            "artists": ArtistForm(request.form),
            "shows": ShowForm(request.form),
            "venues": VenueForm(request.form),
        }
        form = entity_form[entity]

        # Catch and avoid integrity violations
        obj_max_id = self.max_value(db, entity)
        if obj_max_id:
            obj.id = obj_max_id + 1

        # Define entity-specific data
        if entity == "artists":
            data = {
                "name": form.name.data,
                "genres": form.genres.data,
                "city": form.city.data,
                "state": form.state.data,
                "phone": form.phone.data,
                "facebook_link": form.facebook_link.data,
                "seeking_venue": form.seeking_venue.data,
                "image_link": form.image_link.data,
                "website": form.website_link.data,
                "seeking_description": form.seeking_description.data
            }
        elif entity == "shows":
            data = {
                "venue_id": form.venue_id.data,
                "artist_id": form.artist_id.data,
                "start_time": form.start_time.data
            }
        else:
            data = {
                "name": form.name.data,
                "genres": form.genres.data,
                "address": form.address.data,
                "city": form.city.data,
                "state": form.state.data,
                "phone": form.phone.data,
                "website": form.website_link.data,
                "facebook_link": form.facebook_link.data,
                "seeking_talent": form.seeking_talent.data,
                "seeking_description": form.seeking_description.data,
                "image_link": form.image_link.data}

        # For updates, set obj to the existing obj
        if operation == "update":
            old_obj = obj.__class__().query.get(entity_id)
            obj = old_obj

        # only update fields that weren't left blank on edit; for new subs this has no effect
        for key, value in data.items():
            if value != "":
                setattr(obj, key, value)
        try:
            db.session.add(obj)
            db.session.commit()
            flash(f"{cls_name} was successfully {verb}!")
        except Exception as e:
            flash(f"An error occurred. {cls_name} could not be {verb}.")
            print(e, file=sys.stderr)
            db.session.rollback()
        finally:
            db.session.close()
