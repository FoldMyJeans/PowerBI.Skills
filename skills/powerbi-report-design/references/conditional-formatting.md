# Conditional formatting

How to color a visual by its values, and first, when not to.

## Opt-in, not automatic

Build the visual plain, then ask the user whether this visual should carry conditional formatting
and what it should say. Do not add it unprompted. If they say no, ship it plain. When everything is
colored, nothing stands out. When they say yes, steer them to the pattern that fits the question.

## The pattern menu

- Threshold flag. Rules mode, for example below 80 percent is bad, at or above is good. When there
  is a known target.
- Highlight the exceptions only. Color just the 100 percent rows, or just the worst, and leave the
  rest plain.
- Top or bottom N. Rank driven emphasis for leaders or laggards.
- Magnitude heatmap. A gradient across a matrix of one measure where the shape is the story. The
  easiest one to overuse.
- In-cell data bars. Length beside the number, for one ranked column.
- KPI status icons. A small set (up, flat, down, or a traffic light) next to the value.
- On target band. A three stop gradient where the MIDDLE is good and both ends are bad, for
  utilization, capacity or budget adherence, where under is as much a problem as over. Stops of
  bad at 0.5, good at 1.0, bad at 1.2 read as "near 100 percent is where you want to be". A plain
  red to green ramp on a utilization chart cannot say this.

## What you can format, and where

- Background color and Font color: table and matrix cells, and data points on many other visuals.
- Data bars, Icons and Web URL: table and matrix only.
- Series colors take fx on bar, column, pie, donut and line charts once the chart has a Legend
  field (July 2026): rules, a gradient, or a color measure, and a line can be gradient colored by
  its total. A line chart without a legend has one line and nothing to vary, so use a reference
  line or a separate flagged series there. Bars and columns still take fx per data point.
- The plot area behind a cartesian chart takes a background color with fx (October 2026). One
  status measure can shade the whole chart instead of stacked reference bands.
- Red, yellow, green target zones behind a line (a compliance trend against 80, 90 and 100 percent):
  layer several y axis reference lines, each with its shade on and a pale zone color. Later shades
  paint over earlier ones, so 100, then 90, then 80 stack into clean bands. Two gotchas. The shade
  paints over the data line too, so set shade transparency to about 70 or the line disappears.
  Keep zone colors pale (for example #F8CBAD, #FFF2CC, #C6E0B4), full strength status colors
  swallow the chart.

## The three modes

Chosen in the Format by dropdown.

1. Gradient. A ramp between a minimum and maximum, optionally through a center. For continuous
   magnitude.
2. Rules. Fixed bands, for example 0 to 79 bad, 80 to 100 good. For known thresholds, and the most
   explainable.
3. Field value. A measure returns the color. The most flexible, and the default for anything
   semantic, because the logic lives in DAX and travels with the model.

## Field value: measure driven color

The measure must return a CSS color value: a hex code like `#009E73`, RGB, RGBA, HSL, HSLA, or a
CSS color name like `Green`. Theme slot names like `good` or `bad` render nothing. Use the report
theme's hex values and keep them in one place so a theme change is one find and replace.

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

- The measure's data type must be Text. As a variant or a number, the Field value binding will not
  accept it.
- A calculation group can silently break a color measure by turning it into a variant. Test the
  color after adding any calc group.

To follow the theme automatically instead of hardcoding hex, use Rules or Gradient and pick the
theme swatches in the dialog. Field value trades that for full measure driven logic.

## Choose the ramp by meaning, never red to green

- Signed magnitude around a midpoint (variance above and below zero): the divergent slots
  `minimum`, `center`, `maximum`. In the default theme, blue to a light center to orange.
- Good to bad status (compliance, health, pass rate): the `good`, `neutral`, `bad` sentiment
  colors, through Rules with the swatches or a Field value measure returning their hex.
- Both avoid a true red to green ramp. The default `bad` is a red orange for that reason.

A theme sets these slot colors but cannot store the rules or thresholds, which are applied per
visual. See `color-and-theme.md`.

## Data bars, icons, and blanks

- Data bars. Show bar only drops the number when the exact value does not matter. The axis sits at
  zero by default. Data bars do not print unless Background graphics is on in print settings.
- Icons. A built in set, or a custom icon from a Field value measure returning an image URL or an
  SVG data URI. For SVG in DAX (scaling, escaping, unique ids per repeated instance, rendering
  routes), see `powerbi-dax`.
- Blanks and errors. Guard a ratio with DIVIDE so divide by zero returns blank, and set an explicit
  minimum, center and maximum on a gradient so a stray blank does not stretch the scale.

## Accessibility

- Color is never the only cue. Pair a fill with an icon, a data label or a text tag.
- Black text on a saturated `bad` orange fill can fall under 4.5 to 1. Add a Font color format so
  the text flips to white on dark fills, and check the pair with the TPGi eyedropper on the live
  canvas. Two measures travel together, with matching thresholds:

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

  The font threshold is the band boundary where the background turns dark. Change one, change the
  other. Never ship a background color measure without its paired font measure.

- A `SWITCH ( TRUE (), ... )` ladder also handles a ramp that is not monotonic, where both low and
  high are bad, which neither Gradient nor Rules can express.
- See `accessibility.md`.

## Pro vs Premium

Every mode, data bars, icons and field value color measures are Pro.

## Sources

Microsoft Learn on conditional table formatting
(https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting)
and the tips for color formatting
(https://learn.microsoft.com/en-us/power-bi/visuals/service-tips-and-tricks-for-color-formatting),
plus Havens Consulting on report design and Excelerator BI on icons.
