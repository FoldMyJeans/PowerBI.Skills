# Slicer templates: classic and button

Slicer shapes beyond the plain slicer in `visual-types-and-patterns.md`. Every shape came from a
file Desktop wrote or a value that rendered, on visualContainer schema 2.11 to 2.13. These are
styled options, not a required look. Which slicer fits which job is in `slicers-and-navigation.md`
in the `powerbi-report-design` skill.

- All four types bind a `Values` projection, so a conversion keeps the old `query`,
  `filterConfig`, `position` and alt text, and swaps `visualType` and `objects`.
- Any checker must treat `slicer`, `listSlicer`, `advancedSlicerVisual` and `textSlicer` as
  slicers. A checker that tested `visualType == "slicer"` silently skipped every converted
  slicer, so its banned field and duplicate field checks passed on visuals it never read.

## Classic slicer, underline dropdown

A rounded box, a coloured open arrow, and a 3 px accent line along the bottom. Per visual, in
`visual.objects.dropdown`, on a slicer whose `data.mode` is `'Dropdown'`.

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
  against the schema. One report ignored them and another restyled every dropdown in one place.
  Both results may predate the August 2026 GA of the Dropdown section, so retest. Set them in the theme, render one page, and
  fall back to the per visual entry above if nothing changed. The section also takes per corner
  radii, `iconSize`, and fx on border, icon and accent colours. The hierarchy chevron colour is
  `items.expandCollapseIconColor`.
- The open list of a classic dropdown is always exactly as wide as the box, with no setting for
  it. For a wide list on a narrow box, use the list slicer in `list-slicer-dropdown.md`.

### Other classic slicer objects that render

- Tick boxes on a Basic (vertical list) slicer, set per visual:

  ```json
  "selectionIcon": [{ "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0072B2'" } } } } }
  }}]
  ```

- A Between slider: `objects.slider` with `show` true, `color`, `secondaryLineColor`,
  `handleFillColor`, `handleBorderColor` and `handleSize`. A `handleSize` of `16D` draws smaller
  than the default handle, so mention it if grabbing matters. With Responsive off, `handleWidth`
  and `handleHeight` (September 2026) draw a rectangular handle instead. `numericInputStyle` has
  font settings and no corner radius, so the two number boxes cannot be rounded.
- Date picker style: `data.mode` `'RelativeDatePicker'` on a date column (GA August 2026). It
  takes a relative rule (`relativeRange`, `relativeDuration`, `relativePeriod`), a calendar, and
  `selection.singleDate`. The anchor and offset keys are not documented, so set those in Desktop
  and read the file back.
- Theme `visualStyles.slicer["*"].slider` with `show` false hides the slider on every Between
  slicer, except those that carry their own `objects.slider` `show` true. A per visual entry
  wins, so delete those to let the theme decide.
- `items` takes `fontColor`, `background`, `outlineColor`, `textSize` and `padding`.
- Tile layout: "Sep 2026" truncated at about 65 px per tile at 8 pt. About 84 px per tile fit.

## List slicer in dropdown mode

The template, the Fit to space row trap, the sizing rule and the conversion steps are in
`list-slicer-dropdown.md`.

## Button slicer, `advancedSlicerVisual`

GA since October 2025. Role `Values`. This one is a month picker: three tiles in a row, an arrow
to older months, single select, saved selection the constant "Latest". The column behind it is in
`time-intelligence.md` in the `powerbi-dax` skill.

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
- `overFlowStyle` 0 is paginated and `overFlowDirection` 1 is horizontal. The arrow takes the
  theme's foreground colour.
- Without `rowCount`, or under the old CY24SU10 base theme without the `padding` object above,
  tiles showed only outlines or thin bars, because the base theme padding pushed the text out.
- `'rectangleRoundedByPixel'` with `rectangleRoundedCurve` takes pixels. `'rectangleRounded'`
  takes a percentage, so a value of 8 looked square on 30 px buttons.
- A 2 by 2 grid is `autoGrid` false, `columnCount` 2, `rowCount` 2, `cellPadding` 4.
- The field name shows as a subtitle by default, hence `subTitle` off.
- Community reports say its padding or alignment can differ in the Service. Check after publish.
- A button slicer does not share a selection with a classic slicer in a sync group. See
  `filters-and-sync.md`.
