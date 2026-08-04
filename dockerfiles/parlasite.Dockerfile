# ---
# actual image
# ---
FROM node:26-alpine

# install tini
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

# set current directory
WORKDIR /app

# install production dependencies only
COPY parlasite/package.json parlasite/package-lock.json ./
ENV NODE_ENV=production
RUN npm ci

# copy all files and run build
COPY parlasite .

# set user
USER node

# define port
EXPOSE 3066

CMD ["node", "server/index.js"]
