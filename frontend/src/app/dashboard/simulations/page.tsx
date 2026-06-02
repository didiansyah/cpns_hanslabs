"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Brain, Play, CheckCircle2, XCircle, Loader2,
  Target, ArrowRight, History, FileText,
} from "lucide-react";

interface SimulationHistory {
  id: number;
  sim_type: string;
  package_id: number | null;
  part_number: number | null;
  twk_score: number | null;
  tiu_score: number | null;
  tkp_score: number | null;
  total_score: number | null;
  passed: boolean | null;
  duration_seconds: number | null;
  created_at: string;
}

interface TryoutPackage {
  id: number;
  part_number: number;
  title: string;
  sim_type: string;
  counts: { twk: number; tiu: number; tkp: number; total: number };
  attempts: number;
  best_score: number | null;
  latest_score: number | null;
  latest_passed: boolean | null;
}

function formatDuration(seconds: number | null) {
  if (!seconds) return "-";
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}m ${secs}s`;
}

function formatDate(value: string) {
  const date = new Date(value);
  return date.toLocaleDateString("id-ID", { day: "2-digit", month: "short", year: "numeric" });
}

export default function SimulationsPage() {
  const router = useRouter();
  const [sims, setSims] = useState<SimulationHistory[]>([]);
  const [packages, setPackages] = useState<TryoutPackage[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([apiGet("/simulations"), apiGet("/simulations/packages")]).then(([simRes, packageRes]) => {
      if (simRes.ok) setSims(simRes.data);
      if (packageRes.ok) setPackages(packageRes.data);
      setLoading(false);
    });
  }, []);

  const startPackage = async (pkg: TryoutPackage) => {
    setStarting(pkg.id);
    const res = await apiPost("/simulations", { sim_type: "full", package_id: pkg.id });
    if (res.ok) {
      router.push(`/dashboard/simulations/runner?type=full&simId=${res.data.id}`);
    }
    setStarting(null);
  };

  const completedSims = sims.filter((s) => s.total_score !== null && s.total_score !== undefined);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-serif">Try Out SKD</h1>
          <p className="text-sm text-muted-foreground">Pilih part, kerjakan 110 soal, lalu cek skor TWK, TIU, dan TKP kamu.</p>
        </div>
        <div className="rounded-2xl border border-border bg-card px-4 py-3 text-right shadow-sm">
          <p className="text-xs text-muted-foreground">Sudah selesai</p>
          <p className="font-mono text-2xl font-black">{completedSims.length}</p>
        </div>
      </div>

      <Card className="border-border/50 bg-secondary/30">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Target className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-semibold">Target passing grade</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-2 rounded-lg bg-card border border-border/50">
              <p className="text-xs text-muted-foreground">TWK</p>
              <p className="font-bold font-mono">≥ 65</p>
            </div>
            <div className="text-center p-2 rounded-lg bg-card border border-border/50">
              <p className="text-xs text-muted-foreground">TIU</p>
              <p className="font-bold font-mono">≥ 80</p>
            </div>
            <div className="text-center p-2 rounded-lg bg-card border border-border/50">
              <p className="text-xs text-muted-foreground">TKP</p>
              <p className="font-bold font-mono">≥ 166</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-lg font-bold">Pilih paket try out</h2>
            <p className="text-xs text-muted-foreground">Setiap part berisi 30 TWK, 35 TIU, dan 45 TKP.</p>
          </div>
          <Badge variant="secondary" className="font-mono">{packages.length} part tersedia</Badge>
        </div>
        {loading ? (
          <Card><CardContent className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></CardContent></Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {packages.map((pkg) => (
              <Card key={pkg.id} className="group border-border/60 transition-all hover:border-primary/30 hover:shadow-sm">
                <CardContent className="px-6 pb-6 pt-7">
                  <div className="mb-6 flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-serif text-xl font-bold tracking-tight">Part {pkg.part_number}</p>
                        <p className="text-xs font-medium text-muted-foreground">SKD 2026 · paket tetap</p>
                      </div>
                    </div>
                    {pkg.attempts > 0 && (
                      <Badge variant="secondary" className="text-[10px]">{pkg.attempts}x</Badge>
                    )}
                  </div>

                  <div className="grid grid-cols-4 gap-2 text-center">
                    <div className="rounded-lg border border-border/50 bg-secondary/30 p-2">
                      <p className="text-[10px] text-muted-foreground">TWK</p>
                      <p className="font-mono font-bold">{pkg.counts.twk}</p>
                    </div>
                    <div className="rounded-lg border border-border/50 bg-secondary/30 p-2">
                      <p className="text-[10px] text-muted-foreground">TIU</p>
                      <p className="font-mono font-bold">{pkg.counts.tiu}</p>
                    </div>
                    <div className="rounded-lg border border-border/50 bg-secondary/30 p-2">
                      <p className="text-[10px] text-muted-foreground">TKP</p>
                      <p className="font-mono font-bold">{pkg.counts.tkp}</p>
                    </div>
                    <div className="rounded-lg border border-border/50 bg-secondary/30 p-2">
                      <p className="text-[10px] text-muted-foreground">Total</p>
                      <p className="font-mono font-bold">{pkg.counts.total}</p>
                    </div>
                  </div>

                  <div className="mt-5 flex items-center justify-between text-sm">
                    <div>
                      <p className="text-xs text-muted-foreground">Skor terbaik</p>
                      {pkg.best_score === null ? (
                        <p className="text-sm font-medium text-muted-foreground">Belum dicoba</p>
                      ) : (
                        <p className="font-mono text-lg font-black">{pkg.best_score}</p>
                      )}
                    </div>
                    {pkg.latest_score !== null && (
                      <Badge
                        variant="secondary"
                        className={`border-0 text-[10px] ${pkg.latest_passed ? "bg-primary/10 text-primary" : "bg-destructive/10 text-destructive"}`}
                      >
                        Terakhir: {pkg.latest_score}
                      </Badge>
                    )}
                  </div>

                  <Button
                    size="sm"
                    className="mt-5 w-full rounded-lg"
                    onClick={() => startPackage(pkg)}
                    disabled={starting !== null}
                  >
                    {starting === pkg.id ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Play className="mr-1.5 h-4 w-4" />}
                    {pkg.attempts > 0 ? "Ulangi Part" : "Mulai Part"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      <Card className="overflow-hidden rounded-2xl border-border/50">
        <CardHeader className="border-b border-border/50 bg-secondary/20 pb-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2 text-base font-serif">
                <History className="h-4 w-4" /> Riwayat try out
              </CardTitle>
              <p className="mt-1 text-xs text-muted-foreground">Buka hasil lama untuk melihat skor per bagian.</p>
            </div>
            {completedSims.length > 0 && <Badge variant="secondary" className="text-xs font-mono">{completedSims.length} attempt</Badge>}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : completedSims.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
              <Brain className="h-10 w-10 text-muted-foreground/30 mb-3" />
              <p className="text-muted-foreground text-sm">Belum ada riwayat try out.</p>
              <p className="text-xs text-muted-foreground mt-1">Kerjakan satu part dulu, hasilnya akan muncul otomatis di sini.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-sm">
                <thead className="bg-secondary/40 text-xs uppercase tracking-wide text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Part</th>
                    <th className="px-4 py-3 text-left font-semibold">Tanggal</th>
                    <th className="px-4 py-3 text-right font-semibold">TWK</th>
                    <th className="px-4 py-3 text-right font-semibold">TIU</th>
                    <th className="px-4 py-3 text-right font-semibold">TKP</th>
                    <th className="px-4 py-3 text-right font-semibold">Total</th>
                    <th className="px-4 py-3 text-left font-semibold">Durasi</th>
                    <th className="px-4 py-3 text-left font-semibold">Status</th>
                    <th className="px-4 py-3 text-right font-semibold">Detail</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {completedSims.map((s) => (
                    <tr key={s.id} className="cursor-pointer transition-colors hover:bg-secondary/30" onClick={() => router.push(`/dashboard/simulations/result?id=${s.id}`)}>
                      <td className="px-4 py-4">
                        <p className="font-mono font-black">Part {s.part_number ?? "-"}</p>
                        <p className="text-[11px] text-muted-foreground">Percobaan #{s.id}</p>
                      </td>
                      <td className="px-4 py-4 text-muted-foreground">{formatDate(s.created_at)}</td>
                      <td className="px-4 py-4 text-right font-mono font-semibold">{s.twk_score ?? "-"}</td>
                      <td className="px-4 py-4 text-right font-mono font-semibold">{s.tiu_score ?? "-"}</td>
                      <td className="px-4 py-4 text-right font-mono font-semibold">{s.tkp_score ?? "-"}</td>
                      <td className="px-4 py-4 text-right font-mono text-lg font-black">{s.total_score ?? 0}</td>
                      <td className="px-4 py-4 text-muted-foreground">{formatDuration(s.duration_seconds)}</td>
                      <td className="px-4 py-4">
                        <Badge variant="secondary" className={`gap-1 border-0 text-[10px] ${s.passed ? "bg-primary/10 text-primary" : "bg-destructive/10 text-destructive"}`}>
                          {s.passed ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                          {s.passed ? "LULUS" : "BELUM"}
                        </Badge>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <Button variant="ghost" size="sm" className="rounded-full">Detail <ArrowRight className="ml-1 h-4 w-4" /></Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
