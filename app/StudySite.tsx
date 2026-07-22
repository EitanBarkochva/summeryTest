"use client";

import { useMemo, useState } from "react";
import content from "./studyContent.json";

type StudyBlock =
  | { type: "paragraph"; text: string }
  | { type: "image-row"; images: string[] };

type StudySection = {
  id: string;
  title: string;
  blocks: StudyBlock[];
};

const sections = content.sections as StudySection[];

function normalize(value: string) {
  return value.toLocaleLowerCase("he-IL").trim();
}

function sectionText(section: StudySection) {
  return [
    section.title,
    ...section.blocks.map((block) =>
      block.type === "paragraph" ? block.text : "",
    ),
  ].join(" ");
}

export function StudySite() {
  const [query, setQuery] = useState("");
  const [activeId, setActiveId] = useState(sections[0]?.id ?? "");
  const [dense, setDense] = useState(false);

  const filteredSections = useMemo(() => {
    const q = normalize(query);
    if (!q) return sections;
    return sections.filter((section) => normalize(sectionText(section)).includes(q));
  }, [query]);

  const activeSection =
    filteredSections.find((section) => section.id === activeId) ??
    filteredSections[0] ??
    sections[0];

  return (
    <main className="study-shell" dir="rtl">
      <aside className="topic-rail" aria-label="רשימת נושאים">
        <div className="rail-brand">
          <span className="brand-mark">נו</span>
          <div>
            <p>נוירוביולוגיה</p>
            <strong>סיכום למבחן</strong>
          </div>
        </div>

        <label className="search-box">
          <span>חיפוש בחומר</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="לדוגמה: אמיגדלה, זיכרון עבודה..."
          />
        </label>

        <div className="rail-stats" aria-label="נתוני המסמך">
          <span>{content.stats.sections} נושאים</span>
          <span>{content.stats.images} תמונות</span>
          <span>{content.stats.paragraphs} פסקאות</span>
        </div>

        <nav className="topic-list">
          {filteredSections.map((section, index) => (
            <button
              className={section.id === activeSection?.id ? "active" : ""}
              key={section.id}
              onClick={() => setActiveId(section.id)}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              {section.title}
            </button>
          ))}
        </nav>
      </aside>

      <section className="study-main">
        <header className="hero-panel">
          <div>
            <p className="eyebrow">כל החומר מתוך הקובץ</p>
            <h1>{content.title}</h1>
            <p>
              אתר קריאה מסודר לפי נושאים, עם התמונות המקוריות, חיפוש מהיר
              ופריסה שמתאימה למסך מחשב, אייפד וטלפון.
            </p>
          </div>
          <div className="hero-actions" aria-label="אפשרויות תצוגה">
            <button
              className={!dense ? "selected" : ""}
              onClick={() => setDense(false)}
            >
              קריאה נוחה
            </button>
            <button
              className={dense ? "selected" : ""}
              onClick={() => setDense(true)}
            >
              צפוף לחזרה
            </button>
          </div>
        </header>

        <div className="mobile-topic-strip" aria-label="נושאים">
          {filteredSections.map((section, index) => (
            <button
              className={section.id === activeSection?.id ? "active" : ""}
              key={section.id}
              onClick={() => setActiveId(section.id)}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {activeSection ? (
          <article className={dense ? "study-card dense" : "study-card"}>
            <div className="section-kicker">
              נושא {sections.findIndex((section) => section.id === activeSection.id) + 1}
            </div>
            <h2>{activeSection.title}</h2>

            <div className="content-flow">
              {activeSection.blocks.map((block, index) =>
                block.type === "paragraph" ? (
                  <p key={`${activeSection.id}-p-${index}`}>{block.text}</p>
                ) : (
                  <div className="image-grid" key={`${activeSection.id}-i-${index}`}>
                    {block.images.map((image, imageIndex) => (
                      <figure key={`${image}-${imageIndex}`}>
                        <img
                          alt={`תמונה מתוך הסיכום: ${activeSection.title}`}
                          loading="lazy"
                          src={image}
                        />
                      </figure>
                    ))}
                  </div>
                ),
              )}
            </div>
          </article>
        ) : (
          <article className="empty-state">
            <h2>לא נמצאו תוצאות</h2>
            <p>כדאי לנסות מילת חיפוש קצרה יותר או מושג אחר מהחומר.</p>
          </article>
        )}

        <section className="all-topics" aria-label="כל הנושאים">
          <h2>מפת נושאים מלאה</h2>
          <div>
            {filteredSections.map((section, index) => (
              <button key={section.id} onClick={() => setActiveId(section.id)}>
                <span>{index + 1}</span>
                {section.title}
              </button>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
