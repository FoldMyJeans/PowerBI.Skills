---
name: powerbi-dax
description: >-
  Write and fix DAX in a Power BI model: measures, calculated columns, calculated tables,
  time intelligence, and the patterns that come up every day. Use whenever the user wants to
  write a measure, asks for DAX help, or is doing year over year, year to date, a running or
  cumulative total, percent of total, ranking, safe division, or a virtual relationship. Also
  use for "calculated column vs measure", context transition, what CALCULATE does, row context
  vs filter context, DIVIDE, RANKX, RANK, TREATAS, ISINSCOPE, DATEADD, SAMEPERIODLASTYEAR, TOTALYTD,
  a user defined function, a calculation group, a visual calculation, or a
  measure that returns a blank or a wrong total. Trigger on "write a DAX measure", "my measure
  is wrong", "year over year in power bi", "running total", "percent of total", "should this be
  a calculated column or a measure". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI DAX

Checked against Power BI releases through October 2026.

Measures, the measure versus calculated column or table choice, and reusable patterns, on Power BI
Pro. For the model shape a calculation needs (star schema, the Date table, the _Measures table) use
`powerbi-modeling`. For M and getting data in use `powerbi-data-and-refresh`. For DAX Studio, pbip and
TMDL, and the calculated column and table cost facts (`pro-vs-premium-facts.md`) use
`powerbi-project-and-tools`.

## Workflow

1. Default to a measure. A calculated column only when the value must sit on the row (to group,
   relate, or slice on it) and M cannot produce it. See `references/measures-vs-calc.md`.
2. Keep measures in a dedicated _Measures table (`powerbi-modeling`).
3. Start from a pattern in `references/patterns.md`. Do not invent one.
4. Name each step with VAR. Each variable is evaluated once, where it is declared.
5. Anything time based needs a real Date table marked as a date table. Without it the time
   functions return blank or silently wrong numbers.
6. Guard every division whose denominator can be zero or blank with DIVIDE.
7. If a total looks wrong, check context transition (CALCULATE turning the current row into a
   filter) and whether the measure should be evaluated per row and then combined. A ratio over an
   AVERAGE, or any non additive ratio, is right per row and meaningless at the total. See
   `references/ratios-and-totals.md`. Check the numbers in DAX Studio (`powerbi-project-and-tools`).

## Rules of thumb

- Prefer a column computed in M or at the source over a DAX calculated column. It compresses
  better and does not recompute every refresh.
- A calculated table recomputes every refresh and does not fold. It is right when it re-derives
  from data already in the model (a Date table, a bridge, a rollup), whatever its size.
- DIVIDE when the denominator could be zero or blank. With a constant denominator Microsoft
  recommends `/`, because the test is wasted work.
- Qualify columns, never measures: `Sales[Amount]`, `[Total Sales]`. A qualified measure reference
  breaks when the measure's home table changes, which matters with a _Measures table.
  https://learn.microsoft.com/en-us/dax/best-practices/dax-column-measure-references
- In CALCULATE prefer a Boolean filter over FILTER. A Boolean filter cannot reference a measure or
  columns from several tables, nest CALCULATE, or use a function that scans a table, so those still
  need FILTER.
  https://learn.microsoft.com/en-us/dax/best-practices/dax-avoid-avoid-filter-as-filter-argument
- A chart or card built as a DAX string (SVG or HTML) is a real technique. Guard every division,
  name every magic number as a VAR, and escape the string the same way every time. See
  `references/svg-from-dax.md` and `references/html-from-dax.md`.
- Never hard code a normalization bound or a page size as a repeated literal. Compute bounds
  dynamically and derive page windows from one VAR. See `references/scoring-and-pagination.md`.

## References in this skill

- `references/measures-vs-calc.md`: measure vs calculated column vs calculated table, the
  context facts that cause wrong numbers, and the import to calculated table trap.
- `references/patterns.md`: copy ready DAX for base measures, safe division, percent of total,
  year over year, year to date, running totals, ranking, TREATAS, a KPI label with a color, and a
  common mistakes list.
- `references/ratios-and-totals.md`: the measure that is right on a row and wrong on the total,
  ISINSCOPE versus HASONEVALUE, custom totals, the cost of a zero from DIVIDE, releasing specific
  columns, value filter behavior, collapsing duplicate rows, the residual bucket, and a cumulative
  total over a non date column.
- `references/time-intelligence.md`: fair prior period comparisons when the latest period is
  partial, the latest complete month picker, reading snapshots by month, a month axis with no gaps,
  and the preview calendar functions.
- `references/on-time-and-snapshot-rates.md`: an on time rate with items still in their window, and
  a fix rate between snapshots with its usual level.
- `references/functions-and-calculation-groups.md`: DAX user defined functions (GA details, TMDL
  form, TABLEOF and NAMEOF), calculation groups on Pro, their traps for text measures, and how to
  choose between them.
- `references/window-and-visual-calculations.md`: RANK and the window functions, visual
  calculations (LOOKUP INFERRED, small multiples), and where each belongs.
- `references/virtual-relationships.md`: the TREATAS forms, joining two facts at different grains,
  a composite key built in a measure, KEEPFILTERS, LOOKUPVALUE, and string keys when the source
  gives you no surrogate key.
- `references/measure-driven-columns.md`: field parameters and disconnected column header tables,
  with the TMDL for both, so a visual's columns can come from a calculation.
- `references/svg-from-dax.md`: an SVG chart as a DAX string measure, scaling into a viewBox, the
  data URI escaping rules, unique ids for a repeated chart, and Data Category Image URL.
- `references/html-from-dax.md`: an HTML component measure (a KPI card, a panel) for a third
  party HTML rendering visual, theme derived styling VARs, and a hover reveal.
- `references/scoring-and-pagination.md`: min-max normalization to a 0-100 score, inverting the
  scale, an equal weight composite, tier and quadrant labels, and paging a rank for a leaderboard.

## Shared facts

- `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill: the cost of calculated
  columns and tables, and the Pro lens.
