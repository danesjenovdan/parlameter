# ---
# USE THIS DOCKERFILE ONLY IN DEV WITH DOCKER COMPOSE
# ---
FROM node:24-alpine

# set current directory
WORKDIR /app

# install dependencies
COPY parlacards/package.json parlacards/yarn.lock ./
RUN yarn

CMD ["yarn", "dev"]
