# Accessibility

WCAG is not optional. A report that fails contrast or has no tab order excludes real users and
often fails a client review. The rules of thumb are in `design-principles.md`, items
21 to 23. This file is the checklist and the tools.

## Contrast (WCAG)

- Normal text needs a contrast ratio of at least 4.5 to 1 against its background.
- Large text needs at least 3 to 1. Large means about 18 point, or 14 point bold and up.
- Non text elements like chart bars, lines, icons, and control borders need at least 3 to 1 so
  they are distinguishable.
- The house theme colors are chosen to pass on a white background. If you change a background or
  a data color, re-check the pair. Light text on a light fill is the most common failure.

## Alt text

- Add alt text to every non decorative visual. Set it in the Format pane under General, Alt
  text. Describe what the visual shows and its main takeaway, not just the field names.
- Mark a purely decorative shape or image as hidden from the tab order so a screen reader skips
  it. Do not write alt text for decoration.
- Alt text can be dynamic. Drive it from a measure so it states the current number, for example
  "Revenue this month is X, which is Y percent versus target". Build the string in
  `powerbi-dax` and bind it in the alt text field.

### A dynamic alt text measure

Build the sentence from the current selection instead of a fixed string, with a fallback so it
never reads blank:

```DAX
Chart Alt Text =
VAR selCategory = SELECTEDVALUE ( Product[Category], "all categories" )
VAR selRevenue = [Revenue]
RETURN
    "Revenue for " & selCategory & " is " & FORMAT ( selRevenue, "$#,##0" ) &
    " for the selected period."
```

Bind it the same way a dynamic title is bound: the PBIR `visual.json` points the visual's
`general.altText` at the measure, the same expression shape as a title bound to a measure. See
`powerbi-pbir-builder` for that binding mechanic.

Staleness anti-pattern. An alt text measure that hardcodes a specific year or category goes
stale the moment the report period rolls forward. Read the live selection with
`SELECTEDVALUE`, the same as a title measure, not a string frozen at build time.

## Tab order

- Set a logical tab order in the Selection pane. Switch the pane to Tab order and drag the
  visuals into reading order, top left to bottom right, matching the three tier layout.
- Do not leave tab order at the default. The default follows the order visuals were added,
  which is rarely the reading order.
- Remove decorative objects from the tab order in the same pane, so keyboard and screen reader
  users are not stopped on a background shape.

## Do not use color as the only signal

- Back every color meaning with a second cue: a data label, an icon, a text tag, or position.
  A red bar and a green bar look identical to many colorblind readers and in grayscale print.
- For a status column, add an icon or a word next to the color, not just a colored cell.
- For a line chart with several series, vary the marker or use direct labels, so the lines are
  told apart without relying on hue.
- This is why the house theme uses a blue to orange diverging scale and keeps `bad` a red
  orange. Design the meaning to survive without color, then add color on top.
- When you add conditional formatting to a table or matrix, follow the same rule: pair the color
  with an icon or a text tag, and check that text on a saturated fill still passes contrast. See
  `conditional-formatting.md`.

## Free tools to check a live canvas

- TPGi Colour Contrast Analyser. A desktop app with an eyedropper. Sample the actual pixels on
  a rendered Power BI canvas and it reports the pass or fail against WCAG. This is the best way
  to test real rendered colors, including text sitting on a chart.
- WebAIM contrast checker. A web tool for checking two hex codes. Use it while picking theme
  colors, before they are ever on the canvas.
- https://www.tpgi.com/color-contrast-checker/ and https://webaim.org/resources/contrastchecker/

## Verify it, do not assume it

A well built report
was found with a deliberate, curated tab order on all 148 visuals and not one single piece of alt
text. The pass was half done, and nobody noticed because nothing checks.

On a PBIP you can check both in seconds. Run these from the project root with Desktop closed.

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

Run them before you ship, not after a client review. If the alt text count is far below the
visual count, the report is not accessible whatever the contrast checker says.

Decorative shapes and images legitimately have no alt text, so expect the two numbers to differ
by the number of logos and backing shapes. A count of zero is never legitimate.

## Built in support to lean on

- Keyboard navigation and screen reader support are built into Power BI reports. A clean tab
  order and good alt text are what make them work.
- Power BI respects the operating system high contrast mode in the Service. Do not hard code a
  color that breaks in high contrast.

## The Microsoft checklist

Microsoft publishes a report accessibility checklist and an accessibility overview. Run the
checklist before you ship a report to anyone outside your team.
https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-overview

## Pro vs Premium

Every accessibility feature here (alt text, tab order, contrast, keyboard and screen reader
support) is Pro. None of it needs Fabric or Premium.
