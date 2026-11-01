# Test on fake data

`scripts/build_fixture.py` builds a PBIP with no real data in it, so a chart can be opened in Desktop and
its screenshots shared. Use it before putting a new chart in a report, and to see a chart at a new size.

```powershell
python scripts\build_fixture.py --from "C:\work\ABC Sales" --out "C:\work\chart-fixture"
```

`--from` is any project Desktop saved. Only its schema versions, report settings and static resources are
read. Its pages and tables are not copied. Keep `--out` outside any repo, because the static resources can
include a real theme or logo.

Open `ABC_Charts.pbip` in Desktop. Each recipe sits on a page with the fields already bound. To change a
chart, edit its spec, rebuild, and reopen. Do not publish it.

## Why it needs no refresh

Every table is a `DATATABLE` calculated table in TMDL, with its rows in the file. Desktop works those out
when the project opens, with no cache, credentials or data source. This is a fair way to build any fake
model. It is the one PBIP here not started in Desktop, because no real source ever has to connect. For a
real report still follow `powerbi-pbir-builder`, which starts from a PBIP Desktop saved.

## Traps building it hit

- **Table names.** `EVALUATE ADDCOLUMNS ( Kpi, ...)` failed with "The syntax for 'Kpi' is incorrect" and
  renaming to `KpiDim` fixed it. A table called `Calendar` with dates written as `2025-01-01T00:00:00`
  came back empty. Renaming it and writing `2025-01-01 00:00:00` fixed that, though both changed at once.
- **TMDL parsing.** Desktop reports a bad file on open: "TMDL objects cannot be merged because both
  declare the same property: expression" named the measure at fault. Desktop then shows an empty report,
  so a blank report after an edit means read that dialog.

## What the test covered

On Desktop in November 2026 with Deneb 2.0.1, each page rendered from a fresh open:

- Every Deneb chart drew from a `visual.json` written by the helper, with Deneb fetched by Desktop.
- An alias renamed a field for a spec.
- The bullets and sparklines drew in a table, and the card in an image visual and a table.
- The native butterfly drew, with the minus sign hidden.
- The hidden drawer page drew in Desktop, and the page shows the hidden icon on its tab.
- The dark page followed a page filter set to Dark.

Numbers matched the fixture by eye. They were not asserted with DAX, since the data is fake.

## What it did not cover

These were not done, so test them before relying on them. They are listed in the repo's test backlog.

- Publishing to the Service. So Deneb in a browser, in the app, and under a tenant's visual settings.
- Export to PDF or PowerPoint, including whether the card's bars draw when animation does not run.
- Whether the card's bars move in Desktop. A screenshot only shows the finished bars.
- Any click: the drawer's buttons, the slicer sync, the bump highlight, and Deneb cross-filtering.
- Real row counts. The largest fixture is two years of days. The beeswarm's force layout is the one to
  watch.
- The floor plan on a real traced plan, and Synoptic Panel Lite.
