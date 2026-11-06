# Slicer templates: classic, list, and button

The `visual.json` shapes for the slicer family beyond the plain slicer in
`visual-types-and-patterns.md`. Which slicer to use for which job is a design call, covered in
`slicers-and-navigation.md` in the `powerbi-report-design` skill. Every shape below came from a
file Desktop wrote or a value that rendered in Desktop, on visualContainer schema 2.11 to 2.13.

All four types bind the field the same way, a `Values` projection, so a conversion keeps the
old visual's `query`, `filterConfig`, `position` and alt text, and swaps `visualType` and
`objects`.

## Any checker must know all four types

A layout checker and a test runner that tested `visualType == "slicer"` silently skipped every
converted slicer, so the banned field and duplicate field checks passed on visuals they never
read. Treat `slicer`, `listSlicer`, `advancedSlicerVisual` and `textSlicer` as slicers
everywhere a script asks the question.

## Classic slicer, underline dropdown

A rounded box, a coloured open arrow, and a 3 px accent line along the bottom. It goes on each
visual, in `visual.objects.dropdown`, for slicers whose `data.mode` is `'Dropdown'`.

```json
"dropdown": [{ "properties": {
  "borderColor":       { "solid": { "color": { "expr": { "Literal": { "Value": "'#D1D1D1'" } } } } },
  "borderRadius":      { "expr": { "Literal": { "Value": "6L" } } },
  "iconColor":         { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } },
  "accentBarShow":     { "expr": { "Literal": { "Value": "true" } } },
  "accentBarColor":    { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } },
  "accentBarWidth":    { "expr": { "Literal": { "Value": "3D" } } },
  "accentBarPosition": { "expr": { "Literal": { "Value": "'Bottom'" } } }
}}]
```

- `accentBarPosition` takes `Left`, `Right`, `Top` or `Bottom`. With `Left` the rounded corner
  clips the bar, so it looks cut off.
- The same properties under `visualStyles.slicer["*"].dropdown` in a custom theme validate
  against the schema. In one report Desktop ignored them, and an existing theme radius of 4 had
  never shown. In another report the theme restyled every dropdown in one place. So set them in
  the theme, render one page, and fall back to the per visual entry above if nothing changed.
- The open list of a classic dropdown is always exactly as wide as the box. There is no setting
  for it. For a wide list on a narrow box, use the list slicer below.

### Other classic slicer objects that render

- Tick boxes on a Basic (vertical list) slicer, set per visual:

  ```json
  "selectionIcon": [{ "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } }
  }}]
  ```

- A Between slider: `objects.slider` with `show` true, `color`, `secondaryLineColor`,
  `handleFillColor`, `handleBorderColor` and `handleSize`. A `handleSize` of `16D` draws smaller
  than the default handle, so mention it if grabbing matters. `numericInputStyle` has font
  settings and no corner radius, so the two number boxes cannot be rounded.
- Theme `visualStyles.slicer["*"].slider` with `show` false hides the slider on every Between
  slicer, except those that carry their own `objects.slider` `show` true. A per visual entry
  wins, so delete those to let the theme decide.
- `items` takes `fontColor`, `background`, `outlineColor`, `textSize` and `padding`.
- Tile layout: "Sep 2026" truncated at about 65 px per tile at 8 pt. About 84 px per tile fit.

## List slicer in dropdown mode (preview)

`listSlicer` with `data.dropdownMode` true is the only slicer with a setting for the open list
size, `dropdownMenu.width` and `dropdownMenu.maxHeight`. A 128 px box opened a 320 x 420 list,
so long names read in full. This is an October 2026 preview.

Template that renders beside a classic dropdown and looks the same:

