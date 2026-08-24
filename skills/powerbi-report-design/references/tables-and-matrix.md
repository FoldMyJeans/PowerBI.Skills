# Tables and matrix

How to build a Table or a Matrix that reads well and does not blow up render time. The rules of
thumb are in `design-principles.md`. Conditional formatting is a big enough topic to
live on its own in `conditional-formatting.md`, and it is opt-in, not automatic.

## Table or matrix: pick by the shape of the data

- Use a Table (`tableEx`) for a flat list of records, one row per item, exact values in columns.
  Think of it as a clean grid. There is no row hierarchy and no cross tab.
- Use a Matrix (`pivotTable`) the moment you need any of these: a second dimension across the
  top (months as columns), a row hierarchy you can expand and collapse, subtotals per level, or
  a real cross tab of rows against columns. The matrix is the pivot table of Power BI.
- If you are only listing values and never crossing two dimensions, a table is simpler and
  faster. Do not reach for a matrix just because it looks fancier.

## Matrix layout

The matrix has three layouts, set under Format, Row headers, Layout (or the older Row headers,
Stepped layout toggle).

- Compact (stepped). The default. Each level of the row hierarchy is indented under its parent
  in a single column, with an expand caret on the parent. Subtotals sit on the parent row. This
  is the most compact and the house default for a hierarchy.
- Outline. Each level gets its own column, and subtotals sit on their own line. Wider, but the
  levels are labelled in separate columns, which some readers prefer for export.
- Tabular. Flattens the hierarchy so it behaves like a table with repeated group values. Use it
  when someone will copy the grid into Excel and wants every row fully qualified.

Keep the expand and collapse behavior on for a hierarchy. A reader drills only into the branch
they care about, instead of scrolling a fully expanded wall of rows. The plus and minus icons
come from Format, Row headers, +/- icons.

## Subtotals and grand totals

- Subtotals are per level, not all or nothing. Turn them on for the levels that help and off for
  the ones that just add noise. Format, Subtotals, then the per row level and per column level
  switches.
- Choose the position. Subtotals can sit above or below their group. In Compact layout they land
  on the parent row.
- The grand total is a single row (and or column) at the edge. Turn it off when a total makes no
  sense, for example an average of averages or a ratio that does not sum.
- A subtotal or grand total re-evaluates the measure in its own filter context. It is not the
  visible rows added up. A measure like a ratio or a distinct count will show a total that does
  not match the column, and that is correct behavior, not a bug.

## Switch values to rows

By default multiple measures spread across columns. Format, Values, Show on rows moves them down
the side instead. Use it when you have many measures and few columns, so the grid reads tall
rather than impossibly wide.

## Column width

- Autosize is on by default and re-fits columns as data changes, which can make widths jump on
  refresh. Turn off Format, Column headers, Auto-size column width once you are happy, so the
  layout is stable.
- The exact width is stored per column in the visual JSON as a `columnWidth` value. The reliable
  way to set precise widths in code is to drag them once in Desktop, save the PBIP, then read the
  written values back out. See the `powerbi-pbir-builder` skill.

## Native sparklines

A sparkline is a tiny line or column chart inside a table or matrix cell, showing a trend per
row. It is a built in feature, no custom visual and no extra model objects.

- Add it from the Values well, New sparkline, choosing the axis (usually a date) and the measure.
- It is Pro safe.
- Hard limits to respect: at most 5 sparklines per visual, at most 52 points per sparkline, and
  adding sparklines caps the matrix at 25 columns. Reach for one trend column, do not carpet the
  grid with them.
- A visual that contains a sparkline cannot be pinned to a Service dashboard tile.

## Styling that keeps a grid readable

- Start from a Style preset (Format, Style) such as Minimal or None, then adjust. The presets set
  sensible gridlines and banding in one click.
- Row banding (alternating row shading) helps the eye track across a wide row. Do not combine
  heavy banding with a background conditional format on the same cells, the two fight and the
  grid turns muddy. Pick one.
- Turn off vertical gridlines and lighten horizontal ones. Right align numbers with tabular
  figures, left align text labels. Keep the header band quiet.
- Set a sensible sort. Sort by a value column for a ranking, and use Sort by column in the model
  when a text column must sort by a hidden order key (month name by month number, for example).

## Performance: the scrollable table trap

A table or matrix that scrolls does not just fetch the visible rows. The engine builds the whole
unfiltered result first, then windows it to what is on screen. On a wide, unfiltered grid this is
the classic cause of a slow visual and of the error "Visual has exceeded the available
resources".

- Chris Webb measured the gap: the same table unfiltered spooled hundreds of thousands of rows
  and tens of MB, and filtered to a couple of thousand rows it dropped to a couple of MB and a
  fraction of the time. The fix is fewer rows, not more formatting.
- So filter the detail. Apply a Top N filter, lead with slicers, or push the big grid onto a
  drill through page that only ever loads one item's rows. A detail export page for one analyst
  can still be dense, but give it a filter, do not ship an unfiltered 10 column scroll.

## Accessibility

- A table or matrix is keyboard and screen reader navigable. Set a logical tab order in the
  Selection pane like any other visual.
- Any reader can open the underlying grid with Show as a table (the keyboard shortcut is
  Alt+Shift+F11 on the focused visual), which is why clear field and measure names matter.
- If you add conditional color, never let color be the only cue. Pair it with an icon or text.
  See `conditional-formatting.md` and `accessibility.md`.

## Pro vs Premium

Tables, matrices, subtotals, native sparklines, column formatting, and sort by column are all
Pro. Nothing here needs Fabric or Premium.

## Sources

Microsoft Learn on the matrix visual, sparklines, and sort by column, under
https://learn.microsoft.com/en-us/power-bi/visuals/. Plus the Tabular Editor blog table design
guide, and Chris Webb on scrollbar and unfiltered spool cost:
https://blog.crossjoin.co.uk/2022/11/10/performance-tuning-table-visuals-with-filters-applied-in-power-bi/
