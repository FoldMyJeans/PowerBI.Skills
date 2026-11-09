# List slicer in dropdown mode

`listSlicer` with `data.dropdownMode` true (October 2026, preview, Pro). It is the only slicer
with a setting for the size of the open list, `dropdownMenu.width` and `dropdownMenu.maxHeight`,
so a narrow box can open a wide list and long names read in full. The classic slicer's open list
is always as wide as its box. Microsoft gives no range or default for either size.

Other objects in theme schema 2.159: `pills` (the removable selections), `search`, and
`selectedOnly` (Show selected first, also on the button slicer).

This is one styled option, not a required look. It was built to sit beside classic dropdowns and
look the same. The template below is the shape a script wrote into a whole report of slicers on
Desktop 2.159, rendered page by page, then published, with every property name checked against
theme schema 2.159.

## Converting a classic slicer

Keep `query`, `filterConfig`, `position`, the saved `general.filter`, the `selection` object
(`singleSelect`, `strictSingleSelect`, `selectAllCheckboxEnabled`) and `general.altText`. Swap
`visualType` and `objects`. A Clear all slicers button clears list slicers too.

Three behaviours to know before converting a saved selection: Select all and then clearing items
saves a NOT filter, items sort by Value only, never by Label, and a selection on a value hidden by
search stays active.

## Template

```json
{
  "visualType": "listSlicer",
  "objects": {
    "data": [{ "properties": {
      "dropdownMode": { "expr": { "Literal": { "Value": "true" } } } } }],
    "general": [{ "properties": {
      "selfFilterEnabled": { "expr": { "Literal": { "Value": "true" } } } } }],
    "dropdownMenu": [{ "properties": {
      "width":          { "expr": { "Literal": { "Value": "320D" } } },
      "maxHeight":      { "expr": { "Literal": { "Value": "296D" } } },
      "cornerRadius":   { "expr": { "Literal": { "Value": "6D" } } },
      "paddingUniform": { "expr": { "Literal": { "Value": "4D" } } } } }],
    "dropdownButton": [{ "properties": {
      "cornerRadius": { "expr": { "Literal": { "Value": "6D" } } },
      "iconShow":     { "expr": { "Literal": { "Value": "true" } } },
      "iconColor":    { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } } } }],
    "selectionBox": [{ "properties": {
      "placeholderText":   { "expr": { "Literal": { "Value": "'All'" } } },
      "borderShow":        { "expr": { "Literal": { "Value": "true" } } },
      "borderColor":       { "solid": { "color": { "expr": { "Literal": { "Value": "'#D1D1D1'" } } } } },
      "borderWidth":       { "expr": { "Literal": { "Value": "1D" } } },
      "cornerRadius":      { "expr": { "Literal": { "Value": "6D" } } },
      "fontSize":          { "expr": { "Literal": { "Value": "8D" } } },
      "accentBarShow":     { "expr": { "Literal": { "Value": "true" } } },
      "accentBarWidth":    { "expr": { "Literal": { "Value": "3D" } } },
      "accentBarPosition": { "expr": { "Literal": { "Value": "'Bottom'" } } } } }],
    "value": [{ "properties": {
      "fontSize": { "expr": { "Literal": { "Value": "8D" } } } }, "selector": { "id": "default" } }],
    "padding": [{ "properties": {
      "paddingSelection": { "expr": { "Literal": { "Value": "'Custom'" } } },
      "topMargin":    { "expr": { "Literal": { "Value": "2D" } } },
      "bottomMargin": { "expr": { "Literal": { "Value": "2D" } } },
      "leftMargin":   { "expr": { "Literal": { "Value": "4D" } } },
      "rightMargin":  { "expr": { "Literal": { "Value": "4D" } } } }, "selector": { "id": "default" } }],
    "layout": [{ "properties": {
      "style":         { "expr": { "Literal": { "Value": "'Table'" } } },
      "orientation":   { "expr": { "Literal": { "Value": "1D" } } },
      "autoGrid":      { "expr": { "Literal": { "Value": "false" } } },
      "columnCount":   { "expr": { "Literal": { "Value": "1D" } } },
      "showFixedSize": { "expr": { "Literal": { "Value": "true" } } },
      "fixedHeight":   { "expr": { "Literal": { "Value": "24D" } } },
      "cellPadding":   { "expr": { "Literal": { "Value": "0D" } } },
      "rowPadding":    { "expr": { "Literal": { "Value": "0D" } } } } }],
    "overFlow": [{ "properties": {
      "overFlowStyle":     { "expr": { "Literal": { "Value": "1D" } } },
      "overFlowDirection": { "expr": { "Literal": { "Value": "0D" } } } } }],
    "selectionIcon": [{ "properties": {
      "size": { "expr": { "Literal": { "Value": "12D" } } } }, "selector": { "id": "default" } }],
    "pills":  [{ "properties": { "fontSize": { "expr": { "Literal": { "Value": "8D" } } } } }],
    "search": [{ "properties": { "fontSize": { "expr": { "Literal": { "Value": "8D" } } } } }]
  },
  "visualContainerObjects": {
    "title": [{ "properties": {
      "show":       { "expr": { "Literal": { "Value": "true" } } },
      "text":       { "expr": { "Literal": { "Value": "'Owner'" } } },
      "fontSize":   { "expr": { "Literal": { "Value": "8D" } } },
      "fontFamily": { "expr": { "Literal": { "Value": "'Segoe UI Semibold'" } } },
      "fontColor":  { "solid": { "color": { "expr": { "Literal": { "Value": "'#616161'" } } } } } } }],
    "subTitle":   [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }],
    "border":     [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }],
    "background": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }],
    "padding": [{ "properties": {
      "top":    { "expr": { "Literal": { "Value": "0D" } } },
      "bottom": { "expr": { "Literal": { "Value": "2D" } } },
      "left":   { "expr": { "Literal": { "Value": "5D" } } },
      "right":  { "expr": { "Literal": { "Value": "5D" } } } } }],
    "spacing": [{ "properties": {
      "customizeSpacing": { "expr": { "Literal": { "Value": "true" } } },
      "spaceBelowTitle":  { "expr": { "Literal": { "Value": "7D" } } } } }]
  }
}
```

