import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

export const dynamic = "force-dynamic";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OneShot - Multi-Agent AI Platform",
  description:
    "7 AI agents. Two parallel waves. One prompt. Platform-ready social content in seconds.",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
  },
  manifest: "/site.webmanifest",
  openGraph: {
    title: "OneShot - Multi-Agent AI Platform",
    description:
      "7 AI agents. Two parallel waves. One prompt. Platform-ready social content in seconds.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "OneShot - 7 AI agents, two parallel waves, one prompt",
      },
    ],
    type: "website",
    siteName: "OneShot",
  },
  twitter: {
    card: "summary_large_image",
    title: "OneShot - Multi-Agent AI Platform",
    description:
      "7 AI agents. Two parallel waves. One prompt. Platform-ready social content in seconds.",
    images: ["/twitter-card.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const runtimeConfig = {
    apiUrl:
      process.env.RUNTIME_API_URL ??
      process.env.API_BASE_URL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "",
    wsUrl:
      process.env.RUNTIME_WS_URL ??
      process.env.WS_BASE_URL ??
      process.env.NEXT_PUBLIC_WS_URL ??
      "",
  };
  const runtimeConfigScript = `window.__ONESHOT_RUNTIME_CONFIG__=${JSON.stringify(runtimeConfig).replace(/</g, "\\u003c")};`;

  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <script dangerouslySetInnerHTML={{ __html: runtimeConfigScript }} />
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