```json
{
  "visualType": "listSlicer",
  "objects": {
    "data": [{ "properties": {
      "dropdownMode": { "expr": { "Literal": { "Value": "true" } } } } }],
    "general": [{ "properties": {
      "selfFilterEnabled": { "expr": { "Literal": { "Value": "true" } } } } }],
    "dropdownMenu": [{ "properties": {
      "width":        { "expr": { "Literal": { "Value": "320D" } } },
      "maxHeight":    { "expr": { "Literal": { "Value": "420D" } } },
      "cornerRadius": { "expr": { "Literal": { "Value": "6D" } } } } }],
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
      "fontSize":          { "expr": { "Literal": { "Value": "10D" } } },
      "accentBarShow":     { "expr": { "Literal": { "Value": "true" } } },
      "accentBarWidth":    { "expr": { "Literal": { "Value": "3D" } } },
      "accentBarPosition": { "expr": { "Literal": { "Value": "'Bottom'" } } } } }]
  },
  "visualContainerObjects": {
    "title": [{ "properties": {
      "show":     { "expr": { "Literal": { "Value": "true" } } },
      "text":     { "expr": { "Literal": { "Value": "'Owner'" } } },
      "fontSize": { "expr": { "Literal": { "Value": "9D" } } } } }],
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

What each piece fixed, in the order it was found:

1. The first render was a bordered card. New visuals pick up the theme's container border and
   background. Container `border` and `background` off.
2. The field name printed twice, pushing the box below a 56 px frame. `label.show` false did
   nothing. The second line is the container subtitle, so `subTitle.show` false.
3. No visible "All". The closed box is styled through `selectionBox`, not `value` or `outline`.
   Top level `outline` and `accentBar` style the items in the open list instead.
4. The box sat 5 px higher than a classic dropdown beside it, at the same 27 px height.
   `spacing.spaceBelowTitleArea` had no effect. `spaceBelowTitle` 5 left it about 1 px high, 7
   matched. Measure this from a render, eyeballing missed it.
5. In a stacked column the boxes ran edge to edge, while classic boxes are inset about 5 px each
   side. Container padding left 5 and right 5.
6. `dropdownButton.iconSize` 14 made no visible difference. The arrow stays a little smaller
   than the classic one.

Preview caveats:

- In another report on an old base theme (CY24SU10) the same mode rendered as a white box with a
  "+1" pill, and was not used. Test it under the report's own base theme before converting.
- If a Desktop or Service update changes how it draws, these are the visuals to check first.

## Button slicer, `advancedSlicerVisual`

GA since October 2025. Data role `Values`. This one is a month picker, three tiles in a row with
an arrow to older months, single select, with a saved selection of the constant "Latest". The
column behind it is in `time-intelligence.md` in the `powerbi-dax` skill.

```json
{
  "visualType": "advancedSlicerVisual",
  "objects": {
    "general": [{ "properties": { "filter": { "filter": {
      "Version": 2,
      "From": [{ "Name": "d", "Entity": "dim_date", "Type": 0 }],
      "Where": [{ "Condition": { "In": {
        "Expressions": [{ "Column": { "Expression": { "SourceRef": { "Source": "d" } }, "Property": "Month Pick" } }],
        "Values": [[{ "Literal": { "Value": "'Latest'" } }]] } } }] } } } }],
    "selection": [{ "properties": {
      "singleSelect":       { "expr": { "Literal": { "Value": "true" } } },
      "strictSingleSelect": { "expr": { "Literal": { "Value": "true" } } } } }],
    "layout": [{ "properties": {
      "autoGrid":      { "expr": { "Literal": { "Value": "false" } } },
      "rowCount":      { "expr": { "Literal": { "Value": "1D" } } },
      "columnCount":   { "expr": { "Literal": { "Value": "3D" } } },
      "columnPadding": { "expr": { "Literal": { "Value": "6D" } } } } }],
    "overFlow": [{ "properties": {
      "overFlowStyle":     { "expr": { "Literal": { "Value": "0D" } } },
      "overFlowDirection": { "expr": { "Literal": { "Value": "1D" } } } } }],
    "padding": [{ "properties": {
      "paddingSelection": { "expr": { "Literal": { "Value": "'Custom'" } } },
      "topMargin":    { "expr": { "Literal": { "Value": "0D" } } },
      "bottomMargin": { "expr": { "Literal": { "Value": "0D" } } },
      "leftMargin":   { "expr": { "Literal": { "Value": "0D" } } },
      "rightMargin":  { "expr": { "Literal": { "Value": "0D" } } } },
      "selector": { "id": "default" } }],
    "shapeCustomRectangle": [{ "properties": {
      "tileShape":             { "expr": { "Literal": { "Value": "'rectangleRoundedByPixel'" } } },
      "rectangleRoundedCurve": { "expr": { "Literal": { "Value": "6D" } } } } }],
    "accentBar": [{ "properties": {
      "show": { "expr": { "Literal": { "Value": "false" } } } },
      "selector": { "id": "default" } }],
    "fillCustom": [
      { "properties": {
          "show":      { "expr": { "Literal": { "Value": "true" } } },
          "fillColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#E8E8E8'" } } } } } },
        "selector": { "id": "default" } },
      { "properties": {
          "fillColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#D1D1D1'" } } } } } },
        "selector": { "id": "interaction:hover" } },
      { "properties": {
          "fillColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } } },
        "selector": { "id": "selection:selected" } }
    ],
    "value": [
      { "properties": {
          "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#333333'" } } } } },
          "fontSize":  { "expr": { "Literal": { "Value": "9D" } } } },
        "selector": { "id": "default" } },
      { "properties": {
          "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FFFFFF'" } } } } },
          "bold":      { "expr": { "Literal": { "Value": "true" } } } },
        "selector": { "id": "selection:selected" } }
    ]
  },
  "visualContainerObjects": {
    "subTitle": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }]
  }
}
```

- State selectors are `default`, `interaction:hover`, `interaction:press`, `selection:selected`
  and `selection:unselected`, combinable with `-`. The theme schema lists them under
  `actionStates-advancedSlicerVisual`. `selected` and `hover` on their own do nothing.
- The per state fill above, `fillCustom`, drew the selected colour. In another report the fill
  was set through `background` instead, and the selected button stayed black with white bold
  text. Drop selector entries Desktop ignores rather than leaving them in the file.
- `overFlowStyle` 0 is paginated and `overFlowDirection` 1 is horizontal. Three tiles plus an
  arrow replace a row of buttons plus a dropdown. The arrow takes the theme's foreground colour.
- Without `rowCount`, or under the old CY24SU10 base theme without the `padding` object above,
  tiles showed only outlines or thin bars, because the base theme padding pushed the text out.
- `'rectangleRoundedByPixel'` with `rectangleRoundedCurve` takes pixels. `'rectangleRounded'`
  takes a percentage, so a value of 8 looked square on 30 px buttons.
- A 2 by 2 grid is `autoGrid` false, `columnCount` 2, `rowCount` 2, `cellPadding` 4.
- The field name shows as a subtitle by default, hence `subTitle` off.
- Community reports say its padding or alignment can differ in the Service. Check after publish.
- A button slicer does not share a selection with a classic slicer in a sync group. See
  `filters-and-sync.md`.
