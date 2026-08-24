# Visual types and data binding

A `visual.json` describes one visual: its type, its data bindings (query roles), and its
formatting. This file covers the type catalog and how to bind fields to it.

Complete copyable files live in `templates-grids.md` (table and matrix) and
`templates-single-value.md` (legacy card, KPI, gauge, textbox). The new card visual and measure
bound titles are in `cards-and-dynamic-text.md`. Formatting and the selector grammar are in
`formatting-and-selectors.md`. Filters and slicer sync are in `filters-and-sync.md`.

## Visual type catalog

The Confirmed column tells you how far to trust the role names. A yes means they are exact. A no
means treat them as a starting guess.

The distinction matters because nothing checks a role name. Desktop ignores one it does not
recognize, with no error anywhere, and the result is a visual that renders empty and looks like
a data problem. For a row marked no, build the visual in Desktop once, save, and read the
`visual.json` back before trusting the names.

| Visual | `visualType` | Main query roles | Confirmed |
| --- | --- | --- | --- |
| Card, new | `cardVisual` | `Data` (the value), `ReferenceLabels` (a comparison), `AdditionalMeasure` (a change metric) | yes |
| Card, legacy | `card` | `Values`. Still the right tool for a thin inline value strip, where `cardVisual` cannot go small | yes |
| Bar or column | `clusteredColumnChart`, `clusteredBarChart`, `columnChart` (stacked), `barChart` (stacked) | `Category`, `Y`, `Series` (optional legend), `Tooltips` | yes |
| Line | `lineChart` | `Category`, `Y`, `Series` (optional) | yes |
| Area | `areaChart` | `Category`, `Y`, `Series` (optional) | yes |
| Combo | `lineClusteredColumnComboChart`, `lineStackedColumnComboChart` | `Category`, `Y` (the columns), `Y2` (the line), `Series` | yes |
| Table | `tableEx` | `Values`, one projection per column, in the column order you want | yes |
| Matrix | `pivotTable` | `Rows`, `Columns`, `Values` | yes |
| Slicer | `slicer` | `Values` | yes |
| Donut or pie | `donutChart`, `pieChart` | `Category`, `Y` | yes |
| Gauge | `gauge` | `Y` (the value), `TargetValue` | yes |
| KPI | `kpi` | `Indicator`, `TrendLine` | yes |
| Image | `image` | none, the source is a formatting object, see below | yes |
| Scatter | `scatterChart` | `Category`, `X`, `Y`, `Size` (optional) | no |
| Waterfall | `waterfallChart` | `Category`, `Y`, `Breakdown` (optional) | no |

Two roles are easy to miss on a cartesian visual:

- `Tooltips` takes extra measure projections that appear on hover without occupying the chart.
  Useful for putting a readable date on a chart whose axis shows a code.
- Small multiples is a projection role on a cartesian chart, not a separate visual type.

The combo chart is the one worth reading twice. Its roles are `Y` and `Y2`, plain positional
names, and nothing in the JSON says column or line. `Y` draws as columns and `Y2` draws as the
line. Putting a measure in the wrong one renders the chart with the two series swapped, which
looks deliberate and is easy to miss in review.

A visual can also be a group rather than a chart. In that case `visual` is replaced by
`visualGroup`, and its children each carry `parentGroupName` pointing at the group's `name`.

## Field references

A field reference is always one of these two shapes:

```json
{ "Column":  { "Expression": { "SourceRef": { "Entity": "TableName" } }, "Property": "ColumnName" } }
```
```json
{ "Measure": { "Expression": { "SourceRef": { "Entity": "MeasureTableName" } }, "Property": "MeasureName" } }
```

`Entity` and `Property` are the exact table and column or measure names in the semantic model,
case sensitive. `queryRef` is conventionally `"Table.Field"`, `nativeQueryRef` is just the field
name. Check the TMDL if unsure. A mismatch here parses fine and renders an empty visual.

## Letting the user choose the field

A field parameter table in the model can drive a role, so one slicer re-cuts the chart. The
`fieldParameters` block is a sibling of `projections` inside the role.

```json
"Series": {
  "projections": [
    { "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_activity" } }, "Property": "Activity" } },
      "queryRef": "dim_activity.Activity", "nativeQueryRef": "Activity", "displayName": "Activity" }
  ],
  "fieldParameters": [
    { "parameterExpr": { "Column": {
        "Expression": { "SourceRef": { "Entity": "Parameter - fact_effort" } },
        "Property": "Legend - Actual vs Estimated Efforts (Hour)" } },
      "index": 0, "length": 1 }
  ]
}
```

