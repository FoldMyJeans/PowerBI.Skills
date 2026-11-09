# Incremental refresh on Pro

Supported on Pro, and it does not change the 2 hour cap. Each refresh reloads only the recent
partitions, history stays in the Service. Most of this file comes from Microsoft docs and has not
been run on a real model here, so treat the REST form as a pattern to test.

## The date range has to reach the source

Microsoft requires that the source can filter by date in some way, not that the query folds. A
filter added as a later step has to fold into the first step. A range built into the request does
not, and the final query can be non folding.

On a REST source, put `RangeStart` and `RangeEnd` inside the `Query` record of `Web.Contents`, in
the format the API wants, inclusive start and exclusive end. For a ServiceNow Table API, both
bounds go in `sysparm_query`:

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

The rest of the paging loop stays as in `rest-paging-pattern.md`.

- `RangeStart` and `RangeEnd` are Power Query date/time parameters with those reserved, case
  sensitive names. Reference them by hand, the Custom Filter dialog cannot.
- On a REST source the policy dialog warns that it cannot check folding. Prove the filter reached
  the source with Query Diagnostics, by reading the request.
- The current date is worked out in UTC unless you set a time zone under Refresh. Check how your
  API reads the times you send.

If the filter does not reach the source, Power BI pulls every row and filters locally, once per
partition, because one query runs for every partition. A paged pull with no working filter repeats
the full pull for each partition and can run out of resources or time.

Files in dated folders work the same way, with the parameters choosing which files to read.
Microsoft calls workbooks in a folder and files in SharePoint advanced scenarios that need their
own testing.

## Pick a partition date that never changes

A row lives in the partition its date points at. If that date changes at the source, the update is
treated as an insert plus a delete. A delete in the historical range is not picked up, so totals
in closed periods move, or the refresh fails with a uniqueness error on the one side of a
relationship or a partition key conflict. On Pro you cannot refresh a single partition to repair
that. For ticket style data, partition on the created date, not on a last updated date.

## Make the refresh window as long as a record can change

History is not reloaded, so a change after a row leaves the refresh window never reaches the
model. A ticket opened in March and closed in June keeps its March values with a 30 day window.
That follows from the documented partition behaviour, though no source states it for a particular
product. Set the window to at least the longest time a record stays open.

Deletes follow the same rule. A delete inside the window disappears with the reload, a delete in a
historical partition stays in the model. If deletes matter, the window has to cover them, or the
table should not use a policy.

## The Pro republish trap

The cost to weigh before you turn it on.

- Once published, a republish from Desktop removes the existing partitions and data. The way round
  is metadata only deployment through the XMLA endpoint, which is Premium.
- You cannot download the model back as a pbix.
- So every model change made in Desktop means a full reload of everything the policy keeps, and
  bootstrapping that load in stages is Premium too.
- Since January 2026 web modeling can edit a published incremental refresh model in the Service on
  Pro (Write permission and the tenant setting needed, no undo). Power Query on the web is not
  available for these models, so this covers model edits such as measures, not M. Whether such an
  edit keeps the partitions is not tested here. Try it on a copy first.
- If the first refresh times out on Pro, the documented remedy is to delete the incomplete model,
  republish, and refresh again. Partitions cannot be inspected on Pro, so diagnosis is trial and
  error.

Treat first load cost as the design limit. Judgement: size the archive period so a full load fits
inside one 2 hour attempt, because a model that cannot reload after one small schema edit is worse
than a slow one. Run the first refresh by hand so you can watch it. A separate thin report file
should stop report edits from forcing a model republish, though that is reasoned rather than
tested.

When that cost is unacceptable, freeze closed history instead (`rest-paging-pattern.md`). A frozen
range survives a republish.

## What it does not fix

- The recalc phase. Merging partitions and recalculation still run each refresh, and calculated
  tables and columns still rebuild. See `refresh-cost-model.md`.
- Desktop timers stop predicting the Service, because Desktop loads only the small parameter window.
- Shared Gen1 dataflows. Incremental refresh does not work in them.

`Detect data changes` is optional and adds a column kept in memory, so reduce its precision if you
use it. `Only refresh complete days` is optional on Pro.

Sources: https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview and
https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-troubleshoot
