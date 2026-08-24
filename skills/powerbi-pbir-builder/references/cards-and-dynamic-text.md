# Cards and text that reacts to filters

The two card visuals, and how to bind a title or a label to a measure so it states the number in
context instead of repeating a field name. Includes the grain trap, which is the one way this
pattern goes wrong, and it goes wrong quietly.

## The new card, confirmed shape

The `Data` role carries the measure, and `displayName` on the projection is the label text shown
next to the value.

```json
"visual": {
  "visualType": "cardVisual",
  "query": {
    "queryState": {
      "Data": {
        "projections": [{
          "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "KPI Critical Label" } },
          "queryRef": "_Measures.KPI Critical Label",
          "nativeQueryRef": "KPI Critical Label",
          "displayName": "Critical Vulnerabilities"
        }]
      }
    }
  },
  "objects": {
    "value": [{
      "properties": {
        "fontSize": { "expr": { "Literal": { "Value": "10D" } } },
        "horizontalAlignment": { "expr": { "Literal": { "Value": "'left'" } } },
        "textWrap": { "expr": { "Literal": { "Value": "true" } } },
        "fontColor": { "solid": { "color": { "expr": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "KPI Critical Color" } } } } }
      },
      "selector": { "id": "default" }
    }],
    "label": [{
      "properties": {
        "position": { "expr": { "Literal": { "Value": "'aboveValue'" } } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } }
      },
      "selector": { "id": "default" }
    }]
  }
}
```

What the live confirmation established:

- Entries under `objects.value` and `objects.label` each need `"selector": { "id": "default" }`.
  The card ignores an entry with no selector.
- The value `fontColor` accepts a `Measure` expression, so a measure returning a hex string
  drives the card font color. This is how a semantic good or bad color reaches the card without a
  hardcoded hex sitting in the report layer.
- Watch overflow. A preformatted label like `439 v -35 vs last month` clips at 13pt inside a 200
  by 112 card. 10pt plus `textWrap: true` fits with room to spare.
- `ReferenceLabels` and `AdditionalMeasure` are the documented extra roles for when the
  comparison is not baked into the measure string.

## Several values in one card

`cardVisual` holds multiple tiles, which is how one card shows a value with its delta.

```json
"objects": {
  "layout": [
    { "properties": { "alignment":   { "expr": { "Literal": { "Value": "'middle'" } } },
                      "maxTiles":    { "expr": { "Literal": { "Value": "5L" } } },
                      "cellPadding": { "expr": { "Literal": { "Value": "5L" } } } } }
  ],
  "shapeCustomRectangle": [{
    "properties": { "tileShape":             { "expr": { "Literal": { "Value": "'rectangleRoundedByPixel'" } } },
                    "rectangleRoundedCurve": { "expr": { "Literal": { "Value": "15L" } } } },
    "selector": { "id": "default" }
  }]
}
```

Per tile number formatting is a second `value` entry selected by the measure's `queryRef`, for
example `"selector": { "metadata": "Sum(fact_effort.Effort (Hours))" }`, carrying
`labelDisplayUnits` and `labelPrecision`.

Note that `layout.rectangleRoundedCurve` also exists and does nothing once
`shapeCustomRectangle` is present. If you see both with different values, the
`shapeCustomRectangle` one wins and the other is leftover.

## The legacy card still has a job

`cardVisual` has a minimum practical size. For a thin inline value strip tucked between two
charts, roughly 208 by 32, the legacy `card` type is still the right tool. Set the title off,
keep the category label off, and let the value carry itself.

Do not reach for it as a KPI tile. For anything with a label, a comparison, or a semantic color,
use `cardVisual`.

## Binding a title to a measure

A visual title does not have to be static text. Bind the title `text` to a measure returning a
string and the title states the number in context and updates as slicers change.

Write the measure blank safe, so it falls back to a plain label when there is no data:

```dax
Title Effort vs Estimate =
VAR r = [Effort Ratio]
RETURN
IF (
    ISBLANK ( r ) || r = 0,
    "Actual vs estimated effort",
    "Actual effort is " & FORMAT ( r, "0%" ) & " of the estimate"
)
```

The fallback string should be exactly what the title would have said if it were hardcoded. Then
an empty selection degrades to a correct static title rather than to a blank bar.

In the `visual.json`, set the title `text` to a measure reference instead of a literal. Only the
`text` property changes, the rest of the title formatting stays as it was:

```json
"visualContainerObjects": {
  "title": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "text": {
          "expr": {
            "Measure": {
              "Expression": { "SourceRef": { "Entity": "_Measures" } },
              "Property": "Title Effort vs Estimate"
            }
          }
        }
      }
    }
  ]
}
```

Name these measures `Title <Visual>`, after the visual they title rather than the number they
compute. When the visual is deleted, the measure to delete is obvious.

A title can also carry a conditional clause that disappears when there is nothing to report:

```dax
Title Team Utilization =
VAR u = [Capacity Utilization (%)]
VAR over = COUNTROWS ( FILTER ( VALUES ( fact_capacity[Owner] ), [Capacity Utilization (%)] > 1 ) )
RETURN
IF (
    ISBLANK ( u ),
    "Capacity utilization by team member",
    "Team utilization averages " & FORMAT ( u, "0%" )
        & IF ( ISBLANK ( over ) || over = 0, "", ", " & over & " above 100%" )
)
```

## The grain trap, read this before you ship one

A title is one string for the whole visual, so the title measure is evaluated at the visual total
grain, not per category. That is fine for a measure that sums cleanly, like effort over estimate,
where the total is a correct weighted ratio. It breaks for a per row ratio.

The classic failure is `DIVIDE ( SUM ( effort ), AVERAGE ( capacity ) )`. Correct per person, but
at the all people level it reads the sum of everyone's effort over one average capacity, so the
title shows a number roughly the head count times too high. A ratio that should sit near 90
percent can render as over 1800 percent.

Fix it by aggregating at the right grain inside the measure:

- If the ratio sums cleanly, use the weighted total, `DIVIDE ( SUM ( num ), SUM ( den ) )`.
- If the ratio is per row and does not sum, average the per row values with `AVERAGEX` over the
  entity, for example `AVERAGEX ( VALUES ( dim_owner[Owner] ), [Per Person Ratio] )`.

The same trap applies to any measure shown as a single number, a card exactly as much as a title.
The `powerbi-dax` skill has the full treatment, including the `HASONEVALUE` form that switches
between the direct calculation at the leaf and the averaged one at every higher grain.

## Alt text can be dynamic too

Alt text takes the same measure binding, so a screen reader hears the current number rather than
a generic description. Build the string the same way and bind it to the alt text property. See
the `powerbi-report-design` skill for what the string should say.
