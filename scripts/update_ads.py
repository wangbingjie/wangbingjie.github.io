#!/usr/bin/env python3
"""Refresh publication metrics and per-paper citation counts in index.html from NASA ADS.

Usage:  ADS_API_TOKEN=... python3 scripts/update_ads.py [path/to/index.html]

Rewrites, in place:
  * <span ... data-ads="first-papers|first-cites|first-h|all-papers|all-cites|all-h">
  * <span data-ads="asof">MM/YYYY</span>
  * <span class="paper-cites" data-bibcode="BIBCODE">N citations</span>  (one per paper tile)
    If ADS now lists the paper under a new bibcode (e.g. arXiv -> journal), the span's
    data-bibcode and the tile's ADS link are updated too.

Exits non-zero if ADS can't be reached or an expected marker is missing, so a failed
run never commits a half-updated page.
"""
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.adsabs.harvard.edu/v1"
ORCID = "0000-0001-9269-5046"
PAPER_TYPES = "doctype:(article OR eprint)"  # excludes proposals, abstracts, software, theses, errata
QUERIES = {
    "first": f'=first_author:"wang, bingjie" AND {PAPER_TYPES}',
    "all": f'((=author:"Wang, Bingjie" AND pubdate:[2015-01 TO *]) OR orcid:{ORCID}) AND {PAPER_TYPES}',
}


def ads(path, params=None, body=None):
    url = f"{API}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + os.environ["ADS_API_TOKEN"],
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def search(q, fl):
    return ads("search/query", {"q": q, "fl": fl, "rows": 2000,
                                "fq": "database:astronomy"})["response"]["docs"]


def metrics(bibcodes):
    m = ads("metrics", body={"bibcodes": bibcodes, "types": ["basic", "citations", "indicators"]})
    return {
        "papers": m["basic stats"]["number of papers"],
        "cites": m["citation stats"]["total number of citations"],
        "h": m["indicators"]["h"],
    }


def fmt(key, value):
    if key == "cites":  # rounded down to the nearest hundred: "> 900", "> 1.1k", "> 10.5k"
        floored = value // 100 * 100
        if floored < 1000:
            return f"&gt; {floored}"
        return f"&gt; {floored / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(value)


def sub_once(pattern, repl, text, what):
    new, n = re.subn(pattern, repl, text, flags=re.S)
    if n == 0:
        sys.exit(f"marker not found: {what}")
    return new


def main(path):
    html = open(path, encoding="utf-8").read()
    out = html

    # Headline metrics
    for group, q in QUERIES.items():
        docs = search(q, "bibcode")
        if not docs:
            sys.exit(f"ADS returned no records for {group!r}; refusing to write zeros")
        m = metrics([d["bibcode"] for d in docs])
        for key, value in m.items():
            out = sub_once(rf'(data-ads="{group}-{key}"[^>]*>)[^<]*(<)',
                           rf"\g<1>{fmt(key, value)}\g<2>", out, f"{group}-{key}")
        print(f"{group}: {m}")

    out = sub_once(r'(data-ads="asof"[^>]*>)[^<]*(<)',
                   rf"\g<1>{datetime.date.today():%m/%Y}\g<2>", out, "asof")

    # Per-paper citation counts
    wanted = re.findall(r'class="paper-cites" data-bibcode="([^"]+)"', out)
    if wanted:
        docs = search("identifier:(" + " OR ".join(f'"{b}"' for b in wanted) + ")",
                      "bibcode,identifier,citation_count")
        by_id = {}
        for d in docs:
            for ident in [d["bibcode"], *d.get("identifier", [])]:
                by_id[ident] = d
        for old in wanted:
            d = by_id.get(old)
            if d is None:  # keep the last known count rather than blanking it
                print(f"warning: {old} not found on ADS; leaving as is")
                continue
            new, n = d["bibcode"], d.get("citation_count", 0)
            label = "citation" if n == 1 else "citations"
            out = out.replace(
                re.search(rf'<span class="paper-cites" data-bibcode="{re.escape(old)}">[^<]*</span>', out).group(0),
                f'<span class="paper-cites" data-bibcode="{new}">{n} {label}</span>')
            if new != old:
                out = out.replace(f"/abs/{old}/", f"/abs/{new}/")
                print(f"{old} -> {new}")

    if out != html:
        open(path, "w", encoding="utf-8").write(out)
        print(f"updated {path}")
    else:
        print("no changes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "index.html")
