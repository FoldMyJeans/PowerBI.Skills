# Formatting charts and tables

Per family formatting. If an entry here does nothing, check the selector against
`formatting-and-selectors.md`.

## Series colour on a line chart

A plain `dataPoint` `fill` with no selector did not colour the line. A `metadata` selector naming
the measure's `queryRef` did.

```json
"dataPoint": [{
  "properties": { "fill": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } } },
  "selector": { "metadata": "_Measures.Completion %" }
}]
```

Labels below the points: `labels` with `labelPosition` `'Under'`.

## Stacked column plus line combo

`lineStackedColumnComboChart` with `Category`, `Y` (the column measure), `Series` (the column that
stacks) and `Y2` (the line measure). This worked in Desktop 2.159:

- Colour each stack segment with a `dataPoint` `fill` entry per series value, its selector a `data`
  `scopeId` Comparison on the `Series` column (the form is in `formatting-and-selectors.md`).
- Hide one segment's labels with a `labels` entry `showSeries` false under the same selector.
- Colour the line with a `metadata` selector naming the `Y2` measure's `queryRef`, as above.
- `valueAxis.secShow` false hides the second axis when the line shares the scale's meaning.

## Row wide font colour in a table

A colour measure on `values.fontColor` colours one column per entry. To colour the whole row, write
one `values` entry per column, each with `fontColor` set to the colour measure and a `metadata`
selector naming that column's `queryRef` (plus `dataViewWildcard` `matchingOption` 1). A single
entry coloured only one column.

## Data labels on bars

- On a stacked bar, label `color` is overridden by auto contrast on dark fills, so a mid tone
  series kept white labels whatever the JSON said. Darken or lighten the series colour instead.
- `hundredPercentStackedBarChart` labels show percentages, not counts. Say "Share of records" in
  the subtitle so nobody reads them as counts.
- Labels that get cut off inside bars, and K units on labels, are in the target tick recipe in
  `recipes-native-and-svg.md` in the `powerbi-chart-recipes` skill.

## Reference line

```json
"y1AxisReferenceLine": [{
  "properties": {
    "show":        { "expr": { "Literal": { "Value": "true" } } },
    "displayName": { "expr": { "Literal": { "Value": "'100%'" } } },
    "value":       { "expr": { "Literal": { "Value": "1D" } } },
    "lineColor":   { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0.5 } } } } },
    "width":       { "expr": { "Literal": { "Value": "2D" } } },
    "style":       { "expr": { "Literal": { "Value": "'dashed'" } } }
  },
  "selector": { "id": "af9ee49dad017971defe" }
}]
```

In `visual.objects`. Each line needs its own generated 20 character hex `selector.id`. Reuse
across visuals is fine. Reuse within one visual collapses two lines into one.

## Table and matrix specifics

```json
"visualContainerObjects": {
  "stylePreset": [{ "properties": { "name": { "expr": { "Literal": { "Value": "'Condensed'" } } } } }]
}
```

Desktop's Style dropdown as a preset name. `'Condensed'` for a dense detail grid,
`'AlternatingRowsNew'` for a short reference table.

### Column widths

The selector differs by visual: a table uses `metadata` with the `queryRef`, a matrix column
generated from a data value uses the `scopeId` comparison form, the grand total the `total` form.
The wrong form parses and never binds. Drag once in Desktop, save, and read back what it wrote.

```json
"columnWidth": [{
  "properties": { "value": { "expr": { "Literal": { "Value": "113D" } } } },
  "selector": { "metadata": "fact_records.User Name" }
}]
```

For an implicit measure the `queryRef` includes the aggregation, for example
`"Sum(fact_effort.Effort (Hours))"`. Set a width for every column. A 12 column table with only 2
widths set still scrolled. All 12, totalling 1,211 px in a 1,264 px visual, fit.

The 2026 width model, all in `columnHeaders` (Desktop's Visual, Layout, Column width):

- `columnAdjustment` is the Auto-size behavior: `'fitToContent'` (the default since January 2026),
  `'growToFit'` or `'fixedWidth'`.
- `defaultColumnWidth` (px) sets every column, including new ones, when the behavior is
  `'fixedWidth'`.
- `customColumnWidth` true turns on the per column `columnWidth` entries above. Setting it false
  clears them all. On a matrix, `customColumnWidthGranularView` sets widths per leaf column.
- Widths take fx, so a measure or a what-if slider can drive them.
- `autoSizeColumnWidth` is the pre 2026 toggle. It is still in the theme schema, but do not pair it
  with the new keys until you have read what Desktop writes on your build.

Use `'growToFit'` only on a visual whose columns change with a slicer or a field parameter. Fixed
tables get `'fixedWidth'`, `wordWrap` true on headers and values, and one width per column summing
to the visual width minus about 40 px. Never set `growToFit` in the theme. On one report it stopped
text wrapping and added a horizontal scrollbar to every small fixed table. The design rule and
width budget are in `tables-and-matrix.md` in the `powerbi-report-design` skill.

## Chart properties added in 2026

Names from the report theme schema (2.159, October 2026). Set one in Desktop and read the file back
before writing it into many visuals.

- `plotArea.color` (fx capable) and `colorTransparency`: a fill behind the plot on bar, column,
  line, area, combo, ribbon, waterfall and scatter charts.
- `valueAxis.roundRange` false: the axis starts flush with the data, and data labels no longer
  stretch it.
- `categoryAxis.outerPadding`: space at the chart edges, as a percent of a category.
- `categoryAxis.initialScrollPosition` `'end'`: a long axis opens on the latest period.
- `categoryAxis.autoExpand` true: several fields picked in a field parameter build an expanded
  axis hierarchy.
- Series colours by legend take fx (bar, column, pie, donut, line). See `conditional-formatting.md`
  in the `powerbi-report-design` skill.
