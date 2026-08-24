# Power BI report design principles

These are the rules of thumb that keep showing up across Microsoft, SQLBI, Zebra BI and
IBCS, Data Goblins, and Storytelling with Data. They are safe defaults. They are not laws.
Read the situation. A dense operational table for one analyst is not the same as an
executive summary page, and the rules bend accordingly. The report-design skill points here
and adds the how-to detail.

## Purpose and layout

1. 5 second rule. The main point of a page should be readable in about 5 seconds. If
   it takes longer, the page is doing too much.
2. One decision per page. Decide what question the page answers, then cut anything that does
   not serve it.
3. Three tier layout. KPIs and the headline on top, the "why" charts (trend, breakdown) in
   the middle, detail tables at the bottom. Executives read top down and stop early.
4. Follow the reading path. Most eyes go top left first, then across and down (a Z or F
   pattern). Put the most important visual top left.
5. Limit density. Roughly 6 to 8 visuals and 10 to 20 fields per page. This helps
   both readability and refresh and render performance.

## Chart selection (match the chart to the question)

6. Comparison across categories: bar or column. Trend over time: line. Variance against a
   target or prior period: bar with a reference, or a waterfall. Correlation or outliers:
   scatter. Part to whole: stacked bar, or a treemap, and only use pie or donut for a
   handful of slices.
7. Avoid pie, donut, and gauge unless it is genuinely part to whole with fewer than about
   eight categories. They are hard to read and waste space.
8. Always show a comparison. A raw number alone tells no story. Pair it with a target,
   budget, prior period, or benchmark. This is the core idea behind IBCS.
9. Prefer small multiples over many overlapping lines. A grid of small charts beats
   spaghetti.

## Color

10. Three to five purposeful colors per page. Give each a consistent meaning. Gray for
    context, one accent for the thing in focus, and reserve the semantic good and bad slots
    (green and a red orange) for positive and negative. Avoid a true red to green pairing,
    which many colorblind readers cannot tell apart. Never let a brand color override a
    semantic meaning (do not make "bad" blue just because blue is the brand).
11. Default to colorblind safe palettes. Okabe-Ito for categorical series, ColorBrewer
    colorblind safe sets for sequential and diverging. Test a palette in Viz Palette before
    you commit. See house-default-theme.json for the ready set.
12. Never use color as the only signal. Back it with a label, an icon, or position, so the
    message survives for a colorblind reader and in grayscale printing.

## Typography

13. Sans serif and a small font set. Segoe UI is the Power BI default for text and reads
    well. DIN is the default for numbers on charts. Keep to one or two families and a tight
    size scale. Note that custom fonts may not render on non Windows clients, so stick to
    web safe sans serif for anything that must travel.
14. Make the hierarchy obvious. Large bold KPI values, medium headings, smaller secondary
    text. Do not center long text. Left align for reading.
15. Insight driven titles. Title a visual with the takeaway, not the field name. "Revenue is
    12 percent below target" beats "Revenue by Month".

## Structure and interaction

16. Use an 8 pixel grid. Align everything, keep consistent gaps of about 8 to 10 pixels, and
    leave generous white space. Misalignment is the fastest way a report looks amateur.
17. Declutter. Drop heavy borders, background fills, redundant gridlines, and legends you do
    not need. Less non data ink means lower cognitive load (Tufte, Knaflic).
18. Slicers. Keep about five visible. Beyond that, switch to dropdowns. Sync slicers across
    pages where it helps, and always give the user a way to clear all. Match the question to
    the slicer type (list, dropdown, between for numeric ranges, relative date for dates). The
    house rule for date slicers is under house conventions below.
19. Navigation. Use buttons plus bookmarks for an app like flow, and a back button for drill
    through. Name every object clearly in the Selection and Bookmarks panes so future you can
    maintain it.
20. Filter pane. Format it to match the report. Hide or lock filters you do not want changed.
    Decide whether it opens expanded or collapsed. Consider a single Apply button so the
    report does not re-query on every click.

## Accessibility (WCAG, and it is not optional)

21. Contrast. At least 4.5 to 1 for normal text, 3 to 1 for large text and non text elements
    like chart bars. Check a live canvas with the TPGi Colour Contrast Analyser eyedropper.
22. Alt text on every non decorative visual, and set a logical tab order in the Selection
    pane. Do not leave tab order at the default.
23. Design once as a system. Encode colors, fonts, and visual defaults in one theme JSON and
    reuse it across pages and reports. This is Kurt Buhler's atomic design idea, and it is the
    single biggest lever for a consistent, professional look. See house-default-theme.json.

## House conventions

Settled preferences for how a report reads and how in-report text is written. They sit on top of
the rules above, not against them.

