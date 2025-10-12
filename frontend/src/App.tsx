import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

type Match = {
  title: string;
  similarity: number;
  type: "phonetic" | "lexical" | "semantic";
};

function toPercent(value: number): string {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return `${pct.toFixed(0)}%`;
}

function App() {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [threshold, setThreshold] = useState<number>(0.75);
  const [version, setVersion] = useState<string>("v1");
  const [adding, setAdding] = useState(false);
  const [addResult, setAddResult] = useState<string | null>(null);

  const apiBase = useMemo(() => {
    return import.meta.env.VITE_API_URL || "http://localhost:4000";
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setStatus(null);
    setMatches([]);
    setAddResult(null);
    const t = title.trim();
    if (!t) {
      setError("Please enter a title");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/titles/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: t, threshold, version }),
      });
      if (!res.ok) {
        const tx = await res.text();
        throw new Error(tx);
      }
      const data = await res.json();
      setStatus(data.status);
      setMatches(data.matches || []);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Request failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const onRegister = async () => {
    const t = title.trim();
    if (!t) return;
    setAdding(true);
    setAddResult(null);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/titles/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: t }),
      });
      if (!res.ok) {
        const tx = await res.text();
        throw new Error(tx || "Failed to add title");
      }
      await res.json();
      setAddResult("Title registered successfully");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Request failed";
      setError(message);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-40 backdrop-blur bg-white/70 border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-brand" />
            <span className="text-xl font-semibold">TitleGuard</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <a href="#how" className="hover:text-brand">
              How it works
            </a>
            <a href="#architecture" className="hover:text-brand">
              Architecture
            </a>
            <a href="#about" className="hover:text-brand">
              About
            </a>
          </nav>
        </div>
      </header>

      {/* Hero / Form */}
      <main className="flex-1">
        <section className="bg-gradient-to-b from-white to-gray-50">
          <div className="max-w-6xl mx-auto px-4 py-12 md:py-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                Check Title Similarity with Confidence
              </h1>
              <p className="mt-3 text-lg text-gray-600">
                Detect phonetic, lexical, and semantic similarities. Tune
                thresholds and preview probabilities.
              </p>
            </div>

            <form
              onSubmit={onSubmit}
              className="mt-10 grid grid-cols-1 md:grid-cols-12 gap-3"
            >
              <input
                aria-label="Proposed title"
                placeholder="Enter a title to verify"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="md:col-span-6 px-4 py-3 rounded-md border border-gray-300 focus:ring-2 focus:ring-brand focus:outline-none"
              />
              <select
                aria-label="Version"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                className="md:col-span-2 px-4 py-3 rounded-md border border-gray-300 focus:ring-2 focus:ring-brand focus:outline-none"
              >
                <option value="v1">v1</option>
                <option value="v2">v2 (coming soon)</option>
              </select>
              <select
                aria-label="Similarity threshold"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="md:col-span-2 px-4 py-3 rounded-md border border-gray-300 focus:ring-2 focus:ring-brand focus:outline-none"
              >
                <option value={0.6}>0.60 (loose)</option>
                <option value={0.7}>0.70</option>
                <option value={0.75}>0.75 (default)</option>
                <option value={0.8}>0.80</option>
                <option value={0.85}>0.85 (strict)</option>
                <option value={0.9}>0.90</option>
              </select>
              <button
                type="submit"
                disabled={loading}
                className="md:col-span-2 px-4 py-3 rounded-md bg-brand text-white font-medium hover:bg-brand-dark transition-colors"
              >
                {loading ? "Checking..." : "Check"}
              </button>
            </form>

            <AnimatePresence initial={false}>
              {error && (
                <motion.p
                  key="error"
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  className="mt-4 text-sm text-red-600"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {status && (
                <motion.div
                  key="status"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ type: "spring", stiffness: 380, damping: 28 }}
                  className="mt-8 p-4 rounded-lg border bg-white shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm">
                      <span className="font-semibold">Status:</span> {status}
                    </p>
                    <p className="text-sm text-gray-500">
                      Threshold: {threshold}
                    </p>
                  </div>
                  {status === "Unique" && (
                    <div className="mt-4 flex items-center gap-3">
                      <button
                        type="button"
                        onClick={onRegister}
                        disabled={adding || !title.trim()}
                        className="px-4 py-2 rounded-md bg-brand text-white font-medium hover:bg-brand-dark transition-colors disabled:opacity-60"
                      >
                        {adding ? "Registering..." : "Register title"}
                      </button>
                      {addResult && (
                        <span className="text-sm text-green-600">
                          {addResult}
                        </span>
                      )}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {matches.length > 0 && (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 12 }}
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  className="mt-6 grid grid-cols-1 gap-4"
                >
                  {matches.map((m, idx) => (
                    <motion.div
                      key={`${m.title}-${m.type}-${idx}`}
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-4 rounded-lg border bg-white shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{m.title}</p>
                          <p className="text-sm text-gray-500 capitalize">
                            {m.type}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Probability</p>
                          <p className="text-xl font-semibold">
                            {toPercent(m.similarity)}
                          </p>
                        </div>
                      </div>
                      <div className="mt-3 h-2 bg-gray-200 rounded">
                        <motion.div
                          className="h-2 bg-brand rounded"
                          initial={{ width: 0 }}
                          animate={{ width: toPercent(m.similarity) }}
                          transition={{ duration: 0.6, delay: 0.05 * idx }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="border-t bg-white">
          <div className="max-w-6xl mx-auto px-4 py-16">
            <h2 className="text-3xl font-bold">How it works</h2>
            <p className="mt-3 text-gray-600 max-w-3xl">
              We compute multiple similarity signals: phonetic (sound-alike),
              lexical (keyword overlap via TF-IDF cosine), and semantic (SBERT
              embeddings). Your selected threshold filters out weak matches, and
              we present probabilities for transparency.
            </p>
          </div>
        </section>

        {/* Architecture */}
        <section id="architecture" className="border-t bg-gray-50">
          <div className="max-w-6xl mx-auto px-4 py-16">
            <h2 className="text-3xl font-bold">Architecture</h2>
            <div className="mt-6 grid md:grid-cols-3 gap-4">
              <motion.div
                whileHover={{ y: -3 }}
                className="p-4 rounded-lg border bg-white shadow-sm"
              >
                <h3 className="font-semibold">Frontend</h3>
                <p className="text-sm text-gray-600 mt-1">
                  React + Tailwind + Framer Motion UI collects input and
                  visualizes probabilities.
                </p>
              </motion.div>
              <motion.div
                whileHover={{ y: -3 }}
                className="p-4 rounded-lg border bg-white shadow-sm"
              >
                <h3 className="font-semibold">Backend API</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Express fetches titles, forwards threshold/version to the ML
                  service.
                </p>
              </motion.div>
              <motion.div
                whileHover={{ y: -3 }}
                className="p-4 rounded-lg border bg-white shadow-sm"
              >
                <h3 className="font-semibold">ML Service</h3>
                <p className="text-sm text-gray-600 mt-1">
                  FastAPI computes phonetic, lexical, and semantic scores,
                  returns matches.
                </p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* About */}
        <section id="about" className="border-t bg-white">
          <div className="max-w-6xl mx-auto px-4 py-16">
            <h2 className="text-3xl font-bold">About</h2>
            <p className="mt-3 text-gray-600 max-w-3xl">
              TitleGuard helps teams avoid duplicate or confusing titles by
              checking multiple similarity signals and exposing clear
              probabilities.
            </p>
          </div>
        </section>
      </main>

      <footer className="border-t bg-white">
        <div className="max-w-6xl mx-auto px-4 py-6 text-sm text-gray-500">
          © {new Date().getFullYear()} TitleGuard
        </div>
      </footer>
    </div>
  );
}

export default App;
