# Slicers and navigation

How to let people filter and move through a report without clutter. The rules of thumb are in
`design-principles.md`.

## Slicer types and when to use each

Match the slicer to the field and the question.

- List. A vertical or horizontal list of values. Best for a short set of categories the user
  scans, for example a handful of regions. Turn on Select all when multi select helps.
- Dropdown. The same as a list but collapsed. Use it when the set is long or when canvas space
  is tight. This is the default once you pass about five visible slicers.
- Between (numeric range). A slider with a low and high end. Use it for a numeric range like
  amount or age. There are also greater than and less than variants.
- Relative date. Filters a date field by a rolling window such as the last 30 days or this
  month to date. Use it for dates so the report follows the calendar without editing.
- Date hierarchy. The house default for a date filter. One Date slicer bound to a Year, Quarter,
  Month hierarchy, so the reader drills from year to quarter to month in a single control, rather
  than separate Year and Month slicers. Format the display and the downstream axes as MMM yyyy,
  for example "Jan 2026".
- Tile or button style. A list styled as buttons. Good for a small, always visible choice like
  a two or three option toggle.

Keep about 5 slicers visible on a page. Beyond that, switch the rest to dropdowns or move
them into the filter pane, or the page turns into a control panel instead of a report.

## Sync, and always a Clear all

- Sync slicers across pages with View, Sync slicers. Tick the pages a slicer should apply to.
  This is how the house Date slicer on page 1 carries its selection to page 2. Sync the fields
  that define the shared context, and leave page specific slicers unsynced. In code this sync is
  stored on each slicer as a `syncGroup` with a shared group name, group by the exact field so two
  slicers built on different tables do not cross drive. See the `powerbi-pbir-builder` skill for the
  exact shape.
- Always give a way to clear. Add a button with the Clear all slicers action, or a bookmark
  that captures the cleared state. A user who cannot reset a filter is stuck.
- Decide single or multi select per slicer. Single select keeps a clean one thing at a time
  view. Multi select suits comparisons.

## Buttons and bookmarks for navigation

Buttons plus bookmarks turn a report into an app like flow.

- Page navigation. Use a Page navigator visual for an automatic set of page buttons, or
  individual buttons with the Page navigation action for a custom menu.
- Bookmarks capture a state. A bookmark stores the current filters, the selected visuals, and
  the current page. Point a button at a bookmark to jump to a saved view, for example toggling
  between a chart view and a table view of the same data.
- Control bookmark scope. In the Bookmarks pane, a bookmark can store Data, Display, and
  Current page, and it can apply to All visuals or only Selected visuals. Untick Data when a
  bookmark should only show or hide visuals and must not freeze the filters. Use Selected
  visuals so one bookmark does not disturb the rest of the page.
- Use a Bookmark navigator visual when you have a set of bookmarks that act like tabs. It keeps
  itself in sync as you add bookmarks.

## Field parameters vs bookmarks

Prefer a field parameter or a measure-bound visual property when the reader switches between
views of the same data. Reserve bookmarks for state a field parameter cannot express, and use
native page navigation for a simple page-to-page move, no bookmark needed.

A report with many toggle states can end up with several dozen bookmarks under inconsistent
naming, unmaintainable, which is why field parameters rank first. A disconnected table driving a
measure-bound axis range is another bookmark-free option, for a chart zoom or filter toggle, one
measure reading the selection instead of several bookmarked states.

## Drill through and the back button

- Drill through sends the user from a summary visual to a detail page filtered to the item they
  right clicked. Set the drill through field on the target page.
- When you add a drill through field, Power BI drops a back button on the page automatically.
  Keep it. It returns the user to where they came from. If you build the page by hand, add a
  Back button so there is always a way out.

## Name every object

In the Selection pane, give every visual, button, shape, and slicer a clear name. Do the same
in the Bookmarks pane. Default names like "Button" and "Bookmark 3" make a report impossible to
maintain, and they also drive screen reader output and tab order. Naming is not cosmetic. See
`accessibility.md`.

## Filter pane formatting

The filter pane is part of the report, so format it, do not leave it raw.

- Match the report. Set the pane and card background, border, and text to match the theme so it
  does not look bolted on.
- Hide or lock filters. Lock a filter the user must not change, and hide a filter that only the
  author needs. Hide fields you do not want exposed at all.
- Decide the default state. Choose whether the pane opens expanded or collapsed for a first
  time viewer. A summary page often opens collapsed, an analysis page expanded.
- Consider a single Apply button. Turn on Apply all filters so the report re-queries once when
  the user is done, instead of on every click. This helps a lot on a slow or wide model.

## Pro vs Premium

Slicers, sync, bookmarks, buttons, drill through, and the filter pane are all Pro. Nothing here
needs Fabric or Premium.
