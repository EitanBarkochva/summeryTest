from __future__ import annotations

import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "app" / "studyContent.json"
OUT = ROOT / "static-site"


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "public" / "doc-assets", OUT / "doc-assets")

    payload = json.dumps(data, ensure_ascii=False)
    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(data["title"])}</title>
  <style>
{(ROOT / "app" / "globals.css").read_text(encoding="utf-8").replace('@import "tailwindcss";', '')}
  </style>
</head>
<body>
  <main class="study-shell" dir="rtl">
    <aside class="topic-rail" aria-label="רשימת נושאים">
      <div class="rail-brand">
        <span class="brand-mark">נו</span>
        <div><p>נוירוביולוגיה</p><strong>סיכום למבחן</strong></div>
      </div>
      <label class="search-box">
        <span>חיפוש בחומר</span>
        <input id="search" placeholder="לדוגמה: אמיגדלה, זיכרון עבודה...">
      </label>
      <div class="rail-stats">
        <span>{data["stats"]["sections"]} נושאים</span>
        <span>{data["stats"]["images"]} תמונות</span>
        <span>{data["stats"]["paragraphs"]} פסקאות</span>
      </div>
      <nav class="topic-list" id="topicList"></nav>
    </aside>
    <section class="study-main">
      <header class="hero-panel">
        <div>
          <p class="eyebrow">כל החומר מתוך הקובץ</p>
          <h1>{html.escape(data["title"])}</h1>
          <p>אתר קריאה מסודר לפי נושאים, עם התמונות המקוריות, חיפוש מהיר ופריסה שמתאימה למסך מחשב, אייפד וטלפון.</p>
        </div>
        <div class="hero-actions">
          <button id="comfortable" class="selected">קריאה נוחה</button>
          <button id="dense">צפוף לחזרה</button>
        </div>
      </header>
      <div class="mobile-topic-strip" id="mobileTopics"></div>
      <article class="study-card" id="studyCard"></article>
      <section class="all-topics">
        <h2>מפת נושאים מלאה</h2>
        <div id="topicMap"></div>
      </section>
    </section>
  </main>
  <script>
    const content = {payload};
    let query = "";
    let activeId = content.sections[0]?.id || "";
    let isDense = false;

    const normalize = (value) => value.toLocaleLowerCase("he-IL").trim();
    const sectionText = (section) => [
      section.title,
      ...section.blocks.map((block) => block.type === "paragraph" ? block.text : "")
    ].join(" ");
    const filtered = () => {{
      const q = normalize(query);
      if (!q) return content.sections;
      return content.sections.filter((section) => normalize(sectionText(section)).includes(q));
    }};
    const escapeHtml = (value) => value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");

    function setActive(id) {{
      activeId = id;
      render();
      window.scrollTo({{ top: 0, behavior: "smooth" }});
    }}

    function renderTopicButton(section, index, compact = false) {{
      const button = document.createElement("button");
      button.className = section.id === activeId ? "active" : "";
      button.type = "button";
      button.onclick = () => setActive(section.id);
      if (compact) {{
        button.textContent = String(index + 1);
      }} else {{
        button.innerHTML = `<span>${{String(index + 1).padStart(2, "0")}}</span>${{escapeHtml(section.title)}}`;
      }}
      return button;
    }}

    function render() {{
      const sections = filtered();
      const active = sections.find((section) => section.id === activeId) || sections[0];
      if (active) activeId = active.id;

      for (const [id, compact] of [["topicList", false], ["mobileTopics", true], ["topicMap", false]]) {{
        const target = document.getElementById(id);
        target.innerHTML = "";
        sections.forEach((section, index) => target.appendChild(renderTopicButton(section, index, compact)));
      }}

      document.getElementById("comfortable").className = isDense ? "" : "selected";
      document.getElementById("dense").className = isDense ? "selected" : "";
      const card = document.getElementById("studyCard");
      card.className = isDense ? "study-card dense" : "study-card";

      if (!active) {{
        card.innerHTML = "<h2>לא נמצאו תוצאות</h2><p>כדאי לנסות מילת חיפוש קצרה יותר או מושג אחר מהחומר.</p>";
        return;
      }}

      const topicNumber = content.sections.findIndex((section) => section.id === active.id) + 1;
      const blocks = active.blocks.map((block, index) => {{
        if (block.type === "paragraph") return `<p>${{escapeHtml(block.text)}}</p>`;
        return `<div class="image-grid">${{block.images.map((image) => {{
          const src = image.replace("/doc-assets/", "doc-assets/");
          return `<figure><img loading="lazy" alt="תמונה מתוך הסיכום: ${{escapeHtml(active.title)}}" src="${{src}}"></figure>`;
        }}).join("")}}</div>`;
      }}).join("");

      card.innerHTML = `<div class="section-kicker">נושא ${{topicNumber}}</div><h2>${{escapeHtml(active.title)}}</h2><div class="content-flow">${{blocks}}</div>`;
    }}

    document.getElementById("search").addEventListener("input", (event) => {{
      query = event.target.value;
      render();
    }});
    document.getElementById("comfortable").addEventListener("click", () => {{
      isDense = false;
      render();
    }});
    document.getElementById("dense").addEventListener("click", () => {{
      isDense = true;
      render();
    }});
    render();
  </script>
</body>
</html>
"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
