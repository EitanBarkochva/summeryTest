from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DOCX_PATH = Path(r"C:\Users\eitan\Downloads\נוירוביולוגיה\סיכום למבחן בבנוירוביולוגיה.docx")
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ASSETS = ROOT / "public" / "doc-assets"
DATA_PATH = ROOT / "app" / "studyContent.json"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}


def qn(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()
    return value


def rels_for_docx(zf: zipfile.ZipFile) -> dict[str, str]:
    rels = {}
    xml = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
    for rel in xml:
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        if rid and target.startswith("media/"):
            rels[rid] = "word/" + target
    return rels


def is_question_or_heading(text: str) -> bool:
    if not text:
        return False
    if len(text) > 95:
        return False
    markers = [
        "?",
        "מה ",
        "מי ",
        "מודל",
        "מערכת",
        "למידה",
        "זיכרון",
        "נוירונים",
        "שלושת",
        "אמיגדלה",
        "פוטנציאל",
        "תפיסה",
        "תפקוד",
        "קשב",
    ]
    return any(marker in text for marker in markers)


def paragraph_to_block(p: ET.Element, rels: dict[str, str], image_map: dict[str, str]) -> dict | None:
    texts = []
    images = []
    for node in p.iter():
        if node.tag == qn("w", "t") and node.text:
            texts.append(node.text)
        elif node.tag == qn("w", "tab"):
            texts.append(" ")
        elif node.tag == qn("w", "br"):
            texts.append("\n")
        elif node.tag == qn("a", "blip"):
            rid = node.attrib.get(qn("r", "embed"))
            if rid and rid in rels and rels[rid] in image_map:
                images.append(image_map[rels[rid]])

    text = clean_text("".join(texts))
    if not text and not images:
        return None

    style = "paragraph"
    p_style = p.find("./w:pPr/w:pStyle", NS)
    if p_style is not None and p_style.attrib.get(qn("w", "val"), "").lower().startswith("heading"):
        style = "heading"
    elif is_question_or_heading(text):
        style = "heading"

    return {"type": "block", "style": style, "text": text, "images": images}


def extract() -> None:
    PUBLIC_ASSETS.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DOCX_PATH) as zf:
        rels = rels_for_docx(zf)
        media_names = sorted(
            [name for name in zf.namelist() if name.startswith("word/media/")],
            key=lambda name: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name)],
        )
        image_map = {}
        for index, name in enumerate(media_names, 1):
            suffix = Path(name).suffix.lower() or ".png"
            out_name = f"image-{index:03d}{suffix}"
            out_path = PUBLIC_ASSETS / out_name
            with zf.open(name) as src, out_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            image_map[name] = f"/doc-assets/{out_name}"

        document = ET.fromstring(zf.read("word/document.xml"))
        body = document.find("w:body", NS)
        raw_blocks = []
        if body is not None:
            for child in body:
                if child.tag == qn("w", "p"):
                    block = paragraph_to_block(child, rels, image_map)
                    if block:
                        raw_blocks.append(block)

    sections = []
    current = None
    intro_title = "פתיחה וחומרי רקע"
    for block in raw_blocks:
        text = block["text"]
        if block["style"] == "heading" and text:
            if current:
                sections.append(current)
            current = {
                "id": f"topic-{len(sections) + 1}",
                "title": text,
                "blocks": [],
            }
            if block["images"]:
                current["blocks"].append({"type": "image-row", "images": block["images"]})
        else:
            if current is None:
                current = {"id": "topic-1", "title": intro_title, "blocks": []}
            if text:
                current["blocks"].append({"type": "paragraph", "text": text})
            if block["images"]:
                current["blocks"].append({"type": "image-row", "images": block["images"]})
    if current:
        sections.append(current)

    output = {
        "title": "סיכום למבחן בנוירוביולוגיה",
        "sourceFile": DOCX_PATH.name,
        "stats": {
            "sections": len(sections),
            "paragraphs": sum(1 for section in sections for block in section["blocks"] if block["type"] == "paragraph"),
            "images": len(media_names),
        },
        "sections": sections,
    }
    DATA_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["stats"], ensure_ascii=False))


if __name__ == "__main__":
    extract()
