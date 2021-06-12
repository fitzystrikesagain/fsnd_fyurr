#!/bin/bash

source config.env
source secrets.env
docker compose down
docker build .
docker compose up --build --force-recreate -d
sleep 5
open http://localhost:"$FLASK_PORT"

if command -v pgcli >/dev/null
then
  pgcli postgresql://"$POSTGRES_USER":"$POSTGRES_PASSWORD"@localhost:5432/"$POSTGRES_DB"
  exit
  fi

