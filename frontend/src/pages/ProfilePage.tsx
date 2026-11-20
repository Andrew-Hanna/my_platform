import { useState, type FormEvent } from "react";
import { apiPost, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { button, field, Notice, page } from "./shared";

export default function ProfilePage() {
  const { user } = useAuth();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [notice, setNotice] = useState<{
    tone: "error" | "ok";
    text: string;
  } | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    try {
      await apiPost("/auth/change-password", {
        current_password: current,
        new_password: next,
      });
      setCurrent("");
      setNext("");
      setNotice({ tone: "ok", text: "Your password has been changed." });
    } catch (caught) {
      setNotice({
        tone: "error",
        text:
          caught instanceof ApiError
            ? caught.message
            : "Something went wrong. Please try again.",
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={page}>
      <h1 style={{ fontSize: 22 }}>My profile</h1>
      <p style={{ fontSize: 14, color: "#5d6676" }}>
        {user?.name} · {user?.email}
      </p>
      {notice && <Notice tone={notice.tone}>{notice.text}</Notice>}
      <h2 style={{ fontSize: 18 }}>Change password</h2>
      <form onSubmit={onSubmit}>
        <label htmlFor="current">Current password</label>
        <input
          id="current"
          type="password"
          autoComplete="current-password"
          required
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          style={field}
        />
        <label htmlFor="next">New password</label>
        <input
          id="next"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={next}
          onChange={(e) => setNext(e.target.value)}
          style={field}
        />
        <button type="submit" disabled={busy} style={button}>
          Change password
        </button>
      </form>
    </main>
  );
}
