# Time intelligence: fair comparisons and what is still preview

The basic year to date and prior year measures are in `patterns.md`. The Date table itself is owned
by the `powerbi-modeling` skill.

## A partial period compared with a whole one

Data runs to 18 August. `Sales PY` on the August row returns all of last August, so year over year
compares 18 days with 31 and shows a collapse that did not happen. Months after August show a prior
year value next to nothing. Nothing errors, and the row looks like a business problem.

Fix: limit the current selection to dates that have data, then shift only those. This is our own
form of the DAX Patterns idea (they use a helper flag on the Date table plus a hidden measure), and it
has not yet been run on a real model.

```dax
Sales PY (Fair) =
VAR LastDataDate =
    CALCULATE ( MAX ( Sales[OrderDate] ), REMOVEFILTERS () )
VAR DatesWithData =
    FILTER ( VALUES ( 'Date'[Date] ), 'Date'[Date] <= LastDataDate )
RETURN
    IF (
        NOT ISEMPTY ( DatesWithData ),
        CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DatesWithData ) )
    )
```

The IF blanks periods that have not started, so a chart stops at the last real date. If several
prior period measures need it, hold the logic once in a function (`functions-and-calculation-groups.md`).

Source for the idea: https://www.daxpatterns.com/standard-time-related-calculations/

## The latest complete month, with a picker that rolls forward

A monthly review in November reads October. A "Current Month" card that means the refresh month shows
"No data" or a half finished month right after each month starts. So the report month defaults to the
last complete one:

```dax
Latest Month End = EOMONTH ( TODAY (), -1 )

Report Month End =
VAR __pick = SELECTEDVALUE ( dim_date[Month Pick] )
RETURN
    IF (
        ISBLANK ( __pick ) || __pick = "Latest",
        [Latest Month End],
        CALCULATE ( MAX ( dim_date[Date] ), REMOVEFILTERS ( dim_date ), dim_date[Month Pick] = __pick )
    )
```

Two calculated columns on a month end date table, each on one line in TMDL:

```tmdl
column 'Months Back' = DATEDIFF ( dim_date[Date], EOMONTH ( TODAY (), 0 ), MONTH )
column 'Month Pick' = IF ( dim_date[Months Back] = 1, "Latest", dim_date[Month Name] )
	sortByColumn: 'Months Back'
```

The picker slicer saves the constant "Latest", so it rolls forward on every refresh with no edit. A
visual level filter `Months Back >= 1` hides the month in progress. The slicer shape is in
`powerbi-pbir-builder`.

## The latest row on or before a date

Snapshot rows (a scan, a monthly KPI row) sit on their own dates, so a month end calendar
relationship matches nothing. Read the latest row on or before the report month inside the measure,
and remove the calendar filter so the relationship cannot blank it:

```dax
Critical Count =
VAR __me = [Report Month End]
VAR __d =
    CALCULATE (
        MAX ( Kpi[Date] ),
        REMOVEFILTERS ( Kpi ), REMOVEFILTERS ( dim_date ),
        Kpi[KPI Name] = "Critical", Kpi[Date] <= __me
    )
RETURN
    IF (
        NOT ISBLANK ( __d ),
        CALCULATE (
            SUM ( Kpi[Value] ),
            REMOVEFILTERS ( Kpi ), REMOVEFILTERS ( dim_date ),
            Kpi[KPI Name] = "Critical", Kpi[Date] = __d
        )
    )
```

- It reads the latest snapshot in the month, never an average of the month's snapshots.
- Previous month: the same measure with `EOMONTH ( [Report Month End], -1 )`.
- Year to date: add `YEAR ( Kpi[Date] ) = YEAR ( __me )`.
- With many KPIs this is a family of near identical measures. Generate them with a script, or hold
  the logic once in a function (`functions-and-calculation-groups.md`).

## A month axis that never skips a month

A month with no rows drops off a chart axis. A calculated month table keeps every month that has
passed:

```dax
SELECTCOLUMNS (
    ADDCOLUMNS (
        GENERATESERIES ( 0, DATEDIFF ( DATE ( 2025, 1, 1 ), TODAY (), MONTH ), 1 ),
        "@m", EDATE ( DATE ( 2025, 1, 1 ), [Value] )
    ),
    "Month Start", [@m],
    "Month Label", FORMAT ( [@m], "mmm yyyy" ),
    "Year", YEAR ( [@m] ),
    "Month No", MONTH ( [@m] )
)
```

- The `@` columns are re-emitted under final names, so the `sourceColumn` names declared in TMDL
  match. Add its `ref table` line to `model.tmdl`.
- Sort `Month Label` by `Month Start` and put the text label on the axis. A date column on a
  categorical axis still skipped every other label.
- With no relationship to the facts, a measure reads the axis with `MAX ( month[Month Start] )` or
  `SELECTEDVALUE`, and uses `REMOVEFILTERS` on any slicer column the axis replaces. Label such a
  measure YTD, not "this year".

## Calendar based time intelligence: pilot only

Still preview, behind the Enhanced DAX Time Intelligence option, through the October 2026 release
(TABLEOF, NAMEOF, and the `CalendarRef` parameter type already accept calendars). Confirm on Learn
before relying on it. Microsoft already recommends it over the classic functions, and it lifts the
need for a marked, gap free Gregorian Date table, which could change the sprint and period grain
advice in `powerbi-modeling`. Preview performance is not representative, so do not ship it until GA.
Try it on a throwaway copy, defining the calendar in Desktop rather than writing TMDL from a sample.

Source: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-time-intelligence
