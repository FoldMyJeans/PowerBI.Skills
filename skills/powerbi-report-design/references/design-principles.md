# Power BI report design principles

Rules of thumb drawn from Microsoft, SQLBI, Zebra BI and IBCS, Data Goblins, and Storytelling with
Data. They are safe defaults, not laws. A dense operational table for one analyst is not an
executive summary, and the rules bend accordingly (see the last section). The other references in
this skill hold the how-to.

The judgement rules (question first, no repetition, a comparison beside every number,
accessibility) apply to every style of report. The default conventions further down are a look,
used when a report has no look of its own.

## Purpose and layout

- 5 second rule. The main point of a page reads in about 5 seconds, or the page does too much.
- One decision per page. Name the question the page answers and cut what does not serve it.
- Three tier layout. KPIs and the headline on top, the "why" charts in the middle, detail tables at
  the bottom. Executives read top down and stop early.
- Reading path. Eyes go top left first, then across and down (Z or F). The most important visual
  goes top left.
- Density. Roughly 6 to 8 visuals and 10 to 20 fields per page, for reading and render speed.

## Chart selection

- Comparison: bar or column. Trend: line. Variance against target or prior period: bar with a
  reference, or a waterfall. Correlation or outliers: scatter. Part to whole: stacked bar or
  treemap.
- Pie, donut and gauge only for a real part to whole with fewer than about eight categories.
- Always show a comparison (target, budget, prior period, benchmark). A raw number alone tells no
  story. This is the core of IBCS.
- Small multiples over many overlapping lines.
- An average over a population that changes misleads. A wave of new items drags a mean age down
  and reads as improvement while the old backlog has not moved. Show the composition (age bands
  stacked, oldest at the bottom) with the mean as a line or a label on top.

## Color

- Three to five purposeful colors per page, each with a fixed meaning. Gray for context, one
  accent for the focus, the semantic good and bad slots (green and a red orange) for positive and
  negative. No true red against green, which many colorblind readers cannot tell apart. A brand
  color never overrides a semantic meaning (bad is not blue because the brand is blue).
- Colorblind safe palettes by default. Okabe-Ito for categories, ColorBrewer colorblind safe sets
  for sequential and diverging. Test in Viz Palette before committing.
- Never color as the only signal. Back it with a label, an icon, or position.

## Typography

- One or two sans serif families and a tight size scale. Fonts and sizes are owned by
  `color-and-theme.md`.
- Obvious hierarchy. Large bold KPI values, medium headings, smaller secondary text. Left align
  long text.
- Titles. A neutral title that names the chart is the default (see the conventions below). A
  storytelling page can title a visual with the takeaway ("Revenue is 12 percent below target"
  rather than "Revenue by Month"), bound to a measure so it stays true.

## Structure and interaction

