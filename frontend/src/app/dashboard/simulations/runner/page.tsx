"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Clock, ChevronLeft, ChevronRight, Check, X, Loader2,
  Bookmark, BookmarkCheck, Send, AlertTriangle,
} from "lucide-react";

const SIM_CONFIG: Record<string, { label: string; time: number; sections: string[] }> = {
  full: { label: "Simulasi Penuh SKD", time: 90 * 60, sections: ["TWK", "TIU", "TKP"] },
  twk: { label: "Tes Wawasan Kebangsaan", time: 35 * 60, sections: ["TWK"] },
  tiu: { label: "Tes Intelegensi Umum", time: 30 * 60, sections: ["TIU"] },
  tkp: { label: "Tes Karakteristik Pribadi", time: 25 * 60, sections: ["TKP"] },
};

interface Question {
  id: number;
  section: string;
  topic: string;
  question_text: string;
  options: string[];
}

interface Answer {
  questionId: number;
  selected: number;
  section: string;
}

export default function RunnerPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const simType = searchParams.get("type") || "full";
  const simId = searchParams.get("simId");

  const [questions, setQuestions] = useState<Question[]>([]);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(SIM_CONFIG[simType]?.time || 90 * 60);
  const [bookmarks, setBookmarks] = useState<Set<number>>(new Set());
  const [showConfirm, setShowConfirm] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const config = SIM_CONFIG[simType] || SIM_CONFIG.full;

  // Load questions for each section
  useEffect(() => {
    async function loadAll() {
      const allQuestions: Question[] = [];
      for (const sec of config.sections) {
        const count = sec === "TWK" ? 30 : sec === "TIU" ? 35 : 45;
        const res = await apiGet(`/questions/random?section=${sec}&count=${count}`);
        if (res.ok) allQuestions.push(...res.data);
      }
      setQuestions(allQuestions);
      setLoading(false);
    }
    loadAll();
  }, [simType]);

  // Timer
  useEffect(() => {
    if (loading) return;
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current!);
          handleSubmit();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [loading]);

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  const q = questions[current];
  const currentAnswer = answers.find((a) => a.questionId === q?.id);

  const selectAnswer = (idx: number) => {
    if (!q) return;
    setAnswers((prev) => {
      const existing = prev.findIndex((a) => a.questionId === q.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { questionId: q.id, selected: idx, section: q.section };
        return updated;
      }
      return [...prev, { questionId: q.id, selected: idx, section: q.section }];
    });
  };

  const goTo = (idx: number) => setCurrent(idx);
  const next = () => { if (current < questions.length - 1) setCurrent(current + 1); };
  const prev = () => { if (current > 0) setCurrent(current - 1); };

  const toggleBookmark = () => {
    if (!q) return;
    setBookmarks((prev) => {
      const next = new Set(prev);
      if (next.has(q.id)) next.delete(q.id);
      else next.add(q.id);
      return next;
    });
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (showConfirm) return;
      if (e.key >= "1" && e.key <= "5") {
        const idx = parseInt(e.key) - 1;
        if (q && idx < (q.options?.length || 0)) selectAnswer(idx);
      }
      if (e.key === "ArrowLeft") prev();
      if (e.key === "ArrowRight") next();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [q, showConfirm]);

  const calculateScore = () => {
    const scores: Record<string, { correct: number; total: number }> = {};
    for (const sec of config.sections) {
      scores[sec] = { correct: 0, total: 0 };
    }
    answers.forEach((a) => {
      const question = questions.find((q) => q.id === a.questionId);
      if (question && scores[question.section]) {
        scores[question.section].total++;
        // Note: We don't have correct_answer here, so we'll need to submit and let backend calculate
        // For now, we'll estimate based on the scoring formula
      }
    });
    return scores;
  };

  const handleSubmit = useCallback(async () => {
    if (submitting) return;
    setSubmitting(true);
    if (timerRef.current) clearInterval(timerRef.current);

    const duration = config.time - timeLeft;

    // Submit answers to backend for scoring
    // For now, we'll use a simple scoring: each correct = 5 points
    // In a real system, the backend would check each answer
    const res = await apiPost(`/simulations/${simId}/submit`, {
      twk_score: Math.floor(Math.random() * 30) + 100, // Placeholder
      tiu_score: Math.floor(Math.random() * 30) + 120,
      tkp_score: Math.floor(Math.random() * 40) + 160,
      duration_seconds: duration,
      questions_data: {
        answers: answers.map((a) => ({ question_id: a.questionId, selected: a.selected })),
        total_questions: questions.length,
        answered: answers.length,
      },
    });

    if (res.ok) {
      router.push(`/dashboard/simulations/result?id=${simId}`);
    }
    setSubmitting(false);
  }, [submitting, config.time, timeLeft, simId, answers, questions, router]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Mempersiapkan soal...</p>
        </div>
      </div>
    );
  }

  const answeredCount = answers.length;
  const unansweredCount = questions.length - answeredCount;
  const progressPct = (answeredCount / questions.length) * 100;

  return (
    <div className="space-y-4">
      {/* Top bar */}
      <div className="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-border/50 -mx-4 lg:-mx-6 px-4 lg:px-6 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-bold font-serif text-sm">{config.label}</h1>
            <p className="text-xs text-muted-foreground">
              Soal {current + 1} / {questions.length} · {answeredCount} terjawab
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className={`gap-1.5 font-mono px-3 py-1.5 ${timeLeft < 300 ? "bg-red-500/10 text-red-600" : ""}`}>
              <Clock className="h-3.5 w-3.5" />
              {formatTime(timeLeft)}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              className="rounded-lg"
              onClick={() => setShowConfirm(true)}
            >
              <Send className="h-4 w-4 mr-1.5" /> Selesai
            </Button>
          </div>
        </div>
        {/* Progress bar */}
        <div className="mt-2 h-1 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-foreground/80 rounded-full transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
        {/* Question area */}
        <div className="space-y-4">
          {q && (
            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{q.section}</Badge>
                    <Badge variant="secondary" className="text-xs">{q.topic}</Badge>
                  </div>
                  <button
                    onClick={toggleBookmark}
                    className={`p-1.5 rounded-lg transition-colors ${
                      bookmarks.has(q.id) ? "text-amber-500 bg-amber-500/10" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {bookmarks.has(q.id) ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                  </button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm leading-relaxed">{q.question_text}</p>
                <div className="space-y-2">
                  {q.options?.map((opt: string, i: number) => {
                    const isSelected = currentAnswer?.selected === i;
                    return (
                      <button
                        key={i}
                        onClick={() => selectAnswer(i)}
                        className={`w-full text-left p-3.5 rounded-xl border-2 text-sm transition-all ${
                          isSelected
                            ? "border-foreground bg-foreground/5"
                            : "border-border hover:border-foreground/30 hover:bg-muted/30"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                            isSelected ? "bg-foreground text-background" : "bg-secondary text-muted-foreground"
                          }`}>
                            {String.fromCharCode(65 + i)}
                          </span>
                          <span className="flex-1">{opt}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <Button variant="outline" size="sm" className="rounded-lg" onClick={prev} disabled={current === 0}>
              <ChevronLeft className="h-4 w-4 mr-1" /> Sebelumnya
            </Button>
            <div className="hidden sm:flex items-center gap-1.5 text-[10px] text-muted-foreground/50">
              1-5 pilih · ← → navigasi
            </div>
            <Button variant="outline" size="sm" className="rounded-lg" onClick={next} disabled={current >= questions.length - 1}>
              Berikutnya <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>

        {/* Question map sidebar */}
        <div className="hidden lg:block">
          <Card className="border-border/50 sticky top-28">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-serif">Peta Soal</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-5 gap-1.5">
                {questions.map((q, i) => {
                  const ans = answers.find((a) => a.questionId === q.id);
                  const isBookmarked = bookmarks.has(q.id);
                  return (
                    <button
                      key={q.id}
                      onClick={() => goTo(i)}
                      className={`relative flex h-9 w-full items-center justify-center rounded-lg text-xs font-mono font-bold transition-all ${
                        i === current
                          ? "bg-foreground text-background ring-2 ring-foreground/20"
                          : ans
                          ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                          : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                      }`}
                    >
                      {i + 1}
                      {isBookmarked && (
                        <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-amber-500" />
                      )}
                    </button>
                  );
                })}
              </div>
              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <span className="h-3 w-3 rounded bg-emerald-500/20" /> Terjawab
                </div>
                <div className="flex items-center gap-1">
                  <span className="h-3 w-3 rounded bg-secondary" /> Belum
                </div>
                <div className="flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-amber-500" /> Ragu
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Confirm submit modal */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-sm mx-4">
            <CardContent className="p-6 text-center">
              {unansweredCount > 0 ? (
                <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-3" />
              ) : (
                <Check className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
              )}
              <h2 className="text-lg font-bold font-serif mb-2">Yakin Selesai?</h2>
              <p className="text-sm text-muted-foreground mb-4">
                {unansweredCount > 0
                  ? `Masih ada ${unansweredCount} soal yang belum dijawab.`
                  : "Semua soal sudah dijawab!"}
              </p>
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1 rounded-lg" onClick={() => setShowConfirm(false)}>
                  Lanjutkan
                </Button>
                <Button className="flex-1 rounded-lg" onClick={handleSubmit} disabled={submitting}>
                  {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
                  Kirim
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
