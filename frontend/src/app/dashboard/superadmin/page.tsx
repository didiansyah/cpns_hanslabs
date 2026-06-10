"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { apiDelete, apiGet, apiPatch, apiPost, apiPut } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Activity, BarChart3, BookOpen, CheckCircle2, Edit3, MessageSquare, Plus, RefreshCw, Save, Search, ShieldCheck, Trash2, Users } from "lucide-react";

type AdminSummary = {
  stats: Record<string, number>;
  daily_signups: { date: string; count: number }[];
  question_sections: { section: string; count: number }[];
  recent_users: AdminUser[];
  umami: {
    script_url: string;
    website_id: string;
    collect_url: string;
    status: string;
    stats?: Record<string, number>;
    pageviews?: { x: string; y: number }[];
    sessions?: { x: string; y: number }[];
  };
};

type AdminUser = {
  id: number;
  name: string;
  email: string;
  phone?: string;
  education?: string;
  target_instansi?: string;
  verified: boolean;
  is_superadmin: boolean;
  created_at: string;
  sim_count: number;
  study_days: number;
  streak_days: number;
};


type AdminFeedback = {
  id: number;
  user_id: number;
  user_name?: string;
  user_email?: string;
  category: string;
  rating?: number | null;
  message: string;
  path?: string;
  status: "open" | "reviewed" | "resolved";
  created_at: string;
};

type AdminQuestion = {
  id?: number;
  section: string;
  topic: string;
  year?: number | null;
  difficulty?: string | null;
  question_text: string;
  options: any[];
  correct_answer?: number | null;
  explanation?: string | null;
};

const emptyQuestion: AdminQuestion = {
  section: "TWK",
  topic: "",
  year: new Date().getFullYear(),
  difficulty: "sedang",
  question_text: "",
  options: ["", "", "", "", ""],
  correct_answer: 0,
  explanation: "",
};

