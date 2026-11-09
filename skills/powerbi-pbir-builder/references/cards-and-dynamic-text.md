# Cards and text that reacts to filters

The two card visuals, titles bound to a measure, and the grain trap that makes such a title
quietly wrong.

## The new card, `cardVisual`

The `Data` role carries the measure. `displayName` on the projection is the label shown with the
value.

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

- Entries under `objects.value` and `objects.label` each need `"selector": { "id": "default" }`.
  The card ignores an entry with no selector.
- The value `fontColor` takes a `Measure` expression, so a measure returning a hex string brings
  a semantic good or bad colour to the card with no hardcoded hex.
- Overflow: a preformatted label like `439 v -35 vs last month` clips at 13pt inside a 200 by 112
  card. 10pt plus `textWrap: true` fits with room to spare.
- `ReferenceLabels` and `AdditionalMeasure` are the documented extra roles when the comparison is
  not baked into the measure string.

## Several values in one card

`cardVisual` holds multiple tiles, for example a value with its delta.

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

- Per tile number formatting: a second `value` entry selected by the measure's `queryRef`, for
  example `"selector": { "metadata": "Sum(fact_effort.Effort (Hours))" }`, carrying
  `labelDisplayUnits` and `labelPrecision`.
- `layout.rectangleRoundedCurve` does nothing once `shapeCustomRectangle` is present. If both
  appear with different values, the `shapeCustomRectangle` one wins and the other is leftover.

## A card inside a container border

When the container draws the box (title, subtitle, rounded border), turn the card's own outline
and fill off, or it draws a second box inside the first.

```json
"objects": {
  "label":      [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } }, "selector": { "id": "default" } }],
  "outline":    [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } }, "selector": { "id": "default" } }],
  "fillCustom": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } }, "selector": { "id": "default" } }]
},
"visualContainerObjects": {
  "title":    [{ "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": { "expr": { "Literal": { "Value": "'How far along are we'" } } } } }],
  "subTitle": [{ "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": { "expr": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Card Subtitle" } } } } }]
}
```

The title is the question, the value is the number, and a measure bound subtitle is the reliable
way to get one line of context under a card, for example `FORMAT ( [Passed], "#,0" ) & " of " &
FORMAT ( [Records], "#,0" ) & " passed"`.

## The legacy card still has a job

`cardVisual` has a minimum practical size. For a thin inline value strip between two charts,
roughly 208 by 32, use the legacy `card` with the title and category label off.

Not as a KPI tile. Anything with a label, a comparison or a semantic colour is `cardVisual`. A
theme change can also break the legacy card: when one report moved to a theme that styles
container titles, every legacy `card` lost its value because the title wrapped and filled the
tile. Converting them to `cardVisual` fixed all of them.

## Binding a title to a measure

Bind the title `text` to a measure that returns a string, and the title states the number in
context as slicers change. Write the measure blank safe:

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

The fallback is exactly the hardcoded title, so an empty selection degrades to a correct static
title, not a blank bar. In the `visual.json` only the title `text` changes, to a measure
reference:

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

Name these measures `Title <Visual>`, after the visual, so the measure to delete with the visual
is obvious. A conditional clause can vanish when there is nothing to report:

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

## The grain trap, check before you ship one

A title (or a card) is one value for the whole visual, so its measure runs at the visual total
grain, not per category. A ratio that sums cleanly, like effort over estimate, is fine. A per row
ratio breaks.

`DIVIDE ( SUM ( effort ), AVERAGE ( capacity ) )` is correct per person, but at the all people
level it is everyone's effort over one average capacity, roughly head count times too high. A
ratio near 90 percent rendered as over 1800 percent.

- Ratio sums cleanly: the weighted total, `DIVIDE ( SUM ( num ), SUM ( den ) )`.
- Per row ratio: `AVERAGEX` over the entity, for example
  `AVERAGEX ( VALUES ( dim_owner[Owner] ), [Per Person Ratio] )`.

The full treatment, including the `HASONEVALUE` form that switches between the leaf and the
averaged calculation, is in the `powerbi-dax` skill.

## Alt text can be dynamic too

Alt text takes the same measure binding, so a screen reader hears the current number. What the
string should say is in the `powerbi-report-design` skill.
