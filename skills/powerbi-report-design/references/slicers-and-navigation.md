# Slicers and navigation

How to let people filter and move through a report without clutter. The rules of thumb are in
`design-principles.md`. The JSON for each slicer type is in `slicer-templates.md` in the
`powerbi-pbir-builder` skill.

## Slicer types

- List. A short set of categories the user scans. Turn on Select all when multi select helps.
- Dropdown. A collapsed list, for a long set or tight canvas, and for the slicers past about five
  visible.
- Between. A low and high slider for a numeric range, with greater than and less than variants.
- Relative date. A rolling window (last 30 days, month to date), so the report follows the calendar.
- Date hierarchy. The default convention for a date filter: one slicer on a Year, Quarter, Month
  hierarchy, not separate Year and Month slicers, displayed as MMM yyyy ("Jan 2026").

The slicer family, as of November 2026:

- Classic slicer. List, Dropdown, Between, Relative date, Date picker and Tile styles. Its open
  dropdown list is always exactly as wide as the box, with no setting to change that. Its Dropdown
  section (border, corner radius, open icon, accent bar, with fx on the border, icon and accent
  colours) has been GA since August 2026. On the Fluent 2 base theme a new slicer starts as Dropdown.
- Button slicer, GA since October 2025. A grid of buttons with fixed or fit to space sizing, hover
  and selected states, images per button, and paging arrows when values overflow. For a small,
  always visible choice, and for a picker that shows the latest few periods with an arrow to older
  ones.
- List slicer, still preview. Its dropdown mode (October 2026, also preview) has a configurable
  open list width and height, removable selection pills, search, and Show selected first. The only
  way to open a wide list from a narrow box, so long names read in full. Render it under the
  report's own base theme before converting a page of slicers. It takes hierarchy fields. Size the
  open list to the longest value or to the typical entry, and take its font sizes from the theme's
  slicer header. Both rules are in `list-slicer-dropdown.md` in the `powerbi-pbir-builder` skill.
- Fixed size layout (April 2026) on the card, button slicer and list slicer sets a pixel height or
  width per item, as an alternative to Fit to space.
- Any slicer takes a pasted list of values from its context menu (February 2026).
- Input slicer, GA since February 2026, numeric columns since May 2026. The user types a value.
- Date picker, GA since August 2026, for a single date or a range from a calendar.

There is no slicer style gallery. Style per visual or through the theme, and render a page to check
the theme took.

Keep about 5 slicers visible. Move the rest to dropdowns or the filter pane, or the page becomes a
control panel.

## Sync, and always a Clear all

- View, Sync slicers, tick the pages a slicer applies to. Sync the fields that define the shared
  context, leave page specific slicers unsynced. In code the sync is a `syncGroup` with a shared
  group name on each slicer. Group by the exact field so slicers on different tables do not cross
  drive. The `powerbi-pbir-builder` skill has the shape.
- One slicer type per sync group. A button slicer and a classic slicer synced on one field do not
  share a selection, and the page shows blanks.
- Always a way to clear: a button with the Clear all slicers action, or a bookmark of the cleared
  state.
- Single select for a one thing at a time view, multi select for comparisons.

## Buttons and bookmarks

- Page navigation: a Page navigator visual for automatic page buttons, or buttons with the Page
  navigation action for a custom menu.
- A bookmark stores filters, selected visuals and the current page. A button pointed at one jumps
  to a saved view, for example a chart view and a table view of the same data.
- Bookmark scope. In the Bookmarks pane a bookmark stores Data, Display and Current page, for All
  visuals or Selected visuals. Untick Data when it should only show or hide visuals without
  freezing filters. Use Selected visuals so one bookmark does not disturb the rest of the page.
- A Bookmark navigator visual acts as tabs and keeps itself in sync as bookmarks are added.

## Field parameters before bookmarks

Use a field parameter or a measure bound visual property when the reader switches views of the
same data. Keep bookmarks for state a field parameter cannot express, and native page navigation
for a plain page move. Many toggle states otherwise end as several dozen inconsistently named
bookmarks nobody can maintain.

- Since October 2026 a chart axis with Auto expand builds a hierarchy from every field picked in a
  field parameter slicer.
- A matrix keeps its expanded level when the parameter changes (the Persist hierarchy level report
  setting, on by default).
- A disconnected table driving a measure bound axis range gives a chart zoom or filter toggle with
  one measure reading the selection, no bookmarks.

## Drill through and the back button

- Drill through sends the user from a summary visual to a detail page filtered to the item they
  right clicked. Set the drill through field on the target page.
- Adding a drill through field drops a back button on the page. Keep it. A page built by hand gets
  a Back button added so there is always a way out.

## Name every object

Name every visual, button, shape and slicer in the Selection pane, and every bookmark. Names like
"Button" and "Bookmark 3" make a report unmaintainable, and names drive screen reader output and
tab order. See `accessibility.md`.

## Filter pane formatting

- Match the report. Pane and card background, border and text follow the theme.
- Lock a filter the user must not change, hide one only the author needs, hide fields you do not
  want exposed.
- Default state. A summary page often opens collapsed, an analysis page expanded.
- Apply all filters gives a single Apply button, so the report re-queries once instead of on every
  click. Helps most on a slow or wide model.

## Pro vs Premium

Slicers, sync, bookmarks, buttons, drill through and the filter pane are all Pro.
