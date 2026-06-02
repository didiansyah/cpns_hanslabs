"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { Lock } from "lucide-react";

function ResetPasswordForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { setAuth } = useAuth();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    if (!token) {
      setError("Link reset tidak valid. Minta link baru dari halaman lupa password.");
      return;
    }
    if (password.length < 6) {
      setError("Password minimal 6 karakter");
      return;
    }
    if (password !== confirmPassword) {
      setError("Konfirmasi password tidak sama");
      return;
    }

    setLoading(true);
    try {
      const res = await apiPost("/auth/reset-password", { token, password });
      if (res.ok && res.data) {
        setAuth(res.data.token, res.data.user);
        router.push("/dashboard");
      } else {
        setError(res.error || "Gagal reset password");
      }
    } catch {
      setError("Gagal menghubungi server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl" style={{ fontFamily: "Georgia, serif" }}>Reset Password</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">Buat password baru untuk akun CPNS Anda</p>
      </CardHeader>
      <CardContent>
        {error && <div className="mb-4 p-3 text-sm text-destructive bg-destructive/10 rounded-xl">{error}</div>}
        {!token && <div className="mb-4 p-3 text-sm text-muted-foreground bg-secondary rounded-xl">Token reset tidak ditemukan di URL.</div>}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Password Baru</label>
            <div className="relative mt-1">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimal 6 karakter"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Konfirmasi Password</label>
            <div className="relative mt-1">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Ulangi password baru"
                className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground"
                onKeyDown={(e) => e.key === "Enter" && password && confirmPassword && handleSubmit()}
              />
            </div>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={loading || !token || !password || !confirmPassword}>
            {loading ? "Menyimpan..." : "Simpan Password Baru"}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Butuh link baru? <Link href="/forgot-password" className="text-foreground font-medium hover:underline">Lupa password</Link>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-card">
      <div className="absolute top-4 right-4"><ThemeToggle /></div>
      <Suspense fallback={<div className="text-sm text-muted-foreground">Memuat...</div>}>
        <ResetPasswordForm />
      </Suspense>
    </div>
  );
}
