# Parlameter frontend


## Notes on translations

Integration with our weblate instance for translations is enabled on this repo.

The base language for translations is `en`.

The following components are added:
- parlasite - `defaults.json`, `sitemap.json`
- parlacards - `defaults.yaml`
- parlacards - card specific `.yaml` files are automatically picked up when pushed to the `dev` branch

## Adding new translation files or keys

**When adding new translation keys/files only add them for `en`. Weblate will create a PR when translations for other languages are created.**

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
<!-- - start a `parlacards` dev server on port `3000` -->

> [!NOTE]
> This will not start `parlacards` inside docker because of some underlying issues with how it is run, you will need to run it separately!

**If something (other than `parlacards`) doesn't load you may need to change evironment variables in docker-compose.yaml with correct urls!**

### 2. Start parlacards

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

## Developing parladata

See [parladata/README.md](./parladata/README.md)

## Developing parlacards

See [parlacards/README.md](./parlacards/README.md)

## Developing parlasite

See [parlasite/README.md](./parlasite/README.md)

## Developing parlassets

See [parlassets/README.md](./parlassets/README.md)
