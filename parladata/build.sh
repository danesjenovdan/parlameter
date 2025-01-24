#!/bin/bash

TAG=latest

sudo docker login rg.fr-par.scw.cloud/djnd -u nologin -p $SCW_SECRET_TOKEN

# BUILD AND PUBLISH PRAVNA MREZA
sudo docker build -f Dockerfile -t parladata:$TAG .
sudo docker tag parladata:$TAG rg.fr-par.scw.cloud/djnd/parladata:$TAG
sudo docker push rg.fr-par.scw.cloud/djnd/parladata:$TAG

# BUILD AND PUBLISH SOLR
sudo docker build -f solr/Dockerfile -t parlasolr:$TAG solr
sudo docker tag parlasolr:$TAG rg.fr-par.scw.cloud/djnd/parlasolr:$TAG
sudo docker push rg.fr-par.scw.cloud/djnd/parlasolr:$TAG
