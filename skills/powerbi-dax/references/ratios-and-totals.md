# Ratios and totals that do not lie

Measures that are right on every row and wrong on the total row, and how to fix them. Also
covers releasing specific filters, collapsing duplicate source rows, and cumulative totals
over a non date column.

## The problem

A ratio whose denominator is an AVERAGE, or any ratio that is not additive, is correct per
entity and meaningless at the total. Power BI computes the total by evaluating the same
expression once over all visible rows, so the total becomes a ratio of two grand totals, not
the average of the row ratios.

Nothing errors. The row values look right, so nobody checks the total, which is how this one
reaches production more often than any other DAX mistake.

The fix is always the same shape. Detect whether you are on a leaf row or a total, and switch
to an explicit AVERAGEX over the entity when you are on the total.

## The HASONEVALUE form

```dax
Task Capacity vs Planned Capacity =
VAR PerSprintRatio =
    DIVIDE ( SUM ( fact_effort[Effort (Hours)] ), AVERAGE ( fact_effort[Planned Capacity (Hours)] ) )
RETURN
IF (
    HASONEVALUE ( fact_effort[Sprint] ),
    PerSprintRatio,
    AVERAGEX (
        VALUES ( fact_effort[Sprint] ),
        CALCULATE ( DIVIDE ( SUM ( fact_effort[Effort (Hours)] ), AVERAGE ( fact_effort[Planned Capacity (Hours)] ) ) )
    )
)
```

The CALCULATE inside AVERAGEX is doing the work. It turns each sprint row into a filter
(context transition) so the ratio is computed per sprint, then the mean of those ratios is
returned. If a slicer can narrow Sprint while Sprint is not on the visual, swap HASONEVALUE for
ISINSCOPE. The test section below explains why.

## The ISFILTERED variant, dropping empty rows first

```dax
Capacity Utilization (%) =
VAR HasSprintFilter = ISFILTERED ( fact_capacity[Sprint] )
RETURN
IF (
    HasSprintFilter,
    DIVIDE ( SUM ( fact_capacity[Total Effort (Hours)] ), SUM ( fact_capacity[Max Capacity (Hours)] ), 0 ),
    AVERAGEX (
        FILTER ( VALUES ( fact_capacity[Sprint] ), CALCULATE ( SUM ( fact_capacity[Max Capacity (Hours)] ) ) > 0 ),
        CALCULATE ( DIVIDE ( SUM ( fact_capacity[Total Effort (Hours)] ), SUM ( fact_capacity[Max Capacity (Hours)] ), 0 ) )
    )
)
```

The `FILTER ( VALUES ( ... ), CALCULATE ( ... ) > 0 )` matters. A sprint with zero capacity
returns a ratio of zero, and AVERAGEX counts it, so a few empty sprints drag the mean toward
zero. Removing them before averaging is the difference between a believable number and a
number the business will argue with.

Which test to use:

- ISINSCOPE is true when the column is a grouping level of the visual. Use it when the branch
  depends on the visual's level, which is what a total test usually means.
- HASONEVALUE is true when exactly one value of the column is visible, whatever narrowed it. A
  slicer down to one sprint makes it true with Sprint nowhere on the visual, so a card or a total
  takes the leaf branch. Use it when the calculation needs a single selected value.
- ISFILTERED is true when the column is filtered at all, from any source including a slicer.
  Use it when the slicer, not the axis, is what narrows the calculation.

Pick by which one matches your visual. Getting this wrong sends you down the wrong branch and
the result looks like the total problem you were fixing. SQLBI also finds ISINSCOPE cheaper because
it counts nothing, and warns that true can mean zero values as well as one, which made one of their
queries far slower than HASONEVALUE.
https://www.sqlbi.com/articles/distinguishing-hasonevalue-from-isinscope/

## Custom totals, with no DAX

On a table or matrix, Customize total calculation on a numeric column changes what the total row
shows: Sum, Min, Max, Count, Count Distinct, Average, or None. Microsoft lists this as generally
available from May 2026 and builds it on visual calculations. It may replace an AVERAGEX total branch
on a matrix, but a card has no total row, so the measure fix stays for cards. This is from Microsoft
docs and has not yet been run on a real model. The limits are in `window-and-visual-calculations.md`.

## The same trap on cards and titles

A card has no axis, so it always evaluates at the whole visual grain. That is the total row by
another name, and an unguarded ratio on a card is wrong for the same reason. A dynamic title
built from a measure has the same shape. For the title version see the
`powerbi-pbir-builder` skill.

## DIVIDE with or without the third argument

