import sys

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
        :return:
        """
        shows = filter(lambda x: x.artists.id == artist_id, self.get_shows(interval))
        return shows

    def get_shows_for_venue(self, venue_id, interval="all"):
        """
        Returns a list of Show objects for a given venue
        :param venue_id: the id of the venue
        :param interval: past, future, or all
        :return:
        """
        shows = filter(lambda x: x.venues.id == venue_id, self.get_shows(interval))
        return list(shows)

    def validate_entity(self, entity, entity_id):
        """
        Ensures that valid ids are passed in for Artist, Show, and Venue. Checks to see if `entity_id` exists
        in valid_entities[entity]:
        :param entity: one of Artist, Show, Venue
        :param entity_id: the id of the entity, i.e. artist_id 1
        :return: boolean
        """
        valid_entities = {
            "artists": [obj.id for obj in Artist.query.all()],
            "shows": [obj.id for obj in Show.query.all()],
            "venues": [obj.id for obj in Venue.query.all()],
        }
        return entity_id in valid_entities[entity]

    def max_value(self, db, entity):
        max_values = {
            "artists": db.session.query(func.max(Artist.id)).scalar(),
            "shows": db.session.query(func.max(Show.id)).scalar(),
            "venues": db.session.query(func.max(Venue.id)).scalar()
        }
        return max_values[entity]
        pass

    @staticmethod
    def search(entity, pattern):
        results = {
            "artists": Artist.query.filter(Artist.name.ilike(f"%{pattern}%")).all(),
            "venues": Venue.query.filter(Venue.name.ilike(f"%{pattern}%")).all(),
        }
        return results[entity]

    def handle_submission(self, obj, operation):
        """
        Custom handler for submissions. Parses form data to either create new or update existing entities
        :param obj: an instance of either Artist, Show, or Venue
        :param operation: CRUD operation, either insert or update
        :return: None
        """
        cls_name = obj.__class__.__name__
        entity = obj.__tablename__
        entity_form = {
            "artists": ArtistForm(request.form),
            "shows": ShowForm(request.form),
            "venues": VenueForm(request.form),
        }
        form = entity_form[entity]
        obj_max_id = self.max_value(db, entity)
        if obj_max_id:
            obj.id = obj_max_id + 1
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

        for key, value in data.items():
            setattr(obj, key, value)
        try:
            db.session.add(obj)
            db.session.commit()
            flash(f"{cls_name} was successfully listed!")
        except Exception as e:
            flash(f"An error occurred. {cls_name} could not be listed.")
            print(e, file=sys.stderr)
            db.session.rollback()
        finally:
            db.session.close()
