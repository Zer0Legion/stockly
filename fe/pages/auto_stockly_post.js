import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AutoStocklyPost() {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [responseBody, setResponseBody] = useState(null);

  const triggerJob = async () => {
    setMessage("");
    setResponseBody(null);

    const trimmed = token.trim();
    if (!trimmed) {
      setMessage("Please enter a Bearer token.");
      return;
    }

    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/auto_stockly_post`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${trimmed}`,
          Accept: "application/json",
        },
      });

      let data = null;
      const text = await res.text();
      try {
        data = text ? JSON.parse(text) : null;
      } catch (_) {
        // not JSON; keep raw text
      }

      if (!res.ok) {
        setMessage(
          data?.error_message ||
            data?.detail ||
            text ||
            `Request failed (${res.status})`,
        );
        setResponseBody(data ?? text);
        return;
      }

      setMessage("Auto stockly post triggered successfully.");
      setResponseBody(data ?? text ?? null);
    } catch (err) {
      setMessage(`Failed to call API: ${err?.message || String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Run Auto Stockly Post</h1>
      <p className="text-sm text-gray-600">
        Enter your Bearer token and click the button to call the GET endpoint at{" "}
        <code>/auto_stockly_post</code>.
      </p>

      <div className="bg-white border rounded-2xl p-6 shadow space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bearer Token
          </label>
          <Input
            type="password"
            placeholder="Paste your token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
        </div>

        <Button onClick={triggerJob} disabled={loading || !token.trim()}>
          {loading ? "Calling..." : "Run Auto Job"}
        </Button>

        {message ? (
          <div className="mt-2 text-sm">
            <span>{message}</span>
          </div>
        ) : null}

        {responseBody ? (
          <pre className="mt-2 text-xs bg-gray-50 border rounded p-3 overflow-auto">
            {typeof responseBody === "string"
              ? responseBody
              : JSON.stringify(responseBody, null, 2)}
          </pre>
        ) : null}
      </div>
    </div>
  );
}
