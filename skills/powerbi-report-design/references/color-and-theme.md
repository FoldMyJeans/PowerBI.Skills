# Color and theme

How a Power BI theme JSON is built, how to apply and validate the house theme, and the color
and font rules. The ready made theme is `house-default-theme.json`.

## How a theme JSON is structured

A theme file has one required key, `name`. Everything else is optional, and any slot you leave
out keeps the Power BI default. Microsoft groups the rest into four parts.

1. Theme colors. The data palette and the status and gradient slots.
   - `dataColors`: an array of hex codes for the series in visuals. It can hold as many colors
     as you want. When they run out, Power BI generates more by shifting saturation and hue.
   - Sentiment slots `good`, `neutral`, `bad`: the status colors used by the waterfall chart
     and the KPI visual.
   - Divergent slots `minimum`, `center`, `maximum`, and `null`: the gradient endpoints in the
     conditional formatting dialog. In the visual JSON gradient (`fillRule`) the same four are
     `minColor`, `midColor`, `maxColor` and `nullColor`. They are not available to DAX, which
     cannot read theme slots at all.
2. Structural colors. The frame of the report.
   - `background` and `secondaryBackground`: page and element backgrounds.
   - `foreground` (also called `firstLevelElements`): primary text, card labels, trend lines.
   - `foregroundNeutralSecondary` (also called `secondLevelElements`): axis and legend labels,
     table headers.
   - `tableAccent`: the table and matrix grid outline.
3. Text classes. Under `textClasses`, set the four primary classes and the rest inherit.
   - `callout`: card data labels and KPI indicators. This is the big number.
   - `title`: axis and visual titles.
   - `header`: tab and matrix style headers.
   - `label`: table and matrix values and general text.
   - Each class takes `fontFace`, `fontSize`, and `color`.
4. Visual styles. Under `visualStyles`, set per visual defaults, for example turn off data
   labels on line charts or set a default gridline style. This is where a theme goes from a
   color swap to a real design system. Keep it lean and set only what you want to change.
   A rule can target one visual type by name, not just the `*` wildcard. A useful pattern is a
   subtle rounded border on every visual, turned off for the image visuals so a logo has no box:

   ```json
   "visualStyles": {
     "*":     { "*": { "border": [ { "show": true, "radius": 8, "color": { "solid": { "color": "#E1DFDD" } } } ] } },
     "image": { "*": { "border": [ { "show": false } ] } }
   }
   ```

Note. You cannot put conditional formatting rules in a theme. The theme sets the gradient
colors, but you still apply the rule on each visual.

## Apply the house theme

In Power BI Desktop, go to View, Themes, Browse for themes, and pick
`house-default-theme.json`. From then on every new visual inherits its colors and
fonts. What the house theme encodes:

- `dataColors` is the Okabe-Ito colorblind safe categorical palette (blue, orange, green,
  vermillion, sky blue, reddish purple, yellow, black). These stay distinct for the common
  forms of color vision deficiency and in grayscale.
- The diverging scale runs blue at `minimum` to a light center to orange at `maximum`. It
  deliberately avoids red to green, which is the pairing most colorblind readers cannot tell
  apart.
- `good` is green and `bad` is vermillion (a red orange), so positive and negative still read
  without relying on a true red and green.
- Segoe UI across the text classes, at a tight size scale.

- A `visualStyles` block that carries the container look: a banded title, a gray subtitle, a
  divider, an 8 pixel border radius, a drop shadow, and 2 pixel padding, plus an 8, 9, 10, 12
  type scale on axes, legends, and grids. This is the part that makes a report look finished, and
  it belongs in the theme rather than on each visual. See the anti-pattern below.

The type scale is 8 for axis labels, legends, slicers, and table text, 9 for subtitles and
secondary text, 10 for axis titles and data labels, and 12 for visual titles. Sizes above that
are for a card's headline number only.

## The anti-pattern: a theme that is only decoration

The failure looks like this. A theme sets exactly three things, a title style, a subtitle style
and a border. All three are ALSO written literally into dozens of individual `visual.json`
files, with identical values. Delete the theme and nothing on the canvas moves.

