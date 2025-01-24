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

```sh
docker-compose up
```

Running docker compose will:
- start a `parlacards` dev server on port `3000`
- serve `parlasite` on port `3066`
- serve `parlassets` on port `8080`

**If cards, static files (css, js, ...) or something doesn't load you may need to change evironment variables in docker-compose.yaml or parlasite/config/index.js with correct urls!**

_TODO: fix parlasite to not use config and move everything to environment variables that can be changed in docker-compose and/or k8s build files. This work is currently ongoing on branch `dev-parlasite-esm`_

## Developing parladata

See [parladata/README.md](./parladata/README.md)

## Developing parlacards

See [parlacards/README.md](./parlacards/README.md)

## Developing parlasite

See [parlasite/README.md](./parlasite/README.md)

## Developing parlassets

See [parlassets/README.md](./parlassets/README.md)
