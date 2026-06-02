"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { apiGet, apiPut } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CalendarDays, Clock, Brain, Flame, Check, Target, ChevronRight, PlayCircle } from "lucide-react";
import Link from "next/link";

const CHECKLIST_LABELS = [
  { key: "chk1", label: "TWK: baca materi 30 menit" },
  { key: "chk2", label: "TIU: kerjakan 15–20 soal" },
  { key: "chk3", label: "TKP: review 10 skenario" },
  { key: "chk4", label: "Cek ulang kesalahan kemarin" },
  { key: "chk5", label: "Catat progress hari ini" },
];

const PASSING = { twk: 65, tiu: 80, tkp: 166 };

type ProgressData = {
  study_days?: number;
  study_hours?: number | string;
  sim_count?: number;
  streak_days?: number;
  current_week?: number;
  twk_score?: number | string;
  tiu_score?: number | string;
  tkp_score?: number | string;
};

type ChecklistData = Record<string, boolean>;

export default function DashboardPage() {
  const { user } = useAuth();
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [checklist, setChecklist] = useState<ChecklistData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiGet("/users/me/progress"), apiGet("/checklists/today")]).then(([p, c]) => {
      if (p.ok) setProgress(p.data);
      if (c.ok) setChecklist(c.data);
      setLoading(false);
    });
  }, []);

  const toggleCheck = async (key: string) => {
    if (!checklist) return;
    const updated = { ...checklist, [key]: !checklist[key] };
    setChecklist(updated);
    await apiPut("/checklists/today", { [key]: updated[key] });
  };

  if (loading) return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="h-8 w-48 bg-muted animate-pulse rounded-lg" />
        <div className="h-4 w-64 bg-muted animate-pulse rounded" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1,2,3,4].map(i => <div key={i} className="h-28 bg-muted animate-pulse rounded-xl" />)}
      </div>
    </div>
  );

  const kpis = [
    { label: "Hari aktif", value: progress?.study_days || 0, icon: CalendarDays, suffix: "hari", color: "text-primary", bg: "bg-primary/10" },
    { label: "Jam belajar", value: Math.round(Number(progress?.study_hours || 0)), icon: Clock, suffix: "jam", color: "text-primary", bg: "bg-primary/10" },
    { label: "Try out", value: progress?.sim_count || 0, icon: Brain, suffix: "x", color: "text-primary", bg: "bg-primary/10" },
    { label: "Streak", value: progress?.streak_days || 0, icon: Flame, suffix: "hari", color: "text-primary", bg: "bg-primary/10" },
  ];

  const scores = [
    { label: "TWK", score: Number(progress?.twk_score || 0), target: PASSING.twk, color: "bg-primary" },
    { label: "TIU", score: Number(progress?.tiu_score || 0), target: PASSING.tiu, color: "bg-primary" },
    { label: "TKP", score: Number(progress?.tkp_score || 0), target: PASSING.tkp, color: "bg-primary" },
  ];

  const completedChecks = checklist ? CHECKLIST_LABELS.filter(c => checklist[c.key]).length : 0;
  const allChecked = completedChecks === CHECKLIST_LABELS.length;
  const hasStarted = (progress?.sim_count || 0) > 0 || scores.some((s) => s.score > 0) || completedChecks > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-serif">
            Halo, {user?.name?.split(" ")[0]}
          </h1>
          <p className="text-sm text-muted-foreground">
            Minggu ke-{progress?.current_week || 1}. Jaga ritme latihanmu sampai hari ujian.
          </p>
        </div>
        <Link href="/dashboard/simulations">
          <Badge className="gap-1.5 cursor-pointer bg-primary px-3 py-1.5 text-primary-foreground shadow-sm transition-colors hover:bg-accent">
            <Brain className="h-3.5 w-3.5" />
            Mulai try out
          </Badge>
        </Link>
      </div>

      {!hasStarted && (
        <Card className="overflow-hidden border-primary/20 bg-primary text-primary-foreground shadow-sm dark:bg-card dark:text-card-foreground">
          <CardContent className="flex flex-col gap-5 px-7 pb-7 pt-8 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-2">
              <Badge variant="secondary" className="mb-2 border-0 bg-primary-foreground/15 text-primary-foreground dark:bg-secondary dark:text-secondary-foreground">
                Langkah pertama
              </Badge>
              <h2 className="font-serif text-xl font-bold tracking-tight">Mulai dari try out pertama</h2>
              <p className="max-w-2xl text-sm text-primary-foreground/70 dark:text-muted-foreground">
                Begitu selesai, skor TWK, TIU, TKP dan riwayat latihanmu akan tercatat di sini.
              </p>
            </div>
            <Link href="/dashboard/simulations" className="shrink-0">
              <Badge variant="secondary" className="w-full justify-center gap-2 px-4 py-2 text-sm sm:w-auto">
                <PlayCircle className="h-4 w-4" /> Kerjakan Try Out
              </Badge>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        {kpis.map((k) => (
          <Card key={k.label} className="border-border/50 min-w-0 group hover:border-primary/30 transition-colors">
            <CardContent className="p-3 lg:p-4">
              <div className="flex items-center justify-between">
                <p className="text-[10px] lg:text-xs font-medium text-muted-foreground uppercase tracking-wider truncate">{k.label}</p>
                <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${k.bg} transition-transform group-hover:scale-110`}>
                  <k.icon className={`h-3.5 w-3.5 ${k.color}`} />
                </div>
              </div>
              <div className="mt-2.5 flex items-baseline gap-1">
                <span className="text-xl lg:text-2xl font-bold tracking-tight font-mono">{k.value}</span>
                <span className="text-xs text-muted-foreground">{k.suffix}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-7">
        {/* Ringkasan skor SKD */}
        <Card className="lg:col-span-4 border-border/50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-serif">Ringkasan skor SKD</CardTitle>
              <Link href="/dashboard/simulations" className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors">
                Latihan <ChevronRight className="h-3 w-3" />
              </Link>
            </div>
            <p className="text-xs text-muted-foreground">Skor terbaikmu dibanding batas passing grade.</p>
          </CardHeader>
          <CardContent className="space-y-5">
            {scores.every((s) => s.score === 0) && (
              <div className="rounded-xl border border-dashed border-border bg-secondary/30 p-4 text-sm text-muted-foreground">
                Belum ada skor. Kerjakan try out pertama dulu, nanti progres tiap bagian muncul di sini.
              </div>
            )}
            {scores.map((s) => {
              const pct = Math.min(100, (s.score / s.target) * 100);
              const passed = s.score >= s.target;
              return (
                <div key={s.label} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{s.label}</span>
                      {passed && (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-primary/10 text-primary border-0 gap-1">
                          <Check className="h-2.5 w-2.5" strokeWidth={3} />
                          Lulus
                        </Badge>
                      )}
                    </div>
                    <span className="text-sm" aria-label={`Skor kamu ${s.score} dari target ${s.target}`}>
                      <span className={`font-mono ${passed ? "text-primary font-semibold" : "font-semibold"}`}>{s.score}</span>
                      <span className="text-muted-foreground">/{s.target}</span>
                    </span>
                  </div>
                  <div className="h-2.5 bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ease-out ${passed ? "bg-primary" : "bg-primary"}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <p className="text-[11px] text-muted-foreground">Skor kamu: {s.score} · Target: {s.target}</p>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Checklist */}
        <Card className="lg:col-span-3 border-border/50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-serif">Checklist hari ini</CardTitle>
              <div className="flex items-center gap-2">
                {allChecked && (
                  <Badge className="text-[10px] bg-primary/10 text-primary border-0">
                    Selesai!
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground font-mono">{completedChecks}/{CHECKLIST_LABELS.length}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="h-2 overflow-hidden rounded-full bg-secondary">
              <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${(completedChecks / CHECKLIST_LABELS.length) * 100}%` }} />
            </div>
            <p className="text-xs text-muted-foreground">Pilih target kecil yang realistis, lalu centang setelah selesai.</p>
            {CHECKLIST_LABELS.map((item) => {
              const checked = checklist?.[item.key] || false;
              return (
                <button
                  key={item.key}
                  onClick={() => toggleCheck(item.key)}
                  className={`flex items-center gap-3 w-full text-left text-sm px-3 py-2.5 rounded-lg transition-all hover:bg-muted/50 active:scale-[0.98] ${
                    checked ? "bg-muted/40" : ""
                  }`}
                >
                  <div className={`flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-[5px] border-2 transition-all ${
                    checked ? "bg-primary border-primary" : "border-border hover:border-primary/50"
                  }`}>
                    {checked && <Check className="h-3 w-3 text-primary-foreground" strokeWidth={3} />}
                  </div>
                  <span className={`transition-all ${checked ? "line-through text-muted-foreground" : ""}`}>{item.label}</span>
                </button>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Passing Grade */}
      <Card className="border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base font-serif">Target passing grade SKD</CardTitle>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Gunakan angka ini sebagai patokan saat latihan dan try out.</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: "TWK", score: "≥ 65", detail: "30 soal · 35 menit", border: "border-l-primary", bg: "bg-primary/5" },
              { label: "TIU", score: "≥ 80", detail: "35 soal · 30 menit", border: "border-l-primary", bg: "bg-primary/5" },
              { label: "TKP", score: "≥ 166", detail: "45 soal · 25 menit", border: "border-l-primary", bg: "bg-primary/5" },
            ].map((p) => (
              <div key={p.label} className={`flex items-center gap-4 p-4 rounded-xl border border-border/50 border-l-4 ${p.border} ${p.bg} transition-colors hover:border-primary/30`}>
                <div>
                  <p className="text-2xl font-bold font-serif">{p.score}</p>
                  <p className="text-sm font-medium">{p.label}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{p.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
