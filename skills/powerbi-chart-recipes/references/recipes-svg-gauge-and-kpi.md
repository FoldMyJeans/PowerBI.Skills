# SVG gauges and KPI blocks for an executive page

Two DAX SVG measures for a one page summary with no tables: a row of 270 degree gauges, and a KPI
block with a change pill. Both are pictures, so they draw the same in Desktop, the Service and an
export, with nothing installed. For the mechanics of SVG in a measure, see `svg-from-dax.md` in
`powerbi-dax`.

## Binding a picture measure to an image visual

Set the measure's Data Category to Image URL, then:

```json
"visualType": "image",
"objects": {"image": [{"properties": {
  "sourceType": {"expr": {"Literal": {"Value": "'imageUrl'"}}},
  "sourceUrl": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Gauges SVG"}}},
  "imageScalingType": {"expr": {"Literal": {"Value": "'Fit'"}}}
}}]},
"visualContainerObjects": {
  "padding": [{"properties": {
    "top": {"expr": {"Literal": {"Value": "0D"}}},
    "right": {"expr": {"Literal": {"Value": "0D"}}},
    "bottom": {"expr": {"Literal": {"Value": "0D"}}},
    "left": {"expr": {"Literal": {"Value": "0D"}}}}}],
  "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
}
```

- Container padding 0 matters. With the default padding the picture scaled down and sat off centre.
- Over a page background picture, a faint 1 px line showed along the bottom edge of the image frames.
  Extending the frames to the page bottom removed it.

## Gauges, `assets/dax/gauge.dax`

One measure draws a gauge per row of a `DATATABLE` (code, label, colour, slot) with `CONCATENATEX`.
Each gauge is a grey track arc from 225 degrees to minus 45, a value arc to `225 - 270 * score / max`,
and a dashed radial tick at the target.

- The SVG arc's large arc flag is `IF ( 270 * score / max > 180, 1, 0 )`. Get it wrong and a high score
  draws the short way round.
- Write every coordinate with `FORMAT ( x, "0.0", "en-US" )`. A locale with a decimal comma otherwise
  writes `35,4`, which SVG reads as two numbers.
- A blank score shows a dash, not zero.
- Replace `[Gauge Score]`, `[Gauge Target]` and `'Gauge Item'[Code]` with the model's names. Scores and
  targets share one scale, set by `MaxScore`.

## KPI block, `assets/dax/kpi-block.dax`

A 24 px number, a 12 px label, an 11 px grey "Previous month" line, and a soft pill with the change:
`rect rx='9' fill-opacity='0.18'` behind a small triangle and the delta text.

- Set `LowerIsBetter` per KPI. The pill is green when the change is good, red when bad, and grey with
  "same" when there is none. A count of open items that rose is red with an up arrow.
- Percent KPIs show the change in points, counts in units.
- The pill's x is estimated from the length of the number text, `LEN ( text ) * 14 + 10` for a 24 px
  semibold number. Check it on the widest value the KPI will show.
- A percent sign in the text is why the escape chain starts with `%`. Without it the block drew faded.

## One picture per DirectQuery source

On a report that reads several published semantic models, a single SVG measure that read all of them
made Desktop stop on the "Potential security risk" prompt. One picture measure per source avoided it.
See composite models in `powerbi-data-and-refresh`.

## Keep the text minimal

These blocks suit a page read in a meeting. Full KPI names as labels, no explanation lines, few or no
tooltips. The owner's taste on this is in `visual-decisions.md` in `powerbi-report-design`.
