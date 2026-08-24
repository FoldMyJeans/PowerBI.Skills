# Layout and charts

How to lay out a page and pick the right chart. The situational rules are in
`design-principles.md`. This file is the how-to.

## Canvas and grid

- Canvas size 1280x720 (16:9), or 1280x800 (16:10) when you want the extra vertical room. Set it in the Format pane under
  Canvas settings. Pick one and use it for every page so the report feels consistent.
- Use an 8 pixel grid. Position and size every visual on multiples of 8, and keep consistent
  gaps of about 8 to 10 pixels. Turn on Snap to grid and use the alignment tools (Format,
  Align) to line up edges. Misalignment is the fastest way a report looks amateur.
- Leave generous white space. Empty space is not wasted, it groups related visuals and gives
  the eye somewhere to rest.
- Build the structure with container formatting, not drawn shapes. The visual container already
  carries a background, a border and padding, so it can group the tiers without adding objects
  to the canvas. See the house convention in `design-principles.md`.

## The three tier layout

Executives read top down and stop early, so put the answer first.

1. Top tier: KPI cards and the headline number. The one or two numbers the page is about.
2. Middle tier: the "why" charts. Trend over time and a breakdown that explains the KPI.
3. Bottom tier: detail tables. The supporting rows for anyone who wants to dig in.

Follow the reading path. Most eyes go top left first, then across and down in a Z or F pattern.
Put the single most important visual top left.

## The 5 second rule and one decision per page

- 5 second rule. The main point of a page should be readable in about 5 seconds. If it
  takes longer, the page is carrying too much.
- One decision per page. Decide the single question the page answers, then cut anything that
  does not serve it. If it is still crowded, work the declutter ladder in
  `design-principles.md`. Splitting into a second page is the last rung, not the first.
- Density limit. About 6 to 8 visuals and 10 to 20 fields per page. This helps both
  readability and render performance. A slow page is often an overloaded page.

## The house page layout preference

Summary page first, supporting detail after, with one Date slicer synced across both. The full
convention, including when it does not apply, is in `design-principles.md` under
house conventions.

## Choose the chart by the question

Match the chart to what the reader is asking. This mirrors the Financial Times Visual
Vocabulary, which sorts charts by intent (comparison, change over time, deviation, correlation,
part to whole, distribution).

| The question | Reach for | Notes |
| --- | --- | --- |
| Compare or rank categories | Bar (long labels) or column, sorted | Sort by value, not alphabetically. Bar handles long category names. |
| Trend over time | Line, or column for a few periods | Line for many points, column when there are only a handful. |
| Variance vs a target or prior period | Bar with a reference line, or a waterfall | Waterfall shows the bridge from a start value to an end value. |
| Correlation or outliers | Scatter | The standard way to show the relationship between two continuous measures. |
| Part to whole | Stacked bar or treemap | Pie or donut only for a small part to whole with fewer than about eight slices. |
| Many series over time | Small multiples grid | A grid of small charts beats overlapping spaghetti lines. |
| Distribution of values | Histogram, or a column with a binned axis | Shows spread and shape, not just an average. |
| Hierarchy or cross tab of values | Matrix (`pivotTable`) | Rows against columns, subtotals, expand and collapse. See `tables-and-matrix.md`. |
| A flat list of records | Table (`tableEx`) | Exact values, one row per item, no hierarchy. |
| Why is the number what it is | Decomposition tree or key influencers | Pro safe native AI visuals. See `analytical-visuals.md`. |

## Rules that keep charts honest

- Always show a comparison. A raw number alone tells no story. Pair it with a target, budget,
  prior period, or benchmark. This is the core idea behind IBCS.
- Prefer small multiples over many overlapping lines. When five or more series cross, split
  them into a grid of small charts with a shared axis.
- Avoid pie, donut, and gauge unless it is genuinely part to whole with fewer than about eight
  categories. They are hard to read and waste space. A sorted bar almost always beats a pie.
- Insight driven titles. Title a visual with the takeaway, not the field name. "Tickets closed
  fell 8 percent last month" beats "Count of Tickets by Month". For a title that stays true as the
  filters change, bind it to a measure that returns a string, a dynamic title. See the dynamic
  titles section in the `powerbi-pbir-builder` skill, and mind the grain trap it describes, a per
  row ratio measure overstates when it is read at the whole visual level.
- Read dates as month and year. Format a date axis and the date slicer as MMM yyyy, for example
  "Jan 2026", everywhere from the slicer to the bottom of the chart.
- Give it a plain-English tooltip. Every non-obvious chart carries a short tooltip that says what
  it shows in plain words, so a reader gets it at a glance and a future maintainer is not left
  guessing.
- Declutter each visual. Turn off redundant gridlines, drop the legend when the series is
  obvious, and remove borders and fills that carry no data.

## When to bend it

- A detail or export page for one power user can be dense and table heavy. The 5 second rule
  does not apply to a data extract.
- An operational monitoring wall can lean on red and green more than an exec deck, because
  alert state is the whole point.
- A single number scorecard can be one big card. Not every page needs three tiers.

See `design-principles.md` for the full list and the sources behind it.
