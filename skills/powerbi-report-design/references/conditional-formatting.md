# Conditional formatting

How to color a visual by its values, and, first, when not to.

## It is opt-in, not automatic

Default to a clean, uncolored table or chart. Conditional formatting is a tool for a specific
job, not a finishing coat you apply to everything. Coloring every visual wastes effort and
dilutes attention, because when everything is colored nothing stands out.

So the rule is: build the visual plain, then ask the user whether this specific visual should
carry conditional formatting, and what it should say. Do not add it unprompted, and do not spend
time wiring color the user did not ask for. If they say no, ship it plain.

When they say yes, keep the best practice patterns below in mind so you can steer them to the one
that fits the question, rather than coloring for its own sake.

## The pattern menu (reach for the one that fits the question)

- Threshold flag. Rules mode, for example anything below 80 percent turns bad, at or above turns
  good. Best when there is a known target.
- Highlight the exceptions only. Color just the 100 percent rows, or just the worst, and leave
  the rest plain. Draws the eye to what matters.
- Top or bottom N. Rank driven emphasis when the reader wants the leaders or the laggards.
- Magnitude heatmap. A gradient across a range, for a matrix of one measure where the shape is
  the story. Use this sparingly, it is the easiest one to overuse.
- In-cell data bars. Length encodes magnitude next to the number. Good for a single ranked
  column in a table or matrix.
- KPI status icons. A small icon set (up, flat, down, or a traffic light) next to the value.
- On target band. A three stop gradient where the MIDDLE is good and both ends are bad. For
  utilization, capacity, or budget adherence, being under is as much a problem as being over, and
  a one directional ramp cannot say that. Stops of bad at 0.5, good at 1.0, bad at 1.2 read as
  "near 100 percent is where you want to be". This is the pattern most people are missing when
  they reach for a plain red to green ramp on a utilization chart.

## What you can format, and where

- Background color and Font color work on table and matrix cells, and on many other visuals'
  data points.
- Data bars, Icons, and Web URL are table and matrix only.
- A line chart does not support conditional formatting on the line itself. Encode meaning another
  way there, for example a reference line or a separate flagged series.
