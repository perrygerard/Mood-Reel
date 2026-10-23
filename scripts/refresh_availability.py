#!/usr/bin/env python3
"""Re-check which services carry each title and drop titles that have left all of them.

Usage:
    export TMDB_TOKEN="your TMDB API Read Access Token"
    python3 scripts/refresh_availability.py            # update data/titles.json
    python3 scripts/refresh_availability.py --dry-run  # report only

Streaming availability comes from TMDB's watch-provider data (powered by JustWatch), US region.
Titles keep their tags, blurbs and images; only the service list (index 10) changes.
"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TITLES = ROOT / "data" / "titles.json"

# TMDB provider ids -> Mood Reel service codes
# BritBox (151 standalone, 197 Prime Video channel) shows up under the Prime Video filter in the app
PROVIDERS = {8: "n", 1796: "n", 9: "p", 119: "p", 15: "h", 151: "b", 197: "b"}
NAMES = {"n": "Netflix", "p": "Prime Video", "h": "Hulu", "b": "BritBox"}


def get(path, token):
    req = urllib.request.Request(
        "https://api.themoviedb.org/3" + path,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    for _ in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            continue
    return None


def services_for(tmdb_key, token):
    kind = "movie" if tmdb_key[0] == "m" else "tv"
    data = get(f"/{kind}/{tmdb_key[1:]}/watch/providers", token)
    if data is None:
        return None  # lookup failed; leave the title as it is
    us = data.get("results", {}).get("US", {})
    offers = us.get("flatrate", []) + us.get("ads", [])
    return "".join(sorted({PROVIDERS[o["provider_id"]] for o in offers if o["provider_id"] in PROVIDERS}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = ap.parse_args()

    token = os.environ.get("TMDB_TOKEN")
    if not token:
        sys.exit("Set TMDB_TOKEN to your TMDB API Read Access Token first.")

    titles = json.loads(TITLES.read_text())
    keys = list(titles)

    with cf.ThreadPoolExecutor(10) as ex:
        results = dict(zip(keys, ex.map(lambda k: services_for(titles[k][11], token), keys)))

    changed, removed, failed = [], [], []
    for k, svc in results.items():
        if svc is None:
            failed.append(k)
        elif not svc:
            removed.append(k)
        elif svc != titles[k][10]:
            changed.append((k, titles[k][10], svc))

    for k, old, new in changed:
        print(f"~ {titles[k][0]}: {', '.join(NAMES[c] for c in old)} -> {', '.join(NAMES[c] for c in new)}")
    for k in removed:
        print(f"- {titles[k][0]} (no longer on Netflix, Prime Video, BritBox or Hulu)")
    print(f"\n{len(changed)} changed, {len(removed)} gone, {len(failed)} lookups failed, {len(titles)} total")

    if args.dry_run:
        return
    for k, _, new in changed:
        titles[k][10] = new
    for k in removed:
        del titles[k]
    TITLES.write_text(json.dumps(titles, separators=(",", ":"), ensure_ascii=False))
    print(f"Wrote {TITLES.relative_to(ROOT)}. Images for removed titles stay in their bundles until you repack.")


if __name__ == "__main__":
    main()
