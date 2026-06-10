"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Clock, ChevronLeft, ChevronRight, Check, Loader2,
  Bookmark, BookmarkCheck, Send, AlertTriangle, Save,
  LayoutGrid, X,
} from "lucide-react";

const AUTOSAVE_DEBOUNCE_MS = 15_000;
const AUTOSAVE_INTERVAL_MS = 30_000;

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

interface RunnerDraft {
  answers: Answer[];
  bookmarks: number[];
  current: number;
  timeLeft: number;
  questionIds: number[];
  updatedAt: number;
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
  const [showMap, setShowMap] = useState(false);
  const [draftRestored, setDraftRestored] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const autosaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const draftStateRef = useRef({ answers, bookmarks, current, timeLeft, questions });

  const config = SIM_CONFIG[simType] || SIM_CONFIG.full;
  const draftKey = `cpns_runner_draft_${simId || simType}`;
  draftStateRef.current = { answers, bookmarks, current, timeLeft, questions };

  const saveDraft = useCallback(() => {
    if (loading || typeof window === "undefined") return;
    const { answers, bookmarks, current, timeLeft, questions } = draftStateRef.current;
    if (questions.length === 0) return;
    const updatedAt = Date.now();
    const draft: RunnerDraft = {
      answers,
      bookmarks: Array.from(bookmarks),
      current,
      timeLeft,
      questionIds: questions.map((item) => item.id),
      updatedAt,
    };
    localStorage.setItem(draftKey, JSON.stringify(draft));
    setLastSavedAt(updatedAt);
  }, [draftKey, loading]);

