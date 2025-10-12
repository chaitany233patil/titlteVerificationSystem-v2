import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import titlesRouter from "./routes/titles";

dotenv.config();
const port = process.env.PORT || 4000;
const app = express();

app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ ok: true }));
app.use("/api/titles", titlesRouter);

app.listen(port, () => console.log(`Backend running on :${port}`));
