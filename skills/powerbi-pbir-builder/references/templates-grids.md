# Complete templates: table and matrix

Two copyable `visual.json` files, for `tableEx` (a flat table) and `pivotTable` (a matrix).
The structure is what Desktop writes. Only the names are placeholders.

Replace `<Table>`, `<Field>` and `<Measure>` with real model names, case sensitive, and give
`name` a fresh 20 character hex string that is unique within the report. Detect the
`visualContainer` version rather than copying the one below, see
`layout-and-schema-versions.md`.

Literal values follow the suffix convention in `formatting-and-selectors.md`. Text is single
quoted inside the JSON string, a double is `90D`, an integer is `0L`, and a boolean is bare.

## Table, `tableEx`

One projection per column, in the order you want them displayed. `Values` is the only role.

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
            "autoSizeColumnWidth": { "expr": { "Literal": { "Value": "true" } } },
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

Three things worth knowing before you change it.

`format` on a projection overrides the model's format string for this visual only. It is the
clean way to show a full date in one table without touching the column's model formatting.

`columnAdjustment` takes `growToFit`, which spreads the columns across the full width, or
`fitToContent`, which shrink wraps them and usually leaves dead space on the right. Pair
`growToFit` with `autoSizeColumnWidth`.

`sortDefinition` sorts on any field in the query, and it does not have to be a column you
display. Sorting a table by a measure it does not show is normal and works.

## Matrix, `pivotTable`

Same field reference shapes, three roles instead of one. `Rows` and `Columns` take the
dimensions, `Values` takes the measures.

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

`active: true` on a Rows or Columns projection marks which level the matrix is currently
expanded to. Desktop writes it on the first level. Leave it as it is unless you are building a
multi level hierarchy, in which case only one level carries it.

Turn subtotals off by default. A matrix with subtotals on every level is where most matrices
stop being readable, and `subTotals` is the one formatting bucket you will almost always set.

Column widths on a matrix are per column and live under a `columnWidth` object keyed by a
selector, not in this block. Only reach for that when a specific column has to be pinned,
because it fights `autoSizeColumnWidth`.

## When the matrix columns should be a calculation

If the columns need to be things that do not exist as values in any column, for example a
capacity or a variance, a matrix bound to a real field cannot do it. That needs a disconnected
header table and a routing measure, which is in the `powerbi-dax` skill.
