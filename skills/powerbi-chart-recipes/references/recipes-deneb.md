# Deneb recipes

Each section gives the fields the spec reads, then what to change. Bind them with
`scripts/new_deneb_visual.py` (see `deneb-in-pbip.md`). The settings are at the top of each spec. The
matching file in `assets/fixtures` shows the exact data shape.

## Beeswarm, `beeswarm.vega.json`

Fields: `Name` (item key, so rows do not collapse), `Group`, `GroupOrder`, `Value` (days open).

- Set `limit` and `limitLabel` for the SLA line. Dots past it are solid and the rest are faded.
- `dotRadius` is 4. Lower it above a few hundred dots, because they spread until they overlap rows.
- The colour range holds up to four groups in `GroupOrder`.
- It is a force layout, so it recalculates on each filter and each resize. Test it at the real row
  count before committing to it.

## Calendar heatmap, `calendar-heatmap.vl.json`

Fields: `Date`, `Value`. One row per day.

- One row of the chart per year in the data. Filter to the years you want.
- Fixed at 13 pixels a cell, about 800 wide with the legend. Change `step` to fit.
- Weeks start on Monday.

## Waffle, `waffle.vl.json`

Fields: `Name`, `Value` (0 to 100, not 0 to 1).

- A measure works for `Value`. One panel per `Name`, biggest first.
- Three panels fit a 480 wide visual. For more, reduce `width`, `height` and the mark `size`.
- Coverage out of a whole only. Meaningless for a value that can pass 100.

## Funnel Sankey, `funnel-sankey.vega.json`

Fields: `Name`, `StageOrder`, `Value`. One row per stage.

- Each stage must be a subset of the one before. Blue is kept and grey is lost.
- `Value` should be a measure so it follows filters. Percents are of the largest stage.
- For a real three column flow with crossings, use the Sankey in `powerbi-custom-visuals`.

## Bump, `bump.vl.json`

Fields: `Name`, `Period`, `PeriodOrder`, `Value`. One row per name per period.

- The rank is worked out in the spec, biggest `Value` first. Where lower is better, such as click rate,
  change the window sort `order` to `ascending`.
- Ties break by name, so a rank never repeats.
- More than about eight names gets hard to read. Filter to a top list. Click a line to highlight it,
  double click to clear.

## Butterfly, `butterfly.vl.json`

Fields: `Name`, `RowOrder`, `Left`, `Right`.

- Set `leftTitle` and `rightTitle`. Both sides share one scale, so lengths compare honestly.
- `gapShare` sets the width of the label gap. Raise it for long labels.
- Native option: the stacked bar in `recipes-native-and-svg.md` needs no third-party visual, with
  labels at the left.

## Variance trio, `variance-trio.vl.json`

Fields: `Name`, `Actual`, `Plan`.

- `overIsBad` is true for hours or cost, where over plan is orange. Set it false for output, where over
  plan is good.
- Fixed panel widths add to about 700 wide. Change the three `width` values to fit.
- Plan of zero gives no percent pin rather than an error.

## Floor plan, `floor-plan.vega.json`

Fields: `Name`, `Path`, `LabelX`, `LabelY`, `Value`. One row per room.

- `Path` is an SVG path string. Trace the plan once in any SVG editor, one shape per room, copy each
  `d` into a room table in the model, and note the plan's size in `planWidth` and `planHeight`.
- A blank `Value` draws the room grey with no number. Use a measure, and keep the room rows from the
  room table so an empty room still draws.
- Use a native slicer for floors, filtering the room table.
- If drawing paths is too much work, Synoptic Panel Lite by OKVIZ has a map editor:
  https://appsource.microsoft.com/en-us/product/power-bi-visuals/okvizcorp1634637213047.synopticpanelbyokviz-lite

## Ridgeline, `ridgeline.vl.json`

Fields: `Name`, `RowOrder`, `Hour` (0 to 23), `Value`.

- Each row has its own scale, so it shows when a source peaks and nothing about its size. Say so in the
  title.
- `overlap` is how far a peak climbs into the row above. `rowHeight` and the `height` under `spec` must
  match.
- For dates instead of hours, change the `x` field and type and drop the scale domain.

## 24 hour clock, `alert-clock.vega.json`

Fields: `Day`, `DayOrder`, `Hour` (0 to 23), `Value`. One row per day per hour.

- The first day is the inner ring and midnight is at the top. Hours run clockwise.
- Outer rings are bigger than inner ones for the same value, so colour carries the value, not area.
- Square visuals suit it. The chart fits the smaller side.
- This is our own twist on published ring charts. A native matrix heatmap reads more exactly, so offer
  both.
