# Bayesian Adversarial Machine Learning — book companion

A small, dependency-free site for the book’s chapter resources. It is designed for GitHub Pages at **https://bayesian-adversarial-ml.github.io/**.

## Edit the content

Edit `data/catalog.json`, then rebuild:

```sh
python3 build.py
```

The catalogue contains the book’s title, author links, description, and one object per chapter. Every chapter has a summary, topics, code repositories, papers, and optional further resources. Resources without URLs and sections without linked resources are omitted from the published pages.

Repository descriptions distinguish chapter implementations from related tools and examples. Paper links must lead to full text available without a subscription or sign-in, using open publisher pages or author/institutional preprints. Omit papers without a verified open version. The generated pages include no manuscript text beyond the short chapter descriptions in the catalogue, and no analytics or third-party scripts.

Chapter routes use `slug`; avoid changing these after publication unless redirects are added. The build rewrites known pages but intentionally does not delete unrelated files in `docs/`. If a chapter slug is changed, remove its obsolete generated folder separately.

## Images and appearance

The home illustration defaults to `assets/cover-study.svg`. To replace it, add a file inside `assets/` and set:

```json
"coverImage": "assets/home-illustration.jpg",
"coverAlt": "Description of the illustration",
"coverCaption": "Optional image credit"
```

Each chapter also accepts `image`, `imageAlt`, and optional `imageCaption` fields. Leave `image` blank to omit the image; fill it with an `assets/…` path or a public HTTPS URL when ready. Supply meaningful alternative text and any required credit. Put all local images in `assets/` so the build copies them into the published directory.

The visual system lives in `assets/site.css`: warm ivory, ink, and cobalt; system sans-serif labels and Georgia headings. It uses no external font service. `assets/site.js` implements accessible resource search and filters. All content and links remain available without JavaScript.

## Preview

```sh
python3 build.py
python3 -m http.server 8000 --directory docs
```

Open <http://localhost:8000>. Check the home page, a long chapter title, and the resources page at desktop and phone widths. Resource search and the chapter/type filters work together; chapter pages link directly to their filtered resource list.

## Publish to GitHub Pages

The intended organization is `bayesian-adversarial-ml`, and the repository is `bayesian-adversarial-ml.github.io`.

1. Commit the source files **and the generated `docs/` folder** to `main`.
2. In repository **Settings → Pages**, select **Deploy from a branch**, branch `main`, folder `/docs`.
3. Confirm the resulting URL is <https://bayesian-adversarial-ml.github.io/>.

No build action or package installation is needed. `.nojekyll` keeps the generated site static. Re-run `python3 build.py` before committing any content or asset changes. If the organization or site URL changes, update the book fields in `data/catalog.json` and rebuild; these also control the sitemap, canonical metadata, and correction link.

Only this standalone website repository should be published. The book manuscript and private working materials are not part of this site.

## Files

- `data/catalog.json` — editable chapter content and resource URLs.
- `build.py` — Python standard-library page builder.
- `assets/` — styles, script, favicon, artwork, and future chapter images.
- `docs/` — generated GitHub Pages site, including `404.html`, `sitemap.xml`, and `robots.txt`.

The website does not change the licenses of any linked software, papers, or images. Consult each linked project for its own terms.
