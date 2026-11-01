# Incremental refresh on Pro

Incremental refresh is supported on Pro, and it does not change the 2 hour cap. Each refresh reloads
only the recent partitions, and history stays in the Service. Most of this file comes from Microsoft
docs and has not yet been run on a real model here, so treat the REST form as a pattern to test.

## The date range has to reach the source

Microsoft's requirement is that the source can filter by date in some way, not that the query folds.
A filter added as a later step does have to fold into the first step. A range built into the request
does not, and the final query can be non folding.

So on a REST source, put `RangeStart` and `RangeEnd` inside the `Query` record of `Web.Contents`,
formatted the way the API wants them, with an inclusive start and an exclusive end. For a ServiceNow
Table API, both bounds go in `sysparm_query`:

```m
  StartDate = DateTime.ToText(RangeStart, [Format = "yyyy-MM-dd", Culture = "en-US"]),
  StartTime = DateTime.ToText(RangeStart, [Format = "HH:mm:ss", Culture = "en-US"]),
  EndDate   = DateTime.ToText(RangeEnd, [Format = "yyyy-MM-dd", Culture = "en-US"]),
  EndTime   = DateTime.ToText(RangeEnd, [Format = "HH:mm:ss", Culture = "en-US"]),

  // The partition date is the created date. See the next section for why.
  FullQuery = "sys_created_on>=javascript:gs.dateGenerate('" & StartDate & "','" & StartTime & "')"
            & "^sys_created_on<javascript:gs.dateGenerate('" & EndDate & "','" & EndTime & "')"
            & "^ORDERBYsys_id",
```

Everything else in the paging loop stays as it is in `rest-paging-pattern.md`.

- The parameters are Power Query date/time parameters with the reserved, case sensitive names
  `RangeStart` and `RangeEnd`. You reference them by hand, the Custom Filter dialog cannot.
- Desktop shows a warning in the policy dialog when it cannot check folding, and on a REST source it
  will. Then prove the filter reached the source with Query Diagnostics, by reading the request.
- The current date is worked out in UTC unless you set a time zone under Refresh. Check how your API
  reads the times you send.

If the filter does not reach the source, Power BI pulls every row and filters locally, and it does
that once per partition, because one query runs for every partition. A paged pull with no working
filter therefore repeats the full pull for each partition and can run out of resources or time.

Files in dated folders work the same way, with the parameters choosing which files to read. Microsoft
calls workbooks in a folder and files in SharePoint advanced scenarios that need their own testing.

## Pick a partition date that never changes

A row lives in the partition its date points at. If that date changes at the source, Microsoft treats
the update as an insert plus a delete. When the delete falls in the historical range it is not picked
up, so totals in closed periods move, or the refresh fails with a uniqueness error on the one side of
a relationship or a partition key conflict. On Pro you cannot refresh a single partition to repair
that.

For ticket style data, partition on the created date, not on a last updated date.

## Make the refresh window as long as a record can change

History is not reloaded, so anything that changes after it leaves the refresh window never reaches
the model. A ticket opened in March and closed in June keeps its March values if the window is 30
days. That follows from the documented partition behaviour, though no source states it for a
particular product. Set the window to at least the longest time a record stays open, and accept that
a longer window reloads more.

Rows deleted at the source follow the same reasoning. A delete inside the refresh window disappears
with the reload, a delete in a historical partition stays in the model. If deletes matter, the window
has to cover them, or the table should not use a policy at all.

## The Pro republish trap

This is the cost to weigh before you turn it on.

- Once it is published, a republish from Desktop removes the existing partitions and data. The way
  round that is metadata only deployment through the XMLA endpoint, which is Premium.
- You cannot download the model back as a pbix.
- So every model change on Pro means a full reload of everything the policy keeps, and bootstrapping
  that load in stages is Premium too.
- If the first refresh times out on Pro, the documented remedy is to delete the incomplete model,
  republish, and refresh again. Partitions cannot be inspected on Pro, so diagnosis is trial and
  error.

Treat first load cost as the design limit. Judgement: size the archive period so a full load fits
inside one 2 hour attempt, because a model that cannot reload after one small schema edit is worse
than a slow one. Run the first refresh by hand so you can watch it. Keeping the report in a separate
thin report file should stop report edits from forcing a model republish, though that is reasoned
rather than tested.

When that cost is unacceptable, freeze closed history instead, as described in
`rest-paging-pattern.md`. A frozen range survives a republish.

## What it does not fix

- The recalc phase. Merging partitions and recalculation still run on each refresh, and calculated
  tables and columns still rebuild. See `refresh-cost-model.md`.
- Desktop timers stop predicting the Service, because Desktop now loads only the small parameter
  window.
- Shared Gen1 dataflows. Incremental refresh does not work in them.

`Detect data changes` is optional and adds a column kept in memory, so reduce its precision if you use
it. `Only refresh complete days` is optional on Pro.

Sources: https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview and
https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-troubleshoot
