"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { apiGet } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen, ChevronRight, ChevronLeft, Check, X, Lightbulb, Loader2,
  Bookmark, BookmarkCheck, RotateCcw, Trophy, Target, Filter,
  Hash, Timer, Zap, ChevronDown,
} from "lucide-react";

const SECTIONS = ["TWK", "TIU", "TKP"];
const COUNTS = [10, 20, 30];

interface Question {
  id: number;
  section: string;
  topic: string;
  year: number;
  difficulty: string;
  question_text: string;
  options: string[] | { text: string }[];
}

interface Answer {
  questionId: number;
  selected: number;
  correct: boolean;
}

export default function QuestionsPage() {
  const [section, setSection] = useState("TWK");
  const [topic, setTopic] = useState<string>("");
  const [count, setCount] = useState(10);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [bookmarks, setBookmarks] = useState<Set<number>>(new Set());
  const [showSummary, setShowSummary] = useState(false);
  const [topics, setTopics] = useState<{ topic: string; count: number }[]>([]);
  const [showTopicFilter, setShowTopicFilter] = useState(false);
  const [timer, setTimer] = useState(0);
  const [timerActive, setTimerActive] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Load topics for current section
  useEffect(() => {
    apiGet(`/questions/topics?section=${section}`).then((res) => {
      if (res.ok) setTopics(res.data);
    });
  }, [section]);

  // Timer
  useEffect(() => {
    if (timerActive) {
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [timerActive]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  const loadQuestions = async (sec: string, top: string, cnt: number) => {
    setLoading(true);
    setShowSummary(false);
    setAnswers([]);
    setCurrent(0);
    setSelected(null);
    setShowAnswer(false);
    setTimer(0);
    setTimerActive(true);
    let url = `/questions/random?section=${sec}&count=${cnt}`;
    if (top) url += `&topic=${encodeURIComponent(top)}`;
    const res = await apiGet(url);
    if (res.ok) {
      setQuestions(res.data);
      if (res.data.length === 0) setShowSummary(false);
    }
    setLoading(false);
  };

  useEffect(() => { loadQuestions(section, topic, count); }, [section, topic, count]);

  const q = questions[current];
  const currentAnswer = answers.find(a => a.questionId === q?.id);

  const checkAnswer = useCallback(() => {
    if (selected === null || !q) return;
    setShowAnswer(true);
    const correct = selected === (q as any).correct_answer;
    setAnswers(prev => {
      const existing = prev.findIndex(a => a.questionId === q.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { questionId: q.id, selected, correct };
        return updated;
      }
      return [...prev, { questionId: q.id, selected, correct }];
    });
  }, [selected, q]);

  const goToQuestion = useCallback((idx: number) => {
    setCurrent(idx);
    const existing = answers.find(a => a.questionId === questions[idx]?.id);
    setSelected(existing ? existing.selected : null);
    setShowAnswer(!!existing);
  }, [answers, questions]);

  const nextQuestion = useCallback(() => {
    if (current < questions.length - 1) goToQuestion(current + 1);
    else {
      setTimerActive(false);
      setShowSummary(true);
    }
  }, [current, questions.length, goToQuestion]);

  const prevQuestion = useCallback(() => {
    if (current > 0) goToQuestion(current - 1);
  }, [current, goToQuestion]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (showSummary) return;
      // A-E to select options
      if (!showAnswer && e.key >= "a" && e.key <= "e") {
        const idx = e.key.charCodeAt(0) - 97;
        if (q && idx < (q.options?.length || 0)) setSelected(idx);
      }
      // Enter to check or next
      if (e.key === "Enter") {
        if (!showAnswer && selected !== null) checkAnswer();
        else if (showAnswer) nextQuestion();
      }
      // Arrow keys to navigate
      if (e.key === "ArrowLeft") prevQuestion();
      if (e.key === "ArrowRight" && showAnswer) nextQuestion();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [showAnswer, selected, q, showSummary, checkAnswer, nextQuestion, prevQuestion]);

  const toggleBookmark = (id: number) => {
    setBookmarks(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const retryWrong = () => {
    const wrongQuestions = questions.filter(q =>
      answers.some(a => a.questionId === q.id && !a.correct)
    );
    if (wrongQuestions.length === 0) return;
    setQuestions(wrongQuestions);
    setAnswers([]);
    setCurrent(0);
    setSelected(null);
    setShowAnswer(false);
    setShowSummary(false);
    setTimer(0);
    setTimerActive(true);
  };

  const correctCount = answers.filter(a => a.correct).length;
  const wrongCount = answers.filter(a => !a.correct).length;
  const pct = answers.length > 0 ? Math.round((correctCount / answers.length) * 100) : 0;

  // Summary view
  if (showSummary && questions.length > 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold tracking-tight font-serif">Hasil Latihan</h1>

        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex flex-col items-center text-center">
              <div className={`flex h-20 w-20 items-center justify-center rounded-full mb-4 ${
                pct >= 70 ? "bg-emerald-500/10" : pct >= 50 ? "bg-amber-500/10" : "bg-red-500/10"
              }`}>
                {pct >= 70 ? (
                  <Trophy className="h-10 w-10 text-emerald-500" />
                ) : pct >= 50 ? (
                  <Target className="h-10 w-10 text-amber-500" />
                ) : (
                  <Zap className="h-10 w-10 text-red-500" />
                )}
              </div>
              <p className="text-4xl font-bold font-mono mb-1">{pct}%</p>
              <p className="text-muted-foreground text-sm">
                {correctCount} benar dari {answers.length} soal
              </p>
              <div className="flex items-center gap-4 mt-3 text-sm">
                <span className="flex items-center gap-1.5 text-emerald-600">
                  <Check className="h-4 w-4" /> {correctCount} Benar
                </span>
                <span className="flex items-center gap-1.5 text-red-500">
                  <X className="h-4 w-4" /> {wrongCount} Salah
                </span>
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Timer className="h-4 w-4" /> {formatTime(timer)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Question-by-question review */}
        <Card className="border-border/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-serif">Review Jawaban</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
              {questions.map((q, i) => {
                const ans = answers.find(a => a.questionId === q.id);
                const isCorrect = ans?.correct;
                const isBookmarked = bookmarks.has(q.id);
                return (
                  <button
                    key={q.id}
                    onClick={() => {
                      setShowSummary(false);
                      goToQuestion(i);
                    }}
                    className={`relative flex h-10 w-full items-center justify-center rounded-lg text-sm font-mono font-bold transition-all ${
                      isCorrect === true
                        ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30"
                        : isCorrect === false
                        ? "bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/30"
                        : "bg-secondary text-muted-foreground border border-border"
                    }`}
                  >
                    {i + 1}
                    {isBookmarked && (
                      <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-amber-500" />
                    )}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => loadQuestions(section, topic, count)} className="rounded-lg">
            <RotateCcw className="h-4 w-4 mr-2" /> Latihan Lagi
          </Button>
          {wrongCount > 0 && (
            <Button variant="outline" onClick={retryWrong} className="rounded-lg">
              <Zap className="h-4 w-4 mr-2" /> Ulangi yang Salah ({wrongCount})
            </Button>
          )}
          <Button variant="outline" onClick={() => setShowSummary(false)} className="rounded-lg">
            <BookOpen className="h-4 w-4 mr-2" /> Review Soal
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold tracking-tight font-serif">Bank Soal</h1>
        <div className="flex flex-wrap items-center gap-2">
          {/* Timer */}
          <Badge variant="secondary" className="gap-1.5 font-mono px-3 py-1.5">
            <Timer className="h-3.5 w-3.5" />
            {formatTime(timer)}
          </Badge>
          {/* Bookmarks count */}
          {bookmarks.size > 0 && (
            <Badge variant="secondary" className="gap-1.5 px-3 py-1.5">
              <BookmarkCheck className="h-3.5 w-3.5" />
              {bookmarks.size}
            </Badge>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Section tabs */}
        <div className="flex gap-1.5">
          {SECTIONS.map((s) => (
            <Button
              key={s}
              variant={section === s ? "default" : "outline"}
              size="sm"
              className="rounded-lg"
              onClick={() => { setSection(s); setTopic(""); }}
            >
              {s}
            </Button>
          ))}
        </div>

        {/* Topic filter */}
        <div className="relative">
          <Button
            variant="outline"
            size="sm"
            className="rounded-lg gap-1.5"
            onClick={() => setShowTopicFilter(!showTopicFilter)}
          >
            <Filter className="h-3.5 w-3.5" />
            {topic || "Semua Topik"}
            <ChevronDown className="h-3.5 w-3.5" />
          </Button>
          {showTopicFilter && (
            <div className="absolute top-full left-0 mt-1 z-50 w-64 max-h-64 overflow-y-auto rounded-xl border border-border bg-popover shadow-lg">
              <button
                onClick={() => { setTopic(""); setShowTopicFilter(false); }}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-muted/50 transition-colors ${!topic ? "font-semibold" : ""}`}
              >
                Semua Topik
              </button>
              {topics.map((t) => (
                <button
                  key={t.topic}
                  onClick={() => { setTopic(t.topic); setShowTopicFilter(false); }}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-muted/50 transition-colors flex items-center justify-between ${
                    topic === t.topic ? "font-semibold bg-muted/30" : ""
                  }`}
                >
                  <span className="truncate">{t.topic}</span>
                  <Badge variant="secondary" className="text-[10px] ml-2 shrink-0">{t.count}</Badge>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Count selector */}
        <div className="flex items-center gap-1.5 ml-auto">
          <Hash className="h-3.5 w-3.5 text-muted-foreground" />
          {COUNTS.map((c) => (
            <Button
              key={c}
              variant={count === c ? "default" : "outline"}
              size="sm"
              className="rounded-lg w-10"
              onClick={() => setCount(c)}
            >
              {c}
            </Button>
          ))}
        </div>
      </div>

      {/* Question navigation dots */}
      {questions.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {questions.map((q, i) => {
            const ans = answers.find(a => a.questionId === q.id);
            const isBookmarked = bookmarks.has(q.id);
            return (
              <button
                key={q.id}
                onClick={() => goToQuestion(i)}
                className={`relative flex h-8 w-8 items-center justify-center rounded-lg text-xs font-mono font-bold transition-all ${
                  i === current
                    ? "bg-foreground text-background ring-2 ring-foreground/20"
                    : ans?.correct === true
                    ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                    : ans?.correct === false
                    ? "bg-red-500/10 text-red-700 dark:text-red-400"
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
      )}

      {/* Main question card */}
      {loading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Memuat soal...</p>
            </div>
          </CardContent>
        </Card>
      ) : !q ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <BookOpen className="h-10 w-10 text-muted-foreground/40 mb-3" />
            <p className="text-muted-foreground">Tidak ada soal tersedia.</p>
            <p className="text-xs text-muted-foreground mt-1">Coba pilih topik atau section lain.</p>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border/50">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <CardTitle className="text-lg font-serif">Soal {current + 1}</CardTitle>
                <Badge variant="secondary" className="text-xs font-mono">{current + 1}/{questions.length}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleBookmark(q.id)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    bookmarks.has(q.id) ? "text-amber-500 bg-amber-500/10" : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }`}
                >
                  {bookmarks.has(q.id) ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                </button>
                <Badge variant="outline" className="text-xs">{q.section}</Badge>
                <Badge variant="secondary" className="text-xs">{q.topic}</Badge>
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-3 h-1.5 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-foreground/80 rounded-full transition-all duration-300"
                style={{ width: `${((current + 1) / questions.length) * 100}%` }}
              />
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <p className="text-sm leading-relaxed">{q.question_text}</p>
            <div className="space-y-2.5">
              {q.options?.map((opt: any, i: number) => {
                const optText = typeof opt === "string" ? opt : opt.text;
                const isCorrect = showAnswer && i === (q as any).correct_answer;
                const isWrong = showAnswer && selected === i && i !== (q as any).correct_answer;
                const isSelected = selected === i && !showAnswer;
                return (
                  <button
                    key={i}
                    onClick={() => !showAnswer && setSelected(i)}
                    className={`w-full text-left p-3.5 rounded-xl border-2 text-sm transition-all ${
                      isSelected
                        ? "border-foreground bg-foreground/5"
                        : isCorrect
                        ? "border-emerald-500 bg-emerald-500/10"
                        : isWrong
                        ? "border-red-500 bg-red-500/10"
                        : "border-border hover:border-foreground/30 hover:bg-muted/30"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                        isSelected ? "bg-foreground text-background" :
                        isCorrect ? "bg-emerald-500 text-white" :
                        isWrong ? "bg-red-500 text-white" :
                        "bg-secondary text-muted-foreground"
                      }`}>
                        {isCorrect ? <Check className="h-3.5 w-3.5" strokeWidth={3} /> :
                         isWrong ? <X className="h-3.5 w-3.5" strokeWidth={3} /> :
                         String.fromCharCode(65 + i)}
                      </span>
                      <span className="flex-1">{optText}</span>
                      <span className="text-[10px] text-muted-foreground/50 uppercase font-mono mt-0.5">
                        {String.fromCharCode(65 + i)}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
            {showAnswer && (q as any).explanation && (
              <div className="p-4 bg-secondary/50 border border-border/50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold">Pembahasan</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{(q as any).explanation}</p>
              </div>
            )}
            <div className="flex items-center justify-between pt-2">
              <Button
                variant="outline"
                size="sm"
                className="rounded-lg"
                onClick={prevQuestion}
                disabled={current === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-1" /> Sebelumnya
              </Button>

              {/* Keyboard hint */}
              <div className="hidden sm:flex items-center gap-1.5 text-[10px] text-muted-foreground/50">
                {!showAnswer ? (
                  <span>A-E pilih · Enter cek</span>
                ) : (
                  <span>Enter/→ berikutnya</span>
                )}
              </div>

              {!showAnswer ? (
                <Button size="sm" className="rounded-lg" onClick={checkAnswer} disabled={selected === null}>
                  Cek Jawaban
                </Button>
              ) : (
                <Button size="sm" className="rounded-lg" onClick={nextQuestion}>
                  {current >= questions.length - 1 ? "Lihat Hasil" : "Berikutnya"}
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
