# SVG measures in DAX

A measure can build a small SVG chart as a string and hand it to Power BI as an image, with no custom
visual. Typical use: a sparkline per row of a matrix, with the measure set to Data Category Image URL.
It survives export to PDF because it is just an image.

## Assemble a point table

One point per axis value, computed with CALCULATE so it responds to filter context.

```dax
VAR Points =
    ADDCOLUMNS (
        VALUES ( 'Date'[Month Number] ),
        "@Sales", CALCULATE ( [Total Sales] )
    )
```

## Scale into a fixed viewBox

Scale every point from its own min and max into the canvas. Name the canvas size and padding as
VARs once.

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

The `MonthRange = 0` and `SalesRange = 0` guards matter. One month of data or a flat series has a
zero range, and without the guard the whole measure errors instead of drawing a flat line. Park the
point mid axis instead.

## Turn the points into a path string

Sort by the axis column so the line is not drawn out of order.

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

```dax
VAR SvgBody =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 " & ViewboxWidth & " " &
    ViewboxHeight & "'><polyline fill='none' stroke='#0072B2' stroke-width='2' points='" &
    PointsString & "' /></svg>"
VAR EscapedSvg =
    SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SvgBody, "%", "%25" ), "#", "%23" ), "'", """" )
RETURN
    "data:image/svg+xml;utf8," & EscapedSvg
```

Three escapes, all required, in this order:

- `%` becomes `%25`, first. A bare `%` starts a percent escape. Any SVG that prints a percentage
  ("87%") rendered faded until this was added. It goes first because the next escape writes `%`
  characters that must not be escaped again.
- `#` becomes `%23`. A raw `#` starts a URI fragment, so everything after the first `#` (the stroke
  color above) is silently cut.
- The single quote becomes a literal double quote. Harmless alone, required the moment the URI goes
  into another single quoted attribute, such as `<img src='...'>` in an HTML measure, where the first
  inner `'` closes the src early. Swap it every time.

More rules that bit:

- Run the SUBSTITUTE chain once, last, over the finished string. Escaping fragments before assembly
  is how half the string ends up escaped.
- Numbers in coordinates need a point, never a decimal comma. Use an explicit locale,
  `FORMAT ( x, "0.0", "en-US" )`, so a model opened under another locale still draws.
- The image keeps its viewBox aspect ratio. In a table, `grid` `imageWidth` and `imageHeight` set
  the box, but a 160 by 24 viewBox in a 330 wide box only centred a small bar. Make the viewBox
  match the shape you want on screen (300 by 18 filled the column).

## Unique ids when a chart repeats per row

A gradient or filter needs an `id`. On the Image URL route each row is its own document, so repeated
ids do not collide. On the HTML route every row renders into one shared document, `url(#grad)`
resolves to the first one, and every later row silently gets the wrong fill.

Suffix every id with a key unique to the row anyway. It costs nothing on Image URL and keeps working
if the report moves to an HTML visual. Read the key with SELECTEDVALUE, because a bare column name in
a measure errors.

```dax
VAR RowId = "grad" & SELECTEDVALUE ( Product[Product Key] )
VAR GradientDef =
    "<linearGradient id='" & RowId & "' x1='0' y1='0' x2='0' y2='1'>" &
    "<stop offset='0%' stop-color='#0072B2'/><stop offset='100%' stop-color='#56B4E9'/>" &
    "</linearGradient>"
VAR AreaFill = "<polygon fill='url(#" & RowId & ")' points='" & PointsString & "' />"
```

A static id passes every spot check of the measure text and only breaks in the report, the day the
measure lands in a matrix with a category on rows.

## Two ways to render it

- **Data Category = Image URL, no custom visual.** Set the measure's Data Category to Image URL,
  then bind it into a table or matrix image column or a card's image well. The default route: it
  ships with Desktop and exports to PDF as a normal image.
- **A third party HTML rendering visual.** An SVG data URI drops into an `<img>` tag inside its HTML.
  A heavier dependency for the same picture, so use it only when the page already carries that
  visual. See `html-from-dax.md`.

## Check the string before you trust the visual

A broken data URI renders as a blank cell. Copy the measure's value out of a table visual (or DAX
Studio) and paste it into a browser address bar. A valid `data:image/svg+xml` URI draws the shape,
and a bad one shows the escaping mistake.

## Alt text and animation

- Alt text for the image follows `powerbi-report-design`.
- SVG SMIL (`<animate>`) renders inconsistently across the web, Desktop, and export to PDF, and an
  unsupported renderer shows the static end state. Never let animation carry information.

## Anti-patterns

- **Half done escaping.** Handling `#` but not the quote (or the reverse) passes on a simple shape
  and breaks once a color or a second attribute pushes a quote later into the string.
- **Magic pixel numbers inline.** Typing `120`, `40`, and `4` at every point instead of naming
  `ViewboxWidth`, `ViewboxHeight`, and `Padding` once.
- **A static id that collides once the visual repeats.**
- **An external font URL inside the SVG.** It is a network call that fails silently in the service
  (default font) or fails an export to PDF. Use a font already on the rendering machine.
