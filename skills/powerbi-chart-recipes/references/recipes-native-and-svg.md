# Native and SVG recipes

These need no third-party visual. Measures are in `assets/dax`. For the mechanics of SVG in a measure
and its escaping, see `svg-from-dax.md` in `powerbi-dax`.

## KPI table with bullets and split sparklines

Paste `bullet.dax` and `split-sparkline.dax`. Replace the placeholder measures and `'Date'[Month]`.
Set Data Category to Image URL on both, then put them in a `tableEx` with the row label. Image size is
on the grid object:

```json
"objects": {"grid": [{"properties": {
  "imageHeight": {"expr": {"Literal": {"Value": "40D"}}},
  "imageWidth": {"expr": {"Literal": {"Value": "160D"}}}
}}]}
```

- The axis column must be numeric, because the sparkline subtracts it. Use a month index, not a name.
- Turn off totals unless a total bullet means something. The table draws one by default.
- SVG has no legend, so say what the tick and the colours mean in the title or tooltip.
- Do not name a variable after a function. `VAR MinX` made the table show "Something's wrong with one or
  more fields" until it was renamed `LowX`, because `MINX` is a function.
- In the bullet, set `Scale` and the bands to your KPI's range.
- The image keeps its aspect ratio. Raising `imageWidth` alone only centres the same small bullet in a
  wider cell. Set `Width` and `Height` in the measure to the cell size, for example 300 by 18, and match
  `imageWidth` and `imageHeight` to them.

## Animated KPI card

Paste `animated-kpi-card.dax`, set Data Category to Image URL, and bind it to an image visual:

```json
"visualType": "image",
"objects": {"image": [{"properties": {
  "sourceType": {"expr": {"Literal": {"Value": "'imageUrl'"}}},
  "sourceUrl": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Animated KPI Card SVG"}}}
}}]}
```

A one column `tableEx` also draws it, with a header and a scrollbar to hide, so prefer the image visual.

Each bar's real height is its base attribute, and the animation only runs from low to real without
`fill='freeze'`. So a renderer that ignores animation shows correct bars. A design that sets height 0
and animates up would draw empty bars there. Bars replay from the start on each redraw and cannot glide
from their last state. For that, see `powerbi-custom-visuals`.

## Butterfly, native

One stacked bar chart, with the left side negative and a format string that hides the minus:

```dax
Opened Left = -SUM ( Fact[Opened] )
```

```text
Format string for Opened Left: #,0;#,0
```

```json
"visualType": "barChart",
"query": {"queryState": {
  "Category": {"projections": ["<the label column>"]},
  "Y": {"projections": ["<Opened Left>", "<Closed Right>"]}
}}
```

- Hide the value axis and show data labels.
- Sort with Sort by Column on the label column in the model. A `sortDefinition` on a field that is not
  in the visual was ignored, and rows came out alphabetical.
- Labels sit at the left, not the centre. For centre labels use the Deneb spec.
- A log axis cannot show negative values, so the butterfly stays linear and large categories dominate.
  If a few rows dwarf the rest, split them out or use the Deneb spec.

## Target as tick marks on a combo chart

Use this when the category axis has no order, for example members or companies. A target line that
joins unordered categories has a slope that means nothing. On an ordered axis such as a trend, keep the
dashed target line.

Bars in `Y`, the target in `Y2` of `lineStackedColumnComboChart`. The marker properties go on the base
`lineStyles` entry with no selector, and the series entry only turns the stroke off. A marker set on the
series entry alone did not draw.

```json
"lineStyles": [
  {"properties": {
    "showMarker": {"expr": {"Literal": {"Value": "true"}}},
    "markerShape": {"expr": {"Literal": {"Value": "'longDash'"}}},
    "markerSize": {"expr": {"Literal": {"Value": "10D"}}}}},
  {"properties": {
    "strokeShow": {"expr": {"Literal": {"Value": "false"}}},
    "showMarker": {"expr": {"Literal": {"Value": "true"}}},
    "markerShape": {"expr": {"Literal": {"Value": "'longDash'"}}},
    "markerSize": {"expr": {"Literal": {"Value": "10D"}}}},
   "selector": {"metadata": "<target queryRef>"}}
]
```

- Colour the target red with a `dataPoint` `fill` on the same `metadata` selector, for example
  `#C62828`.
- Give the bars `fillTransparency` of about `45D` in their `dataPoint` entry, so the tick shows on top.
- Hide the target's data label with a `labels` entry of `showSeries` false on the target selector. The
  tooltip still shows its value.

## Labels inside bars that get cut off

```json
"categoryAxis": [{"properties": {"innerPadding": {"expr": {"Literal": {"Value": "8L"}}}}}],
"labels": [{"properties": {
  "labelPosition": {"expr": {"Literal": {"Value": "'InsideCenter'"}}},
  "labelDisplayUnits": {"expr": {"Literal": {"Value": "1000D"}}},
  "labelPrecision": {"expr": {"Literal": {"Value": "1L"}}},
  "enableBackground": {"expr": {"Literal": {"Value": "false"}}},
  "fontSize": {"expr": {"Literal": {"Value": "7D"}}},
  "bold": {"expr": {"Literal": {"Value": "true"}}}}}]
```

