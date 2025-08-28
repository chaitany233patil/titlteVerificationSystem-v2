import { Router } from "express";
import { PrismaClient } from "@prisma/client";
import fetch from "node-fetch";

const router = Router();
const prisma = new PrismaClient();

router.get("/", async (_req, res) => {
  try {
    const titles = await prisma.title.findMany({
      orderBy: { createdAt: "desc" },
    });
    res.json({ titles });
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch titles" });
  }
});

router.post("/verify", async (req, res) => {
  try {
    const { title, threshold } = req.body as {
      title?: string;
      threshold?: number;
    };
    if (!title || title.trim().length === 0) {
      return res.status(400).json({ error: "title is required" });
    }

    // Fetch existing titles from DB
    const existing = await prisma.title.findMany({ select: { name: true } });
    const existingTitles = existing.map((t) => t.name);

    // Call ML service
    const mlUrl =
      process.env.ML_SERVICE_URL || "http://localhost:8000/check-similarity";
    const response = await fetch(mlUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        existing_titles: existingTitles,
        threshold,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(502).json({ error: "ML service error", details: text });
    }
    const data = await response.json();

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: "Verification failed" });
  }
});

router.post("/add", async (req, res) => {
  try {
    const { title } = req.body as { title?: string };
    if (!title || title.trim().length === 0) {
      return res.status(400).json({ error: "title is required" });
    }

    const newTitle = await prisma.title.create({ data: { name: title } });
    res.json({ title: newTitle });
  } catch (error) {
    res.status(500).json({ error: "Failed to add title" });
  }
});

router.get("/:id", async (req, res) => {
  const { id } = req.params as { id?: string };
  if (!id) {
    return res.status(400).json({ error: "id is required" });
  }
  const title = await prisma.title.findUnique({ where: { id: parseInt(id) } });
  if (!title) {
    return res.status(404).json({ error: "Title not found" });
  }
  res.json({ title });
});

export default router;
