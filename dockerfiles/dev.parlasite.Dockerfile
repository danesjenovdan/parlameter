# ---
# USE THIS DOCKERFILE ONLY IN DEV WITH DOCKER COMPOSE
# ---
FROM node:24-alpine

# set current directory
WORKDIR /app

# install dependencies
COPY parlasite/package.json parlasite/yarn.lock ./
RUN yarn

CMD ["yarn", "dev"]
