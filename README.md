# Title Verification System v2

A full-stack application for checking title similarity using multiple algorithms (phonetic, lexical, and semantic matching).

## Project Structure

```
├── backend/          # Node.js + Express API with PostgreSQL
├── frontend/         # React + TypeScript + Vite
└── ml-service/       # Python FastAPI ML service
```

## Quick Start

### Prerequisites

- Node.js (v16+)
- Python (v3.10+)
- PostgreSQL database

### 1. Backend Setup

```bash
cd backend
npm install
```

Create a `.env` file in the `backend/` folder:
```
DATABASE_URL="postgresql://user:password@localhost:5432/titledb"
PORT=4000
ML_SERVICE_URL="http://localhost:8000/check-similarity"
```

Set up the database:
```bash
npx prisma migrate dev
npx prisma generate
```

Start the backend:
```bash
npm run dev
```

The backend will run on http://localhost:4000

### 2. ML Service Setup

```bash
cd ml-service
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the ML service:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The ML service will run on http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend/` folder (optional):
```
VITE_API_URL=http://localhost:4000
```

Start the frontend:
```bash
npm run dev
```

The frontend will run on http://localhost:5173

## Running the Full Application

1. Start the backend (Terminal 1): `cd backend && npm run dev`
2. Start the ML service (Terminal 2): `cd ml-service && source venv/bin/activate && uvicorn app.main:app --reload`
3. Start the frontend (Terminal 3): `cd frontend && npm run dev`

Open your browser at http://localhost:5173

## Additional Commands

### Backend
- Build: `npm run build`
- Start production: `npm start`
- Seed database: `npm run seed`

### Frontend
- Build: `npm run build`
- Preview production: `npm run preview`

### ML Service
- Run tests: `python test_similarity.py`
