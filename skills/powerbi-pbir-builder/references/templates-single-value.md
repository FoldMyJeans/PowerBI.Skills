# Complete templates: legacy card, KPI, gauge, textbox

Four visuals that show one number or one block of text. The new card visual, `cardVisual`, is a
different shape and lives in `cards-and-dynamic-text.md`.

Replace `<Measure>` and `<Title>`, give `name` a fresh 20 character hex string, and detect the
`visualContainer` version rather than copying the one below.

## Legacy card, `card`

Still the right tool for a thin value strip, where the new card visual cannot go small enough.
One role, `Values`, one projection.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "c3d4e5f60718293a4b5c",
  "position": { "x": 8, "y": 8, "z": 300, "height": 56, "width": 200, "tabOrder": 300 },
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<Measure>" } },
              "queryRef": "_Measures.<Measure>",
              "nativeQueryRef": "<Measure>"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [
        { "properties": {
            "fontSize": { "expr": { "Literal": { "Value": "10D" } } },
            "bold": { "expr": { "Literal": { "Value": "true" } } },
            "fontFamily": { "expr": { "Literal": { "Value": "'Segoe UI'" } } },
            "labelDisplayUnits": { "expr": { "Literal": { "Value": "1D" } } },
            "labelPrecision": { "expr": { "Literal": { "Value": "0L" } } }
        } }
      ],
      "categoryLabels": [
        { "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }
      ]
    },
    "visualContainerObjects": {
      "title": [
        { "properties": { "text": { "expr": { "Literal": { "Value": "'<Title>'" } } } } }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

The two objects are easy to mix up. `labels` is the big number itself. `categoryLabels` is the
small measure name underneath it, and turning it off is almost always right, because the
container title is already saying what the number is. Leaving both on prints the same words
twice.

`labelDisplayUnits` of `1D` means no unit scaling, so 1200000 prints in full. Use `1000D` for
thousands and `1000000D` for millions. Setting it to `0D` lets Power BI choose, which means the
unit can change as the filter changes, and a card that switches between K and M mid session is
worse than one that is simply long.

## KPI, `kpi`

Two roles, and neither is named what you would guess. `Indicator` is the value, `TrendLine` is
the series it is drawn against.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "d4e5f60718293a4b5c6d",
  "position": { "x": 216, "y": 8, "z": 400, "height": 96, "width": 240, "tabOrder": 400 },
  "visual": {
    "visualType": "kpi",
    "query": {
      "queryState": {
        "Indicator": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<Measure>" } },
              "queryRef": "_Measures.<Measure>",
              "nativeQueryRef": "<Measure>"
            }
          ]
        },
        "TrendLine": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_date" } }, "Property": "Month" } },
              "queryRef": "dim_date.Month",
              "nativeQueryRef": "Month"
            }
          ]
        }
      }
    },
    "objects": {
      "indicator": [
        { "properties": {
            "fontSize": { "expr": { "Literal": { "Value": "13D" } } },
            "bold": { "expr": { "Literal": { "Value": "false" } } }
        } }
      ]
    },
    "visualContainerObjects": {
      "title": [
        { "properties": { "text": { "expr": { "Literal": { "Value": "'<Title>'" } } } } }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

A KPI with no `TrendLine` renders as a bare number with no trend behind it, which is a card
with extra steps. If there is no time axis to put behind it, use a card instead.

## Gauge, `gauge`

Roles are `Y` for the value and `TargetValue` for the target.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "e5f60718293a4b5c6d7e",
  "position": { "x": 464, "y": 8, "z": 450, "height": 160, "width": 240, "tabOrder": 450 },
  "visual": {
    "visualType": "gauge",
    "query": {
      "queryState": {
        "Y": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<Measure>" } },
              "queryRef": "_Measures.<Measure>",
              "nativeQueryRef": "<Measure>"
            }
          ]
        },
        "TargetValue": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<TargetMeasure>" } },
              "queryRef": "_Measures.<TargetMeasure>",
              "nativeQueryRef": "<TargetMeasure>"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [
        { "properties": { "labelDisplayUnits": { "expr": { "Literal": { "Value": "1D" } } } } }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

A gauge spends a lot of canvas to show one number against one target. It reads well on a wall
display and poorly in a dense report, where a card with a variance measure says the same thing
in a fifth of the space.

## Textbox, `textbox`

No query at all. The content lives in a `paragraphs` structure under `general`, and the shape
is deeper than the rest of this file, so build one in Desktop and read it back if you need
anything beyond plain text.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "f60718293a4b5c6d7e8f",
  "position": { "x": 8, "y": 8, "z": 100, "height": 40, "width": 600, "tabOrder": 100 },
  "visual": {
    "visualType": "textbox",
    "objects": {
      "general": [
        { "properties": {
            "paragraphs": [
              {
                "textRuns": [
                  { "value": "<Text>", "textStyle": { "fontSize": "12pt", "fontWeight": "bold" } }
                ]
              }
            ]
        } }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

`paragraphs` is a plain array, not the `expr` and `Literal` wrapper every other property uses.
Font sizes here are CSS style strings like `12pt`, not the bare `12D` doubles used elsewhere.
It is the one visual whose formatting does not follow the house grammar.

A textbox holding a number that should update with the filters is a bug waiting to happen.
Static text only. For a heading that reacts to a slicer, use a card with a measure, which is in
`cards-and-dynamic-text.md`.
