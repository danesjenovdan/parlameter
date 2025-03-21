# Parlameter

## Developing with docker-compose

### 1. Start docker compose

```sh
docker-compose up
```

Running docker compose will:
- start `postgresql`, `memcached`, and `solr`
- start `parladata` on port `8000` (backend)
- start `parlassets` on port `8080` (static files)
- start `parlasite` on port `3066` (frontend)
- start a `parlacards` <!-- dev --> server on port `3000`

You should now be able to access the Parlameter website on http://localhost:3066 and the admin interface at http://localhost:8000/admin.

> [!NOTE]
> This will start the `parlacards` "production" server inside docker. The cards will build and then be statically served on every restart. Because of some underlying issues with how the dev mode differs from production, you will need to run parlacards separately if you want to work on a single card!

**If something doesn't load you may need to change evironment variables in docker-compose.yaml with correct urls.**

### 2. Get some data

You should set up Parladata minimally. Run:
- `docker-compose exec parladata python manage.py migrate` to make sure the database schema is up to date,
- `docker-compose exec parladata python manage.py createsuperuser` to make yourself a superuser,
- import a database. For now, please check [parladata/README.md](./parladata/README.md) for more instructions on this step, but a "simplest version" should appear here shortly after this TODO is resolved.

## Developing individual cards

First open a separate terminal and go to the parlacards folder:
```sh
cd parlacards
```

There are two options for running `parlacards` depending on what you want to do:

#### a) development
```sh
# start a development server (with hot reload and good dev experience, but doesnt work within parlasite)
yarn dev
```

#### b) serving built cards that work inside parlasite
```sh
# build the cards
VITE_PARLASSETS_URL=http://localhost:8080 \
yarn build

# serve the built cards
VITE_PARLASSETS_URL=http://localhost:8080 \
VITE_PARLACARDS_URL=http://localhost:3000 \
VITE_PARLASITE_URL=http://localhost:3066 \
VITE_PARLADATA_URL=http://localhost:8000/v3 \
yarn start
```

> [!NOTE]
> Make sure `parlacards/dist/client` folder exists before running docker compose to prevent permission issues!

---

### More development instructions for each part of Parlameter

For parladata see [parladata/README.md](./parladata/README.md)

For parlacards see [parlacards/README.md](./parlacards/README.md)

For parlasite see [parlasite/README.md](./parlasite/README.md)

For parlassets see [parlassets/README.md](./parlassets/README.md)

---

## Notes on translations

Integration with our weblate instance for translations is enabled on this repo.

The base language for translations is `en`.

The following components are added:
- parlasite - `defaults.json`, `sitemap.json`
- parlacards - `defaults.yaml`
- parlacards - card specific `.yaml` files are automatically picked up when pushed to the `dev` branch

## Adding new translation files or keys

**When adding new translation keys/files only add them for `en`. Weblate will create a PR when translations for other languages are created.**
