from sqlalchemy import func

from models import *


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

    @staticmethod
    def max_value(db, entity):
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


class FormsHelper:
    """
    states and genres used by forms.py
    """
    states_list = [
        ('AL', 'AL'),
        ('AK', 'AK'),
        ('AZ', 'AZ'),
        ('AR', 'AR'),
        ('CA', 'CA'),
        ('CO', 'CO'),
        ('CT', 'CT'),
        ('DE', 'DE'),
        ('DC', 'DC'),
        ('FL', 'FL'),
        ('GA', 'GA'),
        ('HI', 'HI'),
        ('ID', 'ID'),
        ('IL', 'IL'),
        ('IN', 'IN'),
        ('IA', 'IA'),
        ('KS', 'KS'),
        ('KY', 'KY'),
        ('LA', 'LA'),
        ('ME', 'ME'),
        ('MT', 'MT'),
        ('NE', 'NE'),
        ('NV', 'NV'),
        ('NH', 'NH'),
        ('NJ', 'NJ'),
        ('NM', 'NM'),
        ('NY', 'NY'),
        ('NC', 'NC'),
        ('ND', 'ND'),
        ('OH', 'OH'),
        ('OK', 'OK'),
        ('OR', 'OR'),
        ('MD', 'MD'),
        ('MA', 'MA'),
        ('MI', 'MI'),
        ('MN', 'MN'),
        ('MS', 'MS'),
        ('MO', 'MO'),
        ('PA', 'PA'),
        ('RI', 'RI'),
        ('SC', 'SC'),
        ('SD', 'SD'),
        ('TN', 'TN'),
        ('TX', 'TX'),
        ('UT', 'UT'),
        ('VT', 'VT'),
        ('VA', 'VA'),
        ('WA', 'WA'),
        ('WV', 'WV'),
        ('WI', 'WI'),
        ('WY', 'WY'),
    ]

    genres_list = [
        ('Alternative', 'Alternative'),
        ('Blues', 'Blues'),
        ('Classical', 'Classical'),
        ('Country', 'Country'),
        ('Electronic', 'Electronic'),
        ('Folk', 'Folk'),
        ('Funk', 'Funk'),
        ('Hip-Hop', 'Hip-Hop'),
        ('Heavy Metal', 'Heavy Metal'),
        ('Instrumental', 'Instrumental'),
        ('Jazz', 'Jazz'),
        ('Musical Theatre', 'Musical Theatre'),
        ('Pop', 'Pop'),
        ('Punk', 'Punk'),
        ('R&B', 'R&B'),
        ('Reggae', 'Reggae'),
        ('Rock n Roll', 'Rock n Roll'),
        ('Soul', 'Soul'),
        ('Other', 'Other'),
    ]
