# The refresh cost model, and the defaults to set on day one

Most refresh advice is troubleshooting, which is what you read after a model is already slow.
This file is the design time version. It explains where refresh time actually goes, so you can
set the right defaults when the model is still empty and never have the problem.

## A refresh has two phases, and they fail for different reasons

A tabular refresh runs in two stages.

1. **Data phase.** Power Query runs each loaded query, pulls from the source, and the engine
   encodes and compresses the result into columns. Cost here is network round trips, source
   response time, and parsing.
2. **Recalc phase.** After the data lands, the engine rebuilds everything derived: calculated
   columns, calculated tables, relationships, and hierarchies. Cost here is CPU inside the
   engine. Nothing is read from the source during this phase.

Microsoft's TMSL refresh commands make the split explicit. `dataOnly` refreshes data and clears
dependents, `calculate` recalculates dependents only, and `full` does both. The processing
documentation says Process Data loads "without rebuilding hierarchies or relationships or
recalculating calculated columns", and Process Recalc "updates and recalculates hierarchies,
relationships, and calculated columns".

This matters because the two phases have opposite fixes. Filtering at the source does nothing
for a recalc problem. Deleting calculated columns does nothing for a slow API.

### Which phase is yours

- Refresh in Desktop and watch the per table timer. Long timers on individual tables while
  they load is a data phase problem. A long pause at the end, after every table shows a row
  count, is the recalc phase.
- If Desktop is fine but the Service is slow or fails, suspect the data phase, specifically
  duplication. Desktop refreshes all tables against a single shared cache. The Service does
  not. Microsoft states it plainly: "In a cloud environment, each query is refreshed using its
  own separate cache. So a query can't benefit from the same request having already been
  cached for a different query." A staging query referenced by 4 loaded tables is crawled
  once in Desktop and 4 times in the Service.

## What loads the data phase

Ranked for a Pro model reading a REST API and workbooks, which is round trip bound rather than
memory bound. This ranking is judgement, not a published list.

1. Query fan out. Referencing a loaded query re-runs it in full, including its API calls. See
   `folding-and-duplication.md`.
2. No source side filter. On a REST source nothing folds, so filter in the request itself
   (a date clause and a field list in the query string), not in M afterwards.
3. Reading one file by crawling a whole document library instead of a direct file URL.
4. Page sizes the source cannot assemble inside its own transaction limit, which surfaces as
   "the operation was cancelled".

## What loads the recalc phase

1. Calculated tables, rebuilt in full every refresh.
2. Calculated columns, rebuilt for the whole table even when only some rows changed.
3. Auto date/time, which is a large pile of both and is on by default. See below.

Two properties make this phase bite harder than people expect. The rebuild is total, not
incremental, so a calculated column is recomputed for every row of its table on every refresh.
And the work is dependency ordered, so a calculated table cannot start until the tables it
reads have finished. A long chain serialises.

The Best Practice Analyzer rule `REDUCE_NUMBER_OF_CALCULATED_COLUMNS` says calculated columns
"slow down processing times for both the table as well as process recalc". Microsoft's refresh
troubleshooting says to simplify the model "especially if it involves computationally expensive
calculated tables and columns".

## Auto date/time, the default that quietly fills the recalc phase

This is the single highest value default to change, because it is on out of the box and costs
nothing to turn off.

**What it creates.** One hidden date table per date column, not per table. Microsoft's rule is
that a hidden auto date/time table is generated for every column where all three are true: the
table storage mode is Import, the column type is date or date/time, and the column is not on
the many side of a relationship. Note the third condition. A model whose date dimension is not
related to anything qualifies almost everywhere.

Each generated table is itself a calculated table built with `CALENDAR`, carrying six
calculated columns (Day, MonthNo, Month, QuarterNo, Quarter, Year), a 4 level hierarchy, and
a relationship back to the host column. So 10 date columns is 10 calculated tables and 60
calculated columns that no one asked for, all rebuilt in the recalc phase of every refresh.
Microsoft: "When Power BI refreshes the model, each auto date/time table is also refreshed."

**What it costs.** Microsoft states the cost but publishes no number: "Each date column that
generates a hidden auto date/time table increases the model size and also extends the data
refresh time." Be honest about the evidence here. The published before and after measurements
are model size, not refresh duration. Treat "this will cut refresh time by X" as unproven and
measure your own model. The worked case at the end of this file is one measured example, where
removing 14 of these tables took a Service refresh from over an hour to about 15 minutes, but it
is a single case with other changes in the same pass.

**The row count trap.** Each table covers whole calendar years from the earliest to the latest
value in its column, one row per day. Microsoft's own example is 1,461 rows for data spanning
2016 to 2019. The trap is that one bad value sets the range. A sentinel date like 1900-01-01
for "unknown", or a far future placeholder, produces a table spanning centuries. Chris Webb
documented a file whose source held 9 date values generating hidden tables of 109,938 rows
each, which is exactly 1900 through 2200.

Watch for sentinels you create yourself. In DAX a blank date is treated as 30 December 1899, so
a calculated column like `DATE(YEAR(x), MONTH(x), 1)` silently produces 1899 rows whenever `x`
is blank, and the hidden date table then spans from 1899 to today.

