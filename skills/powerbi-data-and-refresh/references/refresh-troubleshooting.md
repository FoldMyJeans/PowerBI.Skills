# Refresh troubleshooting

A slow or failing refresh is almost always one table or one query, not the whole model. Find the
culprit, then fix that.

## Turn on failure notifications first

Do this on every model you publish. In the Service, open the semantic model settings (a side pane
since August 2026, with a link back to the old page), then Refresh. Under refresh failure
notifications, turn on the owner and add a group. A group survives the owner being away or
changing roles.

What it does not cover:

- A refresh that succeeds with wrong data is still a success. That is what the row ceiling guard
  in `rest-paging-pattern.md` is for.
- On demand refreshes and refreshes started programmatically, including from Power Automate, send
  no failure email. Anything you trigger that way needs its own failure branch.
- A model whose owner left stops refreshing and notifies nobody. Take ownership of an inherited
  model before you rely on it.

## Diagnose

0. Work out which phase is slow. Long per table timers while tables load is the data phase
   (source, network, duplication). A long pause at the end, after every table shows a row count,
   is the recalc phase (calculated tables and columns, auto date/time). See `refresh-cost-model.md`.
1. Reproduce in Desktop. Home, Refresh. The dialog lists every table with its own timer. The one
   still spinning after two or three minutes while the rest are done is the culprit. Cancel once
   you can see it.
   - The Power Query preview pulls only the first rows, often only the first page, so it does not
     reproduce a multi hour pull. Only a real refresh does.
   - To time one suspect table alone, refresh just that table: right click it in Desktop's Data
     pane, or, since August 2026, pick it in web modeling's Model explorer. Web modeling's Refresh
     menu (August 2026) also offers Refresh data only and Sync schema only.
   - Read what a refresh actually did, not what the dialog showed. After a TMDL edit to one table's
     M, Desktop's "Refresh now" refreshed only that table, left the rest on three day old data, and
     showed no error. `$SYSTEM.TMSCHEMA_PARTITIONS` shows each partition's `RefreshedTime`. A TMSL
     full refresh per table, then `calculate` on the database, fixed it in under two minutes.
   - Changing a partition's M in TMDL opens that table empty until it is refreshed. New calculated
     columns compute on open.
2. In the Service, open the semantic model settings, Refresh history, the failed run, then
   Show. It lists the attempts and,
   where available, per table durations and the exact error. Attempts that each run about 2 hours
   and then fail are hitting the cap. The cap covers all the work in the attempt, so look at total
   work across the queries, not only one slow query.

## What the common errors mean

- "The operation was cancelled" and "the exception was raised by the IDbCommand interface": a
  timeout or a source side cancellation, not credentials. A query ran too long, or the source (for
  example ServiceNow) cancelled a heavy request. Make that query cheaper (smaller pages, direct
  file reads, less duplication). A `Web.Contents` call with no `Timeout` gives up at 100 seconds,
  which can look similar. The budget is in `rest-paging-pattern.md`.
- A credentials error after about an hour of loading, on an Entra OAuth source such as SharePoint
  Online. The token lasts about an hour and the Service waits up to 2 hours for data, so it can
  expire mid load. Shorten the run before you re-enter credentials. SharePoint OAuth also needs the
  account you sign in to the Service with, and the source in the same tenant. Microsoft names
  SharePoint Online, not a `Web.Contents` workbook read in particular, so that case is an inference
  from the shared credential type.
- `Container exited unexpectedly with code 0x0000DEAD`: Microsoft's documented action is to disable
  the schedule and republish. With incremental refresh, that republish also wipes the history (see
  `incremental-refresh.md`).
- "Formula.Firewall ... information could not be combined": two sources with mismatched privacy
  levels combined in one query. Set them consistently (often Organizational), or turn the firewall
  off at the model level (below).
- "Formula.Firewall: Query 'X' (step 'Y') references other queries or steps, so it may not
  directly access a data source": a query that both references another query and reads a source.
  Since July 2026 Desktop's preview option "Allow data privacy firewall partitions that reference
  other partitions to also access data sources" (on by default) allows it when privacy levels are
  compatible, as the Service already did. If you still see it, check that option before reaching
  for `fastCombine`.
