"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { apiGet, apiPut } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CalendarDays, Clock, Brain, Flame, Check, Target, TrendingUp, ChevronRight, Loader2 } from "lucide-react";
import Link from "next/link";

const CHECKLIST_LABELS = [
  { key: "chk1", label: "TWK: Baca materi 30-60 menit" },
  { key: "chk2", label: "TIU: Latihan soal 15-20 soal" },
  { key: "chk3", label: "TKP: Review skenario 10 soal" },
  { key: "chk4", label: "Review kesalahan kemarin" },
  { key: "chk5", label: "Update progress tracker" },
];

const PASSING = { twk: 65, tiu: 80, tkp: 143 };

export default function DashboardPage() {
  const { user } = useAuth();
  const [progress, setProgress] = useState<any>(null);
  const [checklist, setChecklist] = useState<any>(null);
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
    { label: "Hari Belajar", value: progress?.study_days || 0, icon: CalendarDays, suffix: "hari", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-500/10" },
    { label: "Total Jam", value: Math.round(progress?.study_hours || 0), icon: Clock, suffix: "jam", color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-500/10" },
    { label: "Simulasi", value: progress?.sim_count || 0, icon: Brain, suffix: "x", color: "text-violet-600 dark:text-violet-400", bg: "bg-violet-500/10" },
    { label: "Streak", value: progress?.streak_days || 0, icon: Flame, suffix: "hari", color: "text-orange-600 dark:text-orange-400", bg: "bg-orange-500/10" },
  ];

  const scores = [
    { label: "TWK", score: progress?.twk_score || 0, target: PASSING.twk, color: "bg-emerald-500" },
    { label: "TIU", score: progress?.tiu_score || 0, target: PASSING.tiu, color: "bg-blue-500" },
    { label: "TKP", score: progress?.tkp_score || 0, target: PASSING.tkp, color: "bg-violet-500" },
  ];

  const completedChecks = checklist ? CHECKLIST_LABELS.filter(c => checklist[c.key]).length : 0;
  const allChecked = completedChecks === CHECKLIST_LABELS.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-serif">
            Halo, {user?.name?.split(" ")[0]}
          </h1>
          <p className="text-sm text-muted-foreground">
            Minggu ke-{progress?.current_week || 1} dari 12 minggu menuju SKD
          </p>
        </div>
        <Link href="/dashboard/simulations">
          <Badge variant="secondary" className="gap-1.5 cursor-pointer hover:bg-secondary/80 transition-colors px-3 py-1.5">
            <Brain className="h-3.5 w-3.5" />
            Mulai Simulasi
          </Badge>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        {kpis.map((k) => (
          <Card key={k.label} className="border-border/50 min-w-0 group hover:border-foreground/20 transition-colors">
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
        {/* Progress SKD */}
        <Card className="lg:col-span-4 border-border/50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-serif">Progress SKD</CardTitle>
              <Link href="/dashboard/simulations" className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors">
                Latihan <ChevronRight className="h-3 w-3" />
              </Link>
            </div>
            <p className="text-xs text-muted-foreground">Target passing grade per sesi</p>
          </CardHeader>
          <CardContent className="space-y-5">
            {scores.map((s) => {
              const pct = Math.min(100, (s.score / s.target) * 100);
              const passed = s.score >= s.target;
              return (
                <div key={s.label} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{s.label}</span>
                      {passed && (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-0 gap-1">
                          <Check className="h-2.5 w-2.5" strokeWidth={3} />
                          Lulus
                        </Badge>
                      )}
                    </div>
                    <span className="text-sm">
                      <span className={`font-mono ${passed ? "text-emerald-600 dark:text-emerald-400 font-semibold" : "font-semibold"}`}>{s.score}</span>
                      <span className="text-muted-foreground">/{s.target}</span>
                    </span>
                  </div>
                  <div className="h-2.5 bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ease-out ${passed ? "bg-emerald-500" : "bg-foreground/80"}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  {s.score === 0 && (
                    <p className="text-[11px] text-muted-foreground">Belum ada simulasi — mulai latihan untuk melihat progress</p>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Checklist */}
        <Card className="lg:col-span-3 border-border/50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-serif">Checklist Hari Ini</CardTitle>
              <div className="flex items-center gap-2">
                {allChecked && (
                  <Badge className="text-[10px] bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-0">
                    Selesai!
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground font-mono">{completedChecks}/{CHECKLIST_LABELS.length}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-1">
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
                    checked ? "bg-foreground border-foreground" : "border-border hover:border-foreground/40"
                  }`}>
                    {checked && <Check className="h-3 w-3 text-background" strokeWidth={3} />}
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
            <CardTitle className="text-base font-serif">Passing Grade SKD 2024</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: "TWK", score: "≥ 65", detail: "30 soal · 35 menit", border: "border-l-emerald-500", bg: "bg-emerald-500/5" },
              { label: "TIU", score: "≥ 80", detail: "35 soal · 30 menit", border: "border-l-blue-500", bg: "bg-blue-500/5" },
              { label: "TKP", score: "≥ 143", detail: "45 soal · 25 menit", border: "border-l-violet-500", bg: "bg-violet-500/5" },
            ].map((p) => (
              <div key={p.label} className={`flex items-center gap-4 p-4 rounded-xl border border-border/50 border-l-4 ${p.border} ${p.bg} transition-colors hover:border-foreground/20`}>
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
