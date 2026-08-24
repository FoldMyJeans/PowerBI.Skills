# Filters and slicer sync

The `filterConfig` block on a page or a visual, and how slicers are wired to move together across
pages. These are the parts of PBIR that look cosmetic and change the numbers.

## Excluding blanks from a category

The most common filter you will write. A blank category shows up as an ugly empty bar or a broken
point at the end of a trend line.

A text column needs BOTH conditions. Excluding `null` alone leaves the empty strings behind, and
an API that returns `""` where it means nothing is the usual source of them.

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

The supporting keys matter:

- `ordinal` sets the order filters stack in the filter pane. Give each one a distinct value.
- `howCreated: "User"` marks a filter an author added, as opposed to one Desktop generated.
- `filterSortOrder: "Custom"` keeps the pane in your `ordinal` order rather than resorting it.
- Inside `From`, `Name` is a local alias and every `SourceRef` in the `Where` uses
  `{ "Source": "<alias>" }`, not the entity name again.

Fix the blanks upstream where you can. Normalizing `""` to `null` in M is one step and removes
the need for half of this filter. See the `powerbi-data-and-refresh` skill.

## Excluding a value by substring

Useful for keeping an internal company out of a client list without hardcoding every client.

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

Be careful with this one. A substring exclusion silently removes anything that happens to contain
the string, so a new client whose name embeds it disappears with no warning. Prefer an explicit
categorical exclusion, or a flag column in the model, when the list is stable.

## A slicer's own filter

A slicer carries a `Categorical` filter representing its current selection state.

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

`isInvertedSelectionMode` set to `true` is how a slicer represents "nothing excluded yet". It is
the real internal shape Desktop writes for a slicer with no selection, so keep it as shown rather
than trying to express an empty selection some other way.

## Filter names are scoped to the visual

The `name` on a filter only has to be unique inside that one visual's `filterConfig`. Desktop
reuses the same id across visuals when you duplicate one, so duplicates across the report are
normal and are not the same class of problem as a duplicate `lineageTag` in the model. Do not go
"fixing" them. See the `powerbi-project-and-tools` skill for the model side rule, which is the
opposite and is strict.

## Syncing slicers across pages

Sync is stored on each slicer as a `syncGroup`, at the `visual` level next to `visualType`.

```json
"syncGroup": {
  "groupName": "Companyfacteffort",
  "fieldChanges": true,
  "filterChanges": true
}
```

Slicers sharing a group name, with both change flags on, move together.

Name the group after the field AND the table it comes from, with punctuation and underscores
stripped. `Companyfacteffort`, `Companyfacteps`, and `Companydimworkitem` are three separate
groups for three Company slicers built on three different tables. That naming rule is what stops
same named slicers on different tables cross driving each other, which produces filter behaviour
nobody can explain later.

Leave search box slicers (`selfFilterEnabled`) out of sync groups. They are usually page specific
and syncing a search term across pages is rarely what anyone wants.

## Parking a filter without showing the control

A slicer can be hidden and still filter its page. The `isHidden` key and the tab order band to
use are in `layout-and-schema-versions.md`.

Use it sparingly. A filter nobody can see is a filter nobody can turn off, and the next person to
open the report will spend an hour working out why a number looks wrong. When you use one, name
the visual so its purpose is obvious, for example `vSprintFilterCarrier`, and note it in the page
documentation.

## Page level versus visual level

A `filterConfig` on `page.json` applies to every visual on the page. One on a `visual.json`
applies to that visual only. Prefer the page level filter when the whole page answers one scoped
question, because it is visible in the filter pane and a reader can see the scope. A pile of
identical visual level filters is harder to audit and easy to update inconsistently.
