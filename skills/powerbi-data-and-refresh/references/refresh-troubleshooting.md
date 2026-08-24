# Refresh troubleshooting

A slow or failing refresh is almost always one table or one query, not the whole model. Do
not guess. Find the culprit, then fix that.

## Turn on failure notifications first

Do this on every model you publish, before any of the diagnosis below.

In the Service, open the semantic model settings, then Refresh. Under refresh failure
notifications, turn on the owner and add a group. A group survives the owner being away or
changing roles, which a single contact does not.

Two things it does not cover, so know the edges:

- A refresh that succeeds with wrong data is still a success. Notifications catch failures, not
  a query that quietly returned a short table. That is what the row ceiling guard in
  `rest-paging-pattern.md` is for.
- A model nobody owns, because the owner left, stops refreshing and notifies nobody. Take
  ownership of an inherited model before you rely on it.

## Diagnose

0. Work out which phase is slow before you change anything. Long per table timers while tables
   load is the data phase (source, network, duplication). A long pause at the end, after every
   table already shows a row count, is the recalc phase (calculated tables and columns, auto
   date/time). The two have opposite fixes. See `refresh-cost-model.md`.
1. Reproduce in Desktop. Home, then Refresh. A dialog lists every table with its own timer.
   Watch it. Healthy tables finish in seconds. The one still spinning after two or three
   minutes while the rest are done is the culprit. Cancel once you can see which one it is,
   you do not need to wait it out.
   - Note: the Power Query preview only pulls the first rows and often only the first page,
     so it does not reproduce a multi hour pull. Only a real refresh does.
2. In the Service, open the dataset settings, Refresh history, then the failed run, then
   Show. It lists the attempts and, where available, per table durations and the exact error.
   A repeating pattern of attempts that each run about 2 hours and then fail means a single
   query is hitting the 2 hour cap and being cancelled.

## What the common errors mean

- "The operation was cancelled" and "the exception was raised by the IDbCommand interface":
  a timeout or a source side cancellation. Not credentials. A query ran too long, or the
  source (for example ServiceNow) cancelled a heavy request. Fix by making that query
  cheaper (smaller pages, direct file reads, less duplication) and add a `Timeout`.
- "Formula.Firewall ... information could not be combined": privacy levels. Two sources with
  mismatched privacy are being combined. Set them consistently (often Organizational), or turn
  the firewall off at the model level (see below).
- "Please specify how to connect": missing or wrong credentials on that source.
- "The key did not match any rows" or a missing column: schema drift, the source changed its
  columns. Make the query tolerant (MissingField.Ignore, check column presence).

## The usual culprits, in order

1. A `SharePoint.Files("...site...")` call used to grab one file. It crawls the entire site
   first. Replace with a direct `Web.Contents` file URL. This is a frequent multi hour cause.
2. A REST page that is too large to build inside the source's transaction limit, so the
   source cancels it. Lower the page size (a few thousand), keep the row ceiling by raising
   max pages, add a `Timeout`.
3. Duplication: several loaded tables re-running the same expensive staging query. See
   `folding-and-duplication.md`. Reduce fan out or make the pull cheap.
4. A genuinely large table with no source side filter. Filter at the source, or use
   incremental refresh (below).
5. Auto date/time. On by default, and it builds a hidden calculated date table for EVERY date
   column in every Import table that is not on the many side of a relationship, each with six
   calculated columns, all rebuilt on every refresh. 10 date columns is 10 hidden tables and
   60 hidden calculated columns. One bad date value (a 1900 sentinel, or a blank feeding a
   DAX date expression, which resolves to 1899) makes a single one of those tables span
   centuries. Turn it off and use one date table you own. Detail in `refresh-cost-model.md`.

## The model level switches behind the firewall error

Three data access options live in `model.tmdl` and change how the mashup engine behaves for the
whole model. Desktop writes them when you change the matching setting in the UI, and they are
visible and editable in TMDL:

```tmdl
	dataAccessOptions
		fastCombine
		legacyRedirects
		returnErrorValuesAsNull
```

- `fastCombine` disables the privacy firewall. This is what lets one query combine an API pull
  with a workbook read without a Formula.Firewall error, and it is usually why a model that
  should not work does. Understand the trade before turning it on: with the firewall off, the
  engine may send data from one source to another as part of folding a query, so only use it
  where every source is inside your own tenant and you are comfortable with that.
- `returnErrorValuesAsNull` changes errors into nulls at load. It makes a refresh succeed that
  would otherwise fail, and it hides the row that was wrong. Prefer fixing the transform.
- `legacyRedirects` allows the older HTTP redirect handling. Leave it as Desktop set it.

If a model refreshes on one machine and fails on another, compare this block first.

## The Pro limits that bite

- A single refresh run is capped at 2 hours on Pro. Past that it is cancelled.
- 8 scheduled refreshes per day, at least 30 minutes apart. API triggered refreshes count.
- 1 GB model size. A model near the cap is slow to refresh and may fail.

See `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill for the full list.

## Incremental refresh on Pro

Incremental refresh is available on Pro and is the right tool for a large history that only
grows. Set RangeStart and RangeEnd parameters and a date filter. The catch: it only saves
work if the date filter folds to the source. For a non folding REST or SharePoint source,
inject the RangeStart and RangeEnd into the source request yourself (put the date range in
the API query string), otherwise Power BI still pulls everything before filtering.

## A safe fixing routine

- Make one change at a time and re-test in Desktop before publishing.
- Back up the pbip folder (a plain copy, or git) before editing.
- Keep changes that preserve row counts. If you change a page size, adjust max pages so the
  total ceiling is unchanged, so you never silently truncate data.
- After it refreshes fast in Desktop, republish. If the Service still fails, re-check the
  data source credentials and privacy levels in the dataset settings.
