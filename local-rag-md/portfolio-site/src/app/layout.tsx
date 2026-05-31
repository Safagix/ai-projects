import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "safagix | AI Agent Builder",
  description: "I build agents, apps, and automations that ship to production in days, not months.",
  openGraph: {
    title: "safagix | AI Agent Builder",
    description: "I build agents, apps, and automations that ship to production in days, not months.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-[#050505] text-slate-100">
        <div className="noise" aria-hidden="true" />
        <div className="orb-1" aria-hidden="true" />
        <div className="orb-2" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}
