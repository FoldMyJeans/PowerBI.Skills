# HTML component measures in DAX

A measure can return a full HTML snippet, a KPI card, a small panel, a header block, built with
plain string concatenation, and a third party HTML rendering visual draws it. Values come from
FORMAT(), styling comes from VARs at the top of the measure, and the whole thing lives and
refreshes like any other measure.

This pattern requires a third party HTML rendering custom visual. It is a deliberate, governed
exception to building visuals natively. See `powerbi-report-design` for when a third party
visual like this is worth the dependency, that policy is not repeated here.

## Keep the styling reviewable

The failure mode with an HTML string measure is not the DAX, it is the styling. A card built as
one long literal string of inline CSS is unreviewable in a pull request and drifts from the
report theme the first time someone updates the theme JSON and forgets this measure exists.

Pull every repeated value, color, radius, spacing, out to a VAR at the top of the measure, and
source the color values from the house theme's existing colors, never a fresh hex typed in for
this one card. If a color is not already a theme color, that is a sign the card should not be
using it.

```dax
VAR AccentGood = "#009E73"
VAR AccentBad = "#D55E00"
VAR Neutral = "#605E5C"
VAR CardRadius = "8px"
VAR CardPadding = "12px"
```

These are the house semantic colors, the good, bad, and secondary text values the house theme
already defines (`powerbi-report-design` owns the palette and the theme file). Reading them from
the theme rather than picking a fresh hex means a card built this way reads as part of the same
report, not a one off.

### Share tokens across more than one card

The moment a second card measure needs the same colors, copying the VAR block into it defeats
the point. Move the tokens into small helper measures in `_Measures` instead, and have every
card measure read them.

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

Now the theme lives in one place. Update the three helper measures when the report theme
changes and every card measure that reads them picks up the change on the next evaluation,
instead of someone hunting through every card measure in the model for a stray hex string.

## Worked example: a KPI card

A value, a label, and an accent color that reacts to a threshold measure. This is the whole
shape most component measures need.

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

The visual's data role binds to `[Ticket Card HTML]` directly. No other setup is needed on the
Power BI side, the HTML rendering visual is doing all the work of turning the string into a DOM.

Check the visual's format pane for an explicit setting that tells it to render the field as HTML
rather than plain text. Without that switch on, most of these visuals show the raw markup as
escaped text instead of drawing it, which reads as a broken measure when the measure itself is
fine.

## Composing a panel from more than one card

Keep each card as its own small measure, then build a panel by laying the finished HTML strings
side by side rather than writing the panel as one large measure from scratch.

```dax
Ticket Panel HTML =
VAR OpenCard = [Ticket Card HTML]
VAR ClosedCard = [Closed Tickets Card HTML]
RETURN
    "<div style='display:flex; gap:12px;'>" & OpenCard & ClosedCard & "</div>"
```

Each card measure stays independently testable, readable on its own, and reusable on a
different page without the panel wrapper. If a card measure returns blank because its own guard
caught a missing value, it just contributes an empty div to the flex row rather than breaking
the whole panel.

## An optional hover reveal panel

A small `<style>` block inline in the string can show detail on hover without a second visual or
a tooltip page. Scope the class to the row with a unique suffix, the same way an SVG chart needs
a unique id per row when it repeats, see `svg-from-dax.md` in this skill for why an
unscoped id or class collides once the visual repeats across a table.

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

Treat this as an optional polish layer, not a place to put information the report depends on.
Not every HTML rendering visual honors `:hover` the same way in every host (Desktop, the
service, export to PDF), so anything shown only on hover should be a nice to have, never the
only place a number appears.

## Anti-patterns

- **Literal hex or spacing values instead of theme derived VARs.** A color typed straight into
  the string is invisible to a theme change and invisible to review. Pull it into a VAR sourced
  from a color the theme already defines.
- **No fallback when the measure returns blank.** An empty filter context or a missing threshold
  measure should still render a card, with a "no data" label, not an empty box or a broken
  layout. Guard the value with an `IF ( ISBLANK ( ... ), ... )` before you build the string.
- **One giant measure for the whole page.** Building an entire report page as one HTML string is
  a single point of failure, hard to review, and impossible to reuse. Keep each component, one
  card, one panel, one header, as its own small measure, and compose them on the page the way
  you would compose any other set of visuals.
- **An external image URL inside the HTML string.** A `<img src="https://...">` pointing off the
  local machine is a network call. It fails silently in the service under a restrictive gateway
  and fails an export to PDF outright. Embed the image as a data URI or use a report registered
  image resource instead, never a live external URL.
