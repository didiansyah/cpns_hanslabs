"use client";

import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import { ArrowRight, BarChart3, BookOpenCheck, Brain, CheckCircle2, Clock3, FileText, Gauge, Layers3, LineChart, Play, ShieldCheck, Sparkles, Trophy, Users } from "lucide-react";

const stats = [
  { value: "10K+", label: "soal siap latihan" },
  { value: "110", label: "soal sekali try out" },
  { value: "12", label: "minggu rencana belajar" },
  { value: "Gratis", label: "untuk mulai" },
];

const productCards = [
  { icon: BookOpenCheck, title: "Latihan TWK, TIU, TKP", desc: "Kerjakan soal per kategori, cek kunci jawaban, lalu baca pembahasan tanpa harus pindah tempat." },
  { icon: Gauge, title: "Try out seperti tes asli", desc: "Satu paket berisi 110 soal dengan timer, skor otomatis, dan batas passing grade SKD." },
  { icon: LineChart, title: "Progress yang kebaca", desc: "Lihat skor terbaik, jumlah try out, streak belajar, dan checklist harian kamu." },
  { icon: Layers3, title: "Belajar lebih terarah", desc: "Mulai dari latihan ringan, lanjut try out rutin, lalu evaluasi bagian yang masih lemah." },
];

const workflow = [
  { step: "01", title: "Daftar sebentar", desc: "Buat akun, verifikasi email, lalu langsung masuk ke dashboard belajar." },
  { step: "02", title: "Latihan tiap hari", desc: "Pilih TWK, TIU, atau TKP. Kerjakan beberapa soal dan tandai checklist harian." },
  { step: "03", title: "Ukur dengan try out", desc: "Ambil paket full SKD, lihat hasilnya, lalu ulangi bagian yang masih kurang." },
];

const dashboardRows = [
  { label: "TWK", value: "82", width: "82%" },
  { label: "TIU", value: "91", width: "91%" },
  { label: "TKP", value: "156", width: "88%" },
];

const trust = ["Gratis mulai belajar", "Progress tersimpan", "Bisa dipakai di HP", "Try out bisa diulang"];

function LogoMark() {
  return (
    <span className="inline-flex items-center gap-3">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground font-black tracking-tight">B</span>
      <span className="leading-none">
        <span className="block text-[10px] font-semibold uppercase tracking-[0.24em] text-muted-foreground">Belajar</span>
        <span className="block text-base font-bold tracking-tight">CPNS</span>
      </span>
    </span>
  );
}

