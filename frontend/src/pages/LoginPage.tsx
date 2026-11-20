import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost, ApiError } from "../lib/api";
import { useAuth, type User } from "../lib/auth";
import { button, field, Notice, page } from "./shared";

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const user = await apiPost<User>("/auth/login", { email, password });
      setUser(user);
      navigate("/", { replace: true });
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={page}>
      <h1 style={{ fontSize: 22 }}>Sign in</h1>
      <p style={{ color: "#5d6676", fontSize: 14 }}>
        Accounts are created by your teacher.
      </p>
      {error && <Notice tone="error">{error}</Notice>}
      <form onSubmit={onSubmit}>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={field}
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={field}
        />
        <button type="submit" disabled={busy} style={button}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p style={{ marginTop: 16, fontSize: 14 }}>
        <a href="/forgot-password">Forgot password?</a>
      </p>
    </main>
  );
}
