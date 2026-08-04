# ---
# USE THIS DOCKERFILE ONLY IN DEV WITH DOCKER COMPOSE
# ---
FROM node:26-alpine

# set current directory
WORKDIR /app

# install dependencies
COPY parlacards/package.json parlacards/package-lock.json ./
RUN npm ci

CMD ["npm", "run", "dev"]
