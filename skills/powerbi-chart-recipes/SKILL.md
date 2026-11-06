---
name: powerbi-chart-recipes
description: >-
  Build unusual Power BI charts from ready recipes on Pro: beeswarm, calendar heatmap, waffle,
  funnel Sankey, bump, butterfly or tornado, variance chart, KPI table with bullets and sparklines,
  animated KPI card, floor plan, filter drawer, ridgeline, 24 hour clock, wall screen dark mode, SVG
  gauges, a KPI block with change pill, a waterfall bridge, and target tick marks. Ships Deneb specs,
  DAX SVG measures, a helper that writes a Deneb visual into a PBIP, and a fake data test report. Use
  whenever the user wants one of these charts, asks for Deneb or Vega, wants a chart Power BI does not
  have, a table with inline charts, a dark mode switch, or asks what a report could
  show. Trigger on "Deneb", "Vega-Lite", "beeswarm", "calendar heatmap", "waffle", "funnel",
  "bump chart", "butterfly chart", "variance chart", "bullet chart", "sparkline", "KPI card",
  "gauge", "waterfall", "target marker", "floor plan", "filter drawer", "ridgeline", "radial
  heatmap", "dark mode". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI chart recipes

A toolbox of charts that can be built on demand. Having a recipe here does not mean a report should
use it. Check `visual-decisions.md` in `powerbi-report-design`, then agree the chart with the report
owner for that report.

## Pick a recipe

| Chart | Answers | Route | Files |
| --- | --- | --- | --- |
| Beeswarm | What does the backlog look like item by item? | Deneb | `assets/deneb/beeswarm.vega.json` |
| Calendar heatmap | Which days spike, is there a weekly rhythm? | Deneb | `assets/deneb/calendar-heatmap.vl.json` |
| Waffle | How close are we to full coverage? | Deneb | `assets/deneb/waffle.vl.json` |
| Funnel Sankey | Where do items drop out? | Deneb | `assets/deneb/funnel-sankey.vega.json` |
| Bump | Who moved up or down the ranking? | Deneb | `assets/deneb/bump.vl.json` |
| Butterfly | Are we closing as fast as we open? | Native, or Deneb for centre labels | `assets/deneb/butterfly.vl.json` |
| Variance trio | Where are we off plan, in units and percent? | Deneb | `assets/deneb/variance-trio.vl.json` |
| KPI table | Which rows miss target, and is the trend recent? | DAX SVG | `assets/dax/bullet.dax`, `assets/dax/split-sparkline.dax` |
| Animated KPI card | One KPI with its recent shape | DAX SVG | `assets/dax/animated-kpi-card.dax` |
| Floor plan | Where in the building is it happening? | Deneb, or Synoptic Panel Lite | `assets/deneb/floor-plan.vega.json` |
| Filter drawer | How do we keep many slicers off the page? | Native plus DAX SVG | `assets/dax/filter-drawer.dax` |
| Ridgeline | When does each source peak? Shape, not size. | Deneb | `assets/deneb/ridgeline.vl.json` |
| 24 hour clock | Which hours and days run hot? | Deneb | `assets/deneb/alert-clock.vega.json` |
| Wall screen dark mode | One switch for wall screen and desk | Native plus DAX | `assets/dax/theme-colours.dax` |
| Gauges | How does each area score against its target? | DAX SVG | `assets/dax/gauge.dax` |
| KPI block | What is the number, and did it get better? | DAX SVG | `assets/dax/kpi-block.dax` |
| Waterfall bridge | How did we get from the last total to this one? | Native | `recipes-native-and-svg.md` |
| Target ticks | Which categories reach their own target? | Native combo | `recipes-native-and-svg.md` |

`assets/gallery` holds a screenshot from Desktop of each one on fake data. Show the owner that before
building. `assets/fixtures` holds the fake rows behind each spec, which is also the shape of data the
spec expects.

## Decide the route first

Native and DAX SVG need nothing installed. Deneb is a free certified third-party visual. Plan on one or
two third-party visuals per report, more if the owner asks. See `powerbi-report-design`. Every Deneb
chart in one report counts as the same visual. Test publish to My workspace the first time a report
takes Deneb, because that step has not been run here.

## Workflow

1. Confirm the chart and the question with the owner. Read the chart's section in
   `references/recipes-deneb.md` or `references/recipes-native-and-svg.md`.
2. Shape the data. Each recipe names the fields it reads. Reorder fields and ranks in the model where
   the recipe says so, because a spec cannot fix a wrong grain.
3. Try it first on fake data if the chart is new to this report. See `references/test-on-fake-data.md`.
4. Close Desktop and back up the report.
5. Build. For Deneb run `scripts/new_deneb_visual.py`. See `references/deneb-in-pbip.md`. For the
   others paste the DAX and write the visual with `powerbi-pbir-builder`.
6. Reopen in Desktop. Check the total against the model with DAX, because a chart that draws can still
   show a wrong number. `powerbi-project-and-tools` has the verification loop.
7. Add alt text and a plain tooltip, per `powerbi-report-design`. Log the owner's reaction in
   `visual-decisions.md`.

## Rules of thumb

- Colours in the specs and measures are the house palette, written as literals so they survive being
  copied. A different theme means changing them in the spec.
- Numbers on these charts are often read one by one, so keep labels on the chart rather than only in
  tooltips.
- Do not use the clock or the ridgeline to compare size. Rings differ in area and each ridge has its
  own scale.
- A floor plan shows where sensitive rooms are. Check who can see the report before building one.
- Animation is polish. The card draws its real values if a renderer ignores the animation.

## Pro vs Premium

Every recipe here is Pro safe. Nothing needs Fabric, Premium or XMLA. Deneb is a certified visual and
needs the tenant to allow AppSource visuals. See `powerbi-project-and-tools` for licensing facts.

## References in this skill

- `references/deneb-in-pbip.md`: writing a Deneb visual into a report, sizing, field names, the
  errors these specs hit, the traps with no error, and hatching.
- `references/recipes-deneb.md`: fields, settings and limits for each Deneb chart.
- `references/recipes-native-and-svg.md`: the KPI table, card, native butterfly, target ticks, labels
  inside bars, stacked totals, waterfall bridge, filter drawer and dark mode, with the JSON each needs.
- `references/recipes-svg-gauge-and-kpi.md`: the gauges and KPI block for an executive page, and how
  to bind a picture measure to an image visual.
- `references/test-on-fake-data.md`: the fake data report, using it as a test rig, what the test
  covered, and what it did not.

## Scripts

- `scripts/new_deneb_visual.py`: writes one Deneb visual into a page and registers Deneb in the report.
- `scripts/build_fixture.py`: builds a PBIP that holds only fake data, with every recipe on a page.
