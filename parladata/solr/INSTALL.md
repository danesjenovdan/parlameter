## Installation without docker:

- As user run:

```bash
git clone https://github.com/danesjenovdan/parlasearch.git
```

- Create `config/production.js` (see `config/sample.js`)
- Create `config/ecosystem.config.js` for pm2

```bash
pm2 startOrRestart /home/<user>/parlasearch/config/ecosystem.config.js
```

- Then as root install the solr service:
```bash
# inside home dir
wget http://www-eu.apache.org/dist/lucene/solr/7.7.0/solr-7.7.0.tgz

tar xzf solr-7.7.0.tgz solr-7.7.0/bin/install_solr_service.sh --strip-components=2

./install_solr_service.sh solr-7.7.0.tgz

sudo su - solr -c "/opt/solr/bin/solr create -c parlasearch -n data_driven_schema_configs"

# run script from where you cloned the repo
/home/<user>/parlasearch/solr/scripts/linkconf_prod.sh

service solr restart
```
