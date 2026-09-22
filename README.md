# jnicolaus.com

Personal academic site for Johannes Nicolaus Wibisana. Jekyll, built on a fork
of [Academic Pages](https://github.com/academicpages/academicpages.github.io)
(itself a fork of Minimal Mistakes), deployed to GitHub Pages.

## Layout

```
_pages/about.md        front page: intro text + the section includes
_pages/blog.html       /blog/       listing of _posts
_pages/tutorials.html  /tutorials/  listing of _tutorials
_pages/contact.md      /contact/
_posts/                blog posts, published at /<slug>/
_tutorials/            tutorials, published at /tutorials/<slug>/
_data/                 the structured lists rendered on the front page
_includes/*-list.html  the Liquid that renders each of those lists
admin/                 Sveltia CMS (see admin/README.md)
Awesome-CV/            git submodule holding the LaTeX CV source
files/cv.pdf           the CV, rebuilt from the submodule on every deploy
```

Everything on the front page comes from `_data`:

| File | Section |
| --- | --- |
| `publications.yml` | Publications |
| `talks.yml` | Conference presentations |
| `education.yml` | Education |
| `experience.yml` | Research experience |
| `honors.yml` | Honours and awards |
| `teaching.yml` | Teaching and training |
| `workshops.yml` | Workshops attended |
| `organizations.yml` | Organizational experience |
| `navigation.yml` | Header menu |

Add an entry by adding a list item; the front page picks it up. Each file has a
comment at the top describing its fields.

## Editing

Either edit the files directly, or use the CMS at
[jnicolaus.com/admin/](https://jnicolaus.com/admin/) — see
[`admin/README.md`](admin/README.md).

## Running locally

```bash
bundle install
bundle exec jekyll serve
```

The site is then at <http://localhost:4000>, the CMS at
<http://localhost:4000/admin/>.

## The CV

`Awesome-CV` is a submodule pointing at
[johannesnicolaus/Awesome-CV](https://github.com/johannesnicolaus/Awesome-CV).
`examples/resume.tex` there is the real CV. Every deploy recompiles it from the
tip of that repo and publishes the result as `/files/cv.pdf`, so the download
button always serves the current version — see
[`.github/workflows/README.md`](.github/workflows/README.md) for the details and
the one-time GitHub Pages setting it needs.

To build it by hand:

```bash
cd Awesome-CV && ./makecv.sh
```

## Deployment

`.github/workflows/deploy.yml` compiles the CV, builds the site and publishes it
to GitHub Pages on every push to `master`. GitHub Pages must be set to build
from GitHub Actions (Settings → Pages → Source), not from a branch.

## Credits

Theme: [Academic Pages](https://github.com/academicpages/academicpages.github.io)
/ [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) by Michael
Rose, MIT licensed. CV template:
[Awesome-CV](https://github.com/posquit0/Awesome-CV) by Claud D. Park.
