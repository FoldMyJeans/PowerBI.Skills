# Formatting a visual, and the selector grammar

How formatting is written into a `visual.json`, and how a formatting entry says which part of
the visual it applies to. Getting the selector wrong is the most common reason a formatting
change appears to do nothing at all, with no error.

## Two places formatting lives

- `visual.objects` holds formatting that belongs to the visual TYPE. Axes, legend, data points,
  matrix values, slicer mode.
- `visual.visualContainerObjects` holds formatting that belongs to the CONTAINER around any
  visual. Title, subtitle, border, padding, shadow, the header tooltip.

The container surface is where a report's finished look comes from.

## Prerequisite: the report level switch

```json
"settings": { "useStylableVisualContainerHeader": true }
```

This lives in `definition/report.json`. Without it, the whole subtitle, divider, spacing, drop
shadow, and header tooltip system silently does nothing. No error, no warning, just no effect.
Check it before you write any container styling, and if it is missing, set it in Desktop by
turning on the modern visual header rather than hand editing `report.json`.

## The selector grammar, five forms

A formatting entry is an array. Each element has `properties` and, optionally, a `selector`. An
element with no selector is the default for the whole visual. Add a selector to target
something narrower.

```json
"selector": { "id": "default" }
```
Used by the card visual's value, label, and layout blocks. The card ignores an entry with no
selector, so `default` is required there rather than optional.

```json
"selector": { "id": "Row" }      // and { "id": "Column" }
```
Matrix subtotals only. The row and column subtotal levels are formatted separately, so a matrix
that styles both needs three entries: one bare entry carrying the on and off switches, then one
per axis.

```json
"selector": { "metadata": "_Measures.Task Updates % of Grand Total" }
```
Targets one measure or column by its `queryRef`, spelled exactly as the projection spells it.
This is how a column width or a per measure font size binds.

```json
"selector": { "data": [ { "dataViewWildcard": { "matchingOption": 1 } } ] }
```
Targets every data point. A gradient on chart data points needs this, otherwise it colors
nothing.

```json
"selector": { "data": [ { "scopeId": { "Comparison": {
  "ComparisonKind": 0,
  "Left":  { "Column": { "Expression": { "SourceRef": { "Entity": "dim_activity" } }, "Property": "Activity" } },
  "Right": { "Literal": { "Value": "'Task'" } } } } } ] }
```
Targets one category VALUE. This is how you label some series in a stacked chart and not
others, and how a matrix stores a column width for a column that is generated from data rather
than declared as a field.

A grand total column takes a shape of its own:

```json
"selector": { "data": [ { "total": [ { "Column": { "Expression": { "SourceRef": { "Entity": "dim_epic" } }, "Property": "Category" } } ] } ] }
```

The forms are not interchangeable. A gradient with a `metadata` selector, or a subtotal style
with no `id`, both parse fine and render nothing.

## Referencing a theme color instead of a hex

```json
"fontColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } }
```

`ColorId` indexes the theme: `0` is `background`, `1` is `foreground`, and `2` through `9` are
`dataColors[0]` through `dataColors[7]`. `Percent` is a tint when positive and a shade when
negative, as a fraction, so `0.6` is 60 percent lighter and `-0.25` is 25 percent darker.

Prefer this over a literal hex everywhere the color has a meaning in the theme, so the visual
survives a theme swap.

A pale banded subtotal row, for example, is the bad color at 60 percent lighter rather than a
hand picked pink:

```json
"backColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 5, "Percent": 0.6 } } } } }
```

## The container card, the block that makes a report look finished

Applied to every chart, table, and matrix in the source report.

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

Note what is NOT here. No font family, size, weight, or color. Put those in the theme's
`visualStyles` once, and every visual inherits them. See the `powerbi-report-design` skill for
the theme block that pairs with this.

`padding` at `2D` on all four sides is what lets an 8 pixel gutter still look airy. The border
radius plus the shadow replace the background shapes people normally draw to group visuals,
which also keeps the tab order clean because there are no decorative objects to exclude.

## Explaining a visual in two tiers

```json
"visualHeader":        [{ "properties": { "showTooltipButton": { "expr": { "Literal": { "Value": "true" } } } } }],
"visualHeaderTooltip": [{ "properties": { "text": { "expr": { "Literal": { "Value": "'Utilization percent = hours logged divided by available hours. Available hours = (sprint work days minus vacation and sick days) x 7.'" } } } } }]
```

Both sit in `visualContainerObjects`. The pattern that works: a one line subtitle saying what
the visual shows, and the full calculation rules behind an information icon in the header. End
the subtitle with a pointer to it, for example "Rules under the header help icon", so a reader
knows the detail exists. A matrix has no per column tooltip bucket, so this header tooltip is
also where a per column legend goes when each column follows a different rule.

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
    } } } } },
    "selector": { "data": [ { "dataViewWildcard": { "matchingOption": 1 } } ] }
  }
]
```

Three things that are easy to miss. The first array element must exist as the default data point
placeholder. The `dataViewWildcard` selector is required or the rule colors nothing.
`nullColoringStrategy` of `asZero` stops one blank stretching the whole ramp.

Swap the stops for a target band, where being under and being over are both bad:

```json
"min": { "color": { "Literal": { "Value": "'#D55E00'" } }, "value": { "Literal": { "Value": "0.5D" } } },
"mid": { "color": { "Literal": { "Value": "'#009E73'" } }, "value": { "Literal": { "Value": "1D"   } } },
"max": { "color": { "Literal": { "Value": "'#D55E00'" } }, "value": { "Literal": { "Value": "1.2D" } } }
```

### A contrast safe matrix heatmap

Two measures, one for the fill and one for the text, so the number stays readable as the cell
darkens.

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

This selector needs BOTH parts. The wildcard says every row, the metadata says which measure
column to paint. Either one alone silently does nothing.

Write the two measures so their thresholds match. The font flips to white at the same band where
the background crosses into dark. Change one, change the other.

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

Column widths bind by selector, and the shape differs by visual. A table uses `metadata` with the
`queryRef`. A matrix column generated from a data value uses the `scopeId` comparison form, and
the grand total uses the `total` form. Write a width against the wrong form and it parses and
never binds. Drag once in Desktop, save, then read back what it wrote.

## Watch for formatting that renders nothing

Copy and paste leaves dead overrides behind. A hidden title still carrying a full font and
background block (usually with the text of the visual it was copied from), subtotal styling on a
matrix whose subtotals are off, and two properties that contradict each other are all common.
See `pbir-structure-and-safety.md` for how to find and strip them safely.
