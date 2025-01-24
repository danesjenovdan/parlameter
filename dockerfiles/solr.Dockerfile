FROM solr:8.11.0

COPY ./slolem /opt/solr-slolem
COPY ./parlasearch-conf /parlasearch-conf

# mitigate CVE-2021-45046
USER root
RUN rm server/lib/ext/log4j*.jar
COPY ./log4j/* server/lib/ext/
USER solr

ENV LD_LIBRARY_PATH=/opt/solr-slolem/bin

ENV SOLR_HOME=/var/solr/data

EXPOSE 8983
