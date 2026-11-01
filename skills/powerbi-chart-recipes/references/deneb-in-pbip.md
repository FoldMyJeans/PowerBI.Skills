# Deneb in a PBIP

Deneb is a certified visual that draws a Vega or Vega-Lite spec. It can be written straight into PBIR,
with nothing to import in Desktop. Close Desktop first.

## Use the helper

```powershell
python scripts\new_deneb_visual.py --report "ABC Sales.Report" --page pgOps --name vWaffle `
  --spec assets\deneb\waffle.vl.json `
  --column "Name=dim_control[Control]" `
  --measure "Value=_Measures[Coverage %]" `
  --x 40 --y 80 --w 480 --h 300
```

`Alias=Table[Field]` binds a model field under the name the spec reads. A table column called `Stage`
bound as `Name=Funnel[Stage]` reached the spec as `Name`, so a spec never has to change to match a
model. The helper takes the visual schema from a file Desktop already wrote, so the report needs at
least one visual.

## What it writes

Two things, both matching report files Desktop saved with Deneb in them.

In `definition/report.json`:

```json
"publicCustomVisuals": ["deneb7E15AEF80B9E4D4F8E12924291ECE89A"]
```

No `CustomVisuals` folder and no `resourcePackages` entry were needed. Desktop fetched Deneb itself
when the project opened on a machine with internet. A machine that blocks AppSource may not load it.

In the visual's `visual.json`, the role is `dataset` and the spec is a string:

```json
"visualType": "deneb7E15AEF80B9E4D4F8E12924291ECE89A",
"query": {"queryState": {"dataset": {"projections": [
  {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Funnel"}}, "Property": "Stage"}},
   "queryRef": "Funnel.Stage", "nativeQueryRef": "Name", "displayName": "Name"}
]}}},
"objects": {"vega": [{"properties": {
  "provider": {"expr": {"Literal": {"Value": "'vegaLite'"}}},
  "version": {"expr": {"Literal": {"Value": "'6.4.3'"}}},
  "jsonSpec": {"expr": {"Literal": {"Value": "'<the spec, with each single quote doubled>'"}}},
  "jsonConfig": {"expr": {"Literal": {"Value": "'{}'"}}},
  "enableTooltips": {"expr": {"Literal": {"Value": "true"}}}
}}]}
```

`provider` is `vegaLite` or `vega`. Deneb 2.0.1 bundles Vega-Lite 6.4.3 and Vega 6.4.0. Read
`package-lock.json` in deneb-viz/deneb after an update. Escaping the quotes by hand is where this goes
wrong, so use the helper.

## How Deneb reads data

- **Columns group.** Rows with the same values in every bound field collapse into one. A beeswarm of
  items needs the item key bound, or two items with the same age become one dot.
- **The row cap is 30,000.** That is the data reduction window in Deneb's capabilities.
- **Order fields are data.** Bind a sort column such as `RowOrder` when the spec sorts by it, even
  though nobody sees it. A spec can only read what is bound.
- **Dates arrive as dates.** The calendar spec still wraps them in `toDate`, so it also runs on text.
  Date only text such as `2025-01-01` is read as UTC, which put a stray empty 2024 row on a calendar in
  a time zone behind UTC. Text with a time, `2025-01-01T00:00:00`, reads as local.

## Sizing

- Vega: `"width": {"signal": "denebContainer.width"}`. The older `pbiContainerWidth` was deprecated at
  Deneb 2.0 and is a candidate for removal at 3.0.
- Vega-Lite single view: `"width": "container"`.
- Vega-Lite facets and concatenation take fixed sizes. The size is in the spec, not the visual. Three
  130 pixel waffles put a scrollbar on a 470 wide visual, and 118 fit. Size the spec for the visual.

## Interaction

Tooltips work with `enableTooltips` and a `tooltip` on the mark. To cross-filter other visuals,
set these in the `vega` object, as a report file with cross-filtering does:

```json
"enableSelection": {"expr": {"Literal": {"Value": "true"}}},
"selectionMode": {"expr": {"Literal": {"Value": "'simple'"}}},
"selectionMaxDataPoints": {"expr": {"Literal": {"Value": "50D"}}}
```

This has not been clicked through here, so test it on the fake report first. The bump chart's own click
to highlight is a Vega-Lite selection inside the visual and does not filter anything else.

## Errors these specs hit

| Message | Cause | Fix |
| --- | --- | --- |
| `Cycle detected in dataflow graph` | A scale reads a table whose transform calls that same scale | Leave `dataset` raw. Run the transform on a second table with `"source": "dataset"`. |
| `Duplicate signal name: "pick_tuple"` | A selection param at the top of a layered Vega-Lite spec | Put `params` on one layer |
| `Undefined data set name` | A table used before it is declared | Order the `data` array so sources come first |
| `Dropping {} from channel "y"` | Empty object used to clear an inherited encoding | Use `"y": null` |
| `Domains that should be unioned has conflicting sort` | Panels sort differently, and rows go alphabetical | Add a `RowOrder` with a window transform and sort with `"op": "min"` |

Vega returns `rgb(...)` from a colour scale, so comparing it to a hex string is always false. Test the
value instead. That mistake printed dark text on the darkest room of the floor plan.

## Sources

The specs here are written for this repo. The ideas came from these, which are worth reading for more:
https://github.com/PBI-David/Deneb-Showcase (MIT), https://github.com/avatorl/Deneb-Vega-Templates (MIT)
and https://kerrykolosko.com/portfolio/ (no license stated, so ideas only). Deneb docs:
https://deneb.guide/
