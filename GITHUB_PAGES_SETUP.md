# GitHub Pages setup

The deployment workflow belongs at this exact repository path:

```text
.github/workflows/publish.yml
```

Folders beginning with a period are hidden by default on macOS. In Finder, press
**Command–Shift–Period** to show `.github`.

## Easiest upload method

1. Create an empty GitHub repository.
2. Upload the **contents** of this template folder, not the outer template folder itself.
3. Confirm that GitHub shows `.github/workflows/publish.yml` at the repository root.
4. Go to **Settings → Pages** and choose **GitHub Actions** as the source.
5. Open **Actions** and run **Publish course website**, or push a new commit to `main`.

## If `.github` was omitted

Create the file directly on GitHub:

1. Choose **Add file → Create new file**.
2. Enter this full filename:

   ```text
   .github/workflows/publish.yml
   ```

3. Copy the contents of `PUBLISH_WORKFLOW_COPY.yml` into it.
4. Commit the new file to `main`.

`PUBLISH_WORKFLOW_COPY.yml` is only a visible backup. GitHub runs the copy under
`.github/workflows/`, not the backup at the repository root.
