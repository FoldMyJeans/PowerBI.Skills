# Ratios and totals that do not lie

A ratio whose denominator is an AVERAGE, or any non additive ratio, is right per entity and
meaningless at the total. The total row evaluates the same expression once over all visible rows,
so it becomes a ratio of two grand totals, not the average of the row ratios. Nothing errors and the
rows look right, so nobody checks the total.

The fix: detect leaf row versus total, and on the total switch to an explicit AVERAGEX over the
entity.

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

The CALCULATE inside AVERAGEX turns each sprint into a filter, so the ratio is computed per sprint
and then averaged. If a slicer can narrow Sprint while Sprint is not on the visual, use ISINSCOPE
instead (see the test list below).

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

The `FILTER ( VALUES ( ... ), CALCULATE ( ... ) > 0 )` matters. A sprint with zero capacity returns
a ratio of zero, AVERAGEX counts it, and a few empty sprints drag the mean toward zero.

Which test to use:

- ISINSCOPE is true when the column is a grouping level of the visual. Use it when the branch
  depends on the visual's level, which is what a total test usually means.
- HASONEVALUE is true when exactly one value is visible, whatever narrowed it. A slicer down to one
  sprint makes it true with Sprint nowhere on the visual, so a card or a total takes the leaf
  branch. Use it when the calculation needs a single selected value.
- ISFILTERED is true when the column is filtered from any source, including a slicer. Use it when
  the slicer, not the axis, narrows the calculation.

The wrong test sends you down the wrong branch, and the result looks like the total problem you
were fixing. SQLBI finds ISINSCOPE cheaper because it counts nothing, and warns that true can mean
zero values as well as one, which made one of their queries far slower than HASONEVALUE.
https://www.sqlbi.com/articles/distinguishing-hasonevalue-from-isinscope/

## Custom totals, with no DAX

On a table or matrix, right click a numeric column, Customize total calculation: Sum, Min, Max,
Count, Count Distinct, Average, or None. Generally available from May 2026, built on visual
calculations, and not yet run on a real model here.

- It can replace an AVERAGEX total branch on a matrix. A card has no total row, so the measure fix
  stays for cards.
- Per Microsoft's docs (generate one in Desktop and read `visual.json` back before relying on it),
  Desktop renames the field with a `_Base` suffix, hides it, and adds a visual calculation named
  like the original, for example `EXPANDALL ( AVERAGE ( [X_Base] ), ROWS COLUMNS )`. In `visual.json`
  the projection carries `customTotalMetadata.baseQueryName`.
- Table and matrix only, numeric only, and every visual calculation limit applies
  (`window-and-visual-calculations.md`).

## The same trap on cards and titles

A card has no axis, so it always evaluates at the whole visual grain. That is the total row by
another name, and an unguarded ratio on a card is wrong for the same reason. A dynamic title built
from a measure has the same shape (the title version is in `powerbi-pbir-builder`).

## DIVIDE with or without the third argument

Blank is usually the better default. A measure that always returns a value turns a sparse
calculation dense, so the visual fetches every grouping in the filter context, renders slower, and
shows rows with no data. Microsoft's example is a table trying to list all 18,484 customers
(https://learn.microsoft.com/en-us/dax/best-practices/dax-avoid-converting-blank).

- `DIVIDE ( n, d, 0 )` when a chart reads better with a zero mark, so a gap does not look like
  missing data.
- `DIVIDE ( n, d )` when blank should suppress the row or mark, which is what a matrix wants so
  empty combinations do not print as zeros.

Apply one choice across a report, or the two behaviours look like a bug.

## REMOVEFILTERS over specific columns

Percent of parent in a matrix: release the columns that define the parent and hold everything else.

```dax
Activity % of Month =
VAR Num = SUM ( 'fact_effort'[Effort (Hours)] )
VAR Den = CALCULATE ( SUM ( 'fact_effort'[Effort (Hours)] ), REMOVEFILTERS ( 'fact_effort'[Activity], 'fact_effort'[Team] ) )
RETURN DIVIDE ( Num, Den )
```

For a two axis matrix, release whole dimension tables.

```dax
Task Updates % of Grand Total =
VAR Num = COUNT ( fact_task_activity[Task Number] )
VAR Den = CALCULATE ( COUNT ( fact_task_activity[Task Number] ), REMOVEFILTERS ( dim_day ), REMOVEFILTERS ( dim_hour ) )
RETURN DIVIDE ( Num, Den )
```

`ALL` over the fact would be wrong in both. It also releases the sprint and company slicers, so the
denominator becomes the whole model rather than the whole page, and the percentages sum to less than
100.

## Value filter behavior can change a REMOVEFILTERS result

When two columns of one table are both filtered, DAX can merge them into only the combinations that
exist. Clearing one column then still leaves the other narrowed. In Microsoft's example a measure
that clears Year returns 5 where 6 is expected, because the selected year has no red products.
SQLBI's returns 372 where 657 is expected. Nothing errors. `Activity % of Month` above has this shape
when a slicer sits on the same table as the columns it releases.

- The setting is Value filter behavior, in the model properties in Model view: Automatic,
  Independent, or Coalesced. Independent keeps the filters separate.
- The sources disagree on the default. Microsoft's page (October 2024) says Automatic behaves as
  Coalesced for now and will change for new models later. SQLBI (October 2025) says Automatic gives new models Independent, and
  recommends Independent. Read the setting on your own model.
- Changing it can change numbers. Snapshot your measures with two same table slicers first and
  diff them after. To see the TMDL property, toggle it in Desktop and read the file back.

Sources: https://learn.microsoft.com/en-us/power-bi/transform-model/value-filter-behavior and
https://www.sqlbi.com/articles/understanding-value-filter-behavior-in-summarizecolumns/

## MAXX over FILTER to collapse duplicate source rows

When the source can hold more than one row per key, SUM at the leaf silently doubles. Take one value.

```dax
VAR PlannedVacation =
    MAXX (
        FILTER ( fact_planning, fact_planning[Sprint] = ThisSprint && fact_planning[Team Member] = ThisOwner ),
        fact_planning[Vacation/Sick Days (Days)]
    )
```

MAX and MIN work when the duplicates are identical. MAXX is the safe default because it also survives
a source that emits a partial and a corrected row for the same key.

## The residual bucket

When categories must total exactly 100 percent of a known whole, define the last bucket as the
remainder.

```dax
VAR AdminH = FullCap - MSH - PSH - PreSaleH - MappedInternal - IncCRH - UnavailH
```

The buckets always add to the whole, which a stacked chart or share matrix needs. The trade: the
residual absorbs data quality problems silently, so a broken mapping upstream shows as a fat Admin
number, not an error. Say so in a comment in the measure.

## Cumulative or burn up over a non date column

The running total in `patterns.md` works over any ordered column, so a burn up against a flat
estimate needs no date table.

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

The numerator accumulates and the denominator is flat. The accumulated column only has to sort
correctly, so a `YYYY-MM` text month works. TREATAS forms are in `virtual-relationships.md`.
