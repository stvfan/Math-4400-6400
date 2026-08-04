#!/usr/bin/env python3
"""Generate static Quarto partials from course-data.yml.

The home page is a syllabus-style course hub. Routine changes live in one YAML
file while Quarto receives accessible, searchable, static HTML fragments.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "course-data.yml"
OUT_DIR = ROOT / "_generated"


def load_data() -> dict[str, Any]:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("course-data.yml must contain a YAML mapping")
    return data


def text(value: Any) -> str:
    return escape(str(value or ""), quote=False)


def attr(value: Any) -> str:
    return escape(str(value or ""), quote=True)


def output_href(href: str) -> str:
    """Translate local Quarto source links for use inside raw HTML."""
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return href
    anchor = ""
    if "#" in href:
        href, anchor = href.split("#", 1)
        anchor = f"#{anchor}"
    if href.endswith(".qmd"):
        href = f"{href[:-4]}.html"
    return f"{href}{anchor}"


def links_html(items: list[dict[str, Any]] | None, class_name: str = "material-link") -> str:
    if not items:
        return ""
    return "".join(
        f'<a class="{class_name}" href="{attr(output_href(str(item.get("href", "#"))))}">'
        f'{text(item.get("label", "Open"))}</a>'
        for item in items
    )


def paragraphs_html(items: list[str] | None) -> str:
    return "".join(f"<p>{text(item)}</p>" for item in (items or []))


def write(name: str, content: str) -> None:
    """Write a Quarto include containing an explicit raw-HTML block."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wrapped = f"```{{=html}}\n{content.strip()}\n```\n"
    (OUT_DIR / name).write_text(wrapped, encoding="utf-8")


def build_hero(data: dict[str, Any]) -> str:
    course = data["course"]
    return f"""
<header class="course-header-hero" aria-labelledby="course-title">
  <div class="course-header-title">
    <div class="course-heading-block">
      <div class="hero-course-line">
        <span>{text(course['code'])}</span>
        <span class="hero-dot" aria-hidden="true"></span>
        <span>{text(course['semester'])}</span>
      </div>
      <h1 id="course-title">{text(course['title'])}</h1>
    </div>
    <figure class="course-header-quote">
      <blockquote>“{text(course.get('quote', 'God made the integers; all else is the work of man.'))}”</blockquote>
      <figcaption>— {text(course.get('quote_attribution', 'Leopold Kronecker'))}</figcaption>
    </figure>
  </div>
  <div class="course-header-facts" aria-label="Essential course information">
    <div class="header-fact">
      <span>Meetings</span>
      <strong>{text(course['meetings'])}</strong>
      <div class="header-fact-detail">{text(course['room'])}</div>
    </div>
    <div class="header-fact">
      <span>Instructor</span>
      <strong>{text(course['instructor'])}</strong>
      <div class="header-fact-detail"><a href="mailto:{attr(course['email'])}">{text(course['email'])}</a></div>
    </div>
    <div class="header-fact">
      <span>Office hours</span>
      <strong>{text(course['office_hours'])}</strong>
      <div class="header-fact-detail">{text(course['office'])}</div>
    </div>
  </div>
</header>
"""


def section_heading(kicker: str, title: str, section_id: str, link: tuple[str, str] | None = None) -> str:
    action = ""
    if link:
        label, href = link
        action = f'<a class="section-text-link" href="{attr(output_href(href))}">{text(label)} →</a>'
    return f"""
<div class="section-heading-row">
  <div>
    <div class="section-kicker">{text(kicker)}</div>
    <h2 id="{attr(section_id)}">{text(title)}</h2>
  </div>
  {action}
</div>
"""


def build_course_summary(data: dict[str, Any]) -> str:
    summary = data["course_summary"]
    heading = section_heading("About the course", "Course summary", "summary-heading")
    return f"""
<section id="summary" class="dashboard-section course-summary-section" aria-labelledby="summary-heading">
  {heading}
  <div class="summary-card">
    <div class="summary-copy">{paragraphs_html(summary.get('paragraphs'))}</div>
    <div class="summary-action">
      <a class="course-button course-button-primary" href="{attr(output_href(summary['syllabus_href']))}">{text(summary['syllabus_label'])}</a>
    </div>
  </div>
</section>
"""