export default function LandingPage() {
  const { user, loading } = useAuth();
  const isLoggedIn = Boolean(user);
  const primaryHref = isLoggedIn ? "/dashboard" : "/register";
  const primaryLabel = isLoggedIn ? "Ke Dashboard" : "Mulai Gratis";
  const heroPrimaryLabel = isLoggedIn ? "Lanjut ke dashboard" : "Mulai latihan gratis";

  return (
    <div className="min-h-screen overflow-hidden bg-card text-card-foreground">
      <nav className="sticky top-0 z-50 border-b border-border bg-card/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 md:px-6">
          <Link href="/" className="transition-opacity hover:opacity-70" aria-label="Belajar CPNS home">
            <LogoMark />
          </Link>
          <div className="hidden items-center gap-8 text-sm font-medium text-muted-foreground lg:flex">
            <a href="#produk" className="hover:text-foreground transition-colors">Fitur</a>
            <a href="#workflow" className="hover:text-foreground transition-colors">Cara belajar</a>
            <a href="#analitik" className="hover:text-foreground transition-colors">Progress</a>
            <a href="#faq" className="hover:text-foreground transition-colors">FAQ</a>
          </div>
          <div className="flex items-center gap-2 md:gap-3">
            <ThemeToggle />
            {!loading && !isLoggedIn ? (
              <Link href="/login" className="hidden sm:block"><Button variant="outline" size="sm" className="rounded-full">Masuk</Button></Link>
            ) : null}
            <Link href={primaryHref}><Button size="sm" className="rounded-full">{primaryLabel}</Button></Link>
          </div>
        </div>
      </nav>

      <main>
        <section className="relative border-b border-border">
          <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-[size:72px_72px] opacity-35" />
          <div className="absolute inset-x-0 top-0 -z-10 h-64 bg-gradient-to-b from-secondary to-transparent" />
          <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 py-16 md:px-6 md:py-24 lg:grid-cols-[1.03fr_0.97fr] lg:py-28">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground shadow-sm">
                <Sparkles className="h-3.5 w-3.5" /> Latihan SKD CPNS 2026
              </div>
              <h1 className="mt-7 max-w-4xl text-5xl font-black leading-[0.95] tracking-[-0.06em] md:text-7xl lg:text-8xl">
                Belajar SKD lebih rapi, dari latihan sampai try out.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-muted-foreground md:text-lg">
                Semua kebutuhan latihan CPNS ada di satu tempat: soal TWK, TIU, TKP, try out full SKD, pembahasan, dan catatan progress harian.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link href={primaryHref}>
                  <Button size="lg" className="w-full rounded-full px-7 sm:w-auto">
                    {heroPrimaryLabel} <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <a href="#produk">
                  <Button size="lg" variant="outline" className="w-full rounded-full px-7 sm:w-auto">
                    Lihat isi platform <Play className="ml-2 h-4 w-4" />
                  </Button>
                </a>
              </div>
              <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium text-muted-foreground">
                {trust.map((item) => (
                  <span key={item} className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5" /> {item}
                  </span>
                ))}
              </div>
            </div>

            <div id="analitik" className="relative">
              <div className="absolute -inset-6 -z-10 rounded-[2.5rem] bg-primary/20 blur-3xl" />
              <div className="rounded-[2rem] border border-border bg-card p-2 shadow-2xl shadow-foreground/10">
                <div className="relative overflow-hidden rounded-[1.55rem] border border-primary/20 bg-[radial-gradient(circle_at_18%_10%,rgba(255,255,255,0.42),transparent_24%),linear-gradient(135deg,#f6821f_0%,#ff8a1f_48%,#de6812_100%)] p-4 text-primary-foreground sm:p-5">
                  <div className="absolute right-0 top-0 h-44 w-44 rounded-full bg-white/15 blur-3xl" />
                  <div className="relative flex items-center justify-between border-b border-primary-foreground/20 pb-4">
                    <div className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full bg-white/85 shadow-sm" />
                      <span className="h-3 w-3 rounded-full bg-white/45" />
                      <span className="h-3 w-3 rounded-full bg-white/25" />
                    </div>
                    <span className="rounded-full border border-primary-foreground/25 bg-black/10 px-3 py-1 text-xs font-medium text-primary-foreground/85 backdrop-blur">Contoh progress</span>
                  </div>

                  <div className="relative grid gap-3 py-5 sm:grid-cols-3">
                    {stats.slice(0, 3).map((stat) => (
                      <div key={stat.label} className="rounded-2xl border border-black/10 bg-white/92 p-4 text-[#111111] shadow-sm backdrop-blur">
                        <div className="text-2xl font-black tracking-tight">{stat.value}</div>
                        <div className="mt-2 max-w-24 text-[11px] font-semibold uppercase leading-5 tracking-[0.16em] text-[#5f574f]">{stat.label}</div>
                      </div>
                    ))}
                  </div>

                  <div className="relative rounded-3xl border border-black/10 bg-white/95 p-5 text-[#111111] shadow-sm backdrop-blur">
                    <div className="mb-5 flex items-start justify-between gap-4">
                      <div>
                        <p className="text-base font-bold tracking-tight">Skor try out terakhir</p>
                        <p className="mt-1 text-sm text-[#5f574f]">Dibandingkan target passing grade.</p>
                      </div>
                      <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#fff0e5] text-[#c76a16]">
                        <Trophy className="h-5 w-5" />
                      </span>
                    </div>
                    <div className="space-y-4">
                      {dashboardRows.map((row) => (
                        <div key={row.label}>
                          <div className="mb-2 flex justify-between text-sm">
                            <span className="font-medium text-[#5f574f]">{row.label}</span>
                            <span className="font-mono font-bold">{row.value}</span>
                          </div>
                          <div className="h-2.5 overflow-hidden rounded-full bg-[#241710]">
                            <div className="h-full rounded-full bg-[#f6821f]" style={{ width: row.width }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="relative mt-4 grid gap-4 sm:grid-cols-[0.82fr_1.18fr]">
                    <div className="rounded-3xl border border-black/10 bg-white/95 p-5 text-[#111111] shadow-sm backdrop-blur">
                      <Clock3 className="mb-7 h-5 w-5 text-[#c76a16]" />
                      <div className="text-5xl font-black tracking-[-0.06em]">12</div>
                      <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#5f574f]">minggu belajar</p>
                    </div>
                    <div className="rounded-3xl border border-black/10 bg-white p-5 text-[#111111] shadow-sm">
                      <p className="text-base font-bold tracking-tight">Target hari ini</p>
                      <div className="mt-4 space-y-3 text-sm">
                        {[
                          "Latihan TIU 20 soal",
                          "Baca pembahasan TKP",
                          "Coba Try Out Part 1",
                        ].map((item) => (
                          <div key={item} className="flex items-center gap-3 rounded-2xl bg-[#6d625b] px-3 py-2 text-white">
                            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#f6821f] text-white"><CheckCircle2 className="h-3.5 w-3.5" /></span>
                            <span className="font-medium">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-border bg-secondary/40">
          <div className="mx-auto grid max-w-7xl grid-cols-2 gap-px border-x border-border bg-border md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="bg-card px-6 py-8">
                <div className="text-3xl font-black tracking-tight md:text-4xl">{stat.value}</div>
                <div className="mt-2 text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </section>

        <section id="produk" className="mx-auto max-w-7xl px-4 py-20 md:px-6 md:py-28">
          <div className="mb-12 grid gap-6 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.28em] text-muted-foreground">Fitur</p>
              <h2 className="mt-4 text-4xl font-black tracking-[-0.04em] md:text-6xl">Yang kamu butuhkan buat latihan SKD.</h2>
            </div>
            <p className="max-w-2xl text-base leading-8 text-muted-foreground lg:ml-auto">
              Bukan cuma kumpulan soal. Kamu bisa latihan per materi, ambil try out full SKD, lalu lihat bagian mana yang perlu dikejar lagi.
            </p>
          </div>

          <div className="grid gap-px overflow-hidden rounded-[2rem] border border-border bg-border md:grid-cols-2 lg:grid-cols-4">
            {productCards.map((feature) => (
              <div key={feature.title} className="group bg-card p-7 transition-colors hover:bg-secondary/60">
                <div className="mb-8 flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-card transition-transform group-hover:-translate-y-1">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-bold tracking-tight">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="workflow" className="border-y border-border bg-primary text-primary-foreground">
          <div className="mx-auto max-w-7xl px-4 py-20 md:px-6 md:py-28">
            <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr]">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.28em] text-primary-foreground/60">Cara belajar</p>
                <h2 className="mt-4 text-4xl font-black tracking-[-0.04em] md:text-6xl">Mulai pelan, ukur hasil, ulangi yang lemah.</h2>
                <p className="mt-5 leading-8 text-primary-foreground/65">Alurnya sengaja sederhana: latihan dulu, coba try out, lalu pakai hasilnya untuk menentukan latihan berikutnya.</p>
              </div>
              <div className="space-y-4">
                {workflow.map((item) => (
                  <div key={item.step} className="rounded-3xl border border-primary-foreground/20 bg-primary-foreground/10 p-6">
                    <div className="flex gap-5">
                      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-card text-sm font-black text-foreground">{item.step}</span>
                      <div>
                        <h3 className="font-bold">{item.title}</h3>
                        <p className="mt-2 text-sm leading-7 text-primary-foreground/65">{item.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-20 md:px-6 md:py-28">
          <div className="grid overflow-hidden rounded-[2rem] border border-border lg:grid-cols-2">
            <div className="p-8 md:p-12">
              <p className="text-xs font-bold uppercase tracking-[0.28em] text-muted-foreground">Untuk yang mau konsisten</p>
              <h2 className="mt-4 text-4xl font-black tracking-[-0.04em] md:text-5xl">Fokus ke latihan yang benar-benar kepakai.</h2>
              <p className="mt-5 leading-8 text-muted-foreground">Setiap angka dibuat mudah dibaca: skor terakhir, target passing grade, riwayat try out, dan checklist harian.</p>
              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                {[
                  { icon: Brain, text: "Pembahasan ringkas" },
                  { icon: Users, text: "Leaderboard anonim" },
                  { icon: FileText, text: "Riwayat try out" },
                  { icon: BarChart3, text: "Catatan per kategori" },
                ].map((item) => (
                  <div key={item.text} className="flex items-center gap-3 rounded-2xl border border-border p-4 text-sm font-medium">
                    <item.icon className="h-5 w-5 text-muted-foreground" /> {item.text}
                  </div>
                ))}
              </div>
            </div>
            <div className="border-t border-border bg-secondary/60 p-8 md:p-12 lg:border-l lg:border-t-0">
              <div className="rounded-3xl border border-border bg-card p-6 shadow-xl shadow-foreground/5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-bold">Kesiapan SKD</p>
                    <p className="text-xs text-muted-foreground">Gambaran dari skor latihan</p>
                  </div>
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div className="mt-8 text-7xl font-black tracking-[-0.08em]">86%</div>
                <div className="mt-6 h-3 rounded-full bg-secondary">
                  <div className="h-full w-[86%] rounded-full bg-primary" />
                </div>
                <div className="mt-8 space-y-3">
                  {["TWK sudah lewat target", "TIU masih perlu latihan pola", "TKP mulai stabil"].map((text) => (
                    <div key={text} className="flex items-center justify-between rounded-2xl border border-border px-4 py-3 text-sm">
                      <span>{text}</span>
                      <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="faq" className="border-t border-border bg-secondary/40">
          <div className="mx-auto max-w-7xl px-4 py-20 md:px-6">
            <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.28em] text-muted-foreground">FAQ</p>
                <h2 className="mt-4 text-4xl font-black tracking-[-0.04em] md:text-5xl">Pertanyaan yang sering muncul.</h2>
              </div>
              <div className="divide-y divide-border rounded-[2rem] border border-border bg-card">
                {[
                  ["Apakah harus bayar?", "Tidak. Kamu bisa daftar dan mulai latihan tanpa biaya."],
                  ["Try out-nya isinya apa?", "Satu paket berisi TWK, TIU, dan TKP dengan timer serta skor otomatis."],
                  ["Bisa lanjut dari HP?", "Bisa. Dashboard, latihan, dan try out dibuat nyaman dipakai di layar kecil."],
                ].map(([q, a]) => (
                  <div key={q} className="p-6">
                    <h3 className="font-bold">{q}</h3>
                    <p className="mt-2 text-sm leading-7 text-muted-foreground">{a}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-primary px-4 py-20 text-primary-foreground md:px-6 md:py-28">
          <div className="mx-auto max-w-5xl text-center">
            <h2 className="text-4xl font-black tracking-[-0.05em] md:text-7xl">Siap mulai latihan hari ini?</h2>
            <p className="mx-auto mt-5 max-w-2xl leading-8 text-primary-foreground/65">Daftar gratis, kerjakan beberapa soal, lalu simpan progress kamu dari hari pertama.</p>
            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Link href={primaryHref}><Button size="lg" variant="secondary" className="w-full rounded-full px-8 sm:w-auto">{isLoggedIn ? "Kembali ke dashboard" : "Daftar gratis"}</Button></Link>
              {!loading && !isLoggedIn ? (
                <Link href="/login"><Button size="lg" variant="outline" className="w-full rounded-full border-background/30 bg-transparent px-8 text-primary-foreground hover:bg-primary-foreground hover:text-foreground sm:w-auto">Masuk</Button></Link>
              ) : null}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 md:flex-row md:items-center md:justify-between md:px-6">
          <LogoMark />
          <div className="flex flex-wrap gap-5 text-sm text-muted-foreground">
            <a href="#produk" className="hover:text-foreground">Fitur</a>
            <a href="#workflow" className="hover:text-foreground">Cara belajar</a>
            <a href="#faq" className="hover:text-foreground">FAQ</a>
          </div>
          <p className="text-sm text-muted-foreground">
            © 2026 Belajar CPNS. by{" "}
            <a href="https://x.com/didihansya" target="_blank" rel="noreferrer" className="font-medium text-foreground underline-offset-4 hover:underline">
              @didihansya
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
