# Visual decisions log

Visual design has no right answer, so this file records what the report owner liked and rejected when
shown a real example, and why. Check it before proposing a visual. It is taste and judgement, not
fact, and a later decision can overturn an earlier one. Newest entries go at the top of each list.

To add an entry: show one example, get a reaction, then write down the decision and the reason in the
owner's terms. Ideas nobody has reacted to do not go here.

## Liked

- **Target as tick marks on an unordered axis (2026-11).** A red tick per bar instead of a target line
  when the categories have no order (members, companies). A line joining them has a meaningless slope.
  A trend over months keeps its dashed target line. Recipe in `powerbi-chart-recipes`.
- **A waterfall from the previous scan to the current one (2026-11).** Previous total, minus fixed,
  plus new, then the current total. Beside it a butterfly of new against fixed by team, new in light
  yellow and fixed in green.
- **One page executive summary with no tables (2026-11).** Gauges and KPI blocks drawn as SVG, full
  KPI names as labels, a change pill in green when good, soft red when bad and grey "same" when flat.
  Direction is set per KPI, so a falling vulnerability count is green.
- **Latest complete month by default (2026-11).** A November meeting reads October, with the two months
  before one click away on a paginated button slicer. Snapshot numbers read the latest snapshot in the
  month, never an average of snapshots.
- **Two questions on completion (2026-11).** "How far along are we?" and "Is anyone behind?" as two
  cards, with one on time rule across every page. See `powerbi-dax`.
- **A people waffle (2026-11).** One square per person grouped by department, red when overdue, and a
  hover that lists the person's open items grouped by campaign. Fairer than a raw count by group.
- **Hatched gap to 100% on share columns (2026-11).** The gap reads as missing without a legend.
- **Underline dropdowns (2026-11).** Rounded box, blue open arrow, a 3 px accent line along the bottom,
  on every classic dropdown slicer. A wider open list only on narrow boxes over long names.
- **A black selected button (2026-11).** Accepted when the button slicer's accent cannot be set from
  the files.
- **Keep as is (2026-11).** When the current chart already answers the question, leaving it is a valid
  outcome of a review.
- **One or two third-party visuals per report (2026-11).** Replaces the old limit of exactly one. If a
  chart uploads to the Service and looks good, the visual is fine. More than two only when the owner says
  so.
- **A wider toolbox of charts, none assigned yet (2026-11).** Shown a deck of beeswarm, calendar heatmap,
  waffle, funnel Sankey, bump, butterfly, variance trio, KPI table with bullets and sparklines, animated
  KPI card, floor plan, filter drawer, ridgeline, 24 hour clock and wall screen dark mode. The owner said
  the charts look really interesting and wants to be able to build all of them, depending on the case. So
  they all have recipes in `powerbi-chart-recipes`. This is not approval to use one in a report. Whether
  any goes on a given chart is a later decision, made case by case with the owner.
- **Sankey for where effort goes (2026-11).** Team to service type to activity, on an exploration
  page, replacing a decomposition tree that opened as one bar. It shows how fields connect, which a
  set of totals cannot. Conditions: least possible overlap, no zeros, and no slicer for what the chart
  can filter itself. See `powerbi-custom-visuals`.
- **Filter on the chart (2026-11).** Pick one, some or all teams by clicking the chart. Only the
  Sprint slicer stays as a slicer on that page.
- **Very light blue table header rows (2026-11).** `#E8F3FB` behind the column headers on small
  ranking tables, with the header text left grey.
- **Click to open effect (2026-11).** A block widening and showing its parts was the original spark,
  seen in a LinkedIn post of a custom visual. Liked as motion that explains something.

## Rejected

- **Explanations in subtitles (2026-11).** Legend style lines ("hatching is the gap to 100%") and
  instructions ("hover for names"). The rule is in `design-principles.md`.
- **Per person "days to onboarding" bars (2026-11).** Too much detail for the question.
- **A separate page for one minor measure (2026-11).** Time spent on training is not a critical KPI,
  so it got one chart, not a page.
- **A brand web font (2026-11).** It only shows where installed. Segoe UI everywhere.
- **Slicer changes that make slicers bigger (2026-11).** Style changes must not cost canvas or clicks.
- **Dense ribbon charts where every item is its own line (2026-11).** A Sankey with dozens of labelled
  rows and ribbons crossing everywhere. Avoid that look if the data allows, and accept some overlap
  only if it does not.
- **Share against a raw total (2026-11).** "23% of 27,642 hours". Nobody cares about the total there.
  Say what the share is of in words.
- **Company as a Sankey column (2026-11).** Dozens of companies make the chart unreadable.

## Questioned, not settled

- **A "what changed since last sprint" view (2026-11).** Suggested as more useful for a director. The
  owner doubts they want it, so it needs asking before anyone builds it.
- **Animated custom visuals in general.** The Sankey earned it. Animation for its own sake was not
  discussed further. Check whether a page gets used before spending effort on it.
