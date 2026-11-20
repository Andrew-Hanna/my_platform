import { useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { apiPost, ApiError } from "../lib/api";
import { button, field, Notice, page } from "./shared";

export default function ResetPasswordPage() {
  const { token = "" } = useParams();
  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await apiPost("/auth/password/reset", { token, password });
      setDone(true);
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
      <h1 style={{ fontSize: 22 }}>Choose a new password</h1>
      {error && <Notice tone="error">{error}</Notice>}
      {done ? (
        <>
          <Notice tone="ok">Your password has been changed.</Notice>
          <p>
            <Link to="/login">Go to sign in</Link>
          </p>
        </>
      ) : (
        <form onSubmit={onSubmit}>
          <label htmlFor="password">New password</label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={field}
          />
          <button type="submit" disabled={busy} style={button}>
            Save password
          </button>
        </form>
      )}
    </main>
  );
}
