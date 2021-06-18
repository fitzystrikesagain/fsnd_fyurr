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


# Load env vars and start container
step "1" "Start" "Waiting for $FLASK_CONTAINER_NAME to start"
source .env
docker compose up -d
while [[ "$(curl -s -o /dev/null -w "%{http_code}" localhost:"$FLASK_PORT")" != "200" ]]; do
  printf .
  sleep 1
done
step "1" "End" "Waiting for $FLASK_CONTAINER_NAME to start"

step "2" "Start" "Initializing database and performing migrations"
docker exec -ti "$FLASK_CONTAINER_NAME" flask db init
docker exec -ti "$FLASK_CONTAINER_NAME" flask db migrate
docker exec -ti "$FLASK_CONTAINER_NAME" flask db upgrade
step "2" "End" "Initializing database and performing migrations"

step "3" "Start" "Loading tables with venues, artists, and shows data"
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/venues.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/artists.sql
docker exec -u root "$POSTGRES_CONTAINER_NAME" psql "$POSTGRES_DB" "$POSTGRES_USER" -f /tmp/shows.sql
step "3" "End" "Loading tables with venues, artists, and shows data"

step "4" "Start" "Launching website"
open http://localhost:"$FLASK_PORT"
step "4" "End" "Launching website"
