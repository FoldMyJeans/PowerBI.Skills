# Color and theme

How a theme JSON is built, the base theme under it, the default theme `house-default-theme.json`
(for a report with no look of its own), and the color and font rules.

## Theme JSON structure

One required key, `name`. Any slot left out keeps the base theme's default.

1. Theme colors.
   - `dataColors`: hex codes for series, as many as you like. When they run out, Power BI shifts
     saturation and hue to make more.
   - Sentiment `good`, `neutral`, `bad`: status colors for the waterfall and the KPI visual. One
     waterfall overrides them in its own `sentimentColors` (`increaseFill`, `decreaseFill`,
     `totalFill`).
   - Divergent `minimum`, `center`, `maximum`, `null`: the gradient endpoints in the conditional
     formatting dialog. In visual JSON (`fillRule`) they are `minColor`, `midColor`, `maxColor`,
     `nullColor`. DAX cannot read any theme slot.
2. Structural colors.
   - `background`, `secondaryBackground`: page and element backgrounds.
   - `foreground` (`firstLevelElements`): primary text, card labels, trend lines.
   - `foregroundNeutralSecondary` (`secondLevelElements`): axis and legend labels, table headers.
   - `tableAccent`: the table and matrix grid outline.
3. Text classes. Set the four primary classes under `textClasses` and the rest inherit. Each takes
   `fontFace`, `fontSize`, `color`.
   - `callout`: card data labels and KPI indicators (the big number).
   - `title`: axis and visual titles.
   - `header`: tab and matrix style headers.
   - `label`: table and matrix values and general text.
4. Visual styles. Per visual defaults under `visualStyles`, which turns a color swap into a design
   system. Set only what you want to change. A rule can target one visual type by name, not just
   `*`. For example a rounded border on every visual, off for images so a logo has no box:

   ```json
   "visualStyles": {
     "*":     { "*": { "border": [ { "show": true, "radius": 8, "color": { "solid": { "color": "#E1DFDD" } } } ] } },
     "image": { "*": { "border": [ { "show": false } ] } }
   }
   ```

- A theme cannot hold conditional formatting rules. It sets the gradient colors, the rule is
  applied per visual.
- Since March 2026 a fill can name a structural color instead of a hex,
  `{ "solid": { "color": "foreground" } }`. The schema also has `visualStyles.page."*".pageSize` for
  the size of new pages, not yet seen working, so render a page to check.

## The base theme under your theme

A custom theme is a layer on a base theme, which supplies every default the theme does not set.
Since August 2026 new reports start on Fluent 2. The others are Classic 2026 (the old default) and
Classic 2018 (reports from before 2026). An existing report keeps its base theme until someone
clicks Update theme in the Theme pane banner or Reset to default.

Fluent 2 defaults a hand written visual inherits: new pages at 1920 by 1080, grey wallpaper, titles
and subtitles on (off for table, matrix and card since a September 2026 preview update), axis titles off, more padding and rounded
corners, smooth lines, new slicers as Dropdown, banded table rows. Since August its fonts all come
from your theme's `textClasses`.

- Read the base theme before writing visuals: `report.json`, `themeCollection.baseTheme.name`.
  `CY24SU10` has been read from a real `report.json`. The theme schema (2.156 and later) has a top
  level `baseTheme` key with values like `Fluent2-CY26SU08`, and the string Desktop writes for
  Fluent 2 has not been read from a file yet.
- The same visual JSON draws differently under different base themes. Button slicer padding broke
  this way, and a list slicer dropdown drew a white box until the full template was used, so test a template under the report's own base theme.
- Updating an old report to Fluent 2 restyles every visual that relies on defaults. Treat it as a
  redesign, not a refresh.
- With nothing selected, the Format pane's Customize current theme edits this layer and exports it
  as theme JSON. The quickest way to see the property names Desktop uses.

## The default theme

For a report with no look of its own, apply `house-default-theme.json` in View, Themes, Browse for
themes. A report with an existing theme keeps it. What the default encodes:

