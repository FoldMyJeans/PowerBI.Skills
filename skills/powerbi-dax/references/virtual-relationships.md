# Virtual relationships and composite keys

How to join two tables that have no physical relationship, and what to do when the source
gives you no surrogate key to join on.

## TREATAS, five forms

`patterns.md` shows the basic form, TREATAS over `VALUES` of a dimension column.
That is form A and it is not repeated here. These are the four forms that come up next.

### B. Two columns at once

Two TREATAS arguments in one CALCULATE intersect. Both must match, which is an AND, not an OR.

```dax
PS Estimate Hours =
CALCULATE (
    SUM ( fact_estimate_ps[Estimate of Effort] ),
    TREATAS ( ALLSELECTED ( dim_work_item[Company] ), fact_estimate_ps[Company] ),
    TREATAS ( ALLSELECTED ( dim_work_item[Epic Number] ), fact_estimate_ps[Epic Number] )
)
```

This is how you match on a composite grain (company plus epic) with no key column that holds
both.

### C. VALUES or ALLSELECTED inside TREATAS

This one choice is the whole difference between "the estimate for what is on this row" and
"the estimate for the whole page".

```dax
Estimate (Row) =
CALCULATE (
    SUM ( fact_estimate_ps[Estimate of Effort] ),
    TREATAS ( VALUES ( dim_work_item[Company] ), fact_estimate_ps[Company] )
)

Estimate (Page) =
CALCULATE (
    SUM ( fact_estimate_ps[Estimate of Effort] ),
    TREATAS ( ALLSELECTED ( dim_work_item[Company] ), fact_estimate_ps[Company] )
)
```

Use VALUES for a numerator that walks the rows of a visual. Use ALLSELECTED for a denominator
that must hold the user's full selection while the numerator moves. A model that needs both
usually defines them within a few lines of each other, and the pair is easy to mix up later,
so name them so the difference is visible at a glance.

### D. From a literal one element table

Inside an iterator you often have a scalar, not a table. Wrap it in braces.

```dax
CALCULATE (
    SUM ( fact_capacity[Hours] ),
    TREATAS ( { ThisOwner }, fact_capacity[Owner] )
)
```

### E. From a constant list held in a VAR

```dax
VAR NonAdminCats = { "Pre-Sale", "Professional Services", "Managed Services" }
RETURN
CALCULATE (
    SUM ( fact_effort[Effort (Hours)] ),
    TREATAS ( NonAdminCats, dim_epic[Internal Category] )
)
```

Keeping the list in a VAR means the same set can feed a filter and a residual calculation in
the same measure without being typed twice.

## Fact to fact, at different grains

TREATAS is usually taught as dimension to fact. It is also the only clean way to join two facts
that sit at different grains, for example a work item grain effort table against a company and
month grain estimate table.

A physical relationship would need a shared key column, which means inventing a synthetic key
and storing it on both tables. The virtual relationship needs neither. It costs query time
instead of model size, and it does not add an ambiguous path to the model diagram. When the
two facts have no natural key in common, prefer the virtual join.

## Building a composite key in memory, then joining with it

This is the advanced form. The estimate table is keyed on a company plus month plus year
string. The effort table has a sprint, not a month. The key is built at query time and then
used as the relationship.

```dax
Estimated Effort (Chart Safe) =
VAR SprintsInContext = VALUES ( 'fact_effort'[Sprint] )
VAR CompaniesInContext = VALUES ( 'fact_effort'[Company] )
VAR SprintMonthKeys =
    GENERATE (
        SprintsInContext,
        VAR ThisSprint = 'fact_effort'[Sprint]
        VAR SprintStart =
            CALCULATE ( MIN ( 'dim_sprint'[Sprint Start Date] ), 'dim_sprint'[Sprint Name] = ThisSprint )
        VAR MonthName = FORMAT ( SprintStart, "MMMM" )
        VAR YearTxt = FORMAT ( SprintStart, "yyyy" )
        RETURN
            ADDCOLUMNS ( CompaniesInContext, "EstKey", 'fact_effort'[Company] & " - " & MonthName & " - " & YearTxt )
    )
VAR KeyList = SELECTCOLUMNS ( SprintMonthKeys, "EstKey", [EstKey] )
RETURN
    CALCULATE (
        SUM ( fact_estimate_company_month[Estimated Effort (Hour)] ),
        TREATAS ( KeyList, fact_estimate_company_month[CompanyMonthYearKey] ),
        REMOVEFILTERS ( 'fact_effort'[Activity] )
    )
```

