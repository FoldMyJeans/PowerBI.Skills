# Query folding and the duplication trap

Most refresh performance comes down to two questions: does the work fold to the source, and is
the source read more than once.

## Query folding

- Check it: right click a step in the Power Query editor, "View Native Query". Available means
  steps up to there fold. Greyed out means folding stopped at or before that step, and everything
  after runs locally on all the rows. The new Power Query editor (Desktop preview, 2026) also shows step folding indicators.
- Usual folding breakers: custom M functions, `Table.Buffer`, adding an index, many kinds of
  merge, awkward type changes, and any source that cannot fold at all (a plain REST call, a
  workbook, most file sources).
- A non folding source (REST, SharePoint file) cannot be made to fold. Filter in the request
  instead (a date clause in the query string), never pull everything and filter in M.

Order of preference: reduce at the source, then in a folding step, and only as a last resort in
a non folding local step.

## The duplication trap: a referenced query runs again

In an import model each loaded table is evaluated on its own. `Source = stg_incident` does not
reuse `stg_incident`'s result. It re-executes its full M, API calls included.

This is worse in the Service than in Desktop, which is why a model can refresh fine in Desktop and
fail on a schedule. Microsoft: "In a cloud environment, each query is refreshed using its own
separate cache. So a query can't benefit from the same request having already been cached for a
different query." Desktop shares one cache, but only gets a referenced query down to one run with
parallel loading of tables turned off. Chris Webb measured 4 web calls with it on (the default)
and 1 with it off, and found no such switch in the Service, where queries appeared to always run
in parallel
(https://blog.crossjoin.co.uk/2019/03/26/power-bi-caching-parallelism-and-power-query-refresh-performance/).
That is from 2019, so count your own requests with Query Diagnostics (`refresh-cost-model.md`).

Chains multiply. If `staging` is referenced by `fact`, `fact` by `aggregate`, and all 3 are
loaded, `staging` runs once for itself, again inside `fact`, and again inside `aggregate`. A slow
API pull repeated like that is a classic cause of an 8 or 9 hour refresh. See Chris Webb, "Why
does Power BI query my data source more than once".

## How to reduce it on Pro

There is no free shared cache on Pro. The levers:

1. Make each pull cheap. Filter at the source, use modest REST page sizes, read SharePoint files
   directly. A pull that runs 3 times but is fast is fine.
2. Reduce fan out. Load the staging result once and let the model relate to it, rather than
   re-shaping it in 3 more loaded tables.
3. `Table.Buffer` reuses a result WITHIN one query evaluation (a lookup used many times in the same
   query). It does not help across loaded tables.
4. A DAX calculated table can aggregate or reshape tables already in memory, with no source calls.
   Converting a derivative M table that re-runs its upstream pulls into a calculated table is
   often the single biggest refresh win. Convert only derivative tables, never the source pulls.
   To convert an existing import table by editing TMDL, delete `.pbi\cache.abf` first so Desktop
   rebuilds from the TMDL (see the `powerbi-project-and-tools` skill). This moves cost into the
   recalc phase, so clean that up afterwards, starting with auto date/time. The trade is in
   `refresh-cost-model.md`.
5. A dataflow materializes the staging once, so each source pull happens one time however many
   model queries read it. On Pro that means Dataflow Gen1, legacy, and sequencing it with Power
   Automate has a real cost (`pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill).
   The clean version needs Fabric or Premium.

## Counting the fan out

The number that decides refresh time is how many times each expensive pull runs. Count it before
changing anything.

1. List every query that touches the network.
2. For each, grep the M for every query that names it.
3. Follow those references transitively (the chain rule above).
4. Write the number next to the query. That is how many times its API calls or file downloads
   happen in one Service refresh.

That is a static estimate. Query Diagnostics shows the real requests.

Count LOADED tables too, not just staging queries. Referencing a loaded table re-runs its whole M
like any other query. The worst multipliers are usually loaded tables (a planning table read by 5
queries, a dimension read by 4) while the staging queries everyone suspects sit at one or two.

A worked shape, after counting:

| Query | Kind | Runs per refresh | Why |
| --- | --- | --- | --- |
| `fact_planning` | loaded table, reads a workbook | 5 | itself, plus 4 transform queries each re-derive it |
| `dim_sprint` | loaded table, reads an API | 4 | itself, plus 3 transform queries need its date ranges |
| `stg_epic` | staging, reads an API | 3 | two dimensions plus the union query |
| `stg_task` | staging, reads an API | 2 | a dimension plus the union query |

The fix in both bad cases was the same: the join those transform queries each re-derived belonged
downstream in DAX, not repeated in M.

## Quick checklist

- Filters at the source, not in M after a full pull.
- Folding as far as possible (View Native Query).
- Runs per refresh counted for every query that touches the network, loaded tables included.
- No REST page too large to build inside the source's limit.
- A single SharePoint file read directly, not via a site crawl.
- One workbook read into one loaded table, then referenced, rather than 3 queries against the
  same file.
