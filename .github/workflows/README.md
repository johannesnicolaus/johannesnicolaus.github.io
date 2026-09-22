# Workflows

## `deploy.yml` — build the CV, build the site, publish to GitHub Pages

Runs on every push to `master`, weekly, on demand, and whenever the Awesome-CV
repo sends a `cv-updated` dispatch.

Three jobs:

1. **Compile CV** — checks out the `Awesome-CV` submodule, moves it to the tip
   of that repo (`git submodule update --remote`), and compiles
   `examples/resume.tex` with XeLaTeX inside the `texlive/texlive` container.
   The result is the same PDF `Awesome-CV/makecv.sh` produces locally.
2. **Build site** — drops that PDF in as `files/cv.pdf`, overwriting the copy
   committed in this repo, then runs `jekyll build`.
3. **Deploy** — publishes `_site` to GitHub Pages.

Because step 1 always pulls the CV repo's newest commit, the published site
carries an up-to-date CV even when the submodule pointer here is behind.

### One-time setup

GitHub Pages has to be set to build from Actions rather than from a branch:

**Settings → Pages → Build and deployment → Source → GitHub Actions**

Leave the custom domain set to `jnicolaus.com`; the `CNAME` file at the repo
root is copied into the build output.

### Rebuilding immediately when the CV changes

Without any extra setup the site picks up CV changes on the next push here, or
on the weekly run. To have a CV commit rebuild the site straight away, add a
workflow to the **Awesome-CV** repo that dispatches to this one.

1. In this repo's account, create a fine-grained personal access token with
   **Contents: read and write** on `johannesnicolaus/personal_website_2`.
2. In the **Awesome-CV** repo, save it as the secret `WEBSITE_DISPATCH_TOKEN`
   (Settings → Secrets and variables → Actions).
3. Commit this file to the Awesome-CV repo as
   `.github/workflows/notify-website.yml`:

```yaml
name: Rebuild personal website

on:
  push:
    branches: [master]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Tell the website repo the CV changed
        run: |
          curl -sSf -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.WEBSITE_DISPATCH_TOKEN }}" \
            https://api.github.com/repos/johannesnicolaus/personal_website_2/dispatches \
            -d '{"event_type":"cv-updated"}'
```

### Keeping the committed copies in step

The PDF at `files/cv.pdf` and the submodule pointer are only used for local
builds. To refresh them:

```bash
git submodule update --remote Awesome-CV
(cd Awesome-CV && ./makecv.sh)
cp Awesome-CV/examples/resume.pdf files/cv.pdf
git add Awesome-CV files/cv.pdf
git commit -m "Update CV"
```