Read it in four steps.

1. GENERATE crosses every sprint in context with every company in context. That gives the full
   grid of pairs the visual is asking about.
2. The scalar CALCULATE inside translates a sprint into its start date, which becomes a month
   and a year. This is the grain change.
3. ADDCOLUMNS and SELECTCOLUMNS materialize a one column table of key strings.
4. TREATAS applies that table as a filter on the estimate table's key column.

The result is a relationship that exists only for the duration of one query.

## KEEPFILTERS, or a silently wrong number

A CALCULATE predicate on a column REPLACES any existing filter on that column. It does not add
to it. So a predicate on `[Owner]` discards whatever was already filtering Owner, which
includes the user's slicer selection. The rows keep moving, so nothing looks broken, but owners
the user excluded are quietly back in the numbers.

```dax
CALCULATE (
    SUM ( 'fact_effort'[Effort (Hours)] ),
    KEEPFILTERS ( 'fact_effort'[Owner] = ThisOwner )
)
```

KEEPFILTERS makes the predicate intersect with what is already filtered instead of replacing
it. Nothing errors when you leave it out. You get a wrong number that looks plausible, which
is why this one is worth checking by hand.

## LOOKUPVALUE for a column across a non relationship

`measures-vs-calc.md` cites RELATED as a reason a calculated column earns its
place. RELATED needs a relationship to traverse. When there is none and the value must sit
physically on the row, LOOKUPVALUE is the answer.

```dax
Planned Capacity (Hours) =
LOOKUPVALUE (
    fact_planning[Planned Capacity (Hours)],
    fact_planning[Sprint], fact_effort[Sprint],
    fact_planning[Team Member], fact_effort[Owner]
)
```

Pairs of arguments after the first are (search column, search value), and they intersect. The
usual calculated column caution still applies, so only do this when the value has to be
groupable or sliceable.

## Composite string keys when the source has no surrogate key

`powerbi-modeling` says to build surrogate integer keys upstream, which is right when you
control the source. A ticketing API or a workbook a human maintains gives you none. When the
key has to be a concatenated string, three things keep it from breaking.

- Let the duplicate fail the refresh. The one side of a relationship enforces uniqueness, so a
  duplicate key stops the refresh with a clear error. That is the behaviour you want, because
  the alternative is a relationship that quietly fans out and doubles your numbers.

  Resist the urge to "fix" it upstream with `Table.Distinct`. That silently keeps one arbitrary
  row per key and throws the rest away, so the refresh goes green while the data goes wrong.

  ```m
  // Only when you have confirmed the duplicates are byte identical rows, for example a source
  // that returns the same record twice. Then losing one costs nothing.
  #"Removed Duplicates" = Table.Distinct(Source, {"Task Number"})
  ```

  If the duplicates are not identical, the key is wrong, not the data. Widen it until it is
  unique, or take the grain question back to whoever owns the source.

- TRIM every part of the key on both sides. A trailing space from a hand maintained sheet is
  invisible in the data view and produces a silent non match.

  ```dax
  CompanyMonthYearKey = TRIM ( [Company] ) & " - " & TRIM ( [Month] ) & " - " & FORMAT ( [Year], "0000" )
  ```

- Format numbers explicitly. `FORMAT ( [Year], "0000" )` guarantees the same string on both
  sides. An implicit integer to text conversion can differ between a DAX column and an M step
  or a locale.

This is a fallback. An integer surrogate key is still better, so use one whenever the source
can produce it.
