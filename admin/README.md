# Sveltia CMS

Browser-based editing for this site, at [jnicolaus.com/admin/](https://jnicolaus.com/admin/).

- `admin/index.html` — loads the CMS bundle from unpkg. Nothing else belongs in
  this file: a stylesheet link or `type="module"` on the script tag stops the
  CMS loading entirely.
- `admin/config.yml` — what the CMS can edit. The first line points at the
  published JSON schema, so an editor with schema support validates it as you
  type. The CMS itself re-validates on every load and lists any problems on the
  sign-in screen.

## What you can edit

| Section | Writes to |
| --- | --- |
| Blog posts | `_posts/*.md` |
| Tutorials | `_tutorials/*.md` |
| Pages → Front page | `_pages/about.md` (intro text) |
| Pages → Contact page | `_pages/contact.md` |
| Front page sections | `_data/publications.yml`, `talks.yml`, `education.yml`, `experience.yml`, `honors.yml`, `teaching.yml`, `workshops.yml`, `organizations.yml` |
| Site settings → Navigation | `_data/navigation.yml` |

The front page body holds the intro text plus `{% raw %}{% include %}{% endraw %}` lines that pull in each
list. Edit the prose freely; leave the include lines alone unless you want to
move or remove a whole section.

Images uploaded through the CMS land in `assets/images/` and are referenced as
`/assets/images/...`.

## Signing in

**GitHub** — needs an OAuth app and an authenticator service. Register the app
under Settings → Developer settings → OAuth Apps, then add `base_url` (and
`auth_endpoint` if your authenticator needs it) to the `backend` block in
`config.yml`.

**Access token** — no setup. Create a GitHub personal access token with `repo`
scope and paste it when prompted. Never commit a token.

## Editing locally

Sveltia can work straight off the working directory, no token and no server
round-trip. Serve the site and open the admin page:

```bash
bundle exec jekyll serve
```

Then open <http://localhost:4000/admin/> and choose **Work with Local
Repository**. Changes are written to your files; commit them yourself.

## If something breaks

- **Blank page** — check `admin/index.html` matches the minimal form above.
- **Errors on the sign-in screen** — config validation problems; each message
  names the collection, file and field.
- **Saving drops front matter** — a key exists in the file but not in
  `config.yml`. Add it as a field (use `widget: hidden` if it should not be
  editable).
