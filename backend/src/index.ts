import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => res.json({ ok: true }));

// Routes
import titlesRouter from './routes/titles';
app.use('/api/titles', titlesRouter);

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`Backend running on :${port}`));

