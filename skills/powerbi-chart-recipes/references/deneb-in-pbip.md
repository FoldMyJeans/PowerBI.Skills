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

To replace an existing visual with a Deneb one, copy the old visual's `z`, `tabOrder` and
`filterConfig` into the new `visual.json`, then set the title and subtitle in `visualContainerObjects`.
The helper does not carry those over.

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

## Traps with no error message

These drew something, just the wrong thing.

- **A tooltip key called `title`** shows in the Power BI tooltip as a row literally named "title". Use a
  real label such as `Name`.
- **Hover state sticks.** Anything set in `encode.hover` must also be set in `encode.update`, or it
  stays after the pointer leaves. A waffle kept black outlines on every square that had been hovered:

  ```json
  "update": {"stroke": {"value": null}, "strokeWidth": {"value": 0}},
  "hover": {"stroke": {"value": "#242424"}, "strokeWidth": {"value": 1.5}}
  ```

- **Rows where every measure is blank never arrive.** Power BI drops them before Deneb sees the data. A
  waffle of one square per person lost everyone with nothing overdue. Bind a measure that is never
  blank, such as a record count, so every row comes through.
- **The current month draws as 0%.** A month axis table includes the month in progress with a blank
  value. Filter it out first with `{"type": "filter", "expr": "datum.Pct != null"}`, which a native chart
  does by itself.
- **Scrollbars from padding.** `"autosize": {"type": "none"}` with `"padding": 4` and the width from
  `denebContainer` overflowed by the padding. Use `"padding": 0` and leave a margin in the layout math.
- **Line breaks in a text measure.** A tooltip measure joined with `UNICHAR ( 10 )` shows on one line.
  Split it in the spec with `split(datum.People, '\n')` and put each part under its own tooltip key.
- **A zero bar cannot be hovered.** A column at 0 has no height. Add an invisible full height rect per
  column, `fillOpacity` 0.001, that carries the tooltip.

## Hatching a gap

Vega has no pattern fill. A group per bar that clips diagonal rules from a `sequence` reads as hatching
and stays light. The data table:

```json
{"name": "hatch", "transform": [{"type": "sequence", "start": 0, "stop": 220}]}
```

The mark, one group per row of a `gaps` table that holds the gap from the bar to 100%:

```json
{"type": "group", "from": {"data": "gaps"},
 "encode": {"update": {
   "x": {"scale": "x", "field": "ord"}, "width": {"scale": "x", "band": 1},
   "y": {"scale": "y", "value": 1}, "y2": {"scale": "y", "field": "pct"},
   "fill": {"value": "#D13438"}, "fillOpacity": {"value": 0.05}, "clip": {"value": true}}},
 "marks": [{"type": "rule", "from": {"data": "hatch"},
   "encode": {"update": {
     "x": {"signal": "datum.data * 6 - 400"}, "y": {"value": 400},
     "x2": {"signal": "datum.data * 6"}, "y2": {"value": 0},
     "stroke": {"value": "#D13438"}, "strokeOpacity": {"value": 0.25}}}}]}
```

Inside the group the rules are in the group's own coordinates, so the 400 only has to exceed the
tallest bar. The `stop` sets how far the lines reach across the widest bar.

## Sources

The specs here are written for this repo. The ideas came from these, which are worth reading for more:
https://github.com/PBI-David/Deneb-Showcase (MIT), https://github.com/avatorl/Deneb-Vega-Templates (MIT)
and https://kerrykolosko.com/portfolio/ (no license stated, so ideas only). Deneb docs:
https://deneb.guide/
