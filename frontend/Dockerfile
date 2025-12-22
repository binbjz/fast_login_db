FROM node:18-bullseye-slim

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

COPY . .
EXPOSE 8080

CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--port", "8080"]
