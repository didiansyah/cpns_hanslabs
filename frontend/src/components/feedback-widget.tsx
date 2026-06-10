"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { X } from "lucide-react";
import { apiPost } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";

const categories = [
  { key: "bug", label: "Bug / error" },
  { key: "question", label: "Soal salah" },
  { key: "feature", label: "Saran fitur" },
  { key: "donation", label: "Donasi" },
  { key: "other", label: "Lainnya" },
];

const hiddenOnPaths = ["/dashboard/questions", "/dashboard/simulations"];

export function FeedbackWidget() {
  const pathname = usePathname();
  const hidden = hiddenOnPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState("bug");
  const [rating, setRating] = useState(5);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (open) trackEvent("feedback_open", { path: window.location.pathname });
  }, [open]);

  useEffect(() => {
    if (hidden && open) setOpen(false);
  }, [hidden, open]);

  const submit = async () => {
    if (!message.trim()) {
      setNotice("Tulis feedback dulu ya.");
      return;
    }
    setSaving(true);
    const res = await apiPost("/feedback", {
      category,
      rating,
      message: message.trim(),
      path: window.location.pathname,
    });
    setSaving(false);
    if (res.ok) {
      trackEvent("feedback_submit", { category, rating, feedback_id: res.data?.id });
      setNotice("Makasih, feedback sudah masuk.");
      setMessage("");
      setTimeout(() => {
        setOpen(false);
        setNotice("");
      }, 1200);
    } else {
      setNotice(res.error || "Gagal kirim feedback.");
    }
  };

  if (hidden) return null;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed right-0 top-1/2 z-[70] flex h-36 w-12 -translate-y-1/2 items-center justify-center rounded-l-xl bg-black text-white shadow-2xl shadow-black/25 transition-transform hover:-translate-x-1 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 dark:bg-white dark:text-black dark:focus:ring-white"
        aria-label="Buka feedback"
      >
        <span className="-rotate-90 whitespace-nowrap text-lg font-medium tracking-wide">Feedback</span>
      </button>

      {open ? (
        <div className="fixed inset-0 z-[120] bg-black/35 backdrop-blur-[2px]" role="dialog" aria-modal="true">
          <div className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-border bg-card shadow-2xl">
            <div className="flex items-start justify-between gap-4 border-b border-border px-6 py-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-muted-foreground">Feedback</p>
                <h2 className="mt-2 font-serif text-2xl font-bold tracking-tight">Bantu kami perbaiki platform</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">Laporkan bug, soal yang salah, atau ide fitur. Halaman saat ini ikut tersimpan otomatis.</p>
              </div>
              <button onClick={() => setOpen(false)} className="rounded-full border border-border p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground" aria-label="Tutup feedback">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 space-y-5 overflow-y-auto p-6">
              <div>
                <label className="text-sm font-semibold">Kategori</label>
                <div className="mt-3 grid grid-cols-2 gap-2">
                  {categories.map((item) => (
                    <button
                      key={item.key}
                      type="button"
                      onClick={() => setCategory(item.key)}
                      className={`rounded-2xl border px-3 py-2 text-left text-sm font-semibold transition-colors ${category === item.key ? "border-primary bg-primary text-primary-foreground" : "border-border bg-secondary/45 hover:bg-secondary"}`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold">Rating pengalaman</label>
                <div className="mt-3 flex gap-2">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setRating(n)}
                      className={`flex h-10 w-10 items-center justify-center rounded-xl border font-mono text-sm font-bold transition-colors ${rating === n ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background hover:bg-secondary"}`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold">Pesan</label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  className="mt-3 min-h-36 w-full rounded-2xl border border-border bg-background px-4 py-3 text-sm leading-6 outline-none focus:border-primary"
                  placeholder="Contoh: Di halaman try out, tombol submit tidak bisa diklik setelah soal nomor 10..."
                />
              </div>

              <div className="rounded-2xl border border-dashed border-border bg-secondary/40 px-4 py-3 text-xs leading-5 text-muted-foreground">
                Path: <span className="font-mono text-foreground">{typeof window !== "undefined" ? window.location.pathname : "-"}</span>
              </div>

              {notice ? <p className="rounded-2xl border border-border bg-secondary px-4 py-3 text-sm text-muted-foreground">{notice}</p> : null}
            </div>

            <div className="border-t border-border p-6">
              <button
                type="button"
                disabled={saving}
                onClick={submit}
                className="w-full rounded-2xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/25 transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-60"
              >
                {saving ? "Mengirim..." : "Kirim feedback"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