function StatCard({ label, value, icon: Icon }: { label: string; value: number | string; icon: any }) {
  return (
    <div className="rounded-3xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground">{label}</p>
          <p className="mt-3 font-mono text-3xl font-bold tracking-tight">{value}</p>
        </div>
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}

type AdminTab = "overview" | "analytics" | "users" | "questions" | "feedback";

function tabFromPath(pathname: string): AdminTab {
  if (pathname.endsWith("/analytics")) return "analytics";
  if (pathname.endsWith("/users")) return "users";
  if (pathname.endsWith("/questions")) return "questions";
  if (pathname.endsWith("/feedback")) return "feedback";
  return "overview";
}

export default function SuperAdminPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading } = useAuth();
  const activeTab = tabFromPath(pathname);
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [userSearch, setUserSearch] = useState("");
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [feedback, setFeedback] = useState<AdminFeedback[]>([]);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [questionSearch, setQuestionSearch] = useState("");
  const [questionForm, setQuestionForm] = useState<AdminQuestion>(emptyQuestion);
  const [optionsText, setOptionsText] = useState(emptyQuestion.options.join("\n"));
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const canAdmin = !!user?.is_superadmin;

  useEffect(() => {
    if (!loading && !user) router.push("/login");
    if (!loading && user && !user.is_superadmin) router.push("/dashboard");
  }, [loading, user, router]);

  const loadSummary = async () => {
    const res = await apiGet("/admin/summary");
    if (res.ok) setSummary(res.data);
  };

  const loadUsers = async () => {
    const res = await apiGet(`/admin/users?search=${encodeURIComponent(userSearch)}`);
    if (res.ok) setUsers(res.data.users);
  };

  const loadQuestions = async () => {
    const res = await apiGet(`/admin/questions?search=${encodeURIComponent(questionSearch)}&limit=30`);
    if (res.ok) setQuestions(res.data.questions);
  };

  const loadFeedback = async () => {
    const res = await apiGet(`/admin/feedback?status=${encodeURIComponent(feedbackStatus)}&limit=50`);
    if (res.ok) setFeedback(res.data.feedback);
  };

  useEffect(() => {
    if (canAdmin) {
      loadSummary();
      loadUsers();
      loadQuestions();
      loadFeedback();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canAdmin]);

  const maxSignup = useMemo(() => Math.max(1, ...(summary?.daily_signups || []).map((d) => d.count)), [summary]);

  const saveUser = async (u: AdminUser) => {
    setSaving(true);
    const res = await apiPut(`/admin/users/${u.id}`, {
      name: u.name,
      phone: u.phone,
      education: u.education,
      target_instansi: u.target_instansi,
      verified: u.verified,
    });
    setSaving(false);
    setMessage(res.ok ? "User tersimpan" : res.error || "Gagal simpan user");
    if (res.ok) loadUsers();
  };

  const deleteUser = async (u: AdminUser) => {
    if (!confirm(`Hapus user ${u.email}?`)) return;
    const res = await apiDelete(`/admin/users/${u.id}`);
    setMessage(res.ok ? "User dihapus" : res.error || "Gagal hapus user");
    if (res.ok) loadUsers();
  };

  const editQuestion = (q: AdminQuestion) => {
    setQuestionForm({ ...q });
    setOptionsText((q.options || []).map((o: any) => typeof o === "string" ? o : JSON.stringify(o)).join("\n"));
    router.push("/dashboard/superadmin/questions");
  };

  const resetQuestion = () => {
    setQuestionForm(emptyQuestion);
    setOptionsText(emptyQuestion.options.join("\n"));
  };

  const saveQuestion = async () => {
    setSaving(true);
    const payload = {
      ...questionForm,
      section: questionForm.section.toUpperCase(),
      year: questionForm.year ? Number(questionForm.year) : null,
      correct_answer: questionForm.correct_answer === null || questionForm.correct_answer === undefined ? null : Number(questionForm.correct_answer),
      options: optionsText.split("\n").map((line) => line.trim()).filter(Boolean),
    };
    const res = questionForm.id ? await apiPut(`/admin/questions/${questionForm.id}`, payload) : await apiPost("/admin/questions", payload);
    setSaving(false);
    setMessage(res.ok ? "Soal tersimpan" : res.error || "Gagal simpan soal");
    if (res.ok) {
      resetQuestion();
      loadQuestions();
      loadSummary();
    }
  };

  const updateFeedbackStatus = async (item: AdminFeedback, status: AdminFeedback["status"]) => {
    const res = await apiPatch(`/admin/feedback/${item.id}`, { status });
    setMessage(res.ok ? "Feedback diperbarui" : res.error || "Gagal update feedback");
    if (res.ok) loadFeedback();
  };

  const deleteQuestion = async (q: AdminQuestion) => {
    if (!q.id || !confirm(`Hapus soal #${q.id}?`)) return;
    const res = await apiDelete(`/admin/questions/${q.id}`);
    setMessage(res.ok ? "Soal dihapus" : res.error || "Gagal hapus soal");
    if (res.ok) {
      loadQuestions();
      loadSummary();
    }
  };

  if (loading || !canAdmin) return <div className="p-8 text-sm text-muted-foreground">Memuat akses superadmin...</div>;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="rounded-[2rem] border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.22em] text-muted-foreground">
              <ShieldCheck className="h-4 w-4" /> Superadmin
            </p>
            <h1 className="mt-3 font-serif text-3xl font-bold tracking-tight lg:text-4xl">Control Center CPNS</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">Kelola user, soal, dan pantau funnel produk. Umami tracking aktif via script internal.</p>
          </div>
          <button onClick={() => { loadSummary(); loadUsers(); loadQuestions(); loadFeedback(); }} className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground">
            <RefreshCw className="h-4 w-4" /> Refresh data
          </button>
        </div>
        <div className="mt-6 flex flex-wrap gap-2">
          {[
            ["overview", "Overview", BarChart3, "/dashboard/superadmin"],
            ["analytics", "Analytics", Activity, "/dashboard/superadmin/analytics"],
            ["users", "Users", Users, "/dashboard/superadmin/users"],
            ["questions", "Soal", BookOpen, "/dashboard/superadmin/questions"],
            ["feedback", "Feedback", MessageSquare, "/dashboard/superadmin/feedback"],
          ].map(([key, label, Icon, href]: any) => (
            <button key={key} onClick={() => router.push(href)} className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${activeTab === key ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground hover:bg-muted"}`}>
              <Icon className="h-4 w-4" /> {label}
            </button>
          ))}
        </div>
        {message ? <p className="mt-4 rounded-2xl border border-border bg-secondary px-4 py-3 text-sm text-muted-foreground">{message}</p> : null}
      </div>

      {activeTab === "overview" && summary ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Total user" value={summary.stats.total_users} icon={Users} />
            <StatCard label="Verified" value={summary.stats.verified_users} icon={CheckCircle2} />
            <StatCard label="Total soal" value={summary.stats.total_questions} icon={BookOpen} />
            <StatCard label="Simulasi" value={summary.stats.total_simulations} icon={Activity} />
          </div>

          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="font-serif text-2xl font-bold">Signup 7 hari</h2>
            <div className="mt-6 space-y-3">
              {summary.daily_signups.map((d) => (
                <div key={d.date} className="grid grid-cols-[96px_1fr_42px] items-center gap-3 text-sm">
                  <span className="font-mono text-xs text-muted-foreground">{d.date.slice(5)}</span>
                  <div className="h-3 overflow-hidden rounded-full bg-secondary">
                    <div className="h-full rounded-full bg-primary" style={{ width: `${Math.max(4, (d.count / maxSignup) * 100)}%` }} />
                  </div>
                  <span className="text-right font-mono font-bold">{d.count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="font-serif text-2xl font-bold">User terbaru</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {summary.recent_users.map((u) => (
                <div key={u.id} className="rounded-2xl border border-border bg-secondary/40 p-4">
                  <p className="font-semibold">{u.name}</p>
                  <p className="mt-1 truncate text-xs text-muted-foreground">{u.email}</p>
                  <p className="mt-3 font-mono text-xs text-muted-foreground">sim {u.sim_count} · day {u.study_days}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}


      {activeTab === "analytics" && summary ? (
        <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="font-serif text-2xl font-bold">Umami analytics</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">Tracking aktif di semua halaman via script internal dan custom event page_view setiap route berubah.</p>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-2xl bg-secondary/50 p-4">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">Pageviews</p>
                <p className="mt-2 font-mono text-2xl font-bold">{summary.umami.stats?.pageviews ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-secondary/50 p-4">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">Visitors</p>
                <p className="mt-2 font-mono text-2xl font-bold">{summary.umami.stats?.visitors ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-secondary/50 p-4">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">Visits</p>
                <p className="mt-2 font-mono text-2xl font-bold">{summary.umami.stats?.visits ?? 0}</p>
              </div>
              <div className="rounded-2xl bg-secondary/50 p-4">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">Bounces</p>
                <p className="mt-2 font-mono text-2xl font-bold">{summary.umami.stats?.bounces ?? 0}</p>
              </div>
            </div>
          </div>
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <h2 className="font-serif text-2xl font-bold">Event tracking</h2>
            <div className="mt-5 space-y-3 text-sm text-muted-foreground">
              <p>Status: <span className="font-semibold text-foreground">{summary.umami.status}</span></p>
              <p>Website ID: <span className="font-mono text-xs text-foreground">{summary.umami.website_id}</span></p>
              <p>Script: <span className="font-mono text-xs text-foreground">{summary.umami.script_url}</span></p>
              <p>Collect: <span className="font-mono text-xs text-foreground">{summary.umami.collect_url}</span></p>
              <div className="rounded-2xl border border-border bg-secondary/40 p-4">
                <p className="font-semibold text-foreground">Custom events aktif:</p>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li><span className="font-mono text-foreground">page_view</span> di semua route</li>
                  <li><span className="font-mono text-foreground">donation_cta_click</span> saat tombol donasi diklik</li>
                  <li><span className="font-mono text-foreground">donation_modal_open</span> saat modal donasi kebuka</li>
                  <li><span className="font-mono text-foreground">donation_submit</span> saat submit donasi manual</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {activeTab === "users" ? (
        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <h2 className="font-serif text-2xl font-bold">Control user</h2>
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input value={userSearch} onChange={(e) => setUserSearch(e.target.value)} className="h-11 rounded-xl border border-border bg-background pl-9 pr-3 text-sm outline-none" placeholder="Cari nama/email" />
              </div>
              <button onClick={loadUsers} className="rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground">Cari</button>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {users.map((u, idx) => (
              <div key={u.id} className="grid gap-3 rounded-2xl border border-border bg-secondary/30 p-4 lg:grid-cols-[1.2fr_1fr_1fr_auto] lg:items-center">
                <div>
                  <input value={u.name} onChange={(e) => setUsers((list) => list.map((x, i) => i === idx ? { ...x, name: e.target.value } : x))} className="w-full rounded-xl border border-border bg-background px-3 py-2 text-sm font-semibold" />
                  <p className="mt-1 text-xs text-muted-foreground">{u.email}</p>
                </div>
                <input value={u.phone || ""} onChange={(e) => setUsers((list) => list.map((x, i) => i === idx ? { ...x, phone: e.target.value } : x))} className="rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Phone" />
                <input value={u.target_instansi || ""} onChange={(e) => setUsers((list) => list.map((x, i) => i === idx ? { ...x, target_instansi: e.target.value } : x))} className="rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Target instansi" />
                <div className="flex flex-wrap items-center justify-end gap-2">
                  <label className="flex items-center gap-2 rounded-xl border border-border px-3 py-2 text-xs font-semibold">
                    <input type="checkbox" checked={u.verified} onChange={(e) => setUsers((list) => list.map((x, i) => i === idx ? { ...x, verified: e.target.checked } : x))} /> Verified
                  </label>
                  <button disabled={saving} onClick={() => saveUser(u)} className="inline-flex items-center gap-1 rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground"><Save className="h-3.5 w-3.5" /> Simpan</button>
                  {!u.is_superadmin ? <button onClick={() => deleteUser(u)} className="inline-flex items-center gap-1 rounded-xl border border-red-200 px-3 py-2 text-xs font-semibold text-red-600"><Trash2 className="h-3.5 w-3.5" /> Hapus</button> : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {activeTab === "feedback" ? (
        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="font-serif text-2xl font-bold">Feedback user</h2>
              <p className="mt-2 text-sm text-muted-foreground">Masukan dari tab Feedback kanan. Bisa ditandai reviewed/resolved.</p>
            </div>
            <div className="flex gap-2">
              <select value={feedbackStatus} onChange={(e) => setFeedbackStatus(e.target.value)} className="h-11 rounded-xl border border-border bg-background px-3 text-sm outline-none">
                <option value="">Semua status</option>
                <option value="open">Open</option>
                <option value="reviewed">Reviewed</option>
                <option value="resolved">Resolved</option>
              </select>
              <button onClick={loadFeedback} className="rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground">Filter</button>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {feedback.length ? feedback.map((item) => (
              <div key={item.id} className="rounded-2xl border border-border bg-secondary/30 p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-muted-foreground">
                      <span>#{item.id}</span>
                      <span>{item.category}</span>
                      <span>{item.rating ? `${item.rating}/5` : "-"}</span>
                      <span className="rounded-full bg-background px-2 py-1 text-foreground">{item.status}</span>
                    </div>
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6">{item.message}</p>
                    <p className="mt-3 text-xs text-muted-foreground">{item.user_name || "User"} · {item.user_email || "-"} · <span className="font-mono">{item.path || "-"}</span></p>
                    <p className="mt-1 font-mono text-xs text-muted-foreground">{item.created_at}</p>
                  </div>
                  <div className="flex shrink-0 flex-wrap gap-2">
                    <button onClick={() => updateFeedbackStatus(item, "reviewed")} className="rounded-xl border border-border px-3 py-2 text-xs font-semibold">Reviewed</button>
                    <button onClick={() => updateFeedbackStatus(item, "resolved")} className="rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground">Resolved</button>
                  </div>
                </div>
              </div>
            )) : (
              <p className="rounded-2xl border border-dashed border-border bg-secondary/30 px-4 py-8 text-center text-sm text-muted-foreground">Belum ada feedback.</p>
            )}
          </div>
        </div>
      ) : null}

      {activeTab === "questions" ? (
        <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h2 className="font-serif text-2xl font-bold">{questionForm.id ? `Edit soal #${questionForm.id}` : "Tambah soal"}</h2>
              <button onClick={resetQuestion} className="inline-flex items-center gap-2 rounded-xl border border-border px-3 py-2 text-sm font-semibold"><Plus className="h-4 w-4" /> Baru</button>
            </div>
            <div className="mt-5 space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <input value={questionForm.section} onChange={(e) => setQuestionForm({ ...questionForm, section: e.target.value })} className="rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="TWK" />
                <input value={questionForm.year || ""} onChange={(e) => setQuestionForm({ ...questionForm, year: Number(e.target.value) })} className="rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="2026" />
                <input value={questionForm.difficulty || ""} onChange={(e) => setQuestionForm({ ...questionForm, difficulty: e.target.value })} className="rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="sedang" />
              </div>
              <input value={questionForm.topic} onChange={(e) => setQuestionForm({ ...questionForm, topic: e.target.value })} className="w-full rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Topic" />
              <textarea value={questionForm.question_text} onChange={(e) => setQuestionForm({ ...questionForm, question_text: e.target.value })} className="min-h-28 w-full rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Teks soal" />
              <textarea value={optionsText} onChange={(e) => setOptionsText(e.target.value)} className="min-h-36 w-full rounded-xl border border-border bg-background px-3 py-2 font-mono text-sm" placeholder="Opsi, satu baris per jawaban" />
              <input value={questionForm.correct_answer ?? ""} onChange={(e) => setQuestionForm({ ...questionForm, correct_answer: e.target.value === "" ? null : Number(e.target.value) })} className="w-full rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Index jawaban benar: 0-4" />
              <textarea value={questionForm.explanation || ""} onChange={(e) => setQuestionForm({ ...questionForm, explanation: e.target.value })} className="min-h-24 w-full rounded-xl border border-border bg-background px-3 py-2 text-sm" placeholder="Pembahasan" />
              <button disabled={saving} onClick={saveQuestion} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground"><Save className="h-4 w-4" /> Simpan soal</button>
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <h2 className="font-serif text-2xl font-bold">Bank soal</h2>
              <div className="flex gap-2">
                <input value={questionSearch} onChange={(e) => setQuestionSearch(e.target.value)} className="h-11 rounded-xl border border-border bg-background px-3 text-sm outline-none" placeholder="Cari soal/topic" />
                <button onClick={loadQuestions} className="rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground">Cari</button>
              </div>
            </div>
            <div className="mt-6 space-y-3">
              {questions.map((q) => (
                <div key={q.id} className="rounded-2xl border border-border bg-secondary/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">#{q.id} · {q.section} · {q.topic}</p>
                      <p className="mt-2 line-clamp-2 text-sm font-medium leading-6">{q.question_text}</p>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => editQuestion(q)} className="rounded-xl border border-border p-2"><Edit3 className="h-4 w-4" /></button>
                      <button onClick={() => deleteQuestion(q)} className="rounded-xl border border-red-200 p-2 text-red-600"><Trash2 className="h-4 w-4" /></button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
