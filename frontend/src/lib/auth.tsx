import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { Navigate } from "react-router-dom";
import { apiGet, ApiError } from "./api";

export type User = { id: number; name: string; email: string; role: string };

type AuthState = {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
};

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  setUser: () => {},
});

// Loads the logged-in user once when the app starts (GET /auth/me).
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<User>("/auth/me")
      .then(setUser)
      .catch((error: unknown) => {
        if (!(error instanceof ApiError) || error.status !== 401) {
          console.error(error);
        }
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  return useContext(AuthContext);
}

// Sends logged-out visitors to /login and anyone without an allowed role to /.
export function RequireRole({
  roles,
  children,
}: {
  roles?: string[];
  children: ReactNode;
}) {
  const { user, loading } = useAuth();
  if (loading) return <p style={{ padding: 16 }}>Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}