Drop `search`, and set `selfFilterEnabled` false, on a list of fewer than about ten values.

## What each piece fixes

- `layout` and `overFlow`. The default layout, Fit to space (`autoGrid` true), splits the drawer
  height into equal rows whatever the number of options. A 420 px drawer gave rows about 52 px tall,
  296 gave 37 px, and 144 gave 18 px rows with clipped text. Table style, one column, fixed 24 px
  rows, and continuous scroll (`overFlowStyle` 1, vertical `overFlowDirection` 0) keep every row the
  same height.
- Container `border` and `background` off. New visuals pick up the theme's container border and
  background, so the first render was a bordered card.
- `subTitle.show` false. The field name printed twice and pushed the box below a 56 px frame. The
  second line is the container subtitle. `label.show` false did nothing.
- `selectionBox` styles the closed box (the visible "All"), not `value` or `outline`. Top level
  `outline` and `accentBar` style the items in the open list.
- Title font, size and colour set on the visual. A classic slicer's header style can live in the
  theme (`visualStyles.slicer.*.header`), and a list slicer's title does not inherit it, so copy
  the values across or the row of slicers will not match.
- `spaceBelowTitle` 7 lines the box up with a classic dropdown beside it at the same 27 px height.
  Without it the box sat 5 px high. 5 left it about 1 px high. `spacing.spaceBelowTitleArea` had no
  effect. Measure this from a render, eyeballing missed it. It still lined up at the 8 pt sizes in
  the template. Since July 2026 the spacing keys are `spaceAboveSubtitle`, `spaceAboveDivider` and
  `spaceAbovePlotArea`, and the old `spaceBelow` keys still load and migrate. Keep `spaceBelowTitle`
  here until the matching new key has been read back from a Desktop file.
- Container padding left 5 and right 5. Without it the boxes in a stacked column ran edge to edge,
  while classic boxes are inset about 5 px each side.
- `dropdownButton.iconSize` 14 made no visible difference. The arrow stays a little smaller than the
  classic one.

## Sizing from the data

A rule that held across a report of slicers at 8 pt Segoe UI. The pixel constants are estimates
with slack, not measurements.

- Box: as wide as its label, about 6.5 px per character plus 24, never under 104. When a default
  selection always shows as a pill (a saved "Latest" pick), the box needs the value's width plus
  about 56 px for the pill, its dismiss button and the arrow.
- Drawer width: the longest value at 6.5 px per character, plus 14 for the tick box, 8 gap, 24
  padding, and 10 for the scrollbar when the list scrolls. Ignore one outlier value longer than 20
  characters and more than twice the 90th percentile length, or one long name sets every width.
- Drawer height: rows times 24, plus 32 for the search box when shown, plus padding, capped near
  300 so it scrolls.
- The drawer opens left aligned under the box. A box near the right edge has to sit far enough left
  that its x plus the drawer width stays on the page.
- Round sizes up to a multiple of 8.

## Base theme

On the old CY24SU10 base theme a first attempt drew a white box with a "+1" pill. On Desktop 2.159
the full template above draws correctly on that same base theme, across a whole report of slicers.
Convert one slicer, render it under the report's own base theme, then do the rest. If a Desktop or
Service update changes how it draws, these are the visuals to check first.
