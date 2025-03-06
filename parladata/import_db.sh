#!/bin/bash

# EDIT DATABASE NAME TO CHOOSE WHICH ONE YOU WANT
DATABASE_NAME="parlameter_slovenija"
K8S_NAMESPACE="parlameter-slovenija"
SECRETS_NAME="parladata-slovenija-credentials"

# DATABASE PASSWORD IS DYNAMICALLY RETRIEVED FROM THE CLUSTER
DATABASE_USER=$(kubectl get secret $SECRETS_NAME -n $K8S_NAMESPACE -o jsonpath="{.data.DJANGO_DATABASE_USERNAME}" | base64 --decode)
DATABASE_PASSWORD=$(kubectl get secret $SECRETS_NAME -n $K8S_NAMESPACE -o jsonpath="{.data.DJANGO_DATABASE_PASSWORD}" | base64 --decode)

echo
echo "PORT FORWARDING"
nohup kubectl port-forward pod/postgresql-15-0 54321:5432 --namespace=shared &>/dev/null &

# store the kubectl pid for later
KUBECTL_PID=$!

# wait for port forwarding to initialise
sleep 5

echo
echo "DUMPING DATABASE TO db.dump"
PGPASSWORD=$DATABASE_PASSWORD \
    pg_dump -U $DATABASE_USER \
        -f db.dump \
        -d "$DATABASE_NAME" \
        -p 54321 \
        -h localhost

# echo
# echo "DROPPING THE DB VOLUME"
# docker-compose down -v
# docker-compose up -d

# sleep 5

# echo
# echo "LOADING DB INTO CONTAINER"
# docker container exec -i $(docker-compose ps -q db) psql -U postgres parladata < db.dump

# docker-compose down

echo "STOPPING PORT FORWARDING"
kill $KUBECTL_PID

echo
echo "ALL DONE, DATABASE DUMP SAVED to db.dump"
echo "DROPPING AND IMPORTING DB IS DISABLED, DO IT MANUALLY OR FIX THE SCRIPT :D"
# echo "ALL DONE, YOU CAN RUN docker-compose up AND/OR DELETE db.dump"