**Turn it off, and where.** File, then Options and settings, then Options. The setting is under
Time intelligence on 2 pages. **Global** is labelled "Auto date/time for new files" and is the
one that matters for a new build. **Current file** applies to the file you have open. Both
default to on for a new installation. Microsoft's own instruction: "If the Auto date/time option
isn't relevant to your projects, disable the global Auto date/time option. It ensures that all
new Power BI Desktop files you create don't enable the Auto date/time option."

There is no tenant level or policy based enforcement. The realistic options for a team are the
per machine global setting, a `.pbit` template with it already off, or the Best Practice
Analyzer rule `REMOVE_AUTO-DATE_TABLE` as a review gate.

**Turning it off on an existing file removes the hidden tables, so things break.** Any visual
or filter using a built in date hierarchy loses its field, and any DAX using the extended
`Table[Date].[Year]` syntax stops working. Plan for a pass over date bound visuals afterwards.
If you are editing TMDL by hand rather than using the toggle, the `variation` blocks on the date
columns and the relationships to the hidden tables have to go too, otherwise the file will not
open.

**The replacement** is one date table you own, related to the facts, and marked as a date table.
That is a modeling job, see the `powerbi-modeling` skill.

## Defaults to set on a new model, before any real work

1. Turn off auto date/time globally, so every new file starts clean.
2. Build one date table and relate it to the facts. Mark it as a date table.
3. Disable load on staging queries, and keep the number of loaded tables that reference the same
   expensive staging query as low as possible.
4. Filter and select columns at the source. For a REST API that means the query string.
5. Keep the first argument of `Web.Contents` a literal string and push everything variable into
   `RelativePath` and `Query`, otherwise the Service refuses to refresh a dynamic data source.
6. Prefer a Power Query column over a DAX calculated column when the calculation only needs
   other columns of the same row. It compresses better and is not rebuilt in the recalc phase.

## The trap when you fix the data phase

Collapsing a derived Power Query table into a DAX calculated table removes repeated source
pulls, because a calculated table reads what is already in memory. It is an effective fix when
the source pull dominates, which is the usual shape of a multi hour Pro refresh.

Be clear about what it is, though. It moves cost from the data phase into the recalc phase, it
is not a free win, and the Best Practice Analyzer flags heavy use of calculated tables as
technical debt. Microsoft's own recommended fix for fan out is a dataflow, which on Pro means
Dataflow Gen1 and carries its own problems when a scheduled model reads it.

So the sequence that works is: fix the fan out, then go and clean up the recalc phase you just
loaded. A model that pushed 5 tables into calculated tables and still has auto date/time on
has moved its bottleneck rather than removed it.

## A worked case

A small Pro model, about 5 MB compressed, reading a paged REST API and a few workbooks. Every
timing below is the Power BI Service, not Desktop.

The starting point: the refresh genuinely needed about 3 hours of work, so every scheduled
run was cancelled at the 2 hour cap and failed. Desktop refreshed fine throughout, which is the
shared cache difference above rather than a sign the model was healthy. Note both facts. The cap
explains the failure, the 3 hours explains why it hit the cap.

Two fixes, in order.

1. Data phase. Derived tables that each re-ran the same staging queries were converted to DAX
   calculated tables, cutting the API chain runs from about 40 to 15 per refresh and the
   workbook downloads from 16 to 5. 3 hours became one to one and a half, and refreshes
   started completing.
2. Recalc phase. Auto date/time was turned off, removing 14 hidden date tables, and with them 84
   hidden calculated columns, from a model that already carried 8 calculated tables of its own.
   That hour or more became about 15 minutes.

Read the second step carefully, because it is the reason this file exists. Once the data phase
was fixed, roughly three quarters of the remaining refresh time turned out to be recalc rather
than data, and the hidden date tables were the largest single thing in that phase. A model can
look like it has a source problem when what it really has is a recalc problem.

That size of saving also says something about the hidden tables themselves. Date columns covering
only 2 calendar years would generate tables of a few hundred rows each, which could not cost
that much. Tables large enough to matter mean at least one date column was spanning decades or
centuries, which is the sentinel date trap above. Worth checking your own date columns for a
stray 1900, a far future placeholder, or a blank feeding a DAX date expression.

Caveats. The exact split of the second improvement was not measured, because per table refresh
timings in the Service need the XMLA endpoint, which is Premium. Other changes in the same pass
(a narrower date range on the fact) also reduced recalc work. Treat the numbers as one case, not
a benchmark.

## Measuring on Pro

- Desktop refresh dialog, per table timers. The most useful free signal you have.
- Service refresh history, for total duration, the attempt pattern, and the error.
- Best Practice Analyzer in Tabular Editor 2, against a locally open Desktop file. Free, and it
  catches auto date tables, unused columns, and heavy calculated columns.
- Per table timings inside the Service need XMLA or Log Analytics, which are Premium. On Pro you
  get "which table is fat" from Desktop and "how long it all took" from the Service, and you
  join the two yourself.