A smaller `innerPadding` narrows the gap between categories and widens the bars. Fixed K units show
145,191 as 145.2K, and 7 pt bold fits inside the bar. A format string that switches to K only above
1,000 did not work in data labels. See dynamic format strings in `powerbi-dax`.

## Total at the end of a stacked bar

```json
"totals": [{"properties": {
  "show": {"expr": {"Literal": {"Value": "true"}}},
  "bold": {"expr": {"Literal": {"Value": "true"}}}}}]
```

## Waterfall from one scan to the next

A bridge from the previous total, minus what was fixed, plus what is new. Build a step table as a
calculated table:

```dax
Bridge Step =
DATATABLE (
    "Step", STRING, "Order", INTEGER,
    { { "Previous", 1 }, { "Fixed", 2 }, { "New", 3 } }
)
```

Sort `Step` by `Order`, hide `Order`, and add `ref table 'Bridge Step'` to `model.tmdl` or the table
does not load. One measure drives every bar:

```dax
Bridge Value =
SWITCH (
    SELECTEDVALUE ( 'Bridge Step'[Step] ),
    "Previous", [Previous Total],
    "Fixed", - [Fixed],
    "New", [New]
)
```

Put `Step` in `Category` and the measure in `Y` of a `waterfallChart`. Power BI adds the final bar
itself and labels it "Total". Colours are on the visual:

```json
"sentimentColors": [{"properties": {
  "increaseFill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F2D06B'"}}}}},
  "decreaseFill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#4F9A6A'"}}}}},
  "totalFill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A6A6A6'"}}}}}}}]
```

Every rising bar takes the increase colour, the first one included, so the starting total reads as an
increase. Here a fall is good, so the decrease colour is the green one.

## Filter drawer

The drawer is a page set to hidden, with a see-through button over the left to close it:

```json
"visibility": "HiddenInViewMode"
```

Layers from the bottom, on a page the same size as the report:

| Layer | Visual | Position on 1280 by 720 |
| --- | --- | --- |
| Dim | image, `Drawer Dim SVG` | Full page |
| Click outside | `actionButton`, no text, fill and outline off, navigates back | 0, 0, 900 wide, full height |
| Panel | image, `Drawer Panel SVG` | 904, 16, 360 by 688 |
| Close | `actionButton`, navigates back | 1212, 28, 36 by 36 |
| Slicers | `slicer`, in a sync group with the report pages | From 924, 90, 320 wide |

Open it with a button on each report page. Page navigation goes on the button's container:

```json
"visualContainerObjects": {"visualLink": [{"properties": {
  "show": {"expr": {"Literal": {"Value": "true"}}},
  "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
  "navigationSection": {"expr": {"Literal": {"Value": "'pgReport'"}}}
}}]}
```

- The button needs `"fill": [{"properties": {"show": ...false}}]` in `objects`. Without it the button
  paints white over the dim layer.
- Draw the dim and panel as image measures. A `shape` visual written by hand ignored its fill and kept a
  thick grey outline. If you want a shape, add it in Desktop and read the JSON back.
- A page cannot show another page, so the report is not visible behind the dim. If it must stay live,
  use a bookmark that shows and hides a group on the same page instead. Capture bookmarks in Desktop and
  read them back, because their state is not practical to hand write.
- Slicers reach other pages only through sync groups. See `filters-and-sync.md` in `powerbi-pbir-builder`.
- In Desktop a button needs Ctrl and click.

## Wall screen dark mode

Add a disconnected `Theme` table with one column `Mode` holding Light and Dark, shown as a button slicer.
Paste `theme-colours.dax`. Then bind colours to the measures:

```json
"color": {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Colour Card"}}}}}
```

| Part | Where |
| --- | --- |
| Page | Full page image visual at the bottom, `Page Backdrop SVG` |
| Card and chart background | `visualContainerObjects.background`, `color`, and turn `border` off |
| Card value and label | `objects.labels.color`, `objects.categoryLabels.color` |
| Axis labels and gridlines | `categoryAxis.labelColor`, `valueAxis.labelColor`, `valueAxis.gridlineColor` |
| Line colour | `objects.dataPoint.fill` with `"selector": {"metadata": "_Measures.KPI Actual"}` |

- The page's own background bound to `Colour Page` stayed white with a page filter set to Dark, so the
  backdrop is an image. It follows filters like any visual.
- A `dataPoint.fill` with no selector was ignored on a line chart. It needs the `metadata` selector.
- Every colour in every visual needs binding. That is the cost, so build this for a report family only if
  a wall screen will really use it.
- If the wall screen only ever shows dark, a copy of the report with a dark theme is far cheaper.
- Colour literals inside a Deneb spec or an SVG measure do not follow this unless they read the measures.
