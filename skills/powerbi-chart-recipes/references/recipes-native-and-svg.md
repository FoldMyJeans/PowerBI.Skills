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
