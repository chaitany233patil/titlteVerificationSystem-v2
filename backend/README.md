# Backend - Title Verification API

Node.js + Express backend with PostgreSQL database.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file:
```
DATABASE_URL="postgresql://user:password@localhost:5432/titledb"
PORT=4000
ML_SERVICE_URL="http://localhost:8000/check-similarity"
```

### 3. Setup Database

```bash
npx prisma migrate dev
npx prisma generate
```

### 4. Start the Server

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm run build
npm start
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/titles` - Get all titles
- `POST /api/titles/verify` - Check title similarity
- `POST /api/titles/add` - Add a new title

## Seeding Data

To load titles from an Excel file:
```bash
npm run seed
```
