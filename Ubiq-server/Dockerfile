FROM node:22.9.0

COPY . .

RUN npm install

EXPOSE 8009

RUN useradd -u 8877 ubiq

USER ubiq

CMD ["node", "--loader", "ts-node/esm", "app.ts"]