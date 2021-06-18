#!/bin/bash

set -e

NUM_STEPS=5

step() {
  cat <<EOF
######################################################################
Step ${1}/${NUM_STEPS} [${2}] -- ${3}
######################################################################
EOF
}

# Clean up all containers, fresh build


# Wait for Flask, open website, exec into container
source .env
mkdir -p data
step "1" "Begin" "Waiting for $FLASK_CONTAINER_NAME to start"
docker compose up -d
while [[ "$(curl -s -o /dev/null -w "%{http_code}" localhost:"$FLASK_PORT")" != "200" ]]; do
  printf .
  sleep 1
done
step "1" "End" "Waiting for $FLASK_CONTAINER_NAME to start"

step "2" "Begin" "Initializing database and performing migrations"
docker exec -ti fyyur flask db init
docker exec -ti fyyur flask db migrate
docker exec -ti fyyur flask db upgrade
step "2" "End" "Initializing database and performing migrations"

step "3" "Begin" "Launching website"
open http://localhost:"$FLASK_PORT"
step "3" "End" "Launching website"

step "4" "Begin" "Loading tables with venues, artists, and shows data"
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/venues.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/artists.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/shows.sql
step "4" "End" "Loading tables with venues, artists, and shows data"

step "5" "Launching pgcli"
pgcli "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB"
