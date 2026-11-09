# Accessibility

WCAG is not optional, whatever the report's style. A report that fails contrast or has no tab
order excludes real users and often fails a client review. The rules of thumb are in the
accessibility section of `design-principles.md`. This file is the checklist and the tools.

## Contrast

- Normal text: at least 4.5 to 1 against its background.
- Large text (about 18 point, or 14 point bold and up): at least 3 to 1.
- Non text elements (bars, lines, icons, control borders): at least 3 to 1.
- The default theme's colors pass on white. A changed background or data color needs the pair
  re-checked. Light text on a light fill is the most common failure.

## Alt text

- Every non decorative visual gets alt text (Format pane, General, Alt text) describing what it
  shows and the main takeaway, not the field names.
- A decorative shape or image gets no alt text and is hidden from the tab order.
- Alt text can be dynamic, driven by a measure that states the current number, with a fallback so
  it never reads blank:

```DAX
Chart Alt Text =
VAR selCategory = SELECTEDVALUE ( Product[Category], "all categories" )
VAR selRevenue = [Revenue]
RETURN
    "Revenue for " & selCategory & " is " & FORMAT ( selRevenue, "$#,##0" ) &
    " for the selected period."
```

In PBIR, `general.altText` on the visual points at the measure, the same expression shape as a
title bound to a measure. See `powerbi-pbir-builder` for the binding.

Staleness trap: an alt text measure that hardcodes a year or category goes stale when the period
rolls forward. Read the live selection with `SELECTEDVALUE`.

## Tab order

- In the Selection pane, switch to Tab order and drag visuals into reading order, top left to
  bottom right. The default follows the order visuals were added, which is rarely reading order.
- Remove decorative objects from the tab order there, so keyboard and screen reader users are not
  stopped on a background shape.

## Color is never the only signal

- Back every color meaning with a data label, an icon, a text tag or position. A red bar and a
  green bar look identical to many colorblind readers and in grayscale print.
- A status column gets an icon or a word beside the color.
- A line chart with several series varies the marker or uses direct labels.
- The default theme's blue to orange diverging scale and red orange `bad` follow from this. Design
  the meaning to survive without color, then add color.
- Conditional formatting follows the same rule, and text on a saturated fill must still pass
  contrast. See `conditional-formatting.md`.

## Free tools to check a live canvas

- TPGi Colour Contrast Analyser: a desktop eyedropper that samples rendered pixels on the canvas
  and reports pass or fail. The best test of real colors, including text on a chart.
- WebAIM contrast checker: two hex codes, for picking theme colors before they reach the canvas.
- https://www.tpgi.com/color-contrast-checker/ and https://webaim.org/resources/contrastchecker/

## Verify it on the files

One report had a curated tab order on all 148 visuals and not one piece of alt text, and nobody
noticed because nothing checks. On a PBIP, run these from the project root with Desktop closed:

```powershell
# how many visuals exist, and how many have alt text
$v = Get-ChildItem .\*.Report\definition\pages -Recurse -Filter visual.json
"visuals: $($v.Count)"
"with alt text: $(($v | Select-String -Pattern '"altText"').Count)"
```

```powershell
# any visual left on the default tab order
Get-ChildItem .\*.Report\definition\pages -Recurse -Filter visual.json |
  Where-Object { -not (Select-String -Path $_.FullName -Pattern '"tabOrder"' -Quiet) } |
  Select-Object -ExpandProperty FullName
```

Run them before shipping. The two counts differ by the logos and backing shapes, which rightly
have no alt text. An alt text count of zero is never legitimate.

## Built in support

- Keyboard navigation and screen readers are built in. A clean tab order and good alt text make
  them work.
- The Service respects the operating system high contrast mode. Do not hard code a color that
  breaks in it.
- Microsoft's report accessibility checklist, to run before shipping outside the team:
  https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-overview

## Pro vs Premium

Alt text, tab order, contrast, keyboard and screen reader support are all Pro.
