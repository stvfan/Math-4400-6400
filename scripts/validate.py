#!/usr/bin/env python3
"""Lightweight source validation for the course website template."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_yaml() -> None:
    for path in [ROOT / "_quarto.yml", ROOT / "course-data.yml", ROOT / ".github/workflows/publish.yml"]:
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"invalid YAML in {path.relative_to(ROOT)}: {exc}")
        if not isinstance(value, dict):
            fail(f"expected a mapping in {path.relative_to(ROOT)}")

    data = yaml.safe_load((ROOT / "course-data.yml").read_text(encoding="utf-8"))
    required = (
        "course",
        "course_summary",
        "textbook",
        "lectures",
        "assignments",
        "exams",
        "grading",
        "accommodations_resources",
        "disclaimer",
    )
    for key in required:
        if key not in data:
            fail(f"course-data.yml is missing {key!r}")


def validate_front_matter() -> None:
    for path in ROOT.rglob("*.qmd"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(f"missing YAML front matter in {path.relative_to(ROOT)}")
        end = text.find("\n---\n", 4)
        if end < 0:
            fail(f"unterminated YAML front matter in {path.relative_to(ROOT)}")
        try:
            yaml.safe_load(text[4:end])
        except Exception as exc:
            fail(f"invalid front matter in {path.relative_to(ROOT)}: {exc}")


def resolve_qmd_link(source: Path, href: str) -> Path | None:
    href = href.split("#", 1)[0]
    if not href or "://" in href or href.startswith(("mailto:", "#")):
        return None
    return (source.parent / href).resolve()


def validate_links() -> None:
    markdown_link = re.compile(r"\]\(([^)]+\.qmd(?:#[^)]+)?)\)")
    for path in ROOT.rglob("*.qmd"):
        source = path.read_text(encoding="utf-8")
        for href in markdown_link.findall(source):
            target = resolve_qmd_link(path, href)
            if target and not target.exists():
                fail(f"broken qmd link in {path.relative_to(ROOT)}: {href}")

    data = yaml.safe_load((ROOT / "course-data.yml").read_text(encoding="utf-8"))

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "href" and isinstance(item, str) and ".qmd" in item:
                    clean = item.split("#", 1)[0]
                    target = (ROOT / clean).resolve()
                    if not target.exists():
                        fail(f"broken href in course-data.yml: {item}")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)


def validate_css() -> None:
    css = (ROOT / "assets/styles.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if css.count("{") != css.count("}"):
        fail("unbalanced braces in assets/styles.css")


def validate_javascript() -> None:
    for html_file in [ROOT / "_includes/head.html", ROOT / "_includes/after-body.html"]:
        source = html_file.read_text(encoding="utf-8")
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", source, flags=re.S)
        for index, script in enumerate(scripts):
            temp = ROOT / f".validate-script-{index}.js"
            temp.write_text(script, encoding="utf-8")
            try:
                subprocess.run(["node", "--check", str(temp)], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as exc:
                fail(f"JavaScript syntax error in {html_file.relative_to(ROOT)}: {exc.stderr.strip()}")
            finally:
                temp.unlink(missing_ok=True)


def validate_generator() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts/build_course_data.py")], cwd=ROOT, check=True)
    expected = {
        "home-hero.html",
        "course-summary.html",
        "textbook.html",
        "lectures-preview.html",
        "lectures-full.html",
        "assignments.html",
        "exams.html",
        "grading.html",
        "accommodations.html",
        "disclaimer.html",
    }
    actual = {p.name for p in (ROOT / "_generated").glob("*.html")}
    missing = expected - actual
    extras = actual - expected
    if missing:
        fail(f"generator did not create: {', '.join(sorted(missing))}")
    if extras:
        fail(f"generator left unexpected files: {', '.join(sorted(extras))}")



def validate_section_navigation() -> None:
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    links = config.get("website", {}).get("navbar", {}).get("left", [])
    generated = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "_generated").glob("*.html")
    )
    section_titles = {
        section_id: re.sub(r"<[^>]+>", "", title).strip()
        for section_id, title in re.findall(
            r'<section id="([^"]+)"[^>]*>.*?<h2[^>]*>(.*?)</h2>',
            generated,
            flags=re.S,
        )
    }
    for item in links:
        if not isinstance(item, dict):
            continue
        href = str(item.get("href", ""))
        if not href.startswith("index.qmd#"):
            continue
        section_id = href.split("#", 1)[1]
        if section_id not in section_titles:
            fail(f"navbar points to missing homepage section: {href}")
        label = str(item.get("text", "")).strip()
        allowed_labels = {section_titles[section_id]}
        if section_id == "summary":
            allowed_labels.add("Summary")
        if section_id == "recommended-textbook":
            allowed_labels.add("Textbook")
        if section_id == "accommodations-and-resources":
            allowed_labels.add("Resources")
        if label not in allowed_labels:
            fail(
                f"navbar label {label!r} is not allowed for section title "
                f"{section_titles[section_id]!r} at #{section_id}; allowed labels: {sorted(allowed_labels)!r}"
            )

def main() -> None:
    validate_yaml()
    validate_front_matter()
    validate_links()
    validate_css()
    validate_javascript()
    validate_generator()
    validate_section_navigation()
    print("Validation passed: YAML, front matter, links, section navigation, CSS, JavaScript, and generated course files.")


if __name__ == "__main__":
    main()