The cost is real. Changing the title band color means editing 50 files instead of one, which is
the outcome the design once as a system rule in `design-principles.md` exists to prevent.

The test is simple. Pick a value your theme sets, change it, and reopen the report. If nothing
moves, your visuals are overriding it and you do not have a design system.

So the rule is: put font, size, weight, and color in the theme. Put only the things that differ
per visual, the title TEXT, the subtitle TEXT, and any measure driven color, in the visual.

## How a visual references a theme color

The mechanism:

```json
"fontColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } }
```

`ColorId` indexes the theme. `0` is `background`, `1` is `foreground`, and `2` through `9` are
`dataColors[0]` through `dataColors[7]`. `Percent` is a tint when positive and a shade when
negative, as a fraction, so `0.6` is 60 percent lighter and `-0.25` is 25 percent darker.

A pale banded subtotal row is therefore the bad color at 60 percent lighter, not a hand picked
pink. Prefer this over a literal hex anywhere the color carries a meaning the theme already
names, so the report survives a theme swap. The `powerbi-pbir-builder` skill has the JSON
detail.

## DAX-generated HTML and SVG

Never hardcode typography or color inside DAX-generated HTML or SVG (a custom card, an SVG icon
measure). Reference the same theme tokens the rest of the report uses, the house hex values and
type scale, the way a visual uses `ThemeDataColor` instead of a literal hex.

Ship gate. Before shipping, grep the DAX-generated markup for a hardcoded font-family or
hex-color literal and fix any bare value found. Zero inline font declarations across a whole
layout is an achievable bar, because every typography decision can live in the theme. Hold
DAX-generated markup to it.

## Color rules

- Three to five purposeful colors per page, each with a fixed meaning. Gray for context, one
  accent for the thing in focus, and the `good` and `bad` slots (green and vermillion) reserved
  for positive and negative.
- Keep the semantic encoding. Do not let a brand color override a meaning slot. If the brand is
  blue, that does not make `bad` blue. The status slots exist so bad always looks bad.
- Default to colorblind safe palettes. Okabe-Ito for categorical series, and a ColorBrewer
  colorblind safe set for sequential or diverging scales.
- Test a palette before you commit. Paste it into Viz Palette to simulate color vision
  deficiency (https://projects.susielu.com/viz-palette), or build sequential and diverging ramps
  in ColorBrewer (https://colorbrewer2.org/).
- Never use color as the only signal. Back it with a label, an icon, or position. See
  `accessibility.md`.

## Validate the theme JSON

Power BI mostly ignores theme properties it does not recognize, silently, so a misspelled
property does not fail the import, it just never does anything. Catch that by validating
against the official schema. Download `reportThemeSchema.json` from
the Report Theme JSON Schema folder in `microsoft/powerbi-desktop-samples`, put it next to your
theme, and add the reference:

```json
{
  "$schema": "./reportThemeSchema.json",
  "name": "ABC House Default"
}
```

In VS Code this gives autocomplete on every slot and flags an invalid property as you type. It
is the fastest way to author `visualStyles` without guessing card and property names.

## Fonts

- Segoe UI for text is the Power BI default and reads well. DIN is the default for numbers on
  cards and axes. Keep to one or two families and a tight size scale.
- Custom fonts may not render on non Windows clients, on the web, or on mobile, and they fall
  back to a substitute that can break your layout. Prefer a web safe sans serif for anything
  that must travel. The house theme keeps Segoe UI across all four text classes for exactly
  this reason, rather than leaning on DIN for the callout.
- Make the hierarchy obvious. Large bold KPI values, medium headings, smaller secondary text.
  Do not center long text. Left align for reading.

## Pro vs Premium

Building, applying, and validating a theme is all Pro. The free theme generators
(https://themes.powerbi.tips/, https://bibb.pro/apps/theme-generator/) are Pro friendly.
Applying a theme to a published dataset over XMLA, or
extracting a theme programmatically through Semantic Link Labs in a Fabric notebook, needs
Fabric or Premium. Any Copilot assisted color or narrative feature needs a Fabric capacity too.
