import dotenv from "dotenv";
dotenv.config();

import path from "path";
import fs from "fs";
import { PrismaClient } from "@prisma/client";
import xlsx from "xlsx";

const prisma = new PrismaClient();

function readTitlesFromExcelOrCsv(inputPath: string): string[] {
  const ext = path.extname(inputPath).toLowerCase();
  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found at ${inputPath}`);
  }

  const workbook = xlsx.readFile(inputPath);
  const sheetName = workbook.SheetNames[0] ?? "";
  if (!sheetName) {
    throw new Error("No sheets found in the workbook");
  }
  const maybeSheet = workbook.Sheets[sheetName as string];
  if (!maybeSheet) {
    throw new Error(`Sheet '${sheetName}' not found in workbook`);
  }
  const sheet = maybeSheet; // now typed as WorkSheet
  const rows: any[] = xlsx.utils.sheet_to_json(sheet, { defval: "" });

  // Try to detect a reasonable column for title strings
  // Priority: 'Title Name in Lower', 'title', 'Title', else first stringy column
  const columns = rows.length ? Object.keys(rows[0]) : [];
  let titleCol =
    columns.find((c) => c.toLowerCase().includes("title name in lower")) ||
    columns.find((c) => c.toLowerCase() === "title") ||
    columns.find((c) => c.toLowerCase().includes("title")) ||
    columns[1] || // often second col in excel screenshot
    columns[0];

  if (!titleCol) return [];

  const titles = rows
    .map((r) => String(r[titleCol] ?? "").trim())
    .filter((s) => s.length > 0);

  return Array.from(new Set(titles));
}

async function main() {
  const inputRel = process.argv[2] || "/Clean_Dataset.xlsx";
  const inputPath = path.resolve(process.cwd(), inputRel);
  console.log(`Reading titles from: ${inputPath}`);

  const titles = readTitlesFromExcelOrCsv(inputPath);
  console.log(`Found ${titles.length} titles. Inserting (skip duplicates)...`);

  if (titles.length === 0) {
    console.warn("No titles found to insert.");
    return;
  }

  // Insert in batches to avoid exceeding parameter limits
  const batchSize = 500;
  for (let i = 0; i < titles.length; i += batchSize) {
    const slice = titles.slice(i, i + batchSize);
    await prisma.title.createMany({
      data: slice.map((name) => ({ name })),
      skipDuplicates: true,
    });
    console.log(
      `Inserted ${Math.min(i + batchSize, titles.length)}/${titles.length}`
    );
  }

  console.log("Done.");
}

main()
  .catch((err) => {
    console.error(err);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