Both are valid, and blank is usually the better default. The third argument looks like a display
decision, but it has a cost. A measure that always returns a value turns a sparse calculation into a
dense one, so the visual fetches every grouping in the filter context, renders slower, and shows rows
with no data. Microsoft's example is a table trying to list all 18,484 customers
(https://learn.microsoft.com/en-us/dax/best-practices/dax-avoid-converting-blank). Make it
deliberately.

- `DIVIDE ( n, d, 0 )` when a chart reads better with a zero mark on the axis, so a gap does
  not look like missing data.
- `DIVIDE ( n, d )` when blank should suppress the row or the mark, which is what you want in a
  matrix so empty combinations do not print as zeros.

Apply the choice consistently across a report or the two behaviours look like a bug.

## REMOVEFILTERS over specific columns

`patterns.md` shows `ALL ( Table )` and `ALLSELECTED ( Table )`. Percent of parent
in a matrix needs something narrower. Release the columns that define the parent and hold
everything else.

```dax
Activity % of Month =
VAR Num = SUM ( 'fact_effort'[Effort (Hours)] )
VAR Den = CALCULATE ( SUM ( 'fact_effort'[Effort (Hours)] ), REMOVEFILTERS ( 'fact_effort'[Activity], 'fact_effort'[Team] ) )
RETURN DIVIDE ( Num, Den )
```

For a two axis matrix, release whole dimension tables instead.

```dax
Task Updates % of Grand Total =
VAR Num = COUNT ( fact_task_activity[Task Number] )
VAR Den = CALCULATE ( COUNT ( fact_task_activity[Task Number] ), REMOVEFILTERS ( dim_day ), REMOVEFILTERS ( dim_hour ) )
RETURN DIVIDE ( Num, Den )
```

`ALL ( fact_effort )` would be wrong in the first case and `ALL` over the fact would be wrong
in the second. Both release the sprint and company slicers too, so the denominator becomes the
whole model rather than the whole page. The percentages then sum to less than 100 and nobody
can explain why.

## Value filter behavior can change a REMOVEFILTERS result

When two columns of one table are both filtered, DAX can merge them into only the combinations that
exist. Clearing one column then still leaves the other narrowed. In Microsoft's example, a measure
that clears Year returns 5 where 6 is expected, because the selected year has no red products. SQLBI's
returns 372 where 657 is expected. Nothing errors. `Activity % of Month` above has this shape when a
slicer sits on the same table as the columns it releases.

The setting is Value filter behavior, in the model's properties in Model view: Automatic, Independent,
or Coalesced. Independent keeps the filters separate. The sources disagree on the default. Microsoft's
page, dated October 2024, says Automatic behaves as Coalesced for now and will change for new models
later. SQLBI, in October 2025, says Automatic gives new models Independent, and recommends Independent.
So read the setting on your own model instead of assuming. Changing it can change numbers, so snapshot
your measures with two same table slicers first and diff them after. To see the property in TMDL,
toggle it in Desktop and read the file back.

Sources: https://learn.microsoft.com/en-us/power-bi/transform-model/value-filter-behavior and
https://www.sqlbi.com/articles/understanding-value-filter-behavior-in-summarizecolumns/

## MAXX over FILTER to collapse duplicate source rows

When the source can hold more than one row per key, SUM at the leaf silently doubles. Take one
value instead of adding them.

```dax
VAR PlannedVacation =
    MAXX (
        FILTER ( fact_planning, fact_planning[Sprint] = ThisSprint && fact_planning[Team Member] = ThisOwner ),
        fact_planning[Vacation/Sick Days (Days)]
    )
```

MAX and MIN both work when the duplicates are identical. MAXX is the safe default because it
also survives a source that emits a partial and a corrected row for the same key.

## The residual bucket

When a set of categories must total exactly 100 percent of a known whole, define the last
bucket as the remainder rather than as its own sum.

```dax
VAR AdminH = FullCap - MSH - PSH - PreSaleH - MappedInternal - IncCRH - UnavailH
```

Everything unaccounted for lands there by construction, including unlogged hours and rows in
categories nobody mapped. The buckets always add to the whole, which is what a stacked chart
or a share matrix needs.

The trade is real. The residual bucket absorbs data quality problems silently, so a broken
mapping upstream shows up as a fat Admin number and not as an error. Put a comment in the
measure saying that, so the next person reads the bucket as a remainder and not as a fact.

## Cumulative or burn up over a non date column

The running total in `patterns.md` assumes `'Date'[Date]`. The same shape works
over any ordered column, so a burn up against a flat estimate needs no date table and no time
intelligence.

```dax
PS Cumulative vs Estimate % =
DIVIDE (
    CALCULATE (
        SUM ( dim_work_item[Task Effort (Hours)] ),
        FILTER ( ALLSELECTED ( dim_work_item[LUD Month] ), dim_work_item[LUD Month] <= MAX ( dim_work_item[LUD Month] ) )
    ),
    CALCULATE (
        SUM ( fact_estimate_ps[Estimate of Effort] ),
        TREATAS (
            ALLSELECTED ( dim_work_item[Company], dim_work_item[Epic Number] ),
            fact_estimate_ps[Company],
            fact_estimate_ps[Epic Number]
        )
    ),
    0
)
```

The numerator accumulates and the denominator is flat. That is the burn up shape. The column
being accumulated only has to sort correctly, so a `YYYY-MM` text month works. For the TREATAS
part see `virtual-relationships.md`.