def build_textbook(data: dict[str, Any]) -> str:
    book = data["textbook"]
    heading = section_heading("Course materials", "Recommended textbook", "textbook-heading")
    return f"""
<section id="recommended-textbook" class="dashboard-section textbook-section" aria-labelledby="textbook-heading">
  {heading}
  <div class="textbook-card">
    <div class="textbook-cover" aria-hidden="true">
      <span>Fundamentals</span>
      <strong>Number<br>Theory</strong>
      <small>W. J. LeVeque</small>
    </div>
    <div class="textbook-copy">
      <span class="textbook-label">Recommended · not required</span>
      <h3>{text(book['title'])}</h3>
      <p class="textbook-author">{text(book['author'])}</p>
      <p>{text(book['note'])}</p>
      <a class="course-button course-button-secondary" href="{attr(book['purchase_url'])}">{text(book['purchase_label'])}</a>
    </div>
  </div>
</section>
"""


def lecture_entry(item: dict[str, Any], compact: bool = False) -> str:
    compact_class = " lecture-entry-compact" if compact else ""
    search_text = " ".join(
        [
            str(item.get("date", "")),
            str(item.get("meeting", "")),
            str(item.get("title", "")),
            str(item.get("summary", "")),
            " ".join(item.get("topics", [])),
        ]
    )
    return f"""
<article class="lecture-entry{compact_class}" data-log-entry data-search="{attr(search_text)}">
  <div class="lecture-date">
    <strong>{text(item.get('date'))}</strong>
    <span>{text(item.get('meeting'))}</span>
  </div>
  <div class="lecture-copy">
    <h3>{text(item.get('title'))}</h3>
    <p>{text(item.get('summary'))}</p>
  </div>
  <div class="lecture-links">{links_html(item.get('links'))}</div>
</article>
"""


def build_lectures_preview(data: dict[str, Any]) -> str:
    entries = data.get("lectures", [])[:6]
    body = "".join(lecture_entry(item, compact=True) for item in entries)
    heading = section_heading("Updated after each class", "Lectures", "lectures-heading", ("View all lectures", "lectures.qmd"))
    return f"""
<section id="lectures" class="dashboard-section lectures-home-section" aria-labelledby="lectures-heading">
  {heading}
  <div class="lecture-list">{body}</div>
</section>
"""


def build_lectures_full(data: dict[str, Any]) -> str:
    entries = "".join(lecture_entry(item) for item in data.get("lectures", []))
    return f"""
<div class="class-log-toolbar">
  <label for="class-log-search">Search lectures</label>
  <input id="class-log-search" type="search" placeholder="Try ‘quadratic residues’ or ‘September’" autocomplete="off">
  <span id="class-log-count" aria-live="polite"></span>
</div>
<div class="lecture-list lecture-list-full">{entries}</div>
<div class="class-log-empty" hidden>No lectures match that search.</div>
"""


def assignment_entry(item: dict[str, Any]) -> str:
    return f"""
<article class="assignment-row">
  <div class="assignment-id">
    <strong>{text(item.get('number'))}</strong>
    <span>{text(item.get('due'))}</span>
  </div>
  <div class="assignment-copy">
    <h3>{text(item.get('title'))}</h3>
    <p>{text(item.get('note'))}</p>
  </div>
  <div class="assignment-actions">
    <span class="status-badge status-{attr(item.get('status_style', 'upcoming'))}">{text(item.get('status'))}</span>
    <a class="material-link" href="{attr(output_href(str(item.get('href', '#'))))}">Open</a>
  </div>
</article>
"""


def build_assignments(data: dict[str, Any]) -> str:
    assignments = data["assignments"]
    heading = section_heading("Homework and due dates", "Assignments", "assignments-heading", ("All assignments", "assignments/index.qmd"))
    rows = "".join(assignment_entry(item) for item in assignments.get("items", []))
    return f"""
<section id="assignments" class="dashboard-section assignments-home-section" aria-labelledby="assignments-heading">
  {heading}
  <div class="policy-card">{paragraphs_html(assignments.get('policy'))}</div>
  <div class="assignment-list-home">{rows}</div>
</section>
"""


