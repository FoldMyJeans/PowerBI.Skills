# Visual types and data binding

Type catalog and field binding. Complete files: `templates-grids.md` (table, matrix) and
`templates-single-value.md` (legacy card, KPI, gauge, textbox, image). New card and measure bound
titles: `cards-and-dynamic-text.md`. Selectors: `formatting-and-selectors.md`. Filters and sync:
`filters-and-sync.md`.

## Visual type catalog

Confirmed yes means the role names were read from a file Desktop wrote. No means a starting
guess. Desktop silently ignores a role name it does not recognize, and the visual renders empty
like a data problem. For a no row, build the visual in Desktop once, save, and read the
`visual.json` back.

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
| List slicer (preview) | `listSlicer` | `Values`, the classic slicer's query carried over unchanged | yes |
| Button slicer | `advancedSlicerVisual` | `Values` | yes |
| Input slicer | `textSlicer` | `Values` assumed, not seen in a saved file | no |
| Donut or pie | `donutChart`, `pieChart` | `Category`, `Y` | yes |
| Gauge | `gauge` | `Y` (the value), `TargetValue` | yes |
| KPI | `kpi` | `Indicator`, `TrendLine` | yes |
| Image | `image` | none, the source is a formatting object, see below | yes |
| Scatter | `scatterChart` | `Category`, `X`, `Y`, `Size` (optional) | no |
| Waterfall | `waterfallChart` | `Category`, `Y`, `Breakdown` (optional) | yes for `Category` and `Y`. `Breakdown` not yet seen in a saved file |
| Gantt (preview, October 2026) | `ganttChart` | Task label, Start, End, progress measure, up to three category levels. Role names not documented | no |
| Shape map (GA June 2026) | `shapeMap` | Location and a value. Role names not documented | no |

2026 notes on the catalog: the donut takes a centre value (`centerValue`, `value`, `label`,
`centerBackground`, August 2026), and the July only keys `valueFontColor` and similar were removed.
The card, button slicer and list slicer take `layout.showFixedSize` with `fixedHeight` and
`fixedWidth` (April 2026) as the alternative to Fit to space (`autoGrid`).

- `Tooltips` takes extra measure projections shown on hover, for example a readable date on a
  chart whose axis shows a code.
- Small multiples is a projection role on a cartesian chart, not a separate visual type.
- Combo chart: `Y` draws as columns and `Y2` as the line, and nothing in the JSON says so. A
  measure in the wrong one swaps the series, which looks deliberate and slips past review.
- A group replaces `visual` with `visualGroup`. Each child carries `parentGroupName` set to the
  group's `name`.

## Field references

A field reference is always one of these two shapes:

```json
{ "Column":  { "Expression": { "SourceRef": { "Entity": "TableName" } }, "Property": "ColumnName" } }
```
```json
{ "Measure": { "Expression": { "SourceRef": { "Entity": "MeasureTableName" } }, "Property": "MeasureName" } }
```

`Entity` and `Property` are exact model names, case sensitive. `queryRef` is `"Table.Field"`,
`nativeQueryRef` is the field name. A mismatch parses fine and renders an empty visual.

## Letting the user choose the field

A field parameter can drive a role, so one slicer re-cuts the chart. `fieldParameters` is a
sibling of `projections` inside the role.

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

- `index` is where the swappable field sits in the role, `length` how many slots it takes.
- The `projections` entry is the currently selected field, so it must be a real field.
- On a table: the parameter's first field in the `tableEx` `Values` role, plus the
  `fieldParameters` entry with `index` 0 and `length` 1. A table whose columns change this way
  needs `growToFit` column sizing, see `formatting-charts-and-tables.md`.
- The field parameter table's TMDL is in the `powerbi-dax` skill.

## Worked example: a trend chart

Replace the names, and detect the `visualContainer` version rather than copying this one (see
`layout-and-schema-versions.md`).

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

- `drillFilterOtherVisuals` goes INSIDE `visual`, a sibling of `visualType` and `query`, and is
  `true` on nearly every visual Desktop writes. The schema does not define it at the file root,
  the easiest place to put it by mistake.
- The same file covers every cartesian chart. Swap `lineChart` for `clusteredColumnChart`,
  `columnChart`, `clusteredBarChart`, `barChart` or `areaChart`, keep `Category` and `Y`, and add
  `Series` for a legend. Nothing else differs. The combo chart's `Y` and `Y2` are above.

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

- `mode` is `'Dropdown'` or `'Basic'` (the checkbox list). Dropdown holds its height in a header
  strip whatever the list length. Set it explicitly: on the Fluent 2 base theme a new slicer
  defaults to Dropdown, on older ones it does not.
- `orientation` is `1D` for horizontal and `0D` for vertical.
- `selfFilterEnabled` turns on the search box. Add it past roughly 30 members.
- Container `title` off, slicer `header.text` on. The label then sits inside the control, so a
  56 pixel slicer still says what it filters.

## Matrix, table, and the analytical visuals

- Matrix (`pivotTable`) layout, subtotals and grand totals are formatting objects, not roles.
- Native sparklines are an extra measure projection in a table or matrix with a sparkline
  formatting object. Capped at 5 per visual and 52 points, and they limit a matrix to 25 columns.
- Decomposition tree and key influencers are Pro safe (they run in the engine, not Copilot). Their
  type and role names are less documented and less stable, so generate one in Desktop and read
  its `visual.json` first.
