import { useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiPost, ApiError } from "../lib/api";
import { useAuth, type User } from "../lib/auth";
import { button, field, Notice, page } from "./shared";

export default function InvitePage() {
  const { token = "" } = useParams();
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (password !== confirm) {
      setError("The two passwords do not match.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const user = await apiPost<User>("/auth/invites/accept", {
        token,
        password,
      });
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
      <h1 style={{ fontSize: 22 }}>Welcome</h1>
      <p style={{ color: "#5d6676", fontSize: 14 }}>
        Choose a password to activate your account. Use at least 8 characters.
      </p>
      {error && <Notice tone="error">{error}</Notice>}
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
        <label htmlFor="confirm">Repeat password</label>
        <input
          id="confirm"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          style={field}
        />
        <button type="submit" disabled={busy} style={button}>
          {busy ? "Saving…" : "Set password"}
        </button>
      </form>
    </main>
  );
}
