from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
# Models and db object imported by app
# ----------------------------------------------------------------------------#
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Shows(db.Model):
    __tablename__ = "shows"
    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String)
    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String)
    artist_image_link = db.Column(db.String)
    start_time = db.Column(db.String)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
