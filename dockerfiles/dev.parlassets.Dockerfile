# ---
# USE THIS DOCKERFILE ONLY IN DEV WITH DOCKER COMPOSE
# ---
FROM node:24-alpine

# set current directory
WORKDIR /app

# install dependencies
COPY parlassets/package.json parlassets/yarn.lock ./
RUN yarn

CMD ["yarn", "dev"]
