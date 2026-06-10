"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  education?: string;
  target_instansi?: string;
  is_superadmin?: boolean;
}

interface AuthCtx {
  user: User | null;
  token: string | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthCtx>({ user: null, token: null, setAuth: () => {}, logout: () => {}, loading: true });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("cpns_token");
    const u = localStorage.getItem("cpns_user");
    if (!t || !u) {
      setLoading(false);
      return;
    }

    setToken(t);
    fetch("/api/users/me", { headers: { Authorization: `Bearer ${t}` } })
      .then((res) => res.json())
      .then((res) => {
        if (res.ok && res.data) {
          localStorage.setItem("cpns_user", JSON.stringify(res.data));
          setUser(res.data);
        } else {
          localStorage.removeItem("cpns_token");
          localStorage.removeItem("cpns_user");
          setToken(null);
          setUser(null);
        }
      })
      .catch(() => {
        try { setUser(JSON.parse(u)); } catch {}
      })
      .finally(() => setLoading(false));
  }, []);

  const setAuth = (t: string, u: User) => {
    localStorage.setItem("cpns_token", t);
    localStorage.setItem("cpns_user", JSON.stringify(u));
    setToken(t);
    setUser(u);
  };

  const logout = () => {
    localStorage.removeItem("cpns_token");
    localStorage.removeItem("cpns_user");
    setToken(null);
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, token, setAuth, logout, loading }}>{children}</AuthContext.Provider>;
}

export function useAuth() { return useContext(AuthContext); }
