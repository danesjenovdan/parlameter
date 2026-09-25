# ---
# image for parlassets; use `--target parlassets` to build
# ---
FROM node:26-alpine AS parlassets

# set current directory
WORKDIR /app

# install dependencies
COPY parlassets/package.json parlassets/package-lock.json ./
RUN npm ci

CMD ["npm", "run", "dev"]

# ---
# image for parlacards; use `--target parlacards` to build
# ---
FROM node:26-alpine AS parlacards

# set current directory
WORKDIR /app

# install production dependencies only
COPY parlacards/package.json parlacards/package-lock.json ./
RUN npm ci

# CMD ["npm", "run", "dev"]
CMD ["sh", "-c", "npm run build && npm run start:watch"]

# ---
# image for parlacards dev server; use `--target parlacards-dev` to build
# ---
FROM node:26-alpine AS parlacards-dev

# set current directory
WORKDIR /app

# install production dependencies only
COPY parlacards/package.json parlacards/package-lock.json ./
RUN npm ci

CMD ["npm", "run", "dev"]
