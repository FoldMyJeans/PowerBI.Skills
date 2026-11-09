# Complete templates: legacy card, KPI, gauge, textbox, image

One number, one block of text, or one picture. The new card, `cardVisual`, is in
`cards-and-dynamic-text.md`. Replace `<Measure>` and `<Title>`, give `name` a fresh 20 character
hex string, and detect the `visualContainer` version rather than copying this one.

## Legacy card, `card`

For a thin value strip, where `cardVisual` cannot go small enough. One role, `Values`.

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

- `labels` is the big number. `categoryLabels` is the small measure name under it. Turn that off
  when the container title already names the number, or the same words print twice.
- `labelDisplayUnits` `1D` is no scaling (1200000 prints in full), `1000D` thousands, `1000000D`
  millions. `0D` lets Power BI choose, so the card can switch between K and M as filters change.

## KPI, `kpi`

`Indicator` is the value, `TrendLine` the series it is drawn against.

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

With no `TrendLine` it renders as a bare number. No time axis means use a card.

## Gauge, `gauge`

`Y` is the value, `TargetValue` the target.

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

A gauge suits a wall display. In a dense report a card with a variance measure says the same in a
fifth of the space.

## Textbox, `textbox`

No query. Content is a `paragraphs` structure under `general`. For anything beyond plain text,
build one in Desktop and read it back.

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

- `paragraphs` is a plain array, not the `expr` and `Literal` wrapper every other property uses.
- Font sizes are CSS strings like `12pt`, not `12D` doubles.
- Static text only. A heading that reacts to a slicer is a measure bound card or title, see
  `cards-and-dynamic-text.md`.

## Image, `image`

The source is a formatting object pointing at a registered resource.

```json
"visual": {
  "visualType": "image",
  "objects": { "image": [{ "properties": { "sourceFile": { "image": {
    "name": { "expr": { "Literal": { "Value": "'logo.png'" } } },
    "url":  { "expr": { "ResourcePackageItem": {
                "PackageName": "RegisteredResources", "PackageType": 1,
                "ItemName": "logo12345.png" } } },
    "scaling": { "expr": { "Literal": { "Value": "'Normal'" } } }
  } } } }] }
}
```

- `ItemName` must match an entry in `definition/report.json` under `resourcePackages`, in the
  `RegisteredResources` package, with `"type": "Image"`. Desktop writes it when you insert the
  image, so insert once in Desktop rather than hand registering. Container border off for a logo.
- Page background picture: the same registered resource on the page's `background`, `scaling`
  `'Fill'`. A 1920 x 1080 JPG at quality 90, blended toward the page colour before upload, was
  56 KB.
- Image from a measure (an SVG from DAX): `image.sourceType` `'imageUrl'`, `sourceUrl` a
  `Measure` expression, `imageScalingType` `'Fit'`. Container `padding` 0 on all four sides,
  `background`, `border` and `title` off. With default padding the picture scaled down and sat off
  centre. Frames ending just above the page edge left a faint 1 px line over a background
  picture, so run them to the page bottom.