def exam_card(item: dict[str, Any]) -> str:
    note = f'<span class="exam-note">{text(item.get("note"))}</span>' if item.get("note") else ""
    return f"""
<article class="exam-card">
  <div class="exam-card-topline">
    <h3>{text(item.get('title'))}</h3>
    {note}
  </div>
  <dl>
    <div><dt>Date</dt><dd>{text(item.get('date'))}</dd></div>
    <div><dt>Time</dt><dd>{text(item.get('time'))}</dd></div>
    <div><dt>Location</dt><dd>{text(item.get('location'))}</dd></div>
  </dl>
</article>
"""


def build_exams(data: dict[str, Any]) -> str:
    exams = data["exams"]
    heading = section_heading("Assessment dates and policies", "Exams", "exams-heading")
    cards = "".join(exam_card(item) for item in exams.get("items", []))
    return f"""
<section id="exams" class="dashboard-section exams-home-section" aria-labelledby="exams-heading">
  {heading}
  <div class="policy-card">{paragraphs_html(exams.get('policy'))}</div>
  <div class="exam-grid">{cards}</div>
</section>
"""


def grading_row(item: dict[str, Any]) -> str:
    return f"""
<div class="grading-row">
  <div><strong>{text(item.get('component'))}</strong><span>{text(item.get('note'))}</span></div>
  <b>{text(item.get('weight'))}</b>
</div>
"""


def build_grading(data: dict[str, Any]) -> str:
    grading = data["grading"]
    heading = section_heading("How the final grade is calculated", "Grading", "grading-heading")
    rows = "".join(grading_row(item) for item in grading.get("items", []))
    return f"""
<section id="grading" class="dashboard-section grading-home-section" aria-labelledby="grading-heading">
  {heading}
  <div class="grading-card">
    <p>{text(grading.get('intro'))}</p>
    <div class="grading-list">{rows}</div>
  </div>
</section>
"""


def resource_link(item: dict[str, Any]) -> str:
    return f"""
<a class="university-resource" href="{attr(item.get('href', '#'))}">
  <span><strong>{text(item.get('label'))}</strong><small>{text(item.get('description'))}</small></span>
  <b aria-hidden="true">→</b>
</a>
"""


def build_accommodations(data: dict[str, Any]) -> str:
    section = data["accommodations_resources"]
    heading = section_heading("Support and access", "Accommodations and resources", "accommodations-heading")
    resources = "".join(resource_link(item) for item in section.get("resources", []))
    return f"""
<section id="accommodations-and-resources" class="dashboard-section accommodations-section" aria-labelledby="accommodations-heading">
  {heading}
  <div class="accommodations-grid">
    <div class="accommodations-copy">
      <h3>Special accommodations</h3>
      <p>{text(section.get('accommodation_text'))}</p>
    </div>
    <div class="university-resources">
      <h3>University resources</h3>
      <div>{resources}</div>
    </div>
  </div>
</section>
"""


def build_disclaimer(data: dict[str, Any]) -> str:
    return f"""
<aside class="course-disclaimer" aria-label="Course syllabus disclaimer">
  <strong>Please note</strong>
  <p>{text(data.get('disclaimer'))}</p>
</aside>
"""


def main() -> None:
    data = load_data()
    required = [
        "course",
        "course_summary",
        "textbook",
        "lectures",
        "assignments",
        "exams",
        "grading",
        "accommodations_resources",
        "disclaimer",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise KeyError(f"Missing required sections in course-data.yml: {', '.join(missing)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.html", "*.qmd"):
        for stale in OUT_DIR.glob(pattern):
            stale.unlink()

    write("home-hero.qmd", build_hero(data))
    write("course-summary.qmd", build_course_summary(data))
    write("textbook.qmd", build_textbook(data))
    write("lectures-preview.qmd", build_lectures_preview(data))
    write("lectures-full.qmd", build_lectures_full(data))
    write("assignments.qmd", build_assignments(data))
    write("exams.qmd", build_exams(data))
    write("grading.qmd", build_grading(data))
    write("accommodations.qmd", build_accommodations(data))
    write("disclaimer.qmd", build_disclaimer(data))
    print(f"Generated syllabus-style course homepage in {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
