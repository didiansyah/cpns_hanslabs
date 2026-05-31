"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Brain, Clock, Trophy, Play, CheckCircle2, XCircle, Loader2,
  Target, Zap, ArrowRight, RotateCcw,
} from "lucide-react";

const SIM_TYPES = [
  { type: "full", label: "Simulasi Penuh", desc: "TWK + TIU + TKP", time: "90 menit", questions: "110 soal", icon: Brain, color: "bg-violet-500/10 text-violet-600" },
  { type: "twk", label: "TWK", desc: "Tes Wawasan Kebangsaan", time: "35 menit", questions: "30 soal", icon: Target, color: "bg-emerald-500/10 text-emerald-600" },
  { type: "tiu", label: "TIU", desc: "Tes Intelegensi Umum", time: "30 menit", questions: "35 soal", icon: Zap, color: "bg-blue-500/10 text-blue-600" },
  { type: "tkp", label: "TKP", desc: "Tes Karakteristik Pribadi", time: "25 menit", questions: "45 soal", icon: Clock, color: "bg-amber-500/10 text-amber-600" },
];

export default function SimulationsPage() {
  const router = useRouter();
  const [sims, setSims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState<string | null>(null);

  useEffect(() => {
    apiGet("/simulations").then((res) => {
      if (res.ok) setSims(res.data);
      setLoading(false);
    });
  }, []);

  const startSim = async (type: string) => {
    setStarting(type);
    const res = await apiPost("/simulations", { sim_type: type });
    if (res.ok) {
      router.push(`/dashboard/simulations/runner?type=${type}&simId=${res.data.id}`);
    }
    setStarting(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-serif">Try Out SKD CASN</h1>
          <p className="text-sm text-muted-foreground">Simulasi ujian dengan timer dan passing grade</p>
        </div>
      </div>

      {/* Passing Grade Reference */}
      <Card className="border-border/50 bg-secondary/30">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Target className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-semibold">Passing Grade SKD 2024</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-2 rounded-lg bg-background border border-border/50">
              <p className="text-xs text-muted-foreground">TWK</p>
              <p className="font-bold font-mono">≥ 65</p>
            </div>
            <div className="text-center p-2 rounded-lg bg-background border border-border/50">
              <p className="text-xs text-muted-foreground">TIU</p>
              <p className="font-bold font-mono">≥ 80</p>
            </div>
            <div className="text-center p-2 rounded-lg bg-background border border-border/50">
              <p className="text-xs text-muted-foreground">TKP</p>
              <p className="font-bold font-mono">≥ 143</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Simulation Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {SIM_TYPES.map((s) => (
          <Card key={s.type} className="group hover:border-foreground/20 transition-all hover:shadow-sm">
            <CardContent className="p-5">
              <div className={`mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl ${s.color} transition-transform group-hover:scale-110`}>
                <s.icon className="h-6 w-6" />
              </div>
              <div className="text-center mb-4">
                <p className="font-semibold mb-1 font-serif">{s.label}</p>
                <p className="text-sm text-muted-foreground">{s.desc}</p>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <Badge variant="secondary" className="text-[10px]">{s.questions}</Badge>
                  <span className="text-xs text-muted-foreground">{s.time}</span>
                </div>
              </div>
              <Button
                size="sm"
                className="w-full rounded-lg"
                onClick={() => startSim(s.type)}
                disabled={starting !== null}
              >
                {starting === s.type ? (
                  <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 mr-1.5" />
                )}
                Mulai Try Out
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* History */}
      <Card className="border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-serif">Riwayat Try Out</CardTitle>
            {sims.length > 0 && (
              <Badge variant="secondary" className="text-xs font-mono">{sims.length} percobaan</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : sims.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Brain className="h-10 w-10 text-muted-foreground/30 mb-3" />
              <p className="text-muted-foreground text-sm">Belum ada try out.</p>
              <p className="text-xs text-muted-foreground mt-1">Mulai try out pertama di atas!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sims.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between p-3.5 border border-border/50 rounded-xl hover:border-foreground/20 transition-colors cursor-pointer"
                  onClick={() => router.push(`/dashboard/simulations/result?id=${s.id}`)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                      s.passed ? "bg-emerald-500/10" : "bg-red-500/10"
                    }`}>
                      {s.passed ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-sm">
                        {s.sim_type === "full" ? "Simulasi Penuh" : s.sim_type.toUpperCase()}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(s.created_at).toLocaleDateString("id-ID", {
                          day: "numeric", month: "long", year: "numeric",
                        })}
                        {s.duration_seconds && ` · ${Math.floor(s.duration_seconds / 60)}m ${s.duration_seconds % 60}s`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="font-bold font-mono text-lg">{s.total_score || 0}</p>
                      <Badge
                        variant="secondary"
                        className={`text-[10px] ${
                          s.passed
                            ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                            : "bg-red-500/10 text-red-700 dark:text-red-400"
                        } border-0`}
                      >
                        {s.passed ? "LULUS" : "BELUM LULUS"}
                      </Badge>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
