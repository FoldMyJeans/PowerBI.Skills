# Filters and slicer sync

`filterConfig` on a page or visual, and slicer sync across pages. Both look cosmetic and change
the numbers.

## Excluding blanks from a category

A text column needs BOTH conditions. Excluding `null` alone leaves the empty strings, usually from
an API that returns `""` for nothing.

```json
"filterConfig": {
  "filters": [
    {
      "name": "excludeBlankCompany",
      "ordinal": 0,
      "field": { "Column": { "Expression": { "SourceRef": { "Entity": "fact_effort" } }, "Property": "Company" } },
      "type": "Advanced",
      "filter": {
        "Version": 2,
        "From": [ { "Name": "f", "Entity": "fact_effort", "Type": 0 } ],
        "Where": [ { "Condition": { "And": {
          "Left": { "Not": { "Expression": { "Comparison": {
            "ComparisonKind": 0,
            "Left":  { "Column": { "Expression": { "SourceRef": { "Source": "f" } }, "Property": "Company" } },
            "Right": { "Literal": { "Value": "null" } } } } } },
          "Right": { "Not": { "Expression": { "Comparison": {
            "ComparisonKind": 0,
            "Left":  { "Column": { "Expression": { "SourceRef": { "Source": "f" } }, "Property": "Company" } },
            "Right": { "Literal": { "Value": "''" } } } } } }
        } } } ]
      },
      "howCreated": "User"
    }
  ],
  "filterSortOrder": "Custom"
}
```

- `ordinal` is the stacking order in the filter pane. Give each filter a distinct value.
- `howCreated: "User"` marks an author added filter, as opposed to one Desktop generated.
- `filterSortOrder: "Custom"` keeps the pane in `ordinal` order.
- In `From`, `Name` is a local alias. Every `SourceRef` in `Where` uses `{ "Source": "<alias>" }`,
  not the entity name.
- Better upstream: normalizing `""` to `null` in M removes half of this filter. See the
  `powerbi-data-and-refresh` skill.

## Excluding a value by substring

Keeps an internal company out of a client list without listing every client.

```json
{
  "name": "excludeInternal",
  "ordinal": 1,
  "field": { "Column": { "Expression": { "SourceRef": { "Entity": "fact_effort" } }, "Property": "Company" } },
  "type": "Advanced",
  "filter": {
    "Version": 2,
    "From": [ { "Name": "f", "Entity": "fact_effort", "Type": 0 } ],
    "Where": [ { "Condition": { "Not": { "Expression": { "Contains": {
      "Left":  { "Column": { "Expression": { "SourceRef": { "Source": "f" } }, "Property": "Company" } },
      "Right": { "Literal": { "Value": "'ABC Company'" } }
    } } } } } ]
  },
  "howCreated": "User"
}
```

It also removes a new client whose name happens to contain the string, with no warning. Prefer
an explicit categorical exclusion, or a flag column in the model, when the list is stable.

## A slicer's own filter

A slicer carries a `Categorical` filter for its selection state.

```json
"filterConfig": {
  "filters": [
    {
      "name": "regionCategorical",
      "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_region" } }, "Property": "Region" } },
      "type": "Categorical",
      "objects": {
        "general": [
          { "properties": { "isInvertedSelectionMode": { "expr": { "Literal": { "Value": "true" } } } } }
        ]
      }
    }
  ]
}
```

`isInvertedSelectionMode` `true` is what Desktop writes for a slicer with no selection ("nothing
excluded yet"). Keep it as shown rather than expressing an empty selection another way.

## Filter names are scoped to the visual

A filter `name` only has to be unique inside one visual's `filterConfig`. Desktop reuses ids when
you duplicate a visual, so duplicates across the report are normal. Do not "fix" them. A duplicate
`lineageTag` in the model is the opposite, strict rule (the `powerbi-project-and-tools` skill).

## Syncing slicers across pages

`syncGroup` sits on each slicer at the `visual` level, next to `visualType`.

```json
"syncGroup": {
  "groupName": "Companyfacteffort",
  "fieldChanges": true,
  "filterChanges": true
}
```

Slicers sharing a group name, with both change flags on, move together. Name the group after the
field AND its table, punctuation and underscores stripped. `Companyfacteffort`, `Companyfacteps`
and `Companydimworkitem` are three groups for three Company slicers on three tables, so same
named slicers on different tables never cross drive each other.

Two ways a sync group fails without an error:

- Mixed slicer types. A button slicer (`advancedSlicerVisual`) and a classic `slicer` in one
  group do not share a selection. In one report every card on the page went blank. Keep one
  slicer type per group, or replace the pair with one control.
- Different lists on one field. Each synced slicer keeps its own visual level filters, so two
  synced slicers on the same field can offer different values. A page can then be filtered to a
  value its own dropdown does not list. Give synced slicers the same visual filters.

Leave search box slicers (`selfFilterEnabled`) out of sync groups. They are usually page
specific.

## Parking a filter without showing the control

A hidden slicer still filters its page. The `isHidden` key and its tab order band are in
`layout-and-schema-versions.md`. Use it sparingly: nobody can see or turn off that filter. Name
the visual for its purpose (`vSprintFilterCarrier`) and note it in the page documentation.

## Page level versus visual level

`filterConfig` on `page.json` applies to every visual on the page, on `visual.json` to that visual
only. When the whole page answers one scoped question, prefer the page filter. It shows in the
filter pane, and a pile of identical visual filters is hard to audit and drifts out of step.
