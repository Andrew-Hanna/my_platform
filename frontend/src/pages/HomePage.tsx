import { apiPost } from "../lib/api";
import { useAuth } from "../lib/auth";
import { button, page } from "./shared";

export default function HomePage() {
  const { user, setUser } = useAuth();

  async function logout() {
    await apiPost("/auth/logout");
    setUser(null);
    window.location.assign("/login");
  }

  return (
    <main style={page}>
      <h1 style={{ fontSize: 22 }}>Hello, {user?.name}</h1>
      <p style={{ color: "#5d6676", fontSize: 14 }}>
        Your sessions and booklets will appear here in later phases.
      </p>
      <p>
        <a href="/profile">My profile</a>
      </p>
      <button onClick={logout} style={{ ...button, background: "#5d6676" }}>
        Sign out
      </button>
    </main>
  );
}
