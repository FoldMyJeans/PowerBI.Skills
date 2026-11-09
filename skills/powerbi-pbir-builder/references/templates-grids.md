# Complete templates: table and matrix

The structure is what Desktop wrote, only the names are placeholders, and the pre 2026
`autoSizeColumnWidth` key was removed by hand (check a fresh Desktop table if widths misbehave). The font sizes are one
dense default, so match the report's existing tables when it has them.

- Replace `<Table>`, `<Field>` and `<Measure>` with real model names, case sensitive.
- Give `name` a fresh 20 character hex string, unique within the report.
- Detect the `visualContainer` version rather than copying this one (`layout-and-schema-versions.md`).
- Literal suffixes: text is single quoted inside the JSON string, a double is `90D`, an integer
  `0L`, a boolean bare.

## Table, `tableEx`

`Values` is the only role, one projection per column in display order.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "a1b2c3d4e5f60718293a",
  "position": { "x": 8, "y": 80, "z": 500, "height": 312, "width": 628, "tabOrder": 500 },
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "<Table>" } }, "Property": "<Field>" } },
              "queryRef": "<Table>.<Field>",
              "nativeQueryRef": "<Field>"
            },
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "<Table>" } }, "Property": "<DateField>" } },
              "queryRef": "<Table>.<DateField>",
              "nativeQueryRef": "<DateField>",
              "format": "MMMM d, yyyy"
            },
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<Measure>" } },
              "queryRef": "_Measures.<Measure>",
              "nativeQueryRef": "<Measure>"
            }
          ]
        }
      },
      "sortDefinition": {
        "sort": [
          {
            "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "<Measure>" } },
            "direction": "Descending"
          }
        ]
      }
    },
    "objects": {
      "columnHeaders": [
        { "properties": {
            "columnAdjustment": { "expr": { "Literal": { "Value": "'growToFit'" } } },
            "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
            "bold": { "expr": { "Literal": { "Value": "true" } } }
        } }
      ],
      "values": [
        { "properties": { "fontSize": { "expr": { "Literal": { "Value": "8D" } } } } }
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

- `format` on a projection overrides the model's format string for this visual only, for example
  a full date in one table.
- `columnAdjustment` `growToFit` spreads the columns across the full width. `fitToContent`, the
  default since January 2026, shrink wraps them and usually leaves dead space on the right. A table
  whose columns never change is better on `fixedWidth` with a width per column. The width model is
  in `formatting-charts-and-tables.md`.
- `sortDefinition` sorts on any field in the query, displayed or not. Sorting by a measure the
  table does not show works.

## Matrix, `pivotTable`

`Rows` and `Columns` take the dimensions, `Values` the measures.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "b2c3d4e5f60718293a4b",
  "position": { "x": 8, "y": 80, "z": 600, "height": 400, "width": 768, "tabOrder": 600 },
  "visual": {
    "visualType": "pivotTable",
    "query": {
      "queryState": {
        "Rows": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "<Table>" } }, "Property": "<RowField>" } },
              "queryRef": "<Table>.<RowField>",
              "nativeQueryRef": "<RowField>",
              "active": true
            }
          ]
        },
        "Columns": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "<Table>" } }, "Property": "<ColField>" } },
              "queryRef": "<Table>.<ColField>",
              "nativeQueryRef": "<ColField>",
              "active": true
            }
          ]
        },
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
      "columnHeaders": [
        { "properties": {
            "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
            "bold": { "expr": { "Literal": { "Value": "true" } } }
        } }
      ],
      "rowHeaders": [
        { "properties": { "fontSize": { "expr": { "Literal": { "Value": "8D" } } } } }
      ],
      "values": [
        { "properties": { "fontSize": { "expr": { "Literal": { "Value": "8D" } } } } }
      ],
      "subTotals": [
        { "properties": {
            "rowSubtotals": { "expr": { "Literal": { "Value": "false" } } },
            "columnSubtotals": { "expr": { "Literal": { "Value": "false" } } }
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

- `active: true` marks the level the matrix is expanded to. Desktop writes it on the first level.
  In a multi level hierarchy only one level carries it.
- Subtotals off is the default here. Subtotals on every level is where most matrices stop being
  readable.
- Column widths are a per column `columnWidth` object keyed by a selector, not in this block. See
  `formatting-charts-and-tables.md`.
- Since 2026 a matrix freezes its row headers by default, can show +/- on column headers when
  Columns holds more than one field (`columnHeaders.showExpandCollapseButtons`), and can expand
  new levels on its own (`rowHeaders.autoExpand`, `columnHeaders.autoExpand`).

## When the matrix columns should be a calculation

Columns that are not values of any column (a capacity, a variance) need a disconnected header
table and a routing measure. See the `powerbi-dax` skill.
