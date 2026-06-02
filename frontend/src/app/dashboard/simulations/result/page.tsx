"use client";
import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronDown, Loader2, RotateCcw, ArrowLeft } from "lucide-react";

const PASSING = { twk: 65, tiu: 80, tkp: 166 };
const SECTION_META = {
  TWK: { name: "Tes Wawasan Kebangsaan", target: PASSING.twk, questions: 30, scoreKey: "twk_score" as const },
  TIU: { name: "Tes Intelegensi Umum", target: PASSING.tiu, questions: 35, scoreKey: "tiu_score" as const },
  TKP: { name: "Tes Karakteristik Pribadi", target: PASSING.tkp, questions: 45, scoreKey: "tkp_score" as const },
};

type SectionKey = keyof typeof SECTION_META;

interface SectionStats {
  total?: number;
  correct?: number;
  wrong?: number;
  score?: number;
  max_score?: number;
}

interface QuestionsData {
  sections?: Partial<Record<SectionKey, SectionStats>>;
}

interface SimResult {
  id: number;
  sim_type: string;
  package_id: number | null;
  part_number: number | null;
  twk_score: number | null;
  tiu_score: number | null;
  tkp_score: number | null;
  total_score: number;
  passed: boolean;
  duration_seconds: number | null;
  questions_data: QuestionsData | null;
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

  const activeSectionKeys = result.sim_type === "full"
    ? (["TWK", "TIU", "TKP"] as const)
    : ([result.sim_type.toUpperCase()] as const).filter((s): s is SectionKey => s in SECTION_META);

  const sections = activeSectionKeys.map((short) => {
    const meta = SECTION_META[short];
    const stats = result.questions_data?.sections?.[short];
    const score = result[meta.scoreKey] || 0;
    const questions = stats?.total ?? meta.questions;
    const correct = stats?.correct ?? Math.round(score / 5);
    const wrong = stats?.wrong ?? Math.max(0, questions - correct);
    const maxScore = stats?.max_score ?? questions * 5;
    return { name: meta.name, short, score, target: meta.target, questions, correct, wrong, maxScore };
  });

  const partLabel = result.part_number ?? result.id;
  const title = result.sim_type === "full"
    ? `TRY OUT SKD CASN 2026 – PART ${partLabel}`
    : `TRY OUT ${result.sim_type.toUpperCase()} CASN 2026 – PART ${partLabel}`;

  return (
    <div className="mx-auto max-w-[760px] space-y-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard/simulations")} className="rounded-full px-2">
          <ArrowLeft className="mr-1 h-4 w-4" /> Kembali
        </Button>
        <Button variant="outline" size="sm" onClick={() => router.push("/dashboard/simulations")} className="rounded-full">
          <RotateCcw className="mr-2 h-4 w-4" /> Try Out Lagi
        </Button>
      </div>

      <Card className="overflow-hidden rounded-[2rem] border-border/60 bg-white shadow-[0_18px_50px_rgba(17,17,17,0.08)] dark:bg-[#171717]">
        <CardContent className="p-7 sm:p-10">
          <div className="grid grid-cols-[1fr_auto] gap-5">
            <h1 className="max-w-[520px] text-3xl font-black uppercase leading-tight tracking-tight text-[#9b0017] sm:text-5xl">
              {title}
            </h1>
            <div className="text-right">
              <p className="text-sm font-medium text-foreground sm:text-xl">Total Nilai</p>
              <p className="font-mono text-5xl font-black leading-none text-[#2f5fa8] sm:text-7xl">
                {result.total_score}
              </p>
            </div>
          </div>

          <div className="mt-9 w-full max-w-[540px] rounded-3xl border border-border bg-card px-7 py-4 text-xl text-foreground shadow-sm sm:text-2xl">
            <div className="flex items-center justify-between gap-4">
              <span>Semua Peserta TO</span>
              <ChevronDown className="h-7 w-7 text-muted-foreground" />
            </div>
          </div>

          <div className="mt-8 space-y-5">
            <p className="text-2xl font-medium text-foreground sm:text-3xl">
              Ranking <span className="font-mono">{result.ranking}</span> / <span className="font-mono">{result.total_participants.toLocaleString("id-ID")}</span>
            </p>
            <div className="inline-flex rounded-full bg-secondary px-7 py-2.5 text-base font-black italic text-primary dark:bg-secondary sm:text-lg">
              {result.passed ? "Selamat !!! Anda lulus" : "Belum lulus"}
            </div>
          </div>

          <div className="mt-20 divide-y divide-border">
            {sections.map((s) => (
              <section key={s.short} className="grid grid-cols-[1fr_auto] gap-5 py-7 first:pt-0 last:pb-0">
                <div>
                  <h2 className="text-2xl font-black tracking-tight text-foreground sm:text-3xl">
                    {s.name}
                  </h2>
                  <div className="mt-4 grid max-w-[430px] grid-cols-3 gap-6 sm:gap-10">
                    <div>
                      <p className="text-lg font-semibold text-muted-foreground sm:text-2xl">Pertanyaan</p>
                      <p className="mt-1 font-mono text-2xl font-black text-foreground sm:text-3xl">{s.questions}</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-muted-foreground sm:text-2xl">
                        {s.short === "TKP" ? "Skor 5" : "Benar"}
                      </p>
                      <p className="mt-1 font-mono text-2xl font-black text-foreground sm:text-3xl">{s.correct}</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-muted-foreground sm:text-2xl">
                        {s.short === "TKP" ? "Non-5" : "Salah"}
                      </p>
                      <p className="mt-1 font-mono text-2xl font-black text-foreground sm:text-3xl">{s.wrong}</p>
                    </div>
                  </div>
                </div>
                <div className="self-center text-right font-mono text-4xl font-black leading-none sm:text-5xl">
                  <span className="text-[#2f5fa8]">{s.score}</span>
                  <span className="text-foreground">/{s.target}</span>
                  {s.short === "TKP" && (
                    <p className="mt-2 text-xs font-semibold text-muted-foreground">
                      maks {s.maxScore}
                    </p>
                  )}
                </div>
              </section>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
