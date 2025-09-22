# ---
# build stage image
# ---
FROM node:24-alpine AS build-parlacards

# set current directory
WORKDIR /app

# install dependencies
COPY parlacards/package.json parlacards/yarn.lock ./
RUN yarn

# copy all files and run build
# NOTE: image needs to be build in root not in parlacards folder to have access to parlassets folder
#       so specify paths relative to the root
COPY parlassets /parlassets
COPY parlacards .
ARG VITE_PARLASSETS_URL
RUN yarn build

# ---
# build stage image
# ---
FROM node:24-alpine AS build-parlassets

# set current directory
WORKDIR /app

# install dependencies
COPY parlassets/package.json parlassets/yarn.lock ./
RUN yarn

# copy all files and run build
COPY parlassets .
ENV NODE_ENV=production
RUN yarn build

# ---
# actual image for parlassets; use `--target parlassets` to build
# ---
FROM nginx:alpine AS parlassets

# copy nginx configuration
COPY parlassets/default.conf /etc/nginx/conf.d/default.conf

# copy built files from the 'build' container into the nginx container
COPY --from=build-parlassets /app/public /usr/share/nginx/html
COPY --from=build-parlacards /app/dist/client /usr/share/nginx/html/assets

# ---
# actual image for parlacards; use `--target parlacards` to build
# ---
FROM node:24-alpine AS parlacards

# install tini
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

# set current directory
WORKDIR /app

# install production dependencies only
COPY parlacards/package.json parlacards/yarn.lock ./
ENV NODE_ENV=production
RUN yarn && yarn cache clean

# copy all needed files from build stage image
COPY --from=build-parlacards /app/build ./build
COPY --from=build-parlacards /app/dist ./dist
COPY --from=build-parlacards /app/server ./server
COPY --from=build-parlacards /app/instrument.js ./instrument.js

# set user
USER node

# define port
EXPOSE 3000

CMD ["node", "--import", "./instrument.js", "server/index.js"]
