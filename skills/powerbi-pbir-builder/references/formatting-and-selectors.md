# Formatting a visual, and the selector grammar

A wrong selector is the most common reason a formatting change does nothing, with no error.

## Two places formatting lives

- `visual.objects`: formatting of the visual TYPE. Axes, legend, data points, matrix values,
  slicer mode.
- `visual.visualContainerObjects`: formatting of the CONTAINER around any visual. Title,
  subtitle, border, padding, shadow, header tooltip.

## Prerequisite: the report level switch

```json
"settings": { "useStylableVisualContainerHeader": true }
```

In `definition/report.json`. Without it, subtitle, divider, spacing, drop shadow and header
tooltip silently do nothing. Check it before writing container styling, a new Fluent 2 report may already have it. If it is
missing, turn
on the modern visual header in Desktop rather than hand editing `report.json`.

## The selector grammar, five forms

A formatting entry is an array of elements, each with `properties` and an optional `selector`.
No selector means the whole visual.

```json
"selector": { "id": "default" }
```
The card visual's value, label and layout blocks. The card ignores an entry with no selector, so
`default` is required there.

```json
"selector": { "id": "Row" }      // and { "id": "Column" }
```
Matrix subtotals only. Styling both axes takes three entries: one bare entry with the on and off
switches, then one per axis.

```json
"selector": { "metadata": "_Measures.Task Updates % of Grand Total" }
```
One measure or column by its `queryRef`, spelled exactly as the projection spells it. Column
widths and per measure font sizes bind this way.

```json
"selector": { "data": [ { "dataViewWildcard": { "matchingOption": 1 } } ] }
```
Every data point. A gradient on chart data points colours nothing without it.

```json
"selector": { "data": [ { "scopeId": { "Comparison": {
  "ComparisonKind": 0,
  "Left":  { "Column": { "Expression": { "SourceRef": { "Entity": "dim_activity" } }, "Property": "Activity" } },
  "Right": { "Literal": { "Value": "'Task'" } } } } } ] }
```
One category VALUE. Labels some series of a stacked chart and not others, and stores the width
of a matrix column generated from data rather than declared as a field.

A grand total column:

```json
"selector": { "data": [ { "total": [ { "Column": { "Expression": { "SourceRef": { "Entity": "dim_epic" } }, "Property": "Category" } } ] } ] }
```

The forms are not interchangeable. A gradient with a `metadata` selector, or a subtotal style
with no `id`, both parse fine and render nothing.

## Referencing a theme color instead of a hex

```json
"fontColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } }
```

- `ColorId`: `0` is `background`, `1` is `foreground`, `2` through `9` are `dataColors[0]`
  through `dataColors[7]`.
- `Percent`: a fraction, tint when positive, shade when negative. `0.6` is 60 percent lighter,
  `-0.25` is 25 percent darker.
- Use it wherever the colour has a meaning in the theme, so the visual survives a theme swap.

A pale banded subtotal row as the bad colour 60 percent lighter, not a hand picked pink:

```json
"backColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 5, "Percent": 0.6 } } } } }
```

## The container card block

One finished look, used on every chart, table and matrix in the report it came from. Use it when
the report has no container style of its own. When it has one, copy that instead.

```json
"visualContainerObjects": {
  "title": [{ "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": { "expr": { "Literal": { "Value": "'Actual vs estimated (%), 100% marks the estimate'" } } }
  }}],
  "subTitle": [{ "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": { "expr": { "Literal": { "Value": "'Delivered share of the estimate per client.'" } } }
  }}],
  "divider":    [{ "properties": { "show": { "expr": { "Literal": { "Value": "true" } } } } }],
  "spacing":    [{ "properties": { "verticalSpacing": { "expr": { "Literal": { "Value": "3D" } } } } }],
  "dropShadow": [{ "properties": { "show": { "expr": { "Literal": { "Value": "true" } } } } }],
  "border":     [{ "properties": { "show": { "expr": { "Literal": { "Value": "true" } } },
                                   "radius": { "expr": { "Literal": { "Value": "8D" } } } } }],
  "padding":    [{ "properties": { "top":    { "expr": { "Literal": { "Value": "2D" } } },
                                   "right":  { "expr": { "Literal": { "Value": "2D" } } },
                                   "bottom": { "expr": { "Literal": { "Value": "2D" } } },
                                   "left":   { "expr": { "Literal": { "Value": "2D" } } } } }]
}
```

