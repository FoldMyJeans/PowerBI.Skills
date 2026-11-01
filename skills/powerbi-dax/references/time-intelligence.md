# Time intelligence: fair comparisons and what is still preview

`patterns.md` has the basic year to date and prior year measures. This file covers the partial
period trap, and where the newer calendar functions stand. The Date table itself is owned by the
`powerbi-modeling` skill.

## A partial period compared with a whole one

Say the data runs to 18 August. `Sales YTD` is fine, but `Sales PY` on the August row returns all of
last August, so the year over year number compares 18 days with 31 and shows a collapse that did not
happen. Months after August show a prior year value next to nothing. Nothing errors, and the row
looks like a business problem.

The fix is to limit the current selection to dates that have data, then shift only those. This is our
own form of the idea DAX Patterns uses (a helper flag on the Date table plus a hidden measure), it is
not their code, and it has not yet been run on a real model.

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

The IF blanks periods that have not started, so a chart stops at the last real date instead of
trailing into a future with prior year values only. If several prior period measures need it, a
function can hold the logic once, see `functions-and-calculation-groups.md`.

Source for the idea: https://www.daxpatterns.com/standard-time-related-calculations/

## Calendar based time intelligence: pilot only

Microsoft still labels this preview, behind the Enhanced DAX Time Intelligence option, even though
its page already recommends it over the classic functions. It lifts the requirements of a marked,
gap free Gregorian Date table, which could change the sprint and period grain advice in the
`powerbi-modeling` skill. Microsoft also says preview performance is not representative. Do not use it
in a model you ship until it is generally available. Try it on a throwaway copy if you want to learn
it, and define a calendar in Desktop rather than writing the TMDL from a sample.

Source: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-time-intelligence
