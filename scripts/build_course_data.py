#!/usr/bin/env python3
"""Generate complete Quarto course pages from course-data.yml.

Routine changes live in one YAML file. The generator writes the homepage and
lecture log as complete documents so Quarto receives one stable HTML block per
page rather than a chain of nested includes.
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


def raw_html_block(content: str) -> str:
    """Return one explicit Pandoc raw-HTML block."""
    return f"```{{=html}}\n{content.strip()}\n```\n"


def write(name: str, content: str) -> None:
    """Write a generated partial for inspection and troubleshooting."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(raw_html_block(content), encoding="utf-8")


def write_page(path: Path, front_matter: str, content: str) -> None:
    """Write a complete Quarto page containing one raw-HTML body block."""
    path.write_text(front_matter.strip() + "\n\n" + raw_html_block(content), encoding="utf-8")


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
    <img class="textbook-cover"
         src="{attr(book.get('cover_image', 'assets/leveque-fundamentals-cover.svg'))}"
         alt="{attr(book.get('cover_alt', f"Cover of {book['title']} by {book['author']}"))}">
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
    topics = item.get("topics", []) or []
    topics_html = ""
    if topics:
        topic_tags = "".join(
            f'<span class="lecture-topic">{text(topic)}</span>'
            for topic in topics
        )
        topics_html = (
            '<div class="lecture-topics" aria-label="Lecture topics">'
            f'{topic_tags}</div>'
        )

    search_text = " ".join(
        [
            str(item.get("date", "")),
            str(item.get("meeting", "")),
            str(item.get("title", "")),
            str(item.get("summary", "")),
            " ".join(str(topic) for topic in topics),
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
    {topics_html}
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
    heading = section_heading("Homework and due dates", "Assignments", "assignments-heading", ("All assignments", ""))
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
    solutions_href = item.get("solutions_href")
    solutions_label = item.get("solutions_label", "View solutions")
    solutions_action = ""
    if solutions_href:
        solutions_action = f"""
  <div class="exam-card-actions">
    <a class="exam-solutions-link" href="{attr(output_href(str(solutions_href)))}">
      {text(solutions_label)}
    </a>
  </div>"""
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
  {solutions_action}
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

    hero = build_hero(data)
    summary = build_course_summary(data)
    textbook = build_textbook(data)
    lectures_preview = build_lectures_preview(data)
    lectures_full = build_lectures_full(data)
    assignments = build_assignments(data)
    exams = build_exams(data)
    grading = build_grading(data)
    accommodations = build_accommodations(data)
    disclaimer = build_disclaimer(data)

    # Keep partials as readable diagnostics, but render the live pages from one
    # raw HTML block so Pandoc cannot split the layout into unrelated columns.
    write("home-hero.qmd", hero)
    write("course-summary.qmd", summary)
    write("textbook.qmd", textbook)
    write("lectures-preview.qmd", lectures_preview)
    write("lectures-full.qmd", lectures_full)
    write("assignments.qmd", assignments)
    write("exams.qmd", exams)
    write("grading.qmd", grading)
    write("accommodations.qmd", accommodations)
    write("disclaimer.qmd", disclaimer)

    homepage = "\n".join([
        hero,
        '<div class="dashboard-shell syllabus-home">',
        summary,
        textbook,
        lectures_preview,
        assignments,
        exams,
        grading,
        accommodations,
        disclaimer,
        '</div>',
    ])
    homepage_front_matter = "\n".join([
        "---",
        'pagetitle: "Number Theory"',
        "page-layout: full",
        "toc: false",
        "---",
    ])
    write_page(ROOT / "index.qmd", homepage_front_matter, homepage)

    lectures_page = "\n".join([
        '<div class="page-intro-shell">',
        '<div class="section-kicker">What we covered</div>',
        '<h1>Lectures</h1>',
        '<p>The <a href="schedule.html">schedule</a> shows the semester plan. This page records what we actually covered after each class meeting, with links to the corresponding lecture notes.</p>',
        '</div>',
        '<div class="wide-content-shell">',
        lectures_full,
        '</div>',
    ])
    lectures_front_matter = "\n".join([
        "---",
        'pagetitle: "Lectures | Number Theory"',
        'description: "A reverse-chronological record of what we covered in each lecture."',
        "toc: false",
        "page-layout: full",
        "---",
    ])
    write_page(ROOT / "lectures.qmd", lectures_front_matter, lectures_page)
    print("Generated complete homepage and lecture log from course-data.yml")


if __name__ == "__main__":
    main()