- No font family, size, weight or colour here. Those go in the theme's `visualStyles` once (the
  theme block is in the `powerbi-report-design` skill).
- `padding` `2D` on all sides lets an 8 pixel gutter still look airy.
- Border radius plus shadow replace drawn background shapes, so there are no decorative objects
  to keep out of the tab order.

## Explaining a visual in two tiers

```json
"visualHeader":        [{ "properties": { "showTooltipButton": { "expr": { "Literal": { "Value": "true" } } } } }],
"visualHeaderTooltip": [{ "properties": { "text": { "expr": { "Literal": { "Value": "'Utilization percent = hours logged divided by available hours. Available hours = (sprint work days minus vacation and sick days) x 7.'" } } } } }]
```

Both in `visualContainerObjects`. A one line subtitle says what the visual shows, and the full
calculation rules sit behind the header information icon (wording rules are in the
`powerbi-report-design` skill). A matrix has no per column tooltip, so a per column legend goes
here too.

## Conditional formatting in JSON

### A gradient driven by a measure

```json
"dataPoint": [
  { "properties": { "borderShow": { "expr": { "Literal": { "Value": "true" } } } } },
  {
    "properties": { "fill": { "solid": { "color": { "expr": { "FillRule": {
      "Input": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Effort Ratio" } },
      "FillRule": { "linearGradient3": {
        "min": { "color": { "Literal": { "Value": "'#009E73'" } }, "value": { "Literal": { "Value": "0D"   } } },
        "mid": { "color": { "Literal": { "Value": "'#F0F0F0'" } }, "value": { "Literal": { "Value": "1D"   } } },
        "max": { "color": { "Literal": { "Value": "'#D55E00'" } }, "value": { "Literal": { "Value": "1.2D" } } },
        "nullColoringStrategy": { "strategy": { "Literal": { "Value": "'asZero'" } } }
      } }
    } } } } } },
    "selector": { "data": [ { "dataViewWildcard": { "matchingOption": 1 } } ] }
  }
]
```

- The first array element must exist, as the default data point placeholder.
- Without the `dataViewWildcard` selector the rule colours nothing.
- `nullColoringStrategy` `asZero` stops one blank stretching the whole ramp.

Target band stops, where under and over are both bad:

```json
"min": { "color": { "Literal": { "Value": "'#D55E00'" } }, "value": { "Literal": { "Value": "0.5D" } } },
"mid": { "color": { "Literal": { "Value": "'#009E73'" } }, "value": { "Literal": { "Value": "1D"   } } },
"max": { "color": { "Literal": { "Value": "'#D55E00'" } }, "value": { "Literal": { "Value": "1.2D" } } }
```

### A contrast safe matrix heatmap

One measure for the fill, one for the text, so the number stays readable as the cell darkens.

```json
"values": [
  { "properties": { "fontSize": { "expr": { "Literal": { "Value": "12D" } } } } },
  {
    "properties": {
      "backColor": { "solid": { "color": { "expr": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Heat Color" } } } } },
      "fontColor": { "solid": { "color": { "expr": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Heat Font" } } } } }
    },
    "selector": {
      "data": [ { "dataViewWildcard": { "matchingOption": 1 } } ],
      "metadata": "_Measures.Task Updates % of Grand Total"
    }
  }
]
```

The selector needs BOTH parts: the wildcard for every row, the metadata for which measure column.
Either alone silently does nothing. Keep the two measures' thresholds in step, so the font flips
to white at the band where the fill turns dark.

## Formatting that renders nothing

Copy and paste leaves dead overrides: a hidden title still carrying a full font and background
block (often with the copied visual's text), subtotal styling on a matrix with subtotals off, and
contradicting properties. How to strip them safely is in `pbir-structure-and-safety.md`.
