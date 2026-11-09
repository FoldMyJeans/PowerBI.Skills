# The refresh cost model, and the defaults to set on day one

The design time view: where refresh time goes, so the defaults are right while the model is still
empty. For a model that is already slow or failing, start with `refresh-troubleshooting.md`.

## Two phases, two different fixes

1. **Data phase.** Power Query runs each loaded query, pulls from the source, and the engine
   encodes and compresses the result. Cost is network round trips, source response time, parsing.
2. **Recalc phase.** The engine rebuilds everything derived: calculated columns, calculated
   tables, relationships, hierarchies. Cost is CPU inside the engine. Nothing is read from the
   source.

The TMSL refresh types make the split explicit: `dataOnly` refreshes data and clears dependents,
`calculate` recalculates dependents only, `full` does both. Filtering at the source does nothing
for a recalc problem. Deleting calculated columns does nothing for a slow API.

### Which phase is yours

- Refresh in Desktop and watch the per table timers. Long timers while tables load is the data
  phase. A long pause at the end, after every table shows a row count, is the recalc phase.
- Desktop fine but the Service slow or failing: suspect duplication in the data phase. The
  Service gives each query its own cache, so a staging query referenced by 4 loaded tables is
  crawled 4 times. See `folding-and-duplication.md`.

## What loads the data phase

Ranked for a Pro model reading a REST API and workbooks, which is round trip bound rather than
memory bound. The ranking is judgement, not a published list.

1. Query fan out. Referencing a loaded query re-runs it in full, API calls included.
2. No source side filter. On a REST source nothing folds, so filter in the request (a date clause
   and a field list in the query string), not in M afterwards.
3. Reading one file by crawling a whole document library instead of a direct file URL.
4. Page sizes the source cannot assemble inside its own transaction limit, which surfaces as
   "the operation was cancelled".

## What loads the recalc phase

1. Calculated tables, rebuilt in full every refresh.
2. Calculated columns, rebuilt for every row of the table even when only some rows changed.
3. Auto date/time, a large pile of both, on by default.

The work is dependency ordered, so a calculated table cannot start until the tables it reads have
finished. A long chain serialises. The Best Practice Analyzer rule
`REDUCE_NUMBER_OF_CALCULATED_COLUMNS` says calculated columns "slow down processing times for both
the table as well as process recalc".

## Auto date/time, the default that quietly fills the recalc phase

The highest value default to change: on out of the box and free to turn off.

**What it creates.** One hidden date table per date column, not per table. A column qualifies when
all three hold: the table is Import, the column is date or date/time, and the column is not on the
many side of a relationship. A model whose date dimension is related to nothing qualifies almost
everywhere.

Each generated table is a calculated table built with `CALENDAR`, with six calculated columns (Day,
MonthNo, Month, QuarterNo, Quarter, Year), a 4 level hierarchy, and a relationship back to the host
column. 10 date columns is 10 calculated tables and 60 calculated columns, all rebuilt in every
refresh.

**What it costs.** Microsoft says each one "increases the model size and also extends the data
refresh time" but publishes no number, and the published before and after measurements are model
size, not duration. Measure your own model. The worked case below is one measured example.

