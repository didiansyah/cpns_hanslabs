"use client";
import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Trophy, CheckCircle2, XCircle, Loader2, RotateCcw,
  ArrowLeft, Users, Target, Clock, TrendingUp,
} from "lucide-react";

const PASSING = { twk: 65, tiu: 80, tkp: 143 };

interface SimResult {
  id: number;
  sim_type: string;
  twk_score: number | null;
  tiu_score: number | null;
  tkp_score: number | null;
  total_score: number;
  passed: boolean;
  duration_seconds: number | null;
  questions_data: any;
  created_at: string;
  ranking: number;
  total_participants: number;
}

export default function ResultPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const simId = searchParams.get("id");
  const [result, setResult] = useState<SimResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!simId) {
      router.push("/dashboard/simulations");
      return;
    }
    apiGet(`/simulations/${simId}`).then((res) => {
      if (res.ok) setResult(res.data);
      else router.push("/dashboard/simulations");
      setLoading(false);
    });
  }, [simId, router]);

  if (loading || !result) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const formatDuration = (s: number | null) => {
    if (!s) return "-";
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}m ${sec}s`;
  };

  const sections = [
    {
      name: "Tes Wawasan Kebangsaan",
      short: "TWK",
      score: result.twk_score || 0,
      target: PASSING.twk,
      questions: 30,
      correct: Math.round(((result.twk_score || 0) / 5)),
      wrong: 30 - Math.round(((result.twk_score || 0) / 5)),
    },
    {
      name: "Tes Intelegensi Umum",
      short: "TIU",
      score: result.tiu_score || 0,
      target: PASSING.tiu,
      questions: 35,
      correct: Math.round(((result.tiu_score || 0) / 5)),
      wrong: 35 - Math.round(((result.tiu_score || 0) / 5)),
    },
    {
      name: "Tes Karakteristik Pribadi",
      short: "TKP",
      score: result.tkp_score || 0,
      target: PASSING.tkp,
      questions: 45,
      correct: Math.round(((result.tkp_score || 0) / 5)),
      wrong: 45 - Math.round(((result.tkp_score || 0) / 5)),
    },
  ];

  const totalQuestions = sections.reduce((a, s) => a + s.questions, 0);
  const totalCorrect = sections.reduce((a, s) => a + s.correct, 0);
  const totalWrong = sections.reduce((a, s) => a + s.wrong, 0);
  const pct = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard/simulations")}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Kembali
        </Button>
      </div>

      {/* Title & Total Score */}
      <Card className="border-border/50 overflow-hidden">
        <div className="bg-foreground text-background p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-background/70 font-mono uppercase tracking-wider">
                Try Out SKD CASN 2026
              </p>
              <h1 className="text-2xl font-bold font-serif mt-1">
                {result.sim_type === "full" ? "Simulasi Penuh" : result.sim_type.toUpperCase()}
              </h1>
            </div>
            <div className="text-right">
              <p className="text-xs text-background/50 uppercase tracking-wider">Total Nilai</p>
              <p className="text-5xl font-bold font-mono">{result.total_score}</p>
            </div>
          </div>
        </div>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Ranking <span className="font-bold text-foreground font-mono">{result.ranking}</span> / {result.total_participants.toLocaleString("id-ID")}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {formatDuration(result.duration_seconds)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pass/Fail Status */}
      <Card className={`border-2 ${result.passed ? "border-emerald-500/30 bg-emerald-500/5" : "border-red-500/30 bg-red-500/5"}`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            {result.passed ? (
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10">
                <Trophy className="h-6 w-6 text-emerald-500" />
              </div>
            ) : (
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10">
                <Target className="h-6 w-6 text-red-500" />
              </div>
            )}
            <div>
              <p className={`text-lg font-bold ${result.passed ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                {result.passed ? "Selamat !!! Anda Lulus" : "Belum Lulus"}
              </p>
              <p className="text-sm text-muted-foreground">
                {result.passed
                  ? "Anda memenuhi passing grade SKD CASN 2026"
                  : "Tingkatkan lagi untuk memenuhi passing grade"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section Breakdown */}
      <div className="space-y-3">
        {sections.map((s) => {
          const passed = s.score >= s.target;
          return (
            <Card key={s.short} className="border-border/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-semibold text-sm">{s.name}</p>
                    <p className="text-xs text-muted-foreground">{s.short}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold font-mono">{s.score}</p>
                    <p className="text-xs text-muted-foreground">/ {s.target}</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center p-2 rounded-lg bg-secondary/50">
                    <p className="text-xs text-muted-foreground mb-1">Pertanyaan</p>
                    <p className="font-bold font-mono">{s.questions}</p>
                  </div>
                  <div className="text-center p-2 rounded-lg bg-emerald-500/5">
                    <p className="text-xs text-muted-foreground mb-1">Benar</p>
                    <p className="font-bold font-mono text-emerald-600 dark:text-emerald-400">{s.correct}</p>
                  </div>
                  <div className="text-center p-2 rounded-lg bg-red-500/5">
                    <p className="text-xs text-muted-foreground mb-1">Salah</p>
                    <p className="font-bold font-mono text-red-500">{s.wrong}</p>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-muted-foreground">Progress ke passing grade</span>
                    <span className={passed ? "text-emerald-600 font-semibold" : "text-muted-foreground"}>
                      {Math.min(100, Math.round((s.score / s.target) * 100))}%
                    </span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${passed ? "bg-emerald-500" : "bg-foreground/60"}`}
                      style={{ width: `${Math.min(100, (s.score / s.target) * 100)}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Overall Stats */}
      <Card className="border-border/50">
        <CardContent className="p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Total Soal</p>
              <p className="text-2xl font-bold font-mono">{totalQuestions}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Benar</p>
              <p className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">{totalCorrect}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Akurasi</p>
              <p className="text-2xl font-bold font-mono">{pct}%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button onClick={() => router.push("/dashboard/simulations")} className="flex-1 rounded-lg">
          <RotateCcw className="h-4 w-4 mr-2" /> Try Out Lagi
        </Button>
        <Button variant="outline" onClick={() => router.push("/dashboard")} className="flex-1 rounded-lg">
          <ArrowLeft className="h-4 w-4 mr-2" /> Dashboard
        </Button>
      </div>
    </div>
  );
}
