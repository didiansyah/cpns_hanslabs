"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";
import { Mail, User, Lock, Shield, ArrowLeft, Check } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth } = useAuth();
  const [step, setStep] = useState<"data" | "otp" | "done">("data");
  const [form, setForm] = useState({ name: "", email: "", password: "", phone: "", education: "", target_instansi: "" });
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  const register = async () => {
    setError("");
    if (form.password.length < 6) {
      setError("Password minimal 6 karakter");
      return;
    }
    setLoading(true);
    const res = await apiPost("/auth/register", form);
    setLoading(false);
    if (res.ok) {
      setStep("otp");
      setCooldown(60);
      const timer = setInterval(() => {
        setCooldown((c) => {
          if (c <= 1) { clearInterval(timer); return 0; }
          return c - 1;
        });
      }, 1000);
    } else {
      const errMsg = res.error || (res.detail && typeof res.detail === "string" ? res.detail : res.detail?.[0]?.msg) || "Registrasi gagal";
      setError(errMsg);
    }
  };

  const verifyOTP = async () => {
    setError("");
    setLoading(true);
    const res = await apiPost("/auth/verify-register", {
      email: form.email,
      code,
      name: form.name,
      password: form.password,
      phone: form.phone || undefined,
      education: form.education || undefined,
      target_instansi: form.target_instansi || undefined,
    });
    setLoading(false);
    if (res.ok && res.data) {
      setAuth(res.data.token, res.data.user);
      setStep("done");
      setTimeout(() => router.push("/dashboard"), 1500);
    } else {
      setError(res.error || "Verifikasi gagal");
    }
  };

  const resendOTP = async () => {
    const res = await apiPost("/auth/register", form);
    if (res.ok) {
      setCooldown(60);
      const timer = setInterval(() => {
        setCooldown((c) => {
          if (c <= 1) { clearInterval(timer); return 0; }
          return c - 1;
        });
      }, 1000);
    } else {
      setError(res.error || "Gagal mengirim ulang OTP");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-card">
      <div className="absolute top-4 right-4"><ThemeToggle /></div>
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl" style={{ fontFamily: "Georgia, serif" }}>Daftar Gratis</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">Belajar CPNS 2026</p>
          <div className="flex justify-center gap-2 mt-4">
            {["data", "otp", "done"].map((s, i) => (
              <div key={s} className={`h-1.5 w-16 rounded-full ${["data", "otp", "done"].indexOf(step) >= i ? "bg-primary" : "bg-muted"}`} />
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {error && <div className="mb-4 p-3 text-sm text-destructive bg-destructive/10 rounded-xl">{error}</div>}
          {step === "data" && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Nama Lengkap</label>
                <div className="relative mt-1">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nama kamu" className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Email</label>
                <div className="relative mt-1">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="nama@email.com" className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Password</label>
                <div className="relative mt-1">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Minimal 6 karakter" className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">No. WhatsApp <span className="text-muted-foreground">(opsional)</span></label>
                <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="08xxxxxxxxxx" className="w-full px-4 py-2 border border-border rounded-xl bg-card text-card-foreground mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium">Pendidikan Terakhir</label>
                <select value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })} className="w-full px-4 py-2 border border-border rounded-xl bg-card text-card-foreground mt-1">
                  <option value="">Pilih</option>
                  <option value="SMA">SMA/SMK</option>
                  <option value="D3">D3</option>
                  <option value="S1">S1</option>
                  <option value="S2">S2</option>
                  <option value="S3">S3</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Target Instansi <span className="text-muted-foreground">(opsional)</span></label>
                <input type="text" value={form.target_instansi} onChange={(e) => setForm({ ...form, target_instansi: e.target.value })} placeholder="Contoh: Kemenkeu" className="w-full px-4 py-2 border border-border rounded-xl bg-card text-card-foreground mt-1" />
              </div>
              <Button className="w-full" onClick={register} disabled={loading || !form.name || !form.email || !form.password}>
                {loading ? "Mendaftar..." : "Daftar & Kirim OTP"}
              </Button>
              <p className="text-center text-sm text-muted-foreground">
                Sudah punya akun? <Link href="/login" className="text-foreground font-medium hover:underline">Masuk</Link>
              </p>
            </div>
          )}
          {step === "otp" && (
            <div className="space-y-4">
              <button onClick={() => setStep("data")} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
                <ArrowLeft className="h-4 w-4" /> Kembali
              </button>
              <div className="text-center text-sm text-muted-foreground">
                Kode OTP dikirim ke <strong>{form.email}</strong>
              </div>
              <div>
                <label className="text-sm font-medium">Kode OTP</label>
                <div className="relative mt-1">
                  <Shield className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    placeholder="123456"
                    maxLength={6}
                    className="w-full pl-10 pr-4 py-2 border border-border rounded-xl bg-card text-card-foreground text-center text-2xl tracking-[0.5em]"
                    onKeyDown={(e) => e.key === "Enter" && code.length === 6 && verifyOTP()}
                  />
                </div>
              </div>
              <Button className="w-full" onClick={verifyOTP} disabled={loading || code.length < 6}>
                {loading ? "Memverifikasi..." : "Verifikasi & Masuk"}
              </Button>
              <button onClick={resendOTP} disabled={cooldown > 0} className="w-full text-center text-sm text-muted-foreground hover:text-foreground disabled:opacity-50">
                {cooldown > 0 ? `Kirim ulang (${cooldown}s)` : "Kirim ulang OTP"}
              </button>
            </div>
          )}
          {step === "done" && (
            <div className="text-center py-8">
              <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Check className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold">Registrasi Berhasil!</h3>
              <p className="text-sm text-muted-foreground mt-1">Mengarahkan ke dashboard...</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
