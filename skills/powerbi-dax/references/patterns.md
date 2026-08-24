# DAX patterns

Copy ready patterns that are correct and come up constantly. Change the table and column names
to match the model. Every ratio uses DIVIDE. Everything time based assumes a real Date table
that is marked as a date table (see `powerbi-modeling`).

Names used below: `Sales` is the fact table, `'Date'` is the Date dimension, and `Product` and
`Budget` are dimensions. `[Total Sales]` is the base measure defined first, and the later
patterns reuse it.

## Base measure

Start every model with plain aggregations, then build on them.

```dax
Total Sales = SUM ( Sales[SalesAmount] )
```

Define the base once and reference `[Total Sales]` everywhere else. Do not repeat the SUM.

## Safe division

```dax
Margin % =
DIVIDE (
    [Total Margin],
    [Total Sales]
)
```

DIVIDE returns blank when the denominator is zero or blank, so no divide by zero error. Pass a
third argument if you want something other than blank, for example `DIVIDE ( a, b, 0 )`.

## Percent of total

Remove the filter on the dimension in the denominator so it becomes the total.

```dax
Sales % of All Products =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALL ( Product ) )
)
```

ALL gives percent of the grand total across every product, ignoring any filter on the Product
table. Use ALLSELECTED instead when you want percent of what the user has selected on the page.

```dax
Sales % of Selected =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALLSELECTED ( Product ) )
)
```

## Year over year

Shift the date filter back one year, then compare. SAMEPERIODLASTYEAR and DATEADD both work.

```dax
Sales PY =
CALCULATE (
    [Total Sales],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)
```

```dax
Sales YoY % =
DIVIDE (
    [Total Sales] - [Sales PY],
    [Sales PY]
)
```

DATEADD is the flexible form when you need a different offset (a quarter, a month, several
years).

```dax
Sales PY (DATEADD) =
CALCULATE (
    [Total Sales],
    DATEADD ( 'Date'[Date], -1, YEAR )
)
```

## Year to date

```dax
Sales YTD =
TOTALYTD (
    [Total Sales],
    'Date'[Date]
)
```

TOTALYTD accumulates from January 1 of the current year to the current date in the filter. Add
a year end date as the last argument for a non calendar fiscal year.

## Running total

Accumulate from the start of the visible range up to the current date.

```dax
Sales Running Total =
CALCULATE (
    [Total Sales],
    FILTER (
        ALLSELECTED ( 'Date'[Date] ),
        'Date'[Date] <= MAX ( 'Date'[Date] )
    )
)
```

ALLSELECTED keeps outer slicers in play. MAX reads the last date of the current cell, so each
row shows the total up to and including that date.

## Ranking

```dax
Product Rank by Sales =
RANKX (
    ALL ( Product[Product Name] ),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

RANKX walks the table in the first argument and ranks each item by the expression. ALL sets the
population to rank over. The empty third argument means rank the current item. DESC puts the
largest first, and DENSE avoids gaps after ties.

For a 0-100 score, a composite of several scores, a tier or quadrant label, or windowing this
rank into pages for a leaderboard, see `scoring-and-pagination.md`.

## Virtual relationship with TREATAS

Filter a table that has no physical relationship, by transferring the current selection onto
its column.

```dax
Budget Amount =
CALCULATE (
    SUM ( Budget[Amount] ),
    TREATAS (
        VALUES ( 'Date'[Month] ),
        Budget[Month]
    )
)
```

TREATAS applies the values of the first argument as a filter on the column in the second. Here
the Date slice drives the Budget table even though the two are not related in the model. It is
the lightweight way to relate at a different grain without a physical relationship.

## KPI label with an arrow and a semantic color

The KPI card convention (see the `powerbi-report-design` skill) wants a value, an arrow, a
delta versus the prior period, and a color that encodes good versus bad, never up versus down.
That is a pair of measures, not one: a label string the card shows as its value, and a hex
string measure the card binds to its font color (the JSON binding is in the
`powerbi-pbir-builder` skill).

```dax
KPI Criticals Label =
VAR Cur  = [Open Criticals]
VAR Prev = CALCULATE ( [Open Criticals], DATEADD ( 'Date'[Date], -1, MONTH ) )
VAR Diff = Cur - Prev
VAR Arrow =
    SWITCH ( TRUE (), Diff > 0, UNICHAR ( 9650 ), Diff < 0, UNICHAR ( 9660 ), UNICHAR ( 9644 ) )
RETURN
    IF (
        ISBLANK ( Prev ),
        FORMAT ( Cur, "#,0" ),
        FORMAT ( Cur, "#,0" ) & "  " & Arrow & " " & FORMAT ( ABS ( Diff ), "#,0" )
            & " vs last month"
    )
```

```dax
KPI Criticals Color =
VAR Prev = CALCULATE ( [Open Criticals], DATEADD ( 'Date'[Date], -1, MONTH ) )
VAR Diff = [Open Criticals] - Prev
RETURN
    SWITCH ( TRUE (), ISBLANK ( Prev ) || Diff = 0, "#605E5C", Diff > 0, "#C0504D", "#4F6228" )
```

UNICHAR 9650 is the up triangle, 9660 down, 9644 a flat bar. For open criticals rising is bad,
so up gets the bad color. Flip the color branch, not the arrow, for a metric where rising is
good. The `ISBLANK ( Prev )` guards matter: on the first month of data the comparison clause
drops and the color goes neutral, instead of reading as a rise from zero in the bad color.

One note on the hex values. They are a dark green and a brick red rather than the theme's
semantic pair, which is what happens when a report predates its own palette. For new work take
the good and bad colors from the theme instead (the
`powerbi-report-design` skill owns the palette). That pairing matters here because color is the
only signal separating good from bad in this measure, and a green and red pair is the one a
colorblind reader is least able to tell apart.

## VAR for readable and faster measures

Name each step with VAR. Each variable is evaluated once and then reused, so the measure is
easier to read and often faster.

```dax
Sales YoY % =
VAR CurrentSales = [Total Sales]
VAR PriorSales =
    CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
VAR Result = DIVIDE ( CurrentSales - PriorSales, PriorSales )
RETURN
    Result
```

A VAR captures the context where it is declared, not where it is used later. That is usually
what you want, and it removes repeated subexpressions.

## Common mistakes

- Time intelligence with no Date table. DATEADD, SAMEPERIODLASTYEAR, and TOTALYTD need a real
  Date dimension with contiguous dates, marked as a date table. Without it they return blank or
  silently wrong numbers. Build the Date table in `powerbi-modeling`.
- A calculated column where a measure belongs. If it aggregates or reacts to slicers, it is a
  measure. A calculated column bloats the model and does not respond to filters. See
  `measures-vs-calc.md`.
- Forgetting DIVIDE. Plain `/` returns Infinity or NaN on a zero denominator, which shows up as
  an error or a broken visual. Use DIVIDE for every ratio.
- Measures scattered across fact and dimension tables. Where a measure lives does not change its
  result, but loose measures are hard to find. Keep them in one _Measures table (see
  `powerbi-modeling`).
- Expecting row context to filter. Being on a row does not restrict what a measure sees. Wrap it
  in CALCULATE to turn the row into a filter (context transition). See
  `measures-vs-calc.md`.
