---
name: powerbi-dax
description: >-
  Write and fix DAX in a Power BI model: measures, calculated columns, calculated tables,
  time intelligence, and the patterns that come up every day. Use whenever the user wants to
  write a measure, asks for DAX help, or is doing year over year, year to date, a running or
  cumulative total, percent of total, ranking, safe division, or a virtual relationship. Also
  use for "calculated column vs measure", context transition, what CALCULATE does, row context
  vs filter context, DIVIDE, RANKX, TREATAS, DATEADD, SAMEPERIODLASTYEAR, TOTALYTD, or a
  measure that returns a blank or a wrong total. Trigger on "write a DAX measure", "my measure
  is wrong", "year over year in power bi", "running total", "percent of total", "should this be
  a calculated column or a measure". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI DAX

This skill covers DAX: measures, the choice between a measure and a calculated column or
table, and a set of correct, reusable patterns. It assumes Power BI Pro (no Fabric or
Premium). For the calculated column and table cost and size facts, read
`pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.

## When to use

Use this when writing or fixing DAX, or deciding where a calculation belongs. For the model
shape a calculation needs (star schema, a Date table, a _Measures holder table) use
`powerbi-modeling`. For getting data into the model and M use `powerbi-data-and-refresh`. For
DAX Studio, the pbip and TMDL format, and the calculated table limitation use
`powerbi-project-and-tools`.

## The mental model

1. A measure is a calculation evaluated at query time inside the current filter context. It
   stores nothing and adds nothing to model size. Reach for a measure first.
2. A calculated column is computed once per refresh and stored on the row. It costs model size
   and refresh time and does not compress as well as an imported column. Use it only when a
   real column value is needed and M cannot give it.
3. Filter context is what slices the model (the row of a visual, a slicer, a filter argument
   from CALCULATE). Row context is the current row while scanning a table. CALCULATE turns the
   current row into a filter. That turn is context transition, and it is the one idea behind
   most confusing measure results.

## Workflow

1. Decide measure, calculated column, or calculated table. Default to a measure. See
   `references/measures-vs-calc.md`.
2. Put the measure in the right place. A measure has no natural home row, so keep measures in a
   dedicated _Measures table so they are easy to find. See `powerbi-modeling`.
3. Start from a known good pattern, do not invent one. See `references/patterns.md`.
4. Use VAR variables to name each step. It reads better and each variable is evaluated once.
5. For anything time based (year over year, year to date, a moving total) confirm there is a
   real Date table marked as a date table first. Without it the time functions are wrong or
   blank.
6. Guard every division with DIVIDE so an empty denominator returns blank, not an error.
7. If a total looks wrong, check context transition and whether the measure should aggregate
   over the visible rows. A ratio whose denominator is an AVERAGE, or any ratio that does not
   sum, is correct per row and meaningless at the total until you fix it. See
   `references/ratios-and-totals.md`. Verify in DAX Studio if needed (see
   `powerbi-project-and-tools`).

## Rules of thumb

- Prefer a measure over a calculated column. Prefer a column computed upstream in M or at the
  source over a DAX calculated column, because it compresses better and does not recompute
  every refresh. See `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.
- A calculated column only earns its place when the value must exist on the row and needs model
  or row context that M cannot provide.
- Calculated tables (a Date table, a bridge) are fine, but they recompute every refresh and do
  not fold. Keep them small.
- Time intelligence needs a proper Date table, contiguous dates, and Mark as date table set.
  Build it once in `powerbi-modeling`, not per measure.
- Always use DIVIDE(numerator, denominator) instead of the / operator for a ratio.
- Name intermediate results with VAR. It is faster and far easier to read and debug.
- Where a measure lives does not change its result, but a _Measures table keeps the model clean
  and the measures findable.
- Building a chart or a card as a DAX string (SVG or HTML) is a real technique, not a hack, but
  guard every division, name every magic number as a VAR, and escape the string the same way
  every time. See `references/svg-from-dax.md` and `references/html-from-dax.md`.
- Never hard code a normalization bound or a page size as a repeated literal. Compute bounds
  dynamically and derive page windows from one VAR. See `references/scoring-and-pagination.md`.

## References in this skill

- `references/measures-vs-calc.md`: measure vs calculated column vs calculated table, when each
  is right, row context vs filter context, context transition, and the import to calculated
  table trap.
- `references/patterns.md`: correct, copy ready DAX for base measures, safe division, percent
  of total, year over year, year to date, running totals, ranking, virtual relationships, and
  VAR, plus a common mistakes list.
- `references/ratios-and-totals.md`: the measure that is right on a row and wrong on the total,
  the HASONEVALUE and AVERAGEX fix, releasing specific columns rather than a whole table,
  collapsing duplicate rows before summing, and a cumulative total over a non date column.
- `references/virtual-relationships.md`: the five TREATAS forms, joining two facts at different
  grains, building a composite key in a measure, KEEPFILTERS, and what to do when the source
  gives you no surrogate key.
- `references/measure-driven-columns.md`: field parameters and disconnected column header tables,
  with the TMDL for both, so a visual's columns can come from a calculation.
- `references/svg-from-dax.md`: building an SVG chart as a DAX string measure, scaling points
  into a viewBox, the data URI escaping rules, unique ids for a repeated chart, and Data
  Category Image URL as the no custom visual rendering route.
- `references/html-from-dax.md`: building an HTML component measure (a KPI card, a panel) for a
  third party HTML rendering visual, theme derived styling VARs, and a hover reveal pattern.
- `references/scoring-and-pagination.md`: min-max normalization to a 0-100 score, inverting the
  scale for a lower is better metric, an equal weight composite, tier and quadrant
  classification, and windowing a RANKX rank into pages for a leaderboard.

## Shared facts

- `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill: the cost of calculated
  columns and tables, and the Pro lens.