  const restoreDraft = (loadedQuestions: Question[]) => {
    if (typeof window === "undefined" || loadedQuestions.length === 0) return;
    const raw = localStorage.getItem(draftKey);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw) as RunnerDraft;
      const loadedIds = loadedQuestions.map((item) => item.id).join(",");
      if (draft.questionIds?.join(",") !== loadedIds) {
        localStorage.removeItem(draftKey);
        return;
      }
      setAnswers(Array.isArray(draft.answers) ? draft.answers : []);
      setBookmarks(new Set(Array.isArray(draft.bookmarks) ? draft.bookmarks : []));
      setCurrent(Math.min(Math.max(draft.current || 0, 0), loadedQuestions.length - 1));
      if (typeof draft.timeLeft === "number" && draft.timeLeft > 0) setTimeLeft(draft.timeLeft);
      setDraftRestored(true);
      setLastSavedAt(draft.updatedAt || Date.now());
    } catch {
      localStorage.removeItem(draftKey);
    }
  };

  // Load fixed package questions for tryout parts. Legacy/non-package sims fall back to random practice-style sets.
  useEffect(() => {
    async function loadAll() {
      if (simId) {
        const packageRes = await apiGet(`/simulations/${simId}/questions`);
        if (packageRes.ok && packageRes.data?.length > 0) {
          setQuestions(packageRes.data);
          restoreDraft(packageRes.data);
          setLoading(false);
          return;
        }
      }

      const allQuestions: Question[] = [];
      for (const sec of config.sections) {
        const count = sec === "TWK" ? 30 : sec === "TIU" ? 35 : 45;
        const res = await apiGet(`/questions/random?section=${sec}&count=${count}`);
        if (res.ok) allQuestions.push(...res.data);
      }
      setQuestions(allQuestions);
      restoreDraft(allQuestions);
      setLoading(false);
    }
    loadAll();
  }, [simId, simType]);

  useEffect(() => {
    if (loading || questions.length === 0 || typeof window === "undefined") return;
    if (autosaveTimerRef.current) clearTimeout(autosaveTimerRef.current);
    autosaveTimerRef.current = setTimeout(saveDraft, AUTOSAVE_DEBOUNCE_MS);
    return () => {
      if (autosaveTimerRef.current) clearTimeout(autosaveTimerRef.current);
    };
  }, [answers, bookmarks, current, questions, loading, saveDraft]);

  useEffect(() => {
    if (loading || questions.length === 0 || typeof window === "undefined") return;
    const interval = setInterval(saveDraft, AUTOSAVE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loading, questions.length, saveDraft]);

  useEffect(() => {
    const hasDraft = answers.length > 0 || bookmarks.size > 0;
    if (!hasDraft) return;
    const handler = (event: BeforeUnloadEvent) => {
      saveDraft();
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [answers.length, bookmarks, saveDraft]);

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
  const bookmarkedCount = bookmarks.size;

  const questionGroups = [
    { label: "TWK", start: 0, end: 30 },
    { label: "TIU", start: 30, end: 65 },
    { label: "TKP", start: 65, end: questions.length },
  ].map((group) => ({ ...group, items: questions.slice(group.start, group.end) })).filter((group) => group.items.length > 0);

  const getMapButtonClass = (question: Question, index: number) => {
    const answered = answers.some((a) => a.questionId === question.id);
    const bookmarked = bookmarks.has(question.id);
    if (index === current) return "bg-primary text-primary-foreground ring-2 ring-primary/30 shadow-sm";
    if (bookmarked) return "border border-accent/50 bg-accent/15 text-primary";
    if (answered) return "border border-primary/30 bg-primary/10 text-primary";
    return "border border-border bg-secondary/70 text-muted-foreground hover:bg-secondary hover:text-foreground";
  };

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

  const handleSubmit = useCallback(async () => {
    if (submitting) return;
    setSubmitting(true);
    if (timerRef.current) clearInterval(timerRef.current);

    const duration = config.time - timeLeft;

    const res = await apiPost(`/simulations/${simId}/submit`, {
      duration_seconds: duration,
      questions_data: {
        questions: questions.map((q) => ({ id: q.id, section: q.section })),
        answers: answers.map((a) => ({ question_id: a.questionId, selected: a.selected })),
        total_questions: questions.length,
        answered: answers.length,
      },
    });

    if (res.ok) {
      if (typeof window !== "undefined") localStorage.removeItem(draftKey);
      router.push(`/dashboard/simulations/result?id=${simId}`);
    }
    setSubmitting(false);
  }, [submitting, config.time, timeLeft, simId, answers, questions, router, draftKey]);

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

  const renderQuestionMap = (onPick?: () => void) => (
    <CardContent>
      <div className="mb-4 grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded-lg border border-border bg-secondary/40 p-2">
          <p className="font-mono font-bold">{answeredCount}</p>
          <p className="text-muted-foreground">Terjawab</p>
        </div>
        <div className="rounded-lg border border-border bg-secondary/40 p-2">
          <p className="font-mono font-bold">{unansweredCount}</p>
          <p className="text-muted-foreground">Belum</p>
        </div>
        <div className="rounded-lg border border-accent/30 bg-accent/15 p-2">
          <p className="font-mono font-bold text-primary">{bookmarkedCount}</p>
          <p className="text-muted-foreground">Ragu</p>
        </div>
      </div>
      <div className="space-y-4">
        {questionGroups.map((group) => (
          <div key={group.label} className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold tracking-wide text-muted-foreground">{group.label}</p>
              <p className="text-[10px] font-mono text-muted-foreground">{group.start + 1}-{group.start + group.items.length}</p>
            </div>
            <div className="grid grid-cols-5 gap-1.5">
              {group.items.map((question, groupIndex) => {
                const index = group.start + groupIndex;
                const isBookmarked = bookmarks.has(question.id);
                return (
                  <button
                    key={question.id}
                    onClick={() => { goTo(index); onPick?.(); }}
                    aria-label={`Ke soal ${index + 1}`}
                    className={`relative flex h-8 w-full items-center justify-center rounded-lg text-[11px] font-mono font-bold transition-all ${getMapButtonClass(question, index)}`}
                  >
                    {index + 1}
                    {isBookmarked && index !== current && (
                      <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-accent" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-1"><span className="h-3 w-3 rounded bg-primary" /> Aktif</div>
        <div className="flex items-center gap-1"><span className="h-3 w-3 rounded bg-primary/20" /> Terjawab</div>
        <div className="flex items-center gap-1"><span className="h-3 w-3 rounded border border-border bg-secondary" /> Belum</div>
        <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-accent" /> Ragu</div>
      </div>
    </CardContent>
  );

  return (
    <div className="space-y-4">
      {/* Top bar */}
      <div className="sticky top-0 z-40 bg-card/95 backdrop-blur border-b border-border/50 -mx-4 lg:-mx-6 px-4 lg:px-6 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="font-bold font-serif text-sm">{config.label}</h1>
            <p className="text-xs text-muted-foreground">
              Soal {current + 1} / {questions.length} · {answeredCount} terjawab
            </p>
            <p className="mt-0.5 inline-flex items-center gap-1 text-[10px] text-muted-foreground/70">
              <Save className="h-3 w-3" />
              {draftRestored ? "Draft dipulihkan · " : "Autosave 15–30 dtk · "}
              {lastSavedAt ? `tersimpan ${new Date(lastSavedAt).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })}` : "menunggu perubahan"}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <Button variant="outline" size="sm" className="rounded-lg lg:hidden" onClick={() => setShowMap(true)}>
              <LayoutGrid className="h-4 w-4 sm:mr-1.5" />
              <span className="hidden sm:inline">Peta</span>
            </Button>
            <Badge variant="secondary" className={`gap-1.5 font-mono px-3 py-1.5 ${timeLeft < 300 ? "bg-destructive/10 text-destructive" : ""}`}>
              <Clock className="h-3.5 w-3.5" />
              {formatTime(timeLeft)}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              className="rounded-lg border-primary/30"
              onClick={() => setShowConfirm(true)}
            >
              <Send className="h-4 w-4 sm:mr-1.5" /> <span className="hidden sm:inline">Selesai</span>
            </Button>
          </div>
        </div>
        {/* Progress bar */}
        <div className="mt-2 h-1 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-300"
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
                    aria-label={bookmarks.has(q.id) ? "Hapus tanda ragu" : "Tandai ragu"}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors ${
                      bookmarks.has(q.id) ? "text-primary bg-accent/15 dark:text-primary" : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                    }`}
                  >
                    {bookmarks.has(q.id) ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                    {bookmarks.has(q.id) ? "Ragu" : "Tandai Ragu"}
                  </button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-base font-medium leading-relaxed text-foreground sm:text-[17px]">{q.question_text}</p>
                <div className="space-y-2">
                  {q.options?.map((opt: string, i: number) => {
                    const isSelected = currentAnswer?.selected === i;
                    return (
                      <button
                        key={i}
                        onClick={() => selectAnswer(i)}
                        aria-pressed={isSelected}
                        className={`w-full text-left p-3.5 rounded-xl border-2 text-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/30 ${
                          isSelected
                            ? "border-foreground bg-primary text-primary-foreground shadow-sm"
                            : "border-border hover:border-primary/40 hover:bg-muted/30"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                            isSelected ? "bg-card text-card-foreground" : "bg-secondary text-muted-foreground"
                          }`}>
                            {String.fromCharCode(65 + i)}
                          </span>
                          <span className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border ${
                            isSelected ? "border-background" : "border-border"
                          }`}>
                            {isSelected && <span className="h-2 w-2 rounded-full bg-card" />}
                          </span>
                          <span className={`flex-1 ${isSelected ? "text-primary-foreground" : ""}`}>{opt}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="sticky bottom-0 z-30 -mx-4 flex items-center justify-between border-t border-border/50 bg-card/95 px-4 py-3 backdrop-blur lg:static lg:mx-0 lg:border-0 lg:bg-transparent lg:p-0">
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
            {renderQuestionMap()}
          </Card>
        </div>
      </div>

      {showMap && (
        <div className="fixed inset-0 z-50 bg-black/50 lg:hidden" onClick={() => setShowMap(false)}>
          <div className="absolute inset-x-0 bottom-0 max-h-[86vh] overflow-y-auto rounded-t-2xl bg-card p-4 shadow-xl" onClick={(event) => event.stopPropagation()}>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-serif text-lg font-bold">Peta Soal</h2>
              <Button variant="ghost" size="sm" className="rounded-full" onClick={() => setShowMap(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            {renderQuestionMap(() => setShowMap(false))}
          </div>
        </div>
      )}

      {/* Confirm submit modal */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-sm mx-4">
            <CardContent className="p-6 text-center">
              {unansweredCount > 0 ? (
                <AlertTriangle className="h-12 w-12 text-accent mx-auto mb-3" />
              ) : (
                <Check className="h-12 w-12 text-primary mx-auto mb-3" />
              )}
              <h2 className="text-lg font-bold font-serif mb-2">Yakin Selesai?</h2>
              <p className="text-sm text-muted-foreground mb-4">
                {unansweredCount > 0
                  ? `Masih ada ${unansweredCount} soal yang belum dijawab.`
                  : "Semua soal sudah dijawab!"}
              </p>
              <p className="mb-4 rounded-lg border border-accent/30 bg-accent/15 px-3 py-2 text-xs text-primary">
                Setelah dikirim, jawaban final dan tidak bisa diubah lagi.
              </p>
              <div className="mb-5 grid grid-cols-3 gap-2 text-center text-xs">
                <div className="rounded-lg bg-secondary/60 p-2">
                  <p className="font-mono text-base font-bold">{answeredCount}</p>
                  <p className="text-muted-foreground">Terjawab</p>
                </div>
                <div className="rounded-lg bg-secondary/60 p-2">
                  <p className="font-mono text-base font-bold">{unansweredCount}</p>
                  <p className="text-muted-foreground">Belum</p>
                </div>
                <div className="rounded-lg bg-accent/15 p-2">
                  <p className="font-mono text-base font-bold text-primary">{bookmarkedCount}</p>
                  <p className="text-muted-foreground">Ragu</p>
                </div>
              </div>
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

