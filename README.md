Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local
performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with
artists as a venue owner.

Your job is to build out the data models to power the API endpoints for the Fyyur site by connecting to a PostgreSQL
database for storing, querying, and creating information about artists and venues on Fyyur.

## Contents
* [Requirements](#requirements)
* [Project structure](#project-structure)
* [Development Setup](#development-setup)
    * [The Easy Way](#the-easy-way)
    * [The Hands-on Way](#the-hands-on-way)

## Requirements

This project was built for Docker and runs quite nicely there. As such, the dev setup instructions are written with
Docker in mind. You *can* run it locally if you like, but this requires managing your own Postgres installation. That
might look something like this:

```bash
git clone git@github.com:fitzystrikesagain/fsnd_fyyur.git fyurr
cd fyurr
$ python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python app.py
# ...
# do postgres things
# ...
open localhost:5000
```

While there's nothing wrong with this approach, the Docker version is a bit simpler
(see [Development Setup](#development-setup) below):

```bash
git clone git@github.com:fitzystrikesagain/fsnd_fyyur.git fyurr
cd fyurr
source .env
./startup.sh
```

## Project Structure

  ```bash
  .
├── Dockerfile                             # Builds the base image and manages Python requirements     
├── README.md                              # This document    
├── app.py                                 # The app itself 
├── config.py                              # The config, mostly for the DB URI     
├── docker-compose.yml                     # Creates the Flask and Postgres containers             
├── forms.py                               # Forms for various endpoints, such as artist creation   
├── models.py                              # SQLAlchemy `db.Model` definitions for `Artist`, `Show`, and `Venue`    
├── requirements.txt                       # Python requirements, managed by Docker if run in Docker            
├── sql                                    # Insert statements containing the original data, can be run against Postgres 
│   ├── artists.sql                                      
│   ├── shows.sql                                   
│   └── venues.sql                                   
├── startup.sh                             # A very handy script to get you running with (hopefully) a single command      
├── static                                 # Static assets 
│   ├── css                                   
│   ├── fonts                                   
│   ├── img                                   
│   └── js                                   
├── templates                              # HTML templates for the various pages    
│   ├── errors                                   
│   ├── forms                                   
│   ├── layouts                                   
│   └── pages                                   
├── utils                                  # Various helpers to make app development life easier
│   ├── app_helper.py                                   
│   ├── form_helper.py                                   
│   └── mock_data.py                                   
  ```

## Development Setup

### The easy way

1. **Create a file named `.env` in the project's root directory.**

This file should contain something like this, though you can change any of the Flask or Postgres variables:

```bash
# Add to .gitignore so we don't commit
FLASK_PORT=5000
POSTGRES_HOST=postgres-fyyur
POSTGRES_DB=fyyur
POSTGRES_USER=showfyyur
POSTGRES_PASSWORD=password
PYTHONPATH=/usr/src/app/
PYTHONUNBUFFERED=0
FLASK_CONTAINER_NAME=fyyur
POSTGRES_CONTAINER_NAME=postgres-fyyur
```

The values that matter will get set to defaults elsewhere if you don't do this, but this enables you to do step #2.

2. **Run the startup script**

```bash
./startup.sh
```

This will do the following for you:

```bash
# Bring up the container
docker compose up -d

# Initialize the db and run migrations
docker exec -ti "$FLASK_CONTAINER_NAME" flask db init
docker exec -ti "$FLASK_CONTAINER_NAME" flask db migrate
docker exec -ti "$FLASK_CONTAINER_NAME" flask db upgrade

# Seed Postgres with the data in `/sql`
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/venues.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/artists.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/shows.sql

# Launch the website
open http://localhost:"$FLASK_PORT"
```

### The Hands-on way

This is the same as above, but you do each of the steps yourself

1. **Create an `.env` file with the following values:**

```bash
FLASK_PORT=5000
POSTGRES_HOST=postgres-fyyur
POSTGRES_DB=fyyur
POSTGRES_USER=showfyyur
POSTGRES_PASSWORD=password
PYTHONPATH=/usr/src/app/
PYTHONUNBUFFERED=0
FLASK_CONTAINER_NAME=fyyur
POSTGRES_CONTAINER_NAME=postgres-fyyur
```

2. **Load those variables into your shell:**

```bash
source .env
```

3. **Bring up the container:**

```bash
docker compose up -d
```

4. **Once the container is running, initialize the Flask db**

```bash
docker exec -ti "$FLASK_CONTAINER_NAME" flask db init
```
You should see something like this:
```bash
Creating directory /usr/src/app/migrations ...  done
  Creating directory /usr/src/app/migrations/versions ...  done
  Generating /usr/src/app/migrations/alembic.ini ...  done
  Generating /usr/src/app/migrations/README ...  done
  Generating /usr/src/app/migrations/script.py.mako ...  done
  Generating /usr/src/app/migrations/env.py ...  done
  Please edit configuration/connection/logging settings in '/usr/src/app/migrations/alembic.ini' before
  proceeding.
```

5. **Run a migration**

```bash
docker exec -ti "$FLASK_CONTAINER_NAME" flask db migrate
```
You should see the plan for your new tables:
```bash
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'artists'
INFO  [alembic.autogenerate.compare] Detected added table 'venues'
INFO  [alembic.autogenerate.compare] Detected added table 'shows'
  Generating /usr/src/app/migrations/versions/640ab7c3ab78_.py ...  done
```

6. **Upgrade the db**

```bash
docker exec -ti "$FLASK_CONTAINER_NAME" flask db upgrade
```
Boom, it's done:
```bash
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 640ab7c3ab78, empty message
```
If you have `pgcli` (or `psql`) installed, you can validate this. Here's `pgcli`:
```bash
pgcli "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB"

Server: PostgreSQL 13.3 (Debian 13.3-1.pgdg100+1)
Version: 3.1.0
Chat: https://gitter.im/dbcli/pgcli
Home: http://pgcli.com
showfyyur@localhost:fyyur> \dt
+----------+-----------------+--------+-----------+
| Schema   | Name            | Type   | Owner     |
|----------+-----------------+--------+-----------|
| public   | alembic_version | table  | showfyyur |
| public   | artists         | table  | showfyyur |
| public   | shows           | table  | showfyyur |
| public   | venues          | table  | showfyyur |
+----------+-----------------+--------+-----------+
SELECT 4
```

7. **Seed the new Postgres tables with the data in `/sql`:**

```bash
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/venues.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/artists.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/shows.sql
```
You should see something like this:
```bash
# venues.sql
BEGIN
INSERT 0 3
COMMIT

# artists.sql
BEGIN
INSERT 0 3
COMMIT

# shows.sql
BEGIN
INSERT 0 5
COMMIT
```

8. **Launch the site and get you some Music:**

Navigate to [project homepage](http://localhost:5000). 