- Design once as a system. Colors, fonts and visual defaults go in one theme JSON reused across
  pages and reports (Kurt Buhler's atomic design idea). It is the biggest lever for a consistent
  look, whatever the look is.
- Align to a grid with consistent gaps and generous white space. Misalignment is the fastest way a
  report looks amateur. The default is an 8 pixel grid with 8 to 10 pixel gaps.
- Declutter. Drop heavy borders, fills, redundant gridlines and unneeded legends (Tufte, Knaflic).
- Slicers. About five visible, then dropdowns. Sync across pages where it helps, always a way to
  clear all, and the slicer type matched to the field.
- Navigation. Buttons plus bookmarks or field parameters for an app like flow, a back button for
  drill through, every object named in the Selection and Bookmarks panes.
- Filter pane. Format it to match, hide or lock filters, pick expanded or collapsed, consider a
  single Apply button. The how-to for these three is in `slicers-and-navigation.md`.

## Accessibility (not optional)

- Contrast at least 4.5 to 1 for normal text, 3 to 1 for large text and non text elements.
- Alt text on every non decorative visual, and a logical tab order set in the Selection pane.
- The checklist and the tools are in `accessibility.md`.

## Default conventions

The look this repo uses when a report has none of its own. Follow an existing report's look
instead, and never restyle a report toward these as a side effect of another change. The
judgement items are marked, and those apply to every report.

- One Date slicer. A single slicer on a Year, Quarter, Month hierarchy, not separate Year and Month
  slicers. Keep a Clear all and sync it across pages.
- Month and year on date axes. Date axes and the date slicer read "Jan 2026" (MMM yyyy). Use a
  clean MMM yyyy format where there is no exact built in.
- In-report writing. Titles, labels, tooltips and headers never use an en dash, an em dash or a
  semicolon. Use a hyphen. Canvas text is read at a glance, and punctuation that needs parsing
  costs more there.
- Plain titles and subtitles. The title names the chart in neutral words ("Fixed and new by team",
  not "Team A lags on fixes"). The subtitle says what the chart is, in one line. It never explains
  how to read it ("hatching is the gap to 100%") or gives instructions ("hover for names"). Rules
  for the arithmetic go behind the information icon in the visual header. An executive page drops
  explanation lines altogether. The `powerbi-pbir-builder` skill has both properties.
- Say the period plainly (judgement). "YTD", not "this year". A month axis never skips a month, and
  a year shows every month that has passed. The month table that does this is in `powerbi-dax`.
- Count people, not raw rows, when groups differ in size (judgement). A raw count of overdue items
  by department makes the biggest department look worst. Show people and the group size.
- KPI card style, when there is a KPI. Compact gray fill (the `secondaryBackground` slot), a dark
  border, a touch smaller than the full slot, and always a comparison versus the prior or latest
  month with an arrow, a sign and a semantic color. Color encodes good versus bad, never up versus
  down. A metric that rose but is bad (open critical vulnerabilities) shows an up arrow in the bad
  color.
- Not every report has a KPI (judgement). An operational report where each page answers a
  different working question needs no card row, and one added for a template is a number nobody
  uses. A 22 page operational report built without one is better for it. Add cards when the page
  has a headline.
- No two visuals restate the same fact (judgement). Each visual answers a question no other visual
  on the page answers. Four cards showing one ratio four ways (score, numerator, denominator,
  complement) are one card plus clutter. Name the question a visual alone answers before adding
  it.
- The container carries the structure. A banded title, a short subtitle, an 8 pixel border radius,
  a light shadow and 2 pixel padding group a visual with no drawn background shape. Fewer objects,
  a cleaner tab order, one theme edit to restyle.
- Conditional formatting is opt-in (judgement). Default is a clean, uncolored visual. Ask before
  adding conditional formatting, heatmaps, data bars or status icons. See
  `conditional-formatting.md`.

## Custom visuals

Native visuals first. Stock visuals plus DAX reach deep interactivity, dynamic imagery and
narrative text (the `powerbi-dax` skill has the techniques). Third-party visuals are fine when they
work in the Power BI Service and look good: one or two per report where they fit, more when the
report owner asks. Test publish to My workspace before relying on one, and note its source and
license in the project docs. All charts built on one visual, such as Deneb, count as one.

## Asset discipline

- Embed small images and icons as report registered resources, not an external or CDN URL. The
  report then works offline and a reviewer has no external dependency to trust.
- Deduplicate near-identical images. Two identical backgrounds under different names bloat the
  file.
- A two-page report's static images should not dwarf its data model. If they do, look for an
  unused or oversized image.

## A crowded existing page (the declutter ladder)

Do not reflexively split a crowded page into near-duplicate sheets. Work down this ladder, and get
the user's approval for each step, it is never applied automatically:

1. Cut what does not serve the page's one question.
2. Move supporting detail into tooltips.
3. Collapse many series into small multiples, or emphasize the one series that matters.
4. Offer a field parameter or a slicer toggle so one visual serves several cuts.
5. Use a bookmark toggle to swap a chart view and a table view in the same space.
6. Push row-level detail onto a drill through page.
7. Last resort, a new page, and only if it answers a different question.

Field parameters outrank bookmarks because bookmark counts grow past what is maintainable once a
report has many toggle states. A report can be built with zero bookmarks using field parameters
plus native page navigation.

## When to bend the rules

- A detail or export page for one power user can be dense and table heavy. The 5 second rule does
  not apply to a data extract.
- An operational monitoring wall can use more red and green than an exec deck, because alert state
  is the point.
- A one number scorecard can be a single big card. Not every page needs three tiers.
- IBCS is strict. Adopt its ideas (always compare, consistent notation, unified scaling) without
  every rule.

## Sources

Microsoft Learn report design and accessibility, SQLBI and Data Goblins (Kurt Buhler), Zebra BI and
IBCS, Storytelling with Data, and the Financial Times Visual Vocabulary for chart selection.
