# SVG measures in DAX

A measure can build a small SVG chart as a string and hand it to Power BI as an image, with no
custom visual. This covers the DAX to build the shape, scale it into a fixed viewBox, and wrap
it as a data URI that Desktop and the service will actually render.

Seen in practice: a sparkline trend per row of a matrix, built entirely from measures, with the
column set to Data Category Image URL. No custom visual, no external tool, and it survives
export to PDF because it is just an image.

## Assemble a point table

Start from a small table of one point per category on the axis. Use ADDCOLUMNS over the axis
you want to plot, usually a date or a category column, and compute the value at each point with
CALCULATE so it responds to filter context.

```dax
VAR Points =
    ADDCOLUMNS (
        VALUES ( 'Date'[Month Number] ),
        "@Sales", CALCULATE ( [Total Sales] )
    )
```

## Scale into a fixed viewBox

An SVG viewBox is a fixed pixel canvas. Real values almost never land inside it, so scale every
point from its own min and max into the canvas width and height. Name the canvas size and
padding as VARs once, do not repeat the numbers at every use.

```dax
VAR ViewboxWidth = 120
VAR ViewboxHeight = 40
VAR Padding = 4
VAR MinSales = MINX ( Points, [@Sales] )
VAR MaxSales = MAXX ( Points, [@Sales] )
VAR SalesRange = MaxSales - MinSales
VAR MinMonth = MINX ( Points, 'Date'[Month Number] )
VAR MaxMonth = MAXX ( Points, 'Date'[Month Number] )
VAR MonthRange = MaxMonth - MinMonth
VAR ScaledPoints =
    ADDCOLUMNS (
        Points,
        "@X",
            IF (
                MonthRange = 0,
                Padding,
                Padding + DIVIDE ( 'Date'[Month Number] - MinMonth, MonthRange )
                    * ( ViewboxWidth - 2 * Padding )
            ),
        "@Y",
            IF (
                SalesRange = 0,
                ViewboxHeight / 2,
                ViewboxHeight - Padding - DIVIDE ( [@Sales] - MinSales, SalesRange )
                    * ( ViewboxHeight - 2 * Padding )
            )
    )
```

The `MonthRange = 0` and `SalesRange = 0` guards matter. A product with one month of data or a
perfectly flat series has a zero range, and dividing by that range without the guard returns an
error for the whole measure instead of a flat line. When the range is zero, park the point at
the middle of the axis rather than fail.

## Turn the points into a path string

CONCATENATEX walks the scaled table in order and joins each point into the space separated
list an SVG `points` attribute expects. Sort by the axis column so the line is not drawn out of
order.

```dax
VAR PointsString =
    CONCATENATEX (
        ScaledPoints,
        ROUND ( [@X], 1 ) & "," & ROUND ( [@Y], 1 ),
        " ",
        'Date'[Month Number],
        ASC
    )
```

## Wrap it as a data URI

Build the SVG markup as one string, then wrap it as a `data:` URI so the measure needs no file
and no image host.

```dax
VAR SvgBody =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 " & ViewboxWidth & " " &
    ViewboxHeight & "'><polyline fill='none' stroke='#0072B2' stroke-width='2' points='" &
    PointsString & "' /></svg>"
VAR EscapedSvg =
    SUBSTITUTE ( SUBSTITUTE ( SvgBody, "#", "%23" ), "'", """" )
RETURN
    "data:image/svg+xml;utf8," & EscapedSvg
```

Two escapes, and both are required, not optional:

- `#` becomes `%23`. A raw `#` inside a data URI reads as the start of a URI fragment, so
  everything after the first `#` (the stroke color above) gets silently cut from the image.
- The single quote used to delimit SVG attributes becomes a literal double quote. Single quotes
  are valid in SVG, so this one is harmless on its own, and it is required the moment the
  finished URI is dropped into another attribute that is itself single quoted, for example an
  `<img src='...'>` built by an HTML measure. There the first inner `'` closes the src early and
  the image breaks. Swap it every time rather than remembering which route the string took.

