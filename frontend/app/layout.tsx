import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import NavBar from "@/components/nav/NavBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DV Eval Harness",
  description: "Automated evaluation framework for Design Verification agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-50 min-h-screen flex flex-col`}>
        <NavBar />
        <main className="flex-grow">
          {children}
        </main>
        <footer className="py-6 border-t bg-white text-center text-xs text-gray-400">
          © 2026 Anthony Eugene Lewallen: DV Eval Harness — Design Verification Agent Benchmarking
        </footer>
      </body>
    </html>
  );
}
