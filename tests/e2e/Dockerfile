FROM mcr.microsoft.com/playwright:v1.57.0-noble

WORKDIR /tests

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npx", "playwright", "test"]
