# Seed Data

This document describes the minimal deterministic seed dataset for Release 1.

## Purpose

The seed dataset makes the alpha usable locally without depending on:

- live web scraping
- external ingestion sources
- large raw corpora downloads

It is intentionally small and predictable.

## What The Seed Includes

### Dictionary entries

The seed loads a few lexical entries through the current term and dictionary repositories:

- `mtu`
- `watu`
- `soma`

Each entry includes:

- Swahili meaning
- English translation
- small synonym list
- one usage example

### Linguistic sample

The seed loads a tiny POS-style sample into `grammar_pos` using local fixture rows.

It includes token examples around:

- `mtu`
- `watu`
- `anasoma`
- `wanasoma`
- `ninakupenda`

### News/example records

The seed loads a few deterministic local `news` rows with:

- category
- content
- stable local `source_url` values using the `seed://` scheme
- optional sentiment values

## How To Load The Seed

From the repository root:

```bash
python3 scripts/seed_release1_alpha.py
```

Or with Make:

```bash
make seed-data
```

The seed script initializes the database first, then inserts any missing seed rows.

## Fixture Files

The seed fixtures live in:

- `data/seed/release1_dictionary.json`
- `data/seed/release1_linguistic_sample.json`
- `data/seed/release1_news.json`

## Notes

- The seed is designed to be small and deterministic.
- It avoids live external scraping.
- It is intended for local/internal alpha readiness, not production data loading.
