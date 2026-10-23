# Mood Reel

Find something to watch by how you feel, not by scrolling.

Mood Reel is a Libby-style discovery page for movies and series on **Netflix, Prime Video (including BritBox) and Hulu** (US). You build a sentence one tap at a time:

> Find me **a series** on **Prime Video** that is **understated** and *a whodunit*

Each choice starts as a tag and turns into a film-strip pill in the sentence. Tap a pill to change that step.

- **1,583 titles**, most of them hidden gems: well-reviewed titles that rarely surface on the services' own rows.
- **20 moods** in Netflix's own vocabulary (understated, witty, ominous, mind-bending…), grouped into *Light and easy*, *Slow and stirring* and *Tense and dark*.
- **Story types** for every mood (whodunits, period pieces, true stories, heists…), each shown as a collage of its best matches.
- **Five picks at a time.** Each story deals 5 titles, weighted toward the best matches, and avoids repeats until you've seen the whole pool. *Deal me 5 more* gets a fresh hand.
- **Swipe up to hide** anything you've already seen (with undo). **♡ My list** saves titles for later. Both live in your browser.
- **Pull down** from the results to start over at the moods.

It's a single static page with no build step and no server.

## Run it

**GitHub Pages:** push this repo, then go to *Settings → Pages*, set the source to *Deploy from a branch*, choose `main` and `/ (root)`, and save. The site appears at `https://<your-username>.github.io/<repo-name>/` within a minute or two.

**Locally:** the page loads its data with `fetch`, so open it through a local server rather than double-clicking the file:

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## How it's put together

```
index.html            the whole app: markup, styles and script
data/titles.json      every title with its tags
data/art0–28.json     small title images (400px WebP, base64), 60 per bundle
data/hi0–432.json     sharper stills (640px WebP) for the story collages, grouped by mood and story
scripts/              maintenance scripts
```

Image bundles are only downloaded when a screen needs them, so the first load is just `index.html` and `titles.json`.

Each entry in `data/titles.json` is keyed by an id and holds:

| Index | Field |
|---|---|
| 0 | Title |
| 1 | Year |
| 2 | `m` movie or `s` series |
| 3 | Runtime in minutes (movies) |
| 4 | One-line description |
| 5 | Moods, space-separated, main mood first |
| 6 | Story types, space-separated (codes listed in `STORY` in `index.html`) |
| 7 | Setting |
| 8 | `1` if a hidden gem |
| 9 | Small image bundle number (`data/art{n}.json`) |
| 10 | Services: `n` Netflix, `p` Prime Video, `h` Hulu, `b` BritBox |
| 11 | TMDB id (`m123` movie, `s456` series) |
| 12 | Still bundle number (`data/hi{n}.json`) |

BritBox titles appear under the Prime Video filter, since BritBox is a Prime Video channel in the US. It's a paid add-on, so those cards link to it as "Find on BritBox".

## Keeping it current

Streaming catalogs change weekly. To re-check which services carry each title and drop the ones that have left:

```sh
export TMDB_TOKEN="your TMDB API Read Access Token"
python3 scripts/refresh_availability.py --dry-run   # see what would change
python3 scripts/refresh_availability.py             # update data/titles.json
```

Get a free token at [themoviedb.org](https://www.themoviedb.org/settings/api). Never commit it; the script only reads it from the environment.

Adding new titles means writing tags and a one-line description for each one, then packing its images into the bundles. That part is done by hand (or with an LLM) and isn't scripted here.

## Credits

Title data and images from [TMDB](https://www.themoviedb.org/). Streaming availability from [JustWatch](https://www.justwatch.com/) via TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB. Mood Reel isn't affiliated with Netflix, Amazon, BritBox or Hulu.

Typefaces: Instrument Serif, Instrument Sans and Fragment Mono via Google Fonts.
