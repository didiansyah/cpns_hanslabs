"use client";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Brain, Clock, BarChart3, Check, Users, Target, Trophy } from "lucide-react";

const stats = [
  { value: "10.000+", label: "Bank Soal" },
  { value: "Gratis", label: "Selamanya" },
  { value: "12", label: "Minggu Belajar" },
  { value: "3", label: "Seksi SKD" },
];

const features = [
  { icon: BookOpen, title: "Bank Soal Lengkap", desc: "TWK, TIU, TKP dengan pembahasan detail dari 2020-2025." },
  { icon: Brain, title: "Simulasi CAT", desc: "Simulasi ujian CAT realistis dengan timer dan scoring otomatis." },
  { icon: Clock, title: "Jadwal 12 Minggu", desc: "Jadwal belajar terstruktur dari fondasi sampai pemantapan." },
  { icon: BarChart3, title: "Analisis Progress", desc: "Tracking harian, weekly chart, dan analisis kekuatan/kelemahan." },
];

const steps = [
  { num: "01", title: "Daftar Gratis", desc: "Registrasi dengan email dan verifikasi OTP." },
  { num: "02", title: "Ikuti Jadwal", desc: "Jadwal belajar 12 minggu yang sudah disusun." },
  { num: "03", title: "Lulus SKD", desc: "Simulasi rutin, analisis kelemahan, dan lolos passing grade." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-4">
          <Link href="/" className="text-xl font-serif font-bold tracking-tight">Belajar CPNS</Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            <a href="#fitur" className="hover:text-foreground transition-colors">Fitur</a>
            <a href="#cara-kerja" className="hover:text-foreground transition-colors">Cara Kerja</a>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/login"><Button variant="outline" size="sm">Masuk</Button></Link>
            <Link href="/register"><Button size="sm">Daftar Gratis</Button></Link>
          </div>
        </div>
      </nav>

      <section className="mx-auto max-w-6xl px-6 pt-20 pb-16 text-center">
        <Badge variant="secondary" className="mb-6">CPNS 2026 — 100% Gratis</Badge>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight tracking-tight mx-auto max-w-3xl" style={{ fontFamily: "Georgia, serif" }}>
          Belajar CPNS Gratis, Lulus SKD
        </h1>
        <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
          Platform belajar CPNS 2026 dengan simulasi CAT, bank soal lengkap, jadwal 12 minggu, dan analisis progress. Tanpa bimbel mahal.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link href="/register"><Button size="lg">Mulai Belajar — Gratis</Button></Link>
          <a href="#cara-kerja"><Button variant="outline" size="lg">Pelajari Lebih</Button></a>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">Tanpa biaya · Tanpa kartu kredit · Akses selamanya</p>
      </section>

      <section className="border-y border-border bg-secondary/30">
        <div className="mx-auto max-w-6xl px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-2xl md:text-3xl font-bold" style={{ fontFamily: "Georgia, serif" }}>{s.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="cara-kerja" className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold" style={{ fontFamily: "Georgia, serif" }}>3 Langkah Menuju PNS</h2>
          <p className="mt-3 text-muted-foreground">Tidak perlu bimbel mahal. Ikuti panduan terstruktur.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((s) => (
            <div key={s.num} className="text-center">
              <div className="text-5xl font-bold text-muted/80 mb-4" style={{ fontFamily: "Georgia, serif" }}>{s.num}</div>
              <h3 className="text-lg font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-muted-foreground">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="fitur" className="bg-secondary/30">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold" style={{ fontFamily: "Georgia, serif" }}>Fitur Lengkap</h2>
            <p className="mt-3 text-muted-foreground">Semua yang kamu butuhkan untuk lulus SKD.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f) => (
              <Card key={f.title} className="border-border/60 hover:border-foreground/20 transition-colors">
                <CardContent className="p-5">
                  <div className="mb-3"><f.icon className="h-6 w-6 text-muted-foreground" /></div>
                  <p className="font-semibold mb-1">{f.title}</p>
                  <p className="text-sm text-muted-foreground">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-foreground text-background py-20 text-center">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="text-3xl font-bold font-serif">Mulai Belajar Sekarang</h2>
          <p className="mt-4 text-background/70">Gratis selamanya. Daftar dan langsung belajar.</p>
          <Link href="/register"><Button size="lg" variant="secondary" className="mt-8">Daftar Gratis</Button></Link>
        </div>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-lg font-serif font-bold">Belajar CPNS</div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground">Tentang</a>
            <a href="#" className="hover:text-foreground">Privasi</a>
            <a href="#" className="hover:text-foreground">Kontak</a>
          </div>
          <p className="text-sm text-muted-foreground">© 2026 Belajar CPNS. Gratis untuk semua.</p>
        </div>
      </footer>
    </div>
  );
}
