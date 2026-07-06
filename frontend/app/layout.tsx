import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "POLIS — Collective Intelligence for Complex Decisions",
  description: "Most AI answers. POLIS holds a council. A multi-agent council debates a decision and returns a transparent consensus.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
