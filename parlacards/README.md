# parlacards

Embedable cards for Parlameter.

---

## Developing with docker-compose

See [../README.md](../README.md)

---

## Local card development

### Install dependencies

```sh
npm i
```

### Run card dev server

To develop cards run this command. It will run the card dev server on `http://localhost:3000/` by default.

```sh
npm run dev
```

### Run parlassets

The dev server will expect parlassets to be served from port 8080.

In another terminal open run this command to build and serve the static files required.

```sh
cd ../parlassets && npm run dev
```

---

## Working on the SSR server

_Note that you need to have built the cards at least once before with `npm run build`_

To work on the server that serves the server-side rendered cards run this command. It will run the server on `http://localhost:3000/` by default.

```sh
npm run start:watch
```



---

## Build and run production server

### Install dependencies

```sh
npm i
```

### Build

This will build:
- client js
- server bundles needed for SSR
- locale markdown files

```sh
npm run build
```

### Run server

This runs the production server that will render and serve built cards.

```sh
npm run start
```

---

## See also:

- [More on how cards work](./docs/how-cards-work.md)
