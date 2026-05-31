"use client";
import { useState, useEffect } from "react";
import { apiGet } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BookOpen, ChevronRight, ChevronLeft, Check, X, Lightbulb, Loader2 } from "lucide-react";

const SECTIONS = ["TWK", "TIU", "TKP"];

export default function QuestionsPage() {
  const [section, setSection] = useState("TWK");
  const [questions, setQuestions] = useState<any[]>([]);
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadQuestions = async (sec: string) => {
    setLoading(true);
    const res = await apiGet(`/questions/random?section=${sec}&count=10`);
    if (res.ok) { setQuestions(res.data); setCurrent(0); setSelected(null); setShowAnswer(false); }
    setLoading(false);
  };

  useEffect(() => { loadQuestions(section); }, [section]);

  const q = questions[current];

  const checkAnswer = async () => {
    if (selected === null || !q) return;
    setShowAnswer(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold tracking-tight font-serif">Bank Soal</h1>
        <div className="flex gap-2">
          {SECTIONS.map((s) => (
            <Button key={s} variant={section === s ? "default" : "outline"} size="sm" className="rounded-lg" onClick={() => setSection(s)}>{s}</Button>
          ))}
        </div>
      </div>

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
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border/50">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <CardTitle className="text-lg font-serif">Soal {current + 1}</CardTitle>
                <Badge variant="secondary" className="text-xs font-mono">{current + 1}/{questions.length}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">{q.section}</Badge>
                <span className="text-xs text-muted-foreground">{q.topic}</span>
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-3 h-1 bg-secondary rounded-full overflow-hidden">
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
                const isCorrect = showAnswer && i === q.correct_answer;
                const isWrong = showAnswer && selected === i && i !== q.correct_answer;
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
                    </div>
                  </button>
                );
              })}
            </div>
            {showAnswer && q.explanation && (
              <div className="p-4 bg-secondary/50 border border-border/50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold">Pembahasan</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{q.explanation}</p>
              </div>
            )}
            <div className="flex justify-between pt-2">
              <Button
                variant="outline"
                size="sm"
                className="rounded-lg"
                onClick={() => { setCurrent(Math.max(0, current - 1)); setSelected(null); setShowAnswer(false); }}
                disabled={current === 0}
              >
                <ChevronLeft className="h-4 w-4 mr-1" /> Sebelumnya
              </Button>
              {!showAnswer ? (
                <Button size="sm" className="rounded-lg" onClick={checkAnswer} disabled={selected === null}>
                  Cek Jawaban
                </Button>
              ) : (
                <Button
                  size="sm"
                  className="rounded-lg"
                  onClick={() => { setCurrent(Math.min(questions.length - 1, current + 1)); setSelected(null); setShowAnswer(false); }}
                  disabled={current >= questions.length - 1}
                >
                  Berikutnya <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