`index` is where in the role the swappable field sits and `length` is how many slots it
occupies. The `projections` entry is the currently selected field, so it still has to be a real
field. For the field parameter table's TMDL, see the `powerbi-dax` skill.

## Worked example: a trend chart

Replace the table and field names, and detect the `visualContainer` version rather than copying
the one below (see `layout-and-schema-versions.md`).

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "vSalesTrend",
  "position": { "x": 8, "y": 80, "z": 0, "height": 312, "width": 1264, "tabOrder": 500 },
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_date" } }, "Property": "Month" } },
              "queryRef": "dim_date.Month",
              "nativeQueryRef": "Month",
              "active": true
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Total Sales" } },
              "queryRef": "_Measures.Total Sales",
              "nativeQueryRef": "Total Sales"
            }
          ]
        },
        "Tooltips": {
          "projections": [
            {
              "field": { "Measure": { "Expression": { "SourceRef": { "Entity": "_Measures" } }, "Property": "Sales YoY %" } },
              "queryRef": "_Measures.Sales YoY %",
              "nativeQueryRef": "Sales YoY %"
            }
          ]
        }
      },
      "sortDefinition": {
        "sort": [
          {
            "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_date" } }, "Property": "Month" } },
            "direction": "Ascending"
          }
        ]
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

`drillFilterOtherVisuals` goes INSIDE `visual`, as a sibling of `visualType` and `query`, and is
`true` on essentially every visual Desktop writes. Include it. Putting it at the file root
instead is the easiest mistake to make here, and the schema does not define it there.

### The same template covers every cartesian chart

Column, bar and area charts are this file with a different `visualType` and the roles from the
catalog. There is nothing else structurally different, so do not go looking for another shape.
Swap `lineChart` for `clusteredColumnChart`, `columnChart`, `clusteredBarChart`, `barChart` or
`areaChart`, keep `Category` and `Y`, and add a `Series` role if you want a legend.

The one to read twice is the combo chart, because `Y` draws as columns and `Y2` draws as the
line, and nothing in the JSON says so.

## Worked example: a slicer

```json
{
  "name": "vRegionSlicer",
  "position": { "x": 8, "y": 8, "z": 10000, "height": 56, "width": 128, "tabOrder": 200 },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_region" } }, "Property": "Region" } },
              "queryRef": "dim_region.Region",
              "nativeQueryRef": "Region",
              "active": true
            }
          ]
        }
      }
    },
    "objects": {
      "data": [{ "properties": { "mode": { "expr": { "Literal": { "Value": "'Dropdown'" } } } } }],
      "general": [{ "properties": {
        "orientation":       { "expr": { "Literal": { "Value": "1D" } } },
        "selfFilterEnabled": { "expr": { "Literal": { "Value": "true" } } }
      } }],
      "selection": [{ "properties": {
        "selectAllCheckboxEnabled": { "expr": { "Literal": { "Value": "true" } } },
        "singleSelect":             { "expr": { "Literal": { "Value": "false" } } }
      } }],
      "header": [{ "properties": { "text": { "expr": { "Literal": { "Value": "'Region'" } } } } }]
    },
    "visualContainerObjects": {
      "title": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }]
    }
  }
}
```

Slicer specifics worth knowing:

- `mode` is `'Dropdown'` or `'Basic'`. Dropdown is the right default in a header strip, because
  it holds its height whatever the list length. Basic is the checkbox list.
- `orientation` is `1D` for horizontal and `0D` for vertical.
- `selfFilterEnabled` turns on the search box. Add it once a dimension passes roughly 30 members.
- Turn the container `title` off and set the slicer's own `header.text` instead. The label then
  sits inside the control, which is how a 56 pixel tall slicer still says what it filters.

## The image visual

Not a data visual. The source is a formatting object pointing at a registered resource.

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

The `ItemName` must match an entry in `definition/report.json` under `resourcePackages`, in the
`RegisteredResources` package, with `"type": "Image"`. Desktop writes that entry when you insert
the image, so insert it once in Desktop rather than hand registering the asset. Turn the
container border off so a logo has no box around it.

## Matrix, table, and the analytical visuals

- Matrix (`pivotTable`) uses `Rows`, `Columns`, `Values`. Its layout, subtotals, and grand totals
  are formatting objects, not query roles.
- Native sparklines live inside a table or matrix as an extra measure projection with a sparkline
  formatting object. They are capped at 5 per visual and 52 points, and they limit a matrix to 25
  columns.
- The AI visuals, decomposition tree and key influencers, are Pro safe, their intelligence runs
  in the engine rather than in Copilot. Their internal type and role names are less documented
  and less stable than the core charts, so generate one in Desktop, save, and read its
  `visual.json` before authoring one in code.
