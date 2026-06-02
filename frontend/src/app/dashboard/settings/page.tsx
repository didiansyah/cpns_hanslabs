"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { apiPut } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Loader2, User, Mail, Phone, GraduationCap, Building2 } from "lucide-react";

export default function SettingsPage() {
  const { user, token, setAuth } = useAuth();
  const [form, setForm] = useState({
    name: "", phone: "",
    education: "", target_instansi: "",
  });
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    setForm({
      name: user.name || "",
      phone: user.phone || "",
      education: user.education || "",
      target_instansi: user.target_instansi || "",
    });
  }, [user]);

  const save = async () => {
    setSaving(true);
    setError("");
    const res = await apiPut("/users/me", form);
    if (res.ok && user && token) {
      setAuth(token, { ...user, ...form });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } else {
      setError(res.error || "Gagal menyimpan profil");
    }
    setSaving(false);
  };

  return (
    <div className="space-y-6 max-w-xl">
      <h1 className="text-2xl font-bold tracking-tight font-serif">Pengaturan</h1>

      <Card className="border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-serif">Profil</CardTitle>
            {saved && (
              <Badge className="bg-primary/10 text-primary border-0 gap-1">
                <Check className="h-3 w-3" strokeWidth={3} />
                Tersimpan
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Name */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <User className="h-4 w-4 text-muted-foreground" />
              Nama
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2.5 border border-border rounded-xl bg-card text-card-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-muted-foreground/50"
              placeholder="Nama lengkap"
            />
          </div>

          {/* Email (disabled) */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <Mail className="h-4 w-4 text-muted-foreground" />
              Email
            </label>
            <input
              type="email"
              value={user?.email || ""}
              disabled
              className="w-full px-4 py-2.5 border border-border rounded-xl bg-muted text-muted-foreground text-sm cursor-not-allowed"
            />
            <p className="text-[11px] text-muted-foreground">Email tidak bisa diubah</p>
          </div>

          {/* WhatsApp */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <Phone className="h-4 w-4 text-muted-foreground" />
              WhatsApp
            </label>
            <input
              type="tel"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              placeholder="08xxxxxxxxxx"
              className="w-full px-4 py-2.5 border border-border rounded-xl bg-card text-card-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-muted-foreground/50"
            />
          </div>

          {/* Pendidikan */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <GraduationCap className="h-4 w-4 text-muted-foreground" />
              Pendidikan
            </label>
            <select
              value={form.education}
              onChange={(e) => setForm({ ...form, education: e.target.value })}
              className="w-full px-4 py-2.5 border border-border rounded-xl bg-card text-card-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all appearance-none cursor-pointer"
            >
              <option value="">Pilih pendidikan</option>
              <option value="SMA">SMA/SMK</option>
              <option value="D3">D3</option>
              <option value="S1">S1</option>
              <option value="S2">S2</option>
              <option value="S3">S3</option>
            </select>
          </div>

          {/* Target Instansi */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <Building2 className="h-4 w-4 text-muted-foreground" />
              Target Instansi
            </label>
            <input
              type="text"
              value={form.target_instansi}
              onChange={(e) => setForm({ ...form, target_instansi: e.target.value })}
              placeholder="Contoh: Kemenkeu, BKN, Kemenkumham"
              className="w-full px-4 py-2.5 border border-border rounded-xl bg-card text-card-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-muted-foreground/50"
            />
          </div>

          {error && (
            <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Button onClick={save} className="w-full rounded-lg" disabled={saving}>
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : saved ? (
              <Check className="h-4 w-4 mr-2" strokeWidth={3} />
            ) : null}
            {saving ? "Menyimpan..." : saved ? "Tersimpan" : "Simpan Perubahan"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
