# Formatting charts and tables

Per visual formatting that is specific to one visual family: line and bar series, data labels,
reference lines, and table and matrix columns. The selector grammar these entries use is in
`formatting-and-selectors.md`. Read that first if an entry here appears to do nothing.

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

Lives in `visual.objects`. Each line needs its own 20 character hex `selector.id` that you
generate. Reusing one across visuals is fine, reusing it within one visual collapses two lines
into one.

## Table and matrix specifics

```json
"visualContainerObjects": {
  "stylePreset": [{ "properties": { "name": { "expr": { "Literal": { "Value": "'Condensed'" } } } } }]
}
```

The Style dropdown in Desktop is a preset name string. `'Condensed'` for a dense detail grid and
`'AlternatingRowsNew'` for a short reference table are the two that earn their place.

### Column widths

Column widths bind by selector, and the shape differs by visual. A table uses `metadata` with the
`queryRef`. A matrix column generated from a data value uses the `scopeId` comparison form, and
the grand total uses the `total` form. Write a width against the wrong form and it parses and
never binds. Drag once in Desktop, save, then read back what it wrote.

```json
"columnWidth": [{
  "properties": { "value": { "expr": { "Literal": { "Value": "113D" } } } },
  "selector": { "metadata": "fact_records.User Name" }
}]
```

For an implicit measure the `queryRef` includes the aggregation, for example
`"Sum(fact_effort.Effort (Hours))"`. Set a width for every column. A 12 column table with only 2
widths set still scrolled. All 12, totalling 1,211 px in a 1,264 px visual, fit.

`columnHeaders.columnAdjustment` takes `'fitToContent'`, `'growToFit'` or `'fixedWidth'` (report
theme schema names). Use `'growToFit'` only on a visual whose columns change with a slicer or a
field parameter. Fixed tables get `'fixedWidth'`, `wordWrap` true on headers and values, and one
width per column summing to the visual width minus about 40 px. Never set `growToFit` in the
theme. On one report it stopped text wrapping and added a horizontal scrollbar to every small
fixed table. The design rule and the width budget are in `tables-and-matrix.md` in the
`powerbi-report-design` skill.
