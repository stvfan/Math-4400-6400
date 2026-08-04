# Undergraduate Number Theory — syllabus-style course website

A polished, responsive course website built with [Quarto](https://quarto.org/) and deployed automatically with [GitHub Pages](https://pages.github.com/).

Version 2.4 presents the course as a clear, single-page syllabus hub: essential logistics, course summary, textbook, lecture record, assignments, exams, grading, accommodations, resources, and the syllabus disclaimer.

![Home-page preview](preview-home-v2.4.png)

## What is included

- a compact, number-theory-themed header with prominent course logistics;
- section-jump navigation for **Summary**, **Textbook**, **Lectures**, **Assignments**, **Exams**, **Grading**, and **Resources**;
- a reverse-chronological lecture record with attached notes;
- homework policy, current assignments, due dates, and assignment pages;
- exam policy, dates, times, and locations;
- grading, accommodations, university resources, and syllabus disclaimer;
- a planned semester schedule, searchable lecture archive, dark mode, and GitHub Pages deployment.

## The routine update workflow

Most course updates happen in one file:

```text
course-data.yml
```

Edit the relevant section:

1. `course` — title, meetings, instructor, office hours, and quotation;
2. `course_summary` — course description and syllabus button;
3. `textbook` — recommended book information;
4. `lectures` — add one entry after each class, newest first;
5. `assignments` — homework policy, assignments, and due dates;
6. `exams`, `grading`, and `accommodations_resources` — syllabus information.

Then regenerate the static page fragments:

```bash
python -m pip install -r requirements.txt
python scripts/build_course_data.py
```

The GitHub workflow performs this automatically before each deployment.

## Quick start

1. Create a new GitHub repository and upload this folder, or push it with Git.
2. Edit `course-data.yml` and replace bracketed placeholders in the `.qmd` files.
3. In the repository, open **Settings → Pages** and select **GitHub Actions** as the source.
4. Push to the `main` branch.
5. Find the public URL in **Settings → Pages** or in the completed deployment workflow.

## Preview locally

Install Quarto and the small YAML dependency, then run:

```bash
python -m pip install -r requirements.txt
make validate
make preview
```

Without `make`:

```bash
python scripts/build_course_data.py
quarto preview
```

## Schedule, lectures, notes, and assignments

- `schedule.qmd` is the semester plan: future topics, readings, and deadlines.
- `lectures.qmd` is the historical record of what was actually covered.
- `notes/` contains the mathematical lecture notes themselves.
- `assignments/` contains problem sets and submission information.

Keeping these destinations distinct makes the site easier to scan and prevents assignments from being mixed with course content.

## Add a lecture note

1. Copy `_templates/lecture.qmd` to `notes/03-your-topic.qmd`.
2. Change its front matter and content.
3. Add its link to `notes/index.qmd`, the schedule, and the relevant `lectures` entry in `course-data.yml`.

## Add an assignment

1. Copy `_templates/problem-set.qmd` to `assignments/problem-set-02.qmd`.
2. Replace the metadata and exercises.
3. Add its link to `assignments/index.qmd`, the schedule, and the `assignments` section of `course-data.yml`.

## Repository structure

```text
.
├── .github/workflows/publish.yml   # automatic GitHub Pages deployment
├── _quarto.yml                     # global site configuration
├── course-data.yml                 # routine home-page and lecture updates
├── scripts/build_course_data.py    # static fragment generator
├── _generated/                     # generated page fragments
├── index.qmd                       # simplified home page
├── lectures.qmd                    # actual lecture history
├── schedule.qmd                    # planned semester schedule
├── syllabus.qmd
├── resources.qmd
├── notes/                          # lecture notes
├── assignments/                    # assignments and problem sets
├── _templates/                     # reusable source templates
├── _includes/                      # theme scripts and metadata
└── assets/                         # CSS and original SVG artwork
```

## Optional repository links

After the GitHub repository exists, add these lines under `website:` in `_quarto.yml`:

```yaml
site-url: https://USERNAME.github.io/REPOSITORY
repo-url: https://github.com/USERNAME/REPOSITORY
repo-actions: [edit, issue]
```

## License

The template code is provided under the MIT License. Replace the license or add a separate license for your course materials as appropriate.

## GitHub Pages setup

See [`GITHUB_PAGES_SETUP.md`](GITHUB_PAGES_SETUP.md). The required workflow is stored at `.github/workflows/publish.yml`; a visible backup is included as `PUBLISH_WORKFLOW_COPY.yml` because `.github` is hidden by default on macOS.
