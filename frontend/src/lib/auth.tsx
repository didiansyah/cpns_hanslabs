"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  education?: string;
  target_instansi?: string;
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
    if (t && u) {
      setToken(t);
      try { setUser(JSON.parse(u)); } catch {}
    }
    setLoading(false);
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
