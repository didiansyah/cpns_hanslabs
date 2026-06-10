"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { apiGet, apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { Mail, Lock } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError("");
    setLoading(true);
    const res = await apiPost("/auth/login", { email, password });
    setLoading(false);
    if (res.ok && res.data) {
      setAuth(res.data.token, res.data.user);
      const profile = await apiGet("/users/me");
      if (profile.ok && profile.data) {
        setAuth(res.data.token, profile.data);
        router.push(profile.data.is_superadmin ? "/dashboard/superadmin" : "/dashboard");
      } else {
        router.push("/dashboard");
      }
    } else {
      setError(res.error || "Login gagal");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-card">
      <div className="absolute top-4 right-4"><ThemeToggle /></div>
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl" style={{ fontFamily: "Georgia, serif" }}>Masuk</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Belajar CPNS 2026</p>
        </CardHeader>
        <CardContent>
          {error && <div className="mb-4 p-3 text-sm text-destructive bg-destructive/10 rounded-xl">{error}</div>}
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Email</label>
              <div className="relative mt-1">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="nama@email.com"
                  className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground"
                  onKeyDown={(e) => e.key === "Enter" && email && password && handleLogin()}
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">Password</label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimal 6 karakter"
                  className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground"
                  onKeyDown={(e) => e.key === "Enter" && email && password && handleLogin()}
                />
              </div>
            </div>
            <Button className="w-full" onClick={handleLogin} disabled={loading || !email || !password}>
              {loading ? "Masuk..." : "Masuk"}
            </Button>
            <div className="flex items-center justify-between gap-3 text-sm">
              <Link href="/forgot-password" className="text-muted-foreground hover:text-foreground hover:underline">Lupa password?</Link>
              <span className="text-muted-foreground">
                Belum punya akun? <Link href="/register" className="text-foreground font-medium hover:underline">Daftar</Link>
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