- "Please specify how to connect": missing or wrong credentials on that source.
- "The key did not match any rows" or a missing column: schema drift. Make the query tolerant
  (`MissingField.Ignore`, check column presence, see `m-hardening.md`).

## The usual culprits, in order

1. `SharePoint.Files("...site...")` used to grab one file. It crawls the entire site first.
   Replace with a direct `Web.Contents` file URL. A frequent multi hour cause.
2. A REST page too large to build inside the source's transaction limit, so the source cancels
   it. Lower the page size (a few thousand), raise max pages to keep the row ceiling, and budget
   the `Timeout`.
3. Duplication: several loaded tables re-running the same expensive query. See
   `folding-and-duplication.md`.
4. A large table with no source side filter. Filter at the source, or use incremental refresh.
5. Auto date/time. One hidden calculated date table, with six calculated columns, for every
   qualifying date column, all rebuilt on every refresh. 10 date columns is 10 hidden tables and
   60 hidden calculated columns. One bad date value (a 1900 sentinel, or a blank feeding a DAX date
   expression, which resolves to 1899) makes one of them span centuries. Detail in
   `refresh-cost-model.md`.

## The model level switches behind the firewall error

Three data access options live in `model.tmdl` and change how the mashup engine behaves for the
whole model. Desktop writes them when you change the matching setting, and they are editable in
TMDL:

```tmdl
	dataAccessOptions
		fastCombine
		legacyRedirects
		returnErrorValuesAsNull
```

- `fastCombine` disables the privacy firewall. It is usually why a model that combines an API
  pull with a workbook read works when it should not. Since July 2026 Desktop's preview firewall option (above, on by default) clears the
  "references other queries" error without it when privacy levels are compatible, so check whether
  the model still does. With the firewall off, the engine may send data from one source to another
  while folding a query, so only use it where every source is inside your own tenant.
- `returnErrorValuesAsNull` turns errors into nulls at load. The refresh succeeds and the bad row
  is hidden. Prefer fixing the transform.
- `legacyRedirects` allows the older HTTP redirect handling. Leave it as Desktop set it.

If a model refreshes on one machine and fails on another, compare this block first.

## The Pro limits that bite

- 2 hours per refresh attempt. The cap covers all the work in the attempt, and applies to each
  attempt separately.
- 8 scheduled refreshes per day, at least 30 minutes apart. API triggered refreshes count, manual
  ones do not. A schedule with 13 half hourly slots does not save. The save fails with a 400 from
  `UpdateRefreshSchedule`, which usually means more than 8 slots are still set, or the settings
  page is stale. Reload, keep 8 or fewer slots, then save.
- 1 GB model size. A model near the cap is slow to refresh and may fail.
- 10 GB of uncompressed data processed during a refresh on shared capacity. If refresh fails on
  this, import less.
- A full refresh can use up to double the model's memory, because the Service keeps a snapshot
  until it completes. Watch peak memory as well as resting size.

The full list is `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.

## How a schedule stops or misleads without anyone deciding

- Four consecutive failures, or an unrecoverable error such as expired credentials, deactivates
  the schedule. The threshold cannot be changed. Fix the cause, then turn the schedule back on.
- Two months with nobody visiting a report or dashboard built on the model pauses the schedule.
  The owner is emailed and the schedule shows as Disabled. Any view resets the counter.
- Start times slip. The target is within 15 minutes of the slot, the delay can reach an hour, and
  a refresh can begin up to 5 minutes early. Do not chain one refresh to another on a clock gap.
- A run marked Completed can carry warnings, including for memory limits. The refresh history
  shows them, the REST APIs for refresh history and execution details do not.

Sources: https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios
and https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh

## Incremental refresh on Pro

Available on Pro, and right for a large history that only grows. The date range has to reach the
source: on a non folding REST or SharePoint source, put RangeStart and RangeEnd in the request
yourself, or each partition repeats the full pull. Read `incremental-refresh.md` first, because a
republish wipes the partitions.

## A safe fixing routine

- One change at a time, re-tested in Desktop before publishing.
- Back up the pbip folder (a plain copy, or git) before editing.
- Keep row counts. If you change a page size, adjust max pages so the ceiling is unchanged.
- After it refreshes fast in Desktop, republish. If the Service still fails, re-check the data
  source credentials and privacy levels in the model settings. Desktop does not publish privacy
  settings, so they have to be reapplied there.
