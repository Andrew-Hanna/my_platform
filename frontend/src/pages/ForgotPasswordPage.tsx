import { useState, type FormEvent } from "react";
import { apiPost } from "../lib/api";
import { button, field, Notice, page } from "./shared";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      await apiPost("/auth/password/forgot", { email });
    } finally {
      // The answer is the same whether or not the email exists, so always show the same message.
      setSent(true);
      setBusy(false);
    }
  }

  return (
    <main style={page}>
      <h1 style={{ fontSize: 22 }}>Reset password</h1>
      {sent ? (
        <Notice tone="ok">
          If that email has an account, a reset link is on its way.
        </Notice>
      ) : (
        <form onSubmit={onSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={field}
          />
          <button type="submit" disabled={busy} style={button}>
            Send reset link
          </button>
        </form>
      )}
    </main>
  );
}
