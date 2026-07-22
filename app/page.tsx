import type { Metadata } from "next";
import { StudySite } from "./StudySite";

export const metadata: Metadata = {
  title: "סיכום למבחן בנוירוביולוגיה",
  description: "אתר לימוד רספונסיבי עם כל החומר והתמונות מתוך הסיכום.",
};

export default function Home() {
  return <StudySite />;
}
