# HTML component measures in DAX

A measure can return an HTML snippet (a KPI card, a panel, a header block) built by string
concatenation, drawn by a third party HTML rendering custom visual. Values come from FORMAT(),
styling from VARs at the top of the measure. When such a visual is worth the dependency is decided in
`powerbi-report-design`.

## Keep the styling reviewable

The failure mode is the styling, not the DAX. One long literal string of inline CSS is unreviewable
in a pull request and drifts from the report theme the first time the theme JSON changes.

- Pull every repeated value (color, radius, spacing) into a VAR at the top of the measure, as in the
  worked example below.
- Take the colors from the report's theme (the good, bad, and secondary text colors), never a fresh
  hex typed for one card. `powerbi-report-design` owns the palette and the default theme for a
  report that has no look of its own. If a color is not a theme color, the card should not use it.

### Share tokens across more than one card

Once a second card needs the same colors, move the tokens into helper measures in `_Measures` and
have every card read them. A theme change is then three edits, not a hunt for stray hex strings.

```dax
_Theme Accent Good = "#009E73"
_Theme Accent Bad = "#D55E00"
_Theme Neutral = "#605E5C"
```

```dax
VAR AccentGood = [_Theme Accent Good]
VAR AccentBad = [_Theme Accent Bad]
VAR Neutral = [_Theme Neutral]
```

## Worked example: a KPI card

A value, a label, and an accent color that reacts to a threshold measure.

```dax
Ticket Card HTML =
VAR AccentGood = "#009E73"
VAR AccentBad = "#D55E00"
VAR Neutral = "#605E5C"
VAR CardRadius = "8px"
VAR CardPadding = "12px"
VAR OpenCount = [Open Tickets]
VAR Threshold = [Open Tickets Target]
VAR Accent =
    SWITCH (
        TRUE (),
        ISBLANK ( Threshold ), Neutral,
        OpenCount > Threshold, AccentBad,
        AccentGood
    )
VAR ValueText = FORMAT ( OpenCount, "#,0" )
RETURN
    "<div style='border-left:4px solid " & Accent & "; border-radius:" & CardRadius &
    "; padding:" & CardPadding & "; font-family:Segoe UI, sans-serif;'>" &
    "<div style='font-size:28px; font-weight:600; color:" & Accent & ";'>" & ValueText &
    "</div><div style='font-size:12px; color:" & Neutral & ";'>Open Tickets</div></div>"
```

Bind the visual's data role to `[Ticket Card HTML]` directly. Then find the visual's format pane
setting that renders the field as HTML rather than plain text. With it off, most of these visuals
show the raw markup as text, which reads as a broken measure when the measure is fine.

## Composing a panel from more than one card

Keep each card its own measure and lay the finished strings side by side.

```dax
Ticket Panel HTML =
VAR OpenCard = [Ticket Card HTML]
VAR ClosedCard = [Closed Tickets Card HTML]
RETURN
    "<div style='display:flex; gap:12px;'>" & OpenCard & ClosedCard & "</div>"
```

Each card stays testable and reusable without the panel. A card that returns blank from its own
guard contributes an empty div instead of breaking the panel.

## An optional hover reveal panel

A small inline `<style>` block can show detail on hover without a tooltip page. Scope the class to
the row with a unique suffix, for the same reason an SVG id must be unique per row (`svg-from-dax.md`).

```dax
Ticket Card HTML (Hover) =
VAR RowClass = "card" & SELECTEDVALUE ( Ticket[Ticket Queue Key] )
RETURN
    "<style>." & RowClass & " .detail { display:none; } ." & RowClass &
    ":hover .detail { display:block; }</style>" &
    "<div class='" & RowClass & "'><div class='summary'>" &
    FORMAT ( [Open Tickets], "#,0" ) & "</div>" &
    "<div class='detail'>Avg age " & FORMAT ( [Avg Ticket Age Days], "#,0" ) &
    " days</div></div>"
```

Not every HTML visual honors `:hover` the same way in Desktop, the service, and export to PDF, so
never make hover the only place a number appears.

## Anti-patterns

- **Literal hex or spacing values in the string.** Invisible to a theme change and to review. Use a
  VAR from a theme color.
- **No fallback when the measure returns blank.** An empty filter context or a missing threshold
  should still render a card with a "no data" label. Guard the value with
  `IF ( ISBLANK ( ... ), ... )` before building the string.
- **One giant measure for the whole page.** A single point of failure, hard to review, impossible to
  reuse. One component per measure, composed on the page.
- **An external image URL in the string.** `<img src="https://...">` is a network call that fails
  silently in the service under a restrictive gateway and fails an export to PDF. Embed the image as
  a data URI or use a report registered image resource.
