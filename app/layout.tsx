import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "סיכום למבחן בנוירוביולוגיה",
  description: "אתר לימוד רספונסיבי עם כל החומר והתמונות מתוך קובץ הסיכום.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="he" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
