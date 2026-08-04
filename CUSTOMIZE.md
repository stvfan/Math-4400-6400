# Customization checklist

Use this as a final pass before the site becomes public.

- [ ] Replace every bracketed placeholder (`grep -R "\\[.*\\]" . --include='*.qmd' --include='*.yml'`).
- [ ] Set the course title and footer in `_quarto.yml`.
- [ ] Update the course summary, textbook, lecture, assignment, exam, grading, and resource sections in `course-data.yml`.
- [ ] Keep lecture notes and assignments in their separate folders and homepage sections.
- [ ] Add one item to `lectures` after each class meeting.
- [ ] Verify all dates, weights, policies, and links.
- [ ] Replace or remove the visible “Template note” boxes.
- [ ] Add the repository and site URLs to `_quarto.yml`.
- [ ] Confirm the GitHub Pages source is set to GitHub Actions.
- [ ] Preview on a phone-sized browser window.
- [ ] Run `make validate` and `quarto render` before publishing.

## Top navigation

The top bar links directly to the seven homepage sections. The labels and anchors
are configured in `_quarto.yml`. If you rename a section, update both its title
and the matching navbar text. Keep the stable section `id` in
`scripts/build_course_data.py`, or update the corresponding navbar fragment at
the same time.

