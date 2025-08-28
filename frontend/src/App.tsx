import { useMemo, useState } from "react";
import "./App.css";

type Match = {
  title: string;
  similarity: number;
  type: "phonetic" | "lexical" | "semantic";
};

function App() {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);

  const apiBase = useMemo(() => {
    return import.meta.env.VITE_API_URL || "http://localhost:4000";
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setStatus(null);
    setMatches([]);
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
        body: JSON.stringify({ title: t }),
      });
      if (!res.ok) {
        const tx = await res.text();
        throw new Error(tx);
      }
      const data = await res.json();
      setStatus(data.status);
      setMatches(data.matches || []);
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="container"
      style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}
    >
      <h1>Title Verification</h1>
      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
        <input
          aria-label="Proposed title"
          placeholder="Enter a title to verify"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ flex: 1, padding: 10, fontSize: 16 }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: "10px 16px" }}
        >
          {loading ? "Checking..." : "Check"}
        </button>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {status && (
        <p>
          <strong>Status:</strong> {status}
        </p>
      )}
      {matches.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h3>Similar Matches</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                    padding: 8,
                  }}
                >
                  Title
                </th>
                <th
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                    padding: 8,
                  }}
                >
                  Type
                </th>
                <th
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                    padding: 8,
                  }}
                >
                  Score
                </th>
              </tr>
            </thead>
            <tbody>
              {matches.map((m, idx) => (
                <tr key={idx}>
                  <td style={{ padding: 8, borderBottom: "1px solid #f0f0f0" }}>
                    {m.title}
                  </td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f0f0f0" }}>
                    {m.type}
                  </td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f0f0f0" }}>
                    {m.similarity.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