- One Date slicer. A single slicer on a Year, Quarter, Month hierarchy, never separate Year and
  Month slicers. Keep a Clear all, and sync it across pages.
- Month and year on date axes. Date axis labels and the date slicer read month and year, for
  example "Jan 2026" (MMM yyyy). Use a clean MMM yyyy format where there is no exact built in.
- In-report writing. Text inside a report (visual titles, labels, tooltips, table and matrix
  headers) never uses an en dash or an em dash, use a hyphen, and never uses a semicolon. Canvas
  text is read at a glance, and punctuation that needs parsing costs more there than it does in
  a document.
- Plain-English explanations, in two tiers. Every non-obvious visual carries a one line subtitle
  saying what it shows, in plain words. Where the arithmetic itself needs explaining, the full
  rules go behind the information icon in the visual header, and the subtitle ends by pointing at
  it, for example "Rules under the header help icon". The subtitle stays short because the long
  version has somewhere to live. See the `powerbi-pbir-builder` skill for both properties.
- KPI card style, when there is a KPI. Compact gray fill (the secondaryBackground slot) with a
  dark border, a touch smaller than the full slot, and always a comparison versus the prior or
  latest month with an arrow, a sign, and a semantic color. Color encodes good versus bad, never
  up versus down. A metric that rose but is bad (open critical vulnerabilities) shows an up arrow
  in the bad color.
- Not every report has a KPI. An operational report where each page answers a different working
  question does not need a card row, and adding one to satisfy a template produces a number
  nobody uses. A 22 page operational report built to this house style carries no KPI row at all
  and is better for it. Add cards when the page has a headline, not by default.
- No two visuals restate the same fact. One decision per page applies within the page too: each visual answers
  a question no other visual on the page answers. Four cards showing one ratio four ways (the
  score, its numerator, its denominator, the complement) are one card plus clutter. Before
  adding a visual, name the question it alone answers.
- The container carries the structure. A banded title, a short subtitle, an 8 pixel border
  radius, a light shadow, and 2 pixel padding group a visual without drawing a single background
  shape. That is fewer objects, a cleaner tab order, and one theme edit to restyle. Prefer it
  over drawn backing panels.
- Conditional formatting is opt-in. Default is a clean, uncolored table or chart. Ask before
  adding any conditional formatting, heatmap, data bars, or status icons, because it is
  situational and coloring everything wastes attention. When it is added, fit the pattern to the
  question and keep it colorblind safe. See the report-design conditional-formatting reference.

## Custom visuals

Prefer native Power BI visuals first. They cover more ground than people assume, a report can
reach deep interactivity, dynamic imagery, and narrative text using only stock visuals plus DAX.
See the `powerbi-dax` skill for the DAX-driven native techniques.

If a third-party visual is genuinely needed, treat it as a governed exception. Pick exactly one,
chosen deliberately, note its source and license in the project docs, and never stack several
different third-party visuals in the same report.

## Asset discipline

Embed small images and icons as report-registered resources rather than linking an external or
CDN URL. This keeps the report working offline and avoids handing a reviewer an external
dependency to trust.

Deduplicate near-identical images before shipping. Two visually identical background images
saved under different names bloat the file for no reason.

Size sanity check. A two-page report's static image assets should not dwarf its data model
size. If they do, something is wrong, most often an unused or oversized image.

## Handling a crowded existing page (the declutter ladder)

When an existing page carries too much, do not reflexively split it into more near-duplicate
sheets. Work down this ladder. This decision is situational and always needs the user's approval
per instance, it is never applied automatically:

1. Cut what does not serve the page's one question.
2. Move supporting detail into tooltips.
3. Collapse many series into small multiples, or emphasize the one series that matters.
4. Offer a field parameter or a slicer toggle so one visual serves several cuts.
5. Use a bookmark toggle to swap between a chart view and a table view in the same space.
6. Push row-level detail onto a drill through page.
7. Only as a last resort, split into a new page, and only if that page answers a
   different question.

A report can be built with zero bookmarks using field parameters plus native page navigation.
Bookmark counts tend to grow past what is maintainable once a report has many toggle states,
which is why step 4 outranks step 5 on this ladder.

## When to bend the rules

- A detail or export page for one power user can be dense and table heavy. The 5 second
  rule does not apply to a data extract.
- An operational monitoring wall can use more red and green than an exec deck, because alert
  state is the whole point.
- A one number scorecard can be a single big card. Not every page needs three tiers.
- IBCS is a strict standard. Adopt its ideas (always compare, consistent notation, unified
  scaling) even if you do not adopt every rule.

## Sources

The anchors for design are Microsoft Learn report design and accessibility, SQLBI and Data
Goblins (Kurt Buhler), Zebra BI and IBCS, Storytelling with Data, and the Financial Times
Visual Vocabulary for chart selection.
