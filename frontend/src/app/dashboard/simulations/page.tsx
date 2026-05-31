"use client";
import { useState, useEffect } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Brain, Clock, Trophy, Play, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function SimulationsPage() {
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
      // TODO: navigate to simulation runner page
      setSims(prev => [{ ...res.data, sim_type: type, created_at: new Date().toISOString() }, ...prev]);
    }
    setStarting(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight font-serif">Simulasi CAT</h1>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { type: "full", label: "Simulasi Penuh", desc: "TWK + TIU + TKP", time: "90 menit", icon: Brain, questions: "110 soal" },
          { type: "twk", label: "TWK", desc: "Tes Wawasan Kebangsaan", time: "35 menit", icon: Clock, questions: "30 soal" },
          { type: "tiu", label: "TIU", desc: "Tes Intelegensi Umum", time: "30 menit", icon: Clock, questions: "35 soal" },
          { type: "tkp", label: "TKP", desc: "Tes Karakteristik Pribadi", time: "25 menit", icon: Clock, questions: "45 soal" },
        ].map((s) => (
          <Card key={s.type} className="group hover:border-foreground/20 transition-all hover:shadow-sm">
            <CardContent className="p-5 text-center">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-secondary group-hover:bg-foreground/5 transition-colors">
                <s.icon className="h-6 w-6 text-muted-foreground group-hover:text-foreground transition-colors" />
              </div>
              <p className="font-semibold mb-1 font-serif">{s.label}</p>
              <p className="text-sm text-muted-foreground">{s.desc}</p>
              <div className="flex items-center justify-center gap-2 mt-1.5 mb-4">
                <Badge variant="secondary" className="text-[10px]">{s.questions}</Badge>
                <span className="text-xs text-muted-foreground">{s.time}</span>
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
                Mulai
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-serif">Riwayat Simulasi</CardTitle>
            {sims.length > 0 && (
              <Badge variant="secondary" className="text-xs font-mono">{sims.length} simulasi</Badge>
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
              <p className="text-muted-foreground text-sm">Belum ada simulasi.</p>
              <p className="text-xs text-muted-foreground mt-1">Mulai simulasi pertama di atas!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sims.map((s) => (
                <div key={s.id} className="flex items-center justify-between p-3.5 border border-border/50 rounded-xl hover:border-foreground/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${
                      s.passed ? "bg-emerald-500/10" : "bg-red-500/10"
                    }`}>
                      {s.passed ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-sm">{s.sim_type.toUpperCase()}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(s.created_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}
                      </p>
                    </div>
                  </div>
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
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
