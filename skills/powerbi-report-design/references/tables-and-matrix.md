# Tables and matrix

How to build a table or matrix that reads well and renders fast. Conditional formatting is opt-in
and lives in `conditional-formatting.md`.

## Table or matrix

- Table (`tableEx`): a flat list of records, one row per item, exact values, no hierarchy.
- Matrix (`pivotTable`): as soon as you need a second dimension across the top (months as
  columns), an expandable row hierarchy, subtotals per level, or a real cross tab.
- Only listing values? A table is simpler and faster.

## Matrix layout

Format, Row headers, Layout (or the older Row headers, Stepped layout toggle).

- Compact (stepped). The default. Each level indented under its parent in one column, an expand
  caret on the parent, subtotals on the parent row. The most compact, and the default to use for a
  hierarchy.
- Outline. Each level in its own column, subtotals on their own line. Wider, and some readers
  prefer it for export.
- Tabular. Flattened like a table with repeated group values, for someone copying the grid into
  Excel who wants every row fully qualified.

Keep expand and collapse on for a hierarchy, so a reader drills only into the branch they care
about. The icons are Format, Row headers, +/- icons, and since August 2026 Column headers has its
own +/- icons. Auto expand (Row headers and Column headers, June 2026) opens new levels as they are
added. Row headers are frozen by default, with a Layout, Freeze toggle (August 2026).

## Subtotals and grand totals

- Per level, not all or nothing. Format, Subtotals, then the per row level and per column level
  switches.
- Above or below the group. In Compact they land on the parent row.
- Turn the grand total off when a total makes no sense (an average of averages, a ratio that does
  not sum).
- A total re-evaluates the measure in its own filter context, it does not add the visible rows. A
  ratio or distinct count total that does not match the column is correct, not a bug.

## Switch values to rows

Format, Values, Show on rows moves many measures down the side, so the grid reads tall rather than
impossibly wide.

## Column width

- The setting is Visual, Layout, Column width, Auto-size behavior: Fit to content (the default
  since January 2026), Grow to fit, or Fixed width with a Default width. Custom widths adds a width
  per column, and widths can take fx. Fit to content re-fits as data changes, so widths can jump on
  refresh. Pick Fixed width once the layout is right.
- Readers can right click a header to set or reset a width for their own session, and personal
  bookmarks keep it. That never changes the report.
- The JSON is in `formatting-charts-and-tables.md` in the `powerbi-pbir-builder` skill. For
  precise widths, dragging once in Desktop and reading the file back is still the safe route.

Grow to fit or fixed widths, decided per visual:

- Grow to fit only where the columns change: a matrix whose column headers are field values that
  come and go with a slicer pick (service types, cost buckets), or a table whose columns a field
  parameter swaps. Not a flat table with a fixed field list.
- Fixed tables get a fixed width on every column, sized to fill the visual with no horizontal
  scroll. Leave about 40 px for padding and the scrollbar gutter. In a 476 px table the columns may
  total about 436 px. At 452 px it scrolled. Put the slack on the text column, and turn word wrap
  on for headers and values.
- Set every column. A wide detail table with only a couple of widths set still scrolled.

Grow to fit put on every table and matrix of one report at once, with saved widths dropped: small
fixed tables stopped wrapping and grew a horizontal scrollbar, a matrix that fit started
scrolling, and a wide matrix lost its wrapped headers so fewer columns showed. Tables that already
filled their width looked the same. Everything except the changing column visuals went back to
fixed widths.

## Native sparklines

A tiny line or column chart per row inside a table or matrix cell. Built in, Pro safe, no custom
visual or model objects.

- Values well, New sparkline, pick the axis (usually a date) and the measure.
- Hard limits: at most 5 sparklines per visual, at most 52 points each, and sparklines cap the
  matrix at 25 columns. One trend column, not a carpet.
- A visual with a sparkline cannot be pinned to a Service dashboard tile.

## Styling that keeps a grid readable

- Start from a Style preset (Format, Style) such as Minimal or None, then adjust.
- Row banding helps the eye track a wide row. Do not combine heavy banding with a background
  conditional format on the same cells, the grid turns muddy. Pick one.
- Vertical gridlines off, horizontal ones light. Numbers right aligned with tabular figures, text
  left aligned. A quiet header band.
- Sort by a value column for a ranking. Use Sort by column in the model when text must sort by a
  hidden key (month name by month number).

## Performance: the scrollable table trap

A scrolling table or matrix does not fetch only the visible rows. The engine builds the whole
unfiltered result, then windows it to the screen. On a wide unfiltered grid this is the classic
cause of a slow visual and of "Visual has exceeded the available resources". Measured, the same
table unfiltered spooled hundreds of thousands of rows and tens of MB, and filtered to a couple of
thousand rows it dropped to a couple of MB and a fraction of the time.

The fix is fewer rows, not more formatting: a Top N filter, slicers first, or the big grid on a
drill through page that only loads one item's rows. A dense export page for one analyst still gets
a filter, never an unfiltered 10 column scroll.

## Accessibility

- Tables and matrices are keyboard and screen reader navigable. Set the tab order like any visual.
- Show as a table (Alt+Shift+F11 on the focused visual) opens the grid for any reader, which is why
  clear field and measure names matter.
- Conditional color never stands alone. See `conditional-formatting.md` and `accessibility.md`.

## Pro vs Premium

Tables, matrices, subtotals, sparklines, column formatting and sort by column are all Pro.

## Sources

Microsoft Learn on the matrix visual, sparklines and sort by column, under
https://learn.microsoft.com/en-us/power-bi/visuals/. The Tabular Editor blog table design guide.
The scrollbar and unfiltered spool measurement:
https://blog.crossjoin.co.uk/2022/11/10/performance-tuning-table-visuals-with-filters-applied-in-power-bi/
