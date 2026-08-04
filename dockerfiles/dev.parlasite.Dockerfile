# ---
# USE THIS DOCKERFILE ONLY IN DEV WITH DOCKER COMPOSE
# ---
FROM node:26-alpine

# set current directory
WORKDIR /app

# install dependencies
COPY parlasite/package.json parlasite/package-lock.json ./
RUN npm ci

CMD ["npm", "run", "dev"]
