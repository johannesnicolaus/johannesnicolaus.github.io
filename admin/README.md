# Sveltia CMS (Admin)

This folder contains the Sveltia CMS admin for this Jekyll site.

## Quick overview
- CMS config: `admin/config.yml`
- Admin UI entry: `admin/index.html`

## Local testing (token)
1. Start the Jekyll site locally:

```bash
bundle install
bundle exec jekyll serve
```

2. Serve the admin folder (you can use the npm helper script):

```bash
npm install
npm run serve:admin
# opens at http://localhost:9000 by default
```

3. Open the admin UI in the browser: `http://localhost:9000` (or `http://localhost:4000/admin` if you prefer to use the built-in site server).

4. Sign in using **Access token**: create a GitHub personal access token with `repo` (or `public_repo`) scope and paste it into the admin UI when prompted. Do NOT commit tokens to the repository.

## Local testing (OAuth)
If you prefer OAuth (recommended for multiple users), create a GitHub OAuth App:

1. On GitHub, go to Settings → Developer settings → OAuth Apps → New OAuth App.
2. Application name: `Sveltia CMS for personal_website_2` (or similar).
3. Homepage URL: `http://localhost:4000`
4. Authorization callback URL: use the authenticator service you plan to use. For Netlify's built-in flow use `https://api.netlify.com/authenticate`.

Update `admin/config.yml` with your OAuth base URL if you use a custom authenticator, for example:

```yaml
backend:
  name: github
  repo: johannesnicolaus/personal_website_2
  base_url: https://api.netlify.com    # or your authenticator origin
  auth_endpoint: auth
  branch: main
```

Do not add client secrets or tokens to the repo.

## Notes and recommendations
- `media_folder` and `public_folder` in `admin/config.yml` point to `/images` — check that matches your actual image path.
- If your default branch is `master` instead of `main`, change `branch: main` accordingly in `admin/config.yml`.
- To restrict login methods set `auth_methods: [oauth]` or `[token]`.

## Troubleshooting
- If the editor does not show collections, open browser dev tools and check console errors — common issues are CORS or incorrect repo name/branch.
- For OAuth errors, verify the OAuth App callback and the `base_url` are correct.