**The row count trap.** Each table covers whole calendar years from the earliest to the latest
value in its column, one row per day (Microsoft's example: 1,461 rows for 2016 to 2019). One bad
value sets the range. A 1900-01-01 "unknown" sentinel or a far future placeholder produces a table
spanning centuries. Chris Webb documented a source with 9 date values generating hidden tables of
109,938 rows each, exactly 1900 through 2200.

Watch for sentinels you create yourself. In DAX a blank date is 30 December 1899, so a calculated
column like `DATE(YEAR(x), MONTH(x), 1)` produces 1899 whenever `x` is blank, and the hidden table
then spans 1899 to today.

**Turn it off.** File, Options and settings, Options, Time intelligence, on two pages. **Global**
("Auto date/time for new files") is the one that matters for a new build. **Current file** applies
to the open file. Both default to on. There is no tenant level enforcement. For a team, use the per
machine global setting, a `.pbit` template with it off, or the Best Practice Analyzer rule
`REMOVE_AUTO-DATE_TABLE` as a review gate.

**Turning it off on an existing file breaks things.** Any visual or filter using a built in date
hierarchy loses its field, and DAX using `Table[Date].[Year]` stops working. Plan a pass over date
bound visuals. Editing TMDL by hand instead of using the toggle, the `variation` blocks on the date
columns and the relationships to the hidden tables have to go too, or the file will not open.

**The replacement** is one date table you own, related to the facts and marked as a date table.
That is the `powerbi-modeling` skill.

## Defaults to set on a new model, before any real work

1. Turn off auto date/time globally.
2. Build one date table, relate it to the facts, mark it.
3. Disable load on staging queries, and keep the number of loaded tables that reference the same
   expensive staging query as low as possible.
4. Filter and select columns at the source. For a REST API that means the query string.
5. Keep the first argument of `Web.Contents` a literal string, everything variable in
   `RelativePath` and `Query`, or the Service refuses to refresh a dynamic data source.
6. Prefer a Power Query column over a DAX calculated column when the calculation only needs other
   columns of the same row. It compresses better and is not rebuilt in the recalc phase.

## The trap when you fix the data phase

Collapsing a derived Power Query table into a DAX calculated table removes repeated source pulls,
because a calculated table reads what is already in memory. It works when the source pull
dominates, the usual shape of a multi hour Pro refresh.

It moves cost into the recalc phase, it is not free. The Best Practice Analyzer flags heavy use of
calculated tables as technical debt, and Microsoft's recommended fix for fan out is a dataflow,
which on Pro means Dataflow Gen1 with its own problems. So fix the fan out, then clean up the
recalc phase you just loaded. A model that pushed 5 tables into calculated tables and still has
auto date/time on has moved its bottleneck, not removed it.

## A worked case

A small Pro model, about 5 MB compressed, reading a paged REST API and a few workbooks. Every
timing is the Service.

The refresh needed about 3 hours of work, so every scheduled run was cancelled at the 2 hour cap.
Desktop refreshed fine throughout (the shared cache difference, not a sign of health).

1. Data phase. Derived tables that each re-ran the same staging queries became DAX calculated
   tables. API chain runs went from about 40 to 15 per refresh, workbook downloads from 16 to 5.
   3 hours became one to one and a half, and refreshes started completing.
2. Recalc phase. Auto date/time off removed 14 hidden date tables and 84 hidden calculated
   columns, from a model already carrying 8 calculated tables of its own. That hour or more became
   about 15 minutes.

Once the data phase was fixed, roughly three quarters of the remaining time was recalc, and the
hidden date tables were the largest single thing in it. A model can look like it has a source
problem when it has a recalc problem. Date columns covering 2 years would give tables of a few
hundred rows, which could not cost that much, so at least one column was spanning decades or
centuries. Check your own date columns for a stray 1900, a far future placeholder, or a blank
feeding a DAX date expression.

Caveats. The split of the second step was not measured, because per table timings in the Service
need XMLA, which is Premium. A narrower date range on the fact, in the same pass, also cut recalc
work. One case, not a benchmark.

## Measuring on Pro

- Desktop refresh dialog, per table timers. The most useful free signal. Right click one table to
  refresh and time it alone.
- Query Diagnostics in the Power Query editor (Tools tab), for the requests that really went out.
  The Data Source Query column shows the HTTP request and response on connectors that support it.
  A grep of the M estimates fan out, this gives the observed count. Run it with parallel loading on
  and off. https://learn.microsoft.com/en-us/power-query/query-diagnostics
- SQL Server Profiler opened from DAX Studio against Desktop's local engine, for source time per
  table: Progress Report End with subclass 25 ExecuteSQL, plus 17 Read Data for sources that defer
  work. A table's time includes the queries it references. Compare traced runs with traced runs.
  https://blog.crossjoin.co.uk/2019/02/09/power-query-execution-times-using-sql-server-profiler/
- Service refresh history, for total duration, the attempt pattern, and the error.
- Best Practice Analyzer in Tabular Editor 2, against a locally open Desktop file. Catches auto
  date tables, unused columns, and heavy calculated columns.
- Per table timings inside the Service need XMLA or Log Analytics, which are Premium. On Pro you
  get "which table is fat" from Desktop and "how long it all took" from the Service, and you join
  the two yourself.
