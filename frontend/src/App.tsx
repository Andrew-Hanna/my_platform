import { useEffect, useState } from "react";

type ApiStatus = "checking" | "ok" | "unreachable";

// Asks the backend for its health status through the /api proxy.
export default function App() {
  const [status, setStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((body: { status: string }) =>
        setStatus(body.status === "ok" ? "ok" : "unreachable"),
      )
      .catch(() => setStatus("unreachable"));
  }, []);

  const message =
    status === "checking"
      ? "Checking the API…"
      : status === "ok"
        ? "API OK"
        : "API not reachable. Is the backend running on port 8000?";

  return (
    <main style={{ padding: "16px", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: "22px" }}>LMS</h1>
      <p>{message}</p>
    </main>
  );
}
