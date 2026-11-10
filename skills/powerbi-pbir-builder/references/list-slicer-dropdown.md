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

Drop `search`, and set `selfFilterEnabled` false, on a list of fewer than about ten values. On a
hierarchy slicer count the child rows too (see Hierarchy fields below).

The 8 pt sizes and the 24 px rows are one report's values. Set them from the report's own theme,
as in Font sizes from the theme below.

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

## Font sizes from the theme

- Title and closed box: read `visualStyles.slicer.*.header.textSize` in the report's theme and set
  the title `fontSize` and `selectionBox.fontSize` to it. On a theme whose slicer header was 9 pt,
  both went to 9 so the list slicers matched the classic titles beside them.
- Open list: `value.fontSize` and `search.fontSize` can be one size smaller than the title. 8 pt
  entries under a 9 pt title kept the drawer compact and read fine.
- Rows: 22 px fixed rows held at 8 pt with no overlap, one step tighter than the template's 24.
- The per character width in the sizing rule moves with the size: about 6.5 px at 8 pt, about 7 px
  at 9 pt.

## Hierarchy fields

A slicer on a hierarchy (a parent level and a child level) works in dropdown mode. The open list
draws the expand chevrons and the child rows. The theme schema styles the chevron through the
`expansionIcon` card.

- Keep the classic slicer's `expansionStates` as it is. The child projection's `active: false`,
  copied across from the classic slicer, is fine.
- Count the child rows, not only the parents, when deciding on search and on the drawer height.
  Counted by its parents alone, an 85 row slicer came out with no search box and a 216 px drawer.
- For the width, add about 16 px for the chevron and indent the child level by about 3 characters.

## Sizing from the data

A rule that held across a report of slicers at 8 pt Segoe UI. The pixel constants are estimates
with slack, not measurements.

- Box: as wide as its label, about 6.5 px per character plus 24, never under 104. When a default
  selection always shows as a pill (a saved "Latest" pick), the box needs the value's width plus
  about 56 px for the pill, its dismiss button and the arrow.
- Drawer width: a text length, at 6.5 px per character, plus 14 for the tick box, 8 gap, 24
  padding, and 10 for the scrollbar when the list scrolls. Pick the length with one of two rules.
  - Longest value. Every entry reads in full. Ignore one outlier value longer than 20 characters
    and more than twice the 90th percentile length, or one long name sets every width.
  - Typical entry. Narrower drawers, and a few long names cut off. Start at the average entry
    length. If that cuts off more than a third of the entries, raise it to the length that two
    thirds of the entries fit within. On a field of long names (company, project or epic names),
    a further 1.5 times gives the list room to breathe. That put such drawers at 328 to 352 px.
  - Which rule fits is the report owner's call, a judgement on how much cut off text the readers
    will accept.
- Drawer height: rows (plus one for Select all when it shows) times the row height, plus 32 for
  the search box when shown, plus padding, capped near 300 so it scrolls.
- The drawer opens left aligned under the box. A box near the right edge has to sit far enough left
  that its x plus the drawer width stays on the page.
- Round sizes up to a multiple of 8.

## Measure the list the slicer shows

Size from the values the drawer will draw, not the column's distinct values. A slicer's own
`filterConfig` often hides blanks, a team or a test value, and counting those makes the list
longer and wider than it draws. Translate each slicer's filters into DAX and run the query against
the model, for example over ADOMD to Desktop's local engine (`offscreen-render.md` in the
`powerbi-project-and-tools` skill).

```dax
EVALUATE
CALCULATETABLE (
    SUMMARIZE ( 'Dim Owner', 'Dim Owner'[Team], 'Dim Owner'[Owner] ),
    KEEPFILTERS ( FILTER ( ALL ( 'Dim Owner'[Owner] ),
        NOT ISBLANK ( 'Dim Owner'[Owner] ) && 'Dim Owner'[Owner] <> "" ) ),
    KEEPFILTERS ( FILTER ( ALL ( 'Dim Owner'[Team] ),
        NOT ( 'Dim Owner'[Team] IN { "Internal" } ) ) )
)
```

- One `KEEPFILTERS ( FILTER ( ALL ( column ), ... ) )` per filtered column.
- `Not` becomes `NOT`, `And` becomes `&&`, `Or` becomes `||`, `In` becomes `IN { ... }`,
  `Comparison` becomes `=`, `>`, `>=`, `<`, `<=` for `ComparisonKind` 0 to 4, and `Contains`
  becomes `CONTAINSSTRING`. A `null` literal, in a `Comparison` or inside an `In` list, is
  `ISBLANK`. The filter shapes are in `filters-and-sync.md`.
- `SUMMARIZE` lists the slicer's fields. A hierarchy slicer lists the parent and the child, so the
  result gives the child row count as well.
- A page or report filter on the same table narrows the list too, so add it.
- Read the row count and each value's length from the result, then apply the sizing rule above.

## Base theme

On the old CY24SU10 base theme a first attempt drew a white box with a "+1" pill. On Desktop 2.159
the full template above draws correctly on that same base theme, across a whole report of slicers.
Convert one slicer, render it under the report's own base theme, then do the rest. If a Desktop or
Service update changes how it draws, these are the visuals to check first.