- For full red, yellow, green target zones behind a line (a compliance trend against 80, 90, and
  100 percent thresholds), layer several y axis reference lines, each with its shade turned on
  and a pale zone color. Later shades paint over earlier ones, so a 100 percent shade, then a 90,
  then an 80 stack up into clean bands. Two gotchas. The shade paints over the
  data line too, so set shade transparency to about 70 or the line disappears under the zones.
  And keep the zone colors pale (for example #F8CBAD, #FFF2CC, #C6E0B4), full strength status
  colors swallow the whole chart.

## The three modes

Every conditional format is one of three modes, chosen in the Format by dropdown.

1. Gradient. A color ramp between a minimum and a maximum value, optionally through a center.
   For continuous magnitude.
2. Rules. Fixed bands you define, for example 0 to 79 is bad, 80 to 100 is good. For known
   thresholds and targets. This is the most explainable mode, the bands are written down.
3. Field value. A measure returns the color directly. The most flexible, and the house default
   for anything semantic, because the logic lives in DAX and travels with the model.

## The field value pattern (measure-driven color)

Write a measure that returns a color, then bind it as the Field value. The measure must return a
value from the CSS color spec, a hex code like `#009E73`, an RGB, RGBA, HSL, or HSLA value, or a
CSS color name like `Green`. Theme slot names like `good` or `bad` are NOT valid here, they render
nothing, so reference the house theme's hex values directly and keep them in one place so a theme
change is a single find and replace.

```DAX
SLA Status Color =
SWITCH (
    TRUE (),
    [SLA Compliance] >= 0.95, "#009E73",  -- good
    [SLA Compliance] >= 0.90, "#8A8886",  -- neutral
    "#D55E00"                             -- bad
)
```

Two traps:

- The measure's data type must be Text. If it is left as a variant or a number, the Field value
  binding will not accept it.
- A calculation group in the model can silently break a field value color measure, because it
  turns the measure into a variant. Test the color after adding any calc group.

If you want the color to follow the theme automatically instead of hardcoding hex, use Rules or
Gradient mode and pick the theme swatches in the dialog, those track the theme. Field value trades
that for full measure-driven logic.

## Choose the ramp by meaning, and never red to green

- For a signed magnitude that diverges around a midpoint (variance above and below zero), use the
  theme's divergent slots, `minimum`, `center`, `maximum`. In the house theme that runs blue to a
  light center to orange.
- For a good to bad status scale (compliance, health, pass rate), drive it from the `good`,
  `neutral`, `bad` sentiment colors, through Rules where you pick the swatches, or a Field value
  measure that returns their hex.
- Both deliberately avoid a true red to green ramp, which is the pairing most colorblind readers
  cannot tell apart. The house `bad` is a red orange for exactly this reason.

## Theme JSON cannot carry the rules

A theme file sets the default colors the conditional formatting dialog offers (the `good`,
`neutral`, `bad` sentiment slots and the divergent `minimum`, `center`, `maximum`, `null` slots),
but a theme cannot store the conditional formatting rules or thresholds themselves. Those are
applied per visual. So the theme gives you consistent colors to point at, and the semantic logic
lives in a Field value measure or in Rules on the visual. See `color-and-theme.md`.

## Data bars, icons, and blanks

- Data bars. Turn on Show bar only to drop the number and keep just the bar when the exact value
  does not matter. The axis sits at zero by default. Data bars do not print unless Background
  graphics is enabled in print settings.
- Icons. Use a built in icon set, or drive a custom icon from a Field value measure that returns
  an image URL or an SVG data URI. For the fuller SVG-in-DAX pattern (scaling, escaping, unique
  ids per repeated instance, rendering routes), see `powerbi-dax`.
- Blanks and errors. Guard a ratio with DIVIDE so a divide by zero returns blank rather than an
  error, and set an explicit minimum, center, and maximum on a gradient so a stray blank does not
  stretch the scale.

## Accessibility

- Color is never the only cue. Pair a background color with an icon, a data label, or a text
  tag, so the message survives for a colorblind reader and in grayscale.
- Watch contrast on colored cells. Black text on a saturated `bad` orange fill can fall under
  4.5 to 1. If it does, add a Font color conditional format so the text flips to white on the
  dark fills. Check the pair with the TPGi eyedropper on the live canvas.

  The working pattern is two measures that travel together, one for the fill and one for the
  text, with matching thresholds:

  ```DAX
  Heat Color =
  VAR v = [Task Updates % of Grand Total]
  RETURN
  SWITCH ( TRUE (),
      v <= 0.01, "#FFFFFF",
      v <= 0.03, "#FDD0A2",
      v <= 0.05, "#FD8D3C",
      v <= 0.08, "#D94801",
      "#A63603" )
  ```
  ```DAX
  Heat Font =
  VAR v = [Task Updates % of Grand Total]
  RETURN IF ( v > 0.05, "#FFFFFF", "#252423" )
  ```

  The font measure's threshold is deliberately the same band boundary where the background
  crosses into dark. Change one, change the other. Never ship a background color measure without
  its paired font measure.

  A `SWITCH ( TRUE (), ... )` ladder like this also handles a ramp that is not monotonic, where
  both low and high are bad, which neither Gradient nor Rules mode can express.
- See `accessibility.md`.

## Pro vs Premium

Every conditional formatting mode, data bars, icons, and field value color measures are all Pro.
Nothing here needs Fabric or Premium.

## Sources

Microsoft Learn on conditional table formatting
(https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting)
and the tips for color formatting
(https://learn.microsoft.com/en-us/power-bi/visuals/service-tips-and-tricks-for-color-formatting),
plus Havens Consulting on report design and Excelerator BI on icons.
