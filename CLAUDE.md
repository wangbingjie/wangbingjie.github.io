# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal academic website for Bingjie Wang (NASA Hubble Fellow, Princeton), served via GitHub Pages at `wangbingjie.github.io`. The repo *is* the deployed site — pushing to `master` publishes. There is no build step and no package manager.

## Local preview

Open `index.html` directly in a browser, or serve the directory for relative-path correctness:

```
python3 -m http.server 8000   # then visit http://localhost:8000
```

`config.codekit` is metadata from the CodeKit GUI app; it is not required for development and can be ignored.

## Layout and what's hand-edited vs. vendored

- `index.html` — the only page on the site. All visible content (bio, research blurb, press list, publication counts, links) is hand-edited here. Most updates to this site are edits to this one file.
- `css/styles.css`, `css/queries.css` — site-specific styles (queries.css holds responsive overrides). All other files in `css/` are vendor (Bootstrap, animate.css) — do not edit them.
- `js/scripts.js` — the only JS: dependency-free IntersectionObserver fade-ins on `.wp1`–`.wp6`. There is no jQuery or Waypoints. There are no sliders; the intro and About-me sections are plain markup.
- CDN assets (Font Awesome 5.15.4 on cdnjs, academicons 1.9.6 on jsDelivr) are pinned to exact versions with SRI `integrity` hashes; recompute the hash when bumping a version.
- `img/` — photos and figure cutouts referenced from `index.html`.
- `Wang_Bingjie_CV.pdf`, `wang_aas_2021.pdf` — assets linked directly from the page; replace in place when updating.

## Things that need manual updates and are easy to miss

These values are hardcoded in `index.html` and drift out of date — check them when the user asks to "update the site":

- Publication counts, citations, h-index and the "as of MM/YYYY" date are **automated**: `.github/workflows/update-ads.yml` runs `scripts/update_ads.py` on the 15th of each month (needs the `ADS_TOKEN` repo secret) and rewrites the `<span data-ads="...">` elements in place. Don't hand-edit those numbers or remove the `data-ads` attributes; to refresh locally run `ADS_API_TOKEN=... python3 scripts/update_ads.py`. "Papers" = ADS doctype article OR eprint.
- The SciX (formerly ADS) search URLs in the avatar social bar and the publication metrics — `https://scixplorer.org/search?q=...&sort=date+desc`, with `q` set to the same queries `scripts/update_ads.py` counts (plus `collection:astronomy`), so the linked lists match the numbers. Paper links use `https://scixplorer.org/abs/<bibcode>/abstract`; on-page text says "SciX (ADS)". The metrics script still calls the ADS API at api.adsabs.harvard.edu.
- Affiliation strings (`<title>`, footer email) — the page title currently says "Princeton University"; older revisions said "Johns Hopkins University".
- The Research section's prose (`.research-text`, one `<p>` per paragraph) is a curated narrative with inline SciX links to specific papers; new highlights are added by editing these paragraphs, not by appending a list.

## Conventions

- Section anchors used by the top nav (`<nav class="site-nav">`): `#intro`, `#research`, `#pubs`, `#press`, `#life`, each on its own `<section>`. New sections that should appear in the nav need a matching `id=` and an `<a>` in `.site-nav`.
- `#research`, `#pubs` and `#press` are separate sections styled to read as one block (`.flow-start` / `.flow-end` paddings in `css/styles.css`).
- Paragraph spacing uses real `<p>` tags inside a `.prose` wrapper, not `<br><br>`.
- Animation triggers: applying class `wp1`–`wp6` to an element makes `js/scripts.js` add `animated fadeIn*` when it scrolls into view. Reuse these instead of writing new scroll handlers.
- External links open in new tabs (`target="_blank"`); keep this for consistency.
