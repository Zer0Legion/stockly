import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function MakeIGPost() {
  const [exchange, setExchange] = useState("");
  const [ticker, setTicker] = useState("");
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!exchange.trim() || !ticker.trim()) {
      alert("Exchange and ticker are required");
      return;
    }

    const payload = { exchange: exchange.trim(), ticker: ticker.trim() };

    try {
      setLoading(true);
      const headers = { "Content-Type": "application/json" };
      const trimmed = token.trim();
      if (trimmed) {
        headers["Authorization"] = `Bearer ${trimmed}`;
      }

      const res = await fetch(`${API_URL}/create_stockly_post`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }

      const data = await res.json();
      alert("Post creation started successfully.");
      // Optionally clear fields
      setExchange("");
      setTicker("");
      console.log("create_stockly_post response:", data);
    } catch (err) {
      console.error(err);
      alert("Failed to create post: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Create Stockly Post</h1>

      <div className="bg-white border rounded-2xl p-6 shadow space-y-4">
        <p className="text-sm text-gray-600">
          Enter exchange and ticker to create an end-to-end stock analysis post.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Exchange
            </label>
            <Input
              placeholder="e.g. NYSE"
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ticker
            </label>
            <Input
              placeholder="e.g. AAPL"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bearer Token
            </label>
            <Input
              type="password"
              placeholder="Paste Bearer token if required"
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
          </div>

          <div className="flex gap-2">
            <Button type="submit" disabled={loading}>
              {loading ? "Submitting..." : "Create Post"}
            </Button>
            <Button
              type="button"
              onClick={() => {
                setExchange("");
                setTicker("");
              }}
            >
              Reset
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