Run the SUBSTITUTE chain once, last, over the finished SVG string. Escaping a fragment before it
is assembled means you have to remember to do it again at every concatenation, and that is how
half the string ends up escaped and half does not.

## Unique ids when a chart repeats per row

A gradient or a filter needs an `id`, and SVG ids are just DOM ids. Whether that matters depends
on which route you took.

On the Image URL route each row loads as its own image, an isolated document, so two rows can
both use `id="grad"` and neither notices. On the HTML route every row renders into one shared
document, so identical ids collide and the browser resolves `url(#grad)` to whichever it saw
first. Every row after the first then picks up the wrong fill, silently.

Suffix every id with something unique to the row anyway, usually a key column already on the
table. It costs nothing on the Image URL route and it means the measure keeps working if the
report later moves to an HTML visual. A measure has no row context of its own, so read that key
with SELECTEDVALUE rather than naming the column bare, which returns an error instead of a
value.

```dax
VAR RowId = "grad" & SELECTEDVALUE ( Product[Product Key] )
VAR GradientDef =
    "<linearGradient id='" & RowId & "' x1='0' y1='0' x2='0' y2='1'>" &
    "<stop offset='0%' stop-color='#0072B2'/><stop offset='100%' stop-color='#56B4E9'/>" &
    "</linearGradient>"
VAR AreaFill = "<polygon fill='url(#" & RowId & ")' points='" & PointsString & "' />"
```

Do this even for a chart you are sure only ever shows one row today. The day it lands in a
matrix with a category on rows, a static id turns into a silent rendering bug that only shows up
in the report, never in a spot check of the measure text.

## Two ways to render it

- **Data Category = Image URL, no custom visual.** Set the measure's Data Category to Image URL
  in the model, then bind it into a table or matrix image column, or a card's image well. This
  is the house default. It ships with Desktop, needs no import, and export to PDF renders it as
  a normal image.
- **A third party HTML rendering visual.** Some report pages already carry a third party visual
  that renders raw HTML, and an SVG data URI drops straight into an `<img>` tag inside that HTML.
  That is a heavier dependency for the same picture, so reach for it only when the page is
  already paying for that visual. See `html-from-dax.md` in this skill for the HTML
  side of that pattern.

## Check the string before you trust the visual

A broken data URI usually renders as a blank cell, which tells you nothing about what went
wrong. Copy the measure's value out of a table visual (or DAX Studio) and paste it straight into
a browser address bar. A valid data URI starting with `data:image/svg+xml` renders the shape in
the tab, and a bad one throws whatever the escaping mistake produced, which is much faster to
read than guessing from a blank cell in the report.

## Alt text

Once the image is on the report, it needs alt text like any other visual. That convention, and
how to write it, belongs to `powerbi-report-design`. Point a card or matrix image column at its
guidance rather than inventing wording here.

## Keep animation off the load bearing path

SVG supports SMIL, the `<animate>` tag, for inline animation with no JavaScript. It works, but
it renders inconsistently across the canvas Power BI uses on the web, in Desktop, and in
export to PDF, and a renderer that does not support it just shows the static end state. Treat
animation as a nice to have polish layer, never as the thing that carries information the
report depends on.

## Anti-patterns

- **Half done escaping.** Handling `#` but not the quote (or the reverse) passes a spot check on
  a simple shape and then breaks the first time a color or a second attribute pushes a quote
  later into the string.
- **Magic pixel numbers repeated inline.** Typing `120`, `40`, and `4` at every point instead of
  naming `ViewboxWidth`, `ViewboxHeight`, and `Padding` once. Change the canvas size later and
  you are hunting through the whole measure for every place a number needs to move.
- **A static id that collides once the visual repeats.** Works in a single card, breaks silently
  the day the measure lands on a matrix row.
- **Importing an external font inside the SVG string.** A font URL is a network call. It either
  fails silently in the service and the shape falls back to a default font, or it fails an
  export to PDF entirely. Stick to a font already on the machine rendering it.
