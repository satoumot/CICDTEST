FROM node:22.17.0

WORKDIR /user/src/frontend

COPY package.json package-lock.json* ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]