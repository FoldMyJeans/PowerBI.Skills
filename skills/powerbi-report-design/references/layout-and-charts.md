# Layout and charts

How to lay out a page and pick the chart. The rules (5 second rule, one decision per page,
density, reading path, when to bend them) are in `design-principles.md`. This file is the how-to.

## Canvas and grid

- Page size. A report with pages already keeps their size. A new report: Desktop starts Fluent 2
  reports at 1920x1080 and older ones at 1280x720, either works. 16:10 (1280x800) when you want
  more vertical room. Set it in the Format pane, Canvas settings. One size for every page.
- Grid. The default is 8 pixels: position and size every visual on multiples of 8, gaps of 8 to 10
  pixels. Turn on Snap to grid and use Format, Align. A report with its own grid keeps it.
- White space groups related visuals. It is not wasted.
- Structure with container formatting, not drawn shapes. The visual container already has a
  background, border and padding, so it can group the tiers without adding objects. See the
  container convention in `design-principles.md`.

## The three tier layout

1. Top: KPI cards and the headline number, the one or two numbers the page is about.
2. Middle: the "why" charts, trend over time and a breakdown that explains the KPI.
3. Bottom: detail tables for anyone who wants to dig in.

The most important visual goes top left. A page still crowded after cutting works the declutter
ladder in `design-principles.md`. A slow page is often an overloaded page.

The default page set is a summary page first, supporting detail after, with one Date slicer synced
across both (the date slicer convention in `design-principles.md`).

## Choose the chart by the question

Mirrors the Financial Times Visual Vocabulary, which sorts charts by intent.

| The question | Reach for | Notes |
| --- | --- | --- |
| Compare or rank categories | Bar (long labels) or column, sorted | Sort by value, not alphabetically. Bar handles long category names. |
| Trend over time | Line, or column for a few periods | Line for many points, column when there are only a handful. |
| Variance vs a target or prior period | Bar with a reference line, or a waterfall | Waterfall shows the bridge from a start value to an end value. |
| Correlation or outliers | Scatter | The relationship between two continuous measures. |
| Part to whole | Stacked bar or treemap | Pie or donut only for a small part to whole with fewer than about eight slices. |
| Many series over time | Small multiples grid | A grid of small charts beats overlapping spaghetti lines. |
| Distribution of values | Histogram, or a column with a binned axis | Shows spread and shape, not just an average. |
| Hierarchy or cross tab of values | Matrix (`pivotTable`) | Rows against columns, subtotals, expand and collapse. See `tables-and-matrix.md`. |
| A flat list of records | Table (`tableEx`) | Exact values, one row per item, no hierarchy. |
| Why is the number what it is | Decomposition tree or key influencers | Pro safe native AI visuals. See `analytical-visuals.md`. |

For a chart Power BI lacks (beeswarm, waffle, bullets and sparklines in a table), see the
`powerbi-chart-recipes` skill.

## Rules that keep charts honest

- Always show a comparison: target, budget, prior period or benchmark.
- Small multiples once five or more series cross, a grid on a shared axis.
- A sorted bar almost always beats a pie.
- Titles. The default title is neutral (the title convention in `design-principles.md`). A
  takeaway title ("Tickets closed fell 8 percent last month") bound to a measure suits a
  storytelling page. See "Binding a title to a measure" in `cards-and-dynamic-text.md` in the `powerbi-pbir-builder` skill, and its
  grain trap: a per row ratio measure overstates at the whole visual level.
- Dates read month and year, MMM yyyy ("Jan 2026"), from the slicer to the axis.
- A plain-English tooltip on every non-obvious chart, saying what it shows, so a reader and a
  future maintainer get it at a glance. Since June 2026 the tooltip's sentence format does this
  with no DAX and no tooltip page: a template that names tooltip fields as `{Field name}`.
- Declutter each visual. Redundant gridlines off, no legend when the series is obvious, no border
  or fill that carries no data.
