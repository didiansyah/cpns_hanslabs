"use client";
import { useEffect, useMemo, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { trackEvent } from "@/lib/analytics";
import { FeedbackWidget } from "@/components/feedback-widget";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarTrigger,
  SidebarInset,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  LayoutDashboard,
  BookOpen,
  Brain,
  Settings,
  LogOut,
  Trophy,
  GraduationCap,
  ChevronUp,
  ChevronRight,
  Heart,
  Coffee,
  Utensils,
  BookMarked,
  X,
  Minus,
  Plus,
  Building2,
  Wallet,
  ShieldCheck,
  BarChart3,
  Users,
  MessageSquare,
} from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/simulations", label: "Try Out", icon: Brain },
  { href: "/dashboard/questions", label: "Latihan", icon: BookOpen },
  { href: "/dashboard/leaderboard", label: "Leaderboard", icon: Trophy },
  { href: "/dashboard/settings", label: "Pengaturan", icon: Settings },
];

const adminNav = [
  { href: "/dashboard/superadmin", label: "Overview", icon: ShieldCheck },
  { href: "/dashboard/superadmin/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/superadmin/users", label: "User", icon: Users },
  { href: "/dashboard/superadmin/questions", label: "Soal", icon: BookOpen },
  { href: "/dashboard/superadmin/feedback", label: "Feedback", icon: MessageSquare },
];
const allNav = [...nav, ...adminNav];

const donationItems = [
  { key: "kopi", label: "Traktir Kopi", price: "Rp10.000", amount: 10000, icon: Coffee },
  { key: "nasi", label: "Traktir Nasi", price: "Rp25.000", amount: 25000, icon: Utensils },
  { key: "soal", label: "Bantu tambah soal", price: "Rp50.000", amount: 50000, icon: BookMarked },
];

const donorSeeds = [
  { name: "H***", item: "Traktir Kopi", qty: 1 },
  { name: "A***", item: "Traktir Nasi", qty: 1 },
  { name: "R***", item: "Bantu tambah soal", qty: 2 },
  { name: "D***", item: "Traktir Kopi", qty: 3 },
  { name: "M***", item: "Traktir Nasi", qty: 1 },
  { name: "S***", item: "Traktir Kopi", qty: 2 },
  { name: "F***", item: "Bantu tambah soal", qty: 1 },
  { name: "N***", item: "Traktir Kopi", qty: 1 },
];

const paymentMethods = [
  {
    category: "Bank",
    icon: Building2,
    items: [
      { name: "BCA", account: "8430467701", holder: "Didi Khodriansyah" },
      { name: "Bank Jago", account: "502118255420", holder: "Didi Khodriansyah" },
    ],
  },
  {
    category: "E-Wallet",
    icon: Wallet,
    items: [
      { name: "Gopay / ShopeePay", account: "081377355408", holder: "Didi Khodriansyah" },
    ],
  },
];

function DonationModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [qty, setQty] = useState<Record<string, number>>({ kopi: 1, nasi: 0, soal: 0 });
  const [submitted, setSubmitted] = useState(false);
  const total = donationItems.reduce((sum, item) => sum + (qty[item.key] || 0) * item.amount, 0);
  const totalLabel = new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(total);
  const feed = useMemo(() => {
    const offset = new Date().getMinutes() % donorSeeds.length;
    return donorSeeds.map((_, index) => {
      const donor = donorSeeds[(index + offset) % donorSeeds.length];
      return { ...donor, time: `${index * 2 + 2} jam lalu` };
    }).slice(0, 5);
  }, []);

  useEffect(() => {
    if (open) trackEvent("donation_modal_open", { initial_total: total });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const submitDonation = () => {
    setSubmitted(true);
    trackEvent("donation_submit", {
      total,
      kopi: qty.kopi || 0,
      nasi: qty.nasi || 0,
      soal: qty.soal || 0,
    });
  };

  if (!open) return null;

  const changeQty = (key: string, delta: number) => {
    setSubmitted(false);
    setQty((current) => ({ ...current, [key]: Math.max(0, Math.min(9, (current[key] || 0) + delta)) }));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] border border-border bg-card shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-border px-6 py-5">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-primary">Donasi manual</p>
            <h2 className="mt-2 font-serif text-2xl font-bold tracking-tight">Bantu platform ini lebih baik</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Pilih nominal sesuai item di bawah, lalu transfer manual ke salah satu rekening atau e-wallet. Belum ada payment gateway, jadi ini hanya panduan donasi.</p>
          </div>
          <button onClick={onClose} className="rounded-full border border-border p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground" aria-label="Tutup modal donasi">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="grid gap-6 p-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="space-y-4">
            <div className="rounded-3xl border border-border bg-secondary/40 p-5">
              <div className="mb-4">
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-muted-foreground">Metode donasi</p>
                <h3 className="mt-2 font-serif text-xl font-bold tracking-tight">Transfer manual</h3>
              </div>
              <div className="space-y-4">
                {paymentMethods.map((group) => (
                  <div key={group.category} className="rounded-2xl border border-border bg-card p-4 shadow-sm">
                    <div className="mb-3 flex items-center gap-2">
                      <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <group.icon className="h-4 w-4" />
                      </span>
                      <p className="font-semibold">{group.category}</p>
                    </div>
                    <div className="space-y-3">
                      {group.items.map((method) => (
                        <div key={`${group.category}-${method.name}`} className="rounded-xl border border-border bg-secondary/35 p-3">
                          <p className="text-sm font-semibold text-foreground">{method.name}</p>
                          <p className="mt-1 font-mono text-lg font-bold tracking-tight">{method.account}</p>
                          <p className="mt-1 text-xs text-muted-foreground">a.n {method.holder}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <p className="rounded-2xl border border-dashed border-primary/35 bg-primary/5 px-4 py-3 text-sm leading-6 text-muted-foreground">Setelah transfer, gunakan nominal sesuai pilihan. Nama pada daftar dukungan dibuat anonim supaya tetap nyaman.</p>
          </div>

          <div className="space-y-5">
            <div className="space-y-3">
              {donationItems.map((item) => (
                <div key={item.key} className="rounded-2xl border border-border bg-card p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <item.icon className="h-5 w-5" />
                      </span>
                      <div>
                        <p className="font-semibold">{item.label}</p>
                        <p className="text-xs text-muted-foreground">{item.price} per item</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => changeQty(item.key, -1)} className="rounded-full border border-border p-2 hover:bg-secondary" aria-label={`Kurangi ${item.label}`}>
                        <Minus className="h-4 w-4" />
                      </button>
                      <span className="w-8 text-center font-mono font-bold">{qty[item.key] || 0}</span>
                      <button onClick={() => changeQty(item.key, 1)} className="rounded-full border border-border p-2 hover:bg-secondary" aria-label={`Tambah ${item.label}`}>
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="rounded-3xl border border-primary/20 bg-primary/5 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Total pilihan</p>
                  <p className="mt-1 font-mono text-2xl font-bold">{totalLabel}</p>
                </div>
                <button
                  type="button"
                  disabled={total === 0}
                  onClick={submitDonation}
                  className="rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/25 transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-45"
                >
                  Submit donasi
                </button>
              </div>
              {submitted ? (
                <p className="mt-3 rounded-2xl border border-primary/25 bg-card px-4 py-3 text-sm leading-6 text-muted-foreground">
                  Makasih bro. Setelah transfer manual, nominal <span className="font-semibold text-foreground">{totalLabel}</span> akan dicek manual.
                </p>
              ) : (
                <p className="mt-3 text-sm leading-6 text-muted-foreground">Klik submit setelah memilih item dan transfer, supaya alurnya jelas walau pembayaran masih manual.</p>
              )}
            </div>

            <div className="rounded-3xl border border-border bg-secondary/35 p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="font-serif text-lg font-bold">Dukungan terbaru</h3>
                  <p className="text-xs text-muted-foreground">Contoh display anonim, datanya berganti supaya tidak monoton.</p>
                </div>
                <Heart className="h-5 w-5 text-primary" />
              </div>
              <div className="space-y-2">
                {feed.map((donor, index) => (
                  <div key={`${donor.name}-${index}`} className="grid grid-cols-[76px_1fr] gap-3 rounded-2xl border border-border bg-card px-4 py-3 text-sm">
                    <span className="text-xs text-muted-foreground">{donor.time}</span>
                    <div>
                      <p className="font-semibold">{donor.name}</p>
                      <p className="text-muted-foreground">{donor.item} x{donor.qty}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Breadcrumb() {
  const pathname = usePathname();
  const current = [...allNav].sort((a, b) => b.href.length - a.href.length).find((n) =>
    n.href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(n.href)
  );
  if (!current || pathname === "/dashboard") return null;
  return (
    <div className="flex items-center gap-1.5 text-sm">
      <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
        Dashboard
      </Link>
      <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
      <span className="font-medium">{current.label}</span>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout, loading } = useAuth();
  const [donationOpen, setDonationOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-card">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Memuat...</p>
      </div>
    </div>
  );
  if (!user) return null;

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    if (href === "/dashboard/superadmin") return pathname === href;
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  return (
    <SidebarProvider>
      <Sidebar variant="inset" className="bg-sidebar">
        <SidebarHeader className="border-b border-sidebar-border/70 pb-3">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" render={<Link href="/dashboard" />}>
                <div className="flex aspect-square size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/30">
                  <GraduationCap className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold" style={{ fontFamily: "Georgia, serif" }}>
                    Belajar CPNS
                  </span>
                  <span className="truncate text-xs text-sidebar-foreground/70">2026</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent className="py-3">
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {nav.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton render={<Link href={item.href} />} isActive={isActive(item.href)} className="h-10 rounded-xl data-active:bg-primary data-active:text-primary-foreground data-active:shadow-sm data-active:shadow-primary/30">
                        <item.icon />
                        <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {user.is_superadmin ? (
            <SidebarGroup>
              <SidebarGroupLabel className="px-2 text-[0.68rem] font-bold uppercase tracking-[0.18em] text-sidebar-foreground/55">
                Super Admin
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {adminNav.map((item) => (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton render={<Link href={item.href} />} isActive={isActive(item.href)} className="h-10 rounded-xl data-active:bg-primary data-active:text-primary-foreground data-active:shadow-sm data-active:shadow-primary/30">
                        <item.icon />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ) : null}

          <div className="mx-2 mt-4 rounded-2xl border border-sidebar-border/70 bg-sidebar-accent/70 p-3">
            <p className="text-xs font-medium leading-5 text-sidebar-foreground/75">Bantu biaya server, soal, dan perawatan platform.</p>
            <button
              type="button"
              onClick={() => {
                trackEvent("donation_cta_click", { source: "sidebar" });
                setDonationOpen(true);
              }}
              className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-3 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/25 transition-colors hover:bg-accent"
            >
              <Heart className="h-4 w-4" />
              Bantu platform ini lebih baik
            </button>
          </div>
        </SidebarContent>

        <SidebarFooter className="border-t border-sidebar-border/70 pt-3">
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger
                  className="flex items-center gap-2 w-full px-2 py-2 rounded-lg hover:bg-sidebar-accent data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                >
                  <Avatar className="h-8 w-8 rounded-xl">
                    <AvatarFallback className="rounded-xl bg-primary text-primary-foreground">
                      {user.name[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">{user.name}</span>
                    <span className="truncate text-xs text-sidebar-foreground/65">{user.email}</span>
                  </div>
                  <ChevronUp className="ml-auto size-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  side="top"
                  className="w-[--radix-dropdown-menu-trigger-width]"
                >
                  <DropdownMenuItem onClick={() => { logout(); router.push("/"); }}>
                    <LogOut />
                    Keluar
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-border/70 bg-card/90 px-4 backdrop-blur-xl lg:px-6">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex-1">
            <Breadcrumb />
          </div>
          <ThemeToggle />
        </header>
        <main className="cf-grid-bg flex-1 p-4 lg:p-6">
          {children}
        </main>
      </SidebarInset>
      <DonationModal open={donationOpen} onClose={() => setDonationOpen(false)} />
      <FeedbackWidget />
    </SidebarProvider>
  );
}
