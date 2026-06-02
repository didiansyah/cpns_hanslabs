"use client";

import { useState } from "react";
import Link from "next/link";
import { apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { Mail } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setMessage("");
    setLoading(true);
    try {
      const res = await apiPost("/auth/forgot-password", { email });
      if (res.ok) {
        setMessage(res.message || "Jika email terdaftar, link reset password sudah dikirim.");
      } else {
        setError(res.error || "Gagal mengirim link reset");
      }
    } catch {
      setError("Gagal menghubungi server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-card">
      <div className="absolute top-4 right-4"><ThemeToggle /></div>
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl" style={{ fontFamily: "Georgia, serif" }}>Lupa Password</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Masukkan email akun CPNS Anda</p>
        </CardHeader>
        <CardContent>
          {error && <div className="mb-4 p-3 text-sm text-destructive bg-destructive/10 rounded-xl">{error}</div>}
          {message && <div className="mb-4 p-3 text-sm text-foreground bg-secondary rounded-xl">{message}</div>}
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
                  onKeyDown={(e) => e.key === "Enter" && email && handleSubmit()}
                />
              </div>
            </div>
            <Button className="w-full" onClick={handleSubmit} disabled={loading || !email}>
              {loading ? "Mengirim..." : "Kirim Link Reset"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Ingat password? <Link href="/login" className="text-foreground font-medium hover:underline">Masuk</Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
