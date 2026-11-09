# DAX patterns

Copy ready patterns. Rename tables and columns to match the model. Everything time based assumes a
real Date table marked as a date table (`powerbi-modeling`).

Names used below: `Sales` is the fact, `'Date'` the Date dimension, `Product` a dimension, `Budget` a
fact at a higher grain. `[Total Sales]` is the base measure, and the later patterns reuse it.

## Base measure

Define each plain aggregation once and reference it everywhere else. Do not repeat the SUM.

```dax
Total Sales = SUM ( Sales[SalesAmount] )
```

## Safe division

```dax
Margin % =
DIVIDE (
    [Total Margin],
    [Total Sales]
)
```

DIVIDE returns blank on a zero or blank denominator. A third argument such as `DIVIDE ( a, b, 0 )`
has a cost, read `ratios-and-totals.md` first.

## Percent of total

ALL gives percent of the grand total, ignoring any filter on Product. ALLSELECTED gives percent of
what the user selected on the page.

```dax
Sales % of All Products =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALL ( Product ) )
)
```

```dax
Sales % of Selected =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALLSELECTED ( Product ) )
)
```

For percent of a parent in a matrix, release specific columns instead, see `ratios-and-totals.md`.

## Year over year

```dax
Sales PY =
CALCULATE (
    [Total Sales],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)
```

```dax
Sales YoY % =
VAR CurrentSales = [Total Sales]
VAR PriorSales =
    CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
VAR Result = DIVIDE ( CurrentSales - PriorSales, PriorSales )
RETURN
    Result
```

DATEADD takes any offset (a quarter, a month, several years).

```dax
Sales PY (DATEADD) =
CALCULATE (
    [Total Sales],
    DATEADD ( 'Date'[Date], -1, YEAR )
)
```

When the latest period is only part done, a prior period measure compares it with a whole period.
The fair form is in `time-intelligence.md`.

## Year to date

```dax
Sales YTD =
TOTALYTD (
    [Total Sales],
    'Date'[Date]
)
```

Add a year end date as the last argument for a fiscal year.

## Running total

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

ALLSELECTED keeps outer slicers in play. MAX reads the last date of the current cell. The same shape
over any ordered column is in `ratios-and-totals.md`.

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

ALL sets the population. The empty third argument ranks the current item. DENSE leaves no gaps after
ties. For a tie break on several columns and blank on totals, use RANK
(`window-and-visual-calculations.md`). For scores, tiers, and paging a rank, see
`scoring-and-pagination.md`.

## Virtual relationship with TREATAS

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

The Date slice filters Budget with no physical relationship. A budget held by month repeats the whole
month on a day level visual, so return blank below the fact's grain, as in the higher grain case in
`many-to-many.md` in the `powerbi-modeling` skill. More forms in `virtual-relationships.md`.

## KPI label with an arrow and a semantic color

A pair of measures: a label string the card shows as its value, and a hex string the card binds to
its font color (binding JSON in `powerbi-pbir-builder`). Color encodes good versus bad, never up
versus down (the KPI card convention is in `powerbi-report-design`).

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

- UNICHAR 9650 is the up triangle, 9660 down, 9644 a flat bar.
- Rising open criticals is bad, so up gets the bad color. For a metric where rising is good, flip
  the color branch, not the arrow.
- The `ISBLANK ( Prev )` guards keep the first month neutral instead of reading as a rise from zero
  in the bad color.
- The hex values come from a report that predates its palette. Take the good and bad colors from
  the report's theme instead (`powerbi-report-design` owns the palette). Color is the only signal
  here, and green against red is the pair a colorblind reader separates worst.

## Common mistakes

- Plain `/` on a zero denominator returns Infinity or NaN, which shows as an error or a broken
  visual.
- A count that returns blank. `COUNTROWS` on no rows is blank, so a card reads "(Blank)" and a
  color rule testing `= 0` never fires. Add `+ 0` to a count that should show "0 people".
- A calculated column where a measure belongs. A column does not respond to slicers.
- Expecting row context to filter. See `measures-vs-calc.md`.
