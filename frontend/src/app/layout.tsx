import type { Metadata } from "next";
import Script from "next/script";
import { Suspense } from "react";
import { AuthProvider } from "@/lib/auth";
import { RouteAnalytics } from "@/components/route-analytics";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://cpns.hanslabs.xyz"),
  title: "Belajar CPNS Gratis Selamanya!",
  description: "Latihan TWK, TIU, TKP, try out full SKD, passing grade, pembahasan, dan progress harian. Gratis buat mulai belajar CPNS 2026.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "BELAJAR CPNS GRATIS SELAMANYA!",
    description: "Latihan SKD CPNS 2026: TWK, TIU, TKP, try out full SKD, skor otomatis, dan progress harian.",
    url: "https://cpns.hanslabs.xyz",
    siteName: "Belajar CPNS",
    type: "website",
    locale: "id_ID",
    images: [
      {
        url: "/og-cpns-gratis.png",
        width: 1200,
        height: 630,
        alt: "Belajar CPNS Gratis Selamanya",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "BELAJAR CPNS GRATIS SELAMANYA!",
    description: "Latihan TWK, TIU, TKP + try out full SKD + progress harian.",
    images: ["/og-cpns-gratis.png"],
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body>
        <Script
          src="/umami/script.js"
          data-website-id="4f24bfee-341b-4779-82ce-7f6115291a2b"
          data-host-url="/umami"
          strategy="afterInteractive"
        />
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
          <Suspense fallback={null}>
            <RouteAnalytics />
          </Suspense>
        </ThemeProvider>
      </body>
    </html>
  );
}