- `dataColors`: the Okabe-Ito colorblind safe palette (blue, orange, green, vermillion, sky blue,
  reddish purple, yellow, black). Distinct for the common color vision deficiencies and in
  grayscale.
- Diverging scale blue at `minimum`, light center, orange at `maximum`. No red to green.
- `good` green, `bad` vermillion (a red orange), so status reads without a true red and green.
- Segoe UI across the text classes.
- A `visualStyles` container look: banded title, gray subtitle, divider, 8 pixel border radius,
  drop shadow, 2 pixel padding.
- Type scale: 8 for axis labels, legends, slicers and table text, 9 for subtitles and secondary
  text, 10 for axis titles and data labels, 12 for visual titles. Larger only for a card's
  headline number.

## Anti-pattern: a theme that is only decoration

A theme sets a title style, a subtitle style and a border, and all three are ALSO written literally
into dozens of `visual.json` files with the same values. Delete the theme and nothing moves.
Changing the title band color is then 50 file edits instead of one.

Test: change a value the theme sets and reopen the report. If nothing moves, visuals override it.

Rule: font, size, weight and color go in the theme. Only what differs per visual goes in the
visual: the title TEXT, the subtitle TEXT, any measure driven color.

## How a visual references a theme color

```json
"fontColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } }
```

`ColorId` `0` is `background`, `1` is `foreground`, `2` to `9` are `dataColors[0]` to
`dataColors[7]`. `Percent` is a fraction, a tint when positive and a shade when negative (`0.6` is
60 percent lighter, `-0.25` is 25 percent darker).

So a pale banded subtotal row is the bad color at 60 percent lighter, not a hand picked pink. Use
this over a literal hex wherever the color carries a meaning the theme names, so the report
survives a theme swap. The `powerbi-pbir-builder` skill has the JSON detail.

## DAX-generated HTML and SVG

Never hardcode typography or color inside DAX-generated HTML or SVG (a custom card, an SVG icon
measure). Use the report theme's hex values and type scale, the same tokens the visuals use.

Ship gate: grep the DAX-generated markup for a hardcoded font-family or hex-color literal and fix
each bare value. Zero inline font declarations across a whole layout is achievable, because every
typography decision can live in the theme.

## Color rules

The rules are in `design-principles.md` (three to five colors with fixed meaning, no brand color
over a semantic slot, colorblind safe palettes, never color alone). Tools to test a palette:

- Viz Palette simulates color vision deficiency (https://projects.susielu.com/viz-palette).
- ColorBrewer builds sequential and diverging ramps (https://colorbrewer2.org/).

## Validate the theme JSON

Power BI silently ignores theme properties it does not recognize, so a misspelled property imports
fine and does nothing. Validate against the official schema: download `reportThemeSchema.json`
from the Report Theme JSON Schema folder in `microsoft/powerbi-desktop-samples`, put it next to the
theme, and reference it:

```json
{
  "$schema": "./reportThemeSchema.json",
  "name": "ABC House Default"
}
```

VS Code then autocompletes every slot and flags invalid properties. The fastest way to author
`visualStyles` without guessing card and property names.

## Fonts

- Segoe UI is the Power BI default for text. Classic base themes use DIN for numbers on cards and
  axes. On Fluent 2 since August 2026 every font comes from the theme's `textClasses`.
- Since February 2026 Segoe UI renders on Mac and mobile browsers too.
- A font named in the theme only shows where it is installed on the viewer's machine, otherwise
  it falls back to a substitute that can break the layout. A brand web font was rejected for an
  executive page for that reason. The default theme keeps Segoe UI across all four text classes,
  numbers included, rather than DIN for the callout.

## Pro vs Premium

Building, applying and validating a theme is Pro. The free theme generators
(https://themes.powerbi.tips/, https://bibb.pro/apps/theme-generator/) are Pro friendly. Applying a
theme to a published dataset over XMLA, or extracting a theme through Semantic Link Labs in a
Fabric notebook, needs Fabric or Premium. Any Copilot assisted color or narrative feature needs a
Fabric capacity.
