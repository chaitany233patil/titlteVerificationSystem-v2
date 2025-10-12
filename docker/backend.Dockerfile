FROM node:22

WORKDIR /app

COPY backend/package*.json ./backend/

RUN cd backend && npm install

COPY backend ./backend

RUN cd backend && npx prisma generate

RUN cd backend && npm run build

EXPOSE 4000

CMD ["node", "backend/dist/index.js"]
