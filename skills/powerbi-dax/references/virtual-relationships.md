# Virtual relationships and composite keys

Joining two tables that have no physical relationship, and what to do when the source gives you no
surrogate key.

## TREATAS forms

Form A, TREATAS over `VALUES` of a dimension column, is in `patterns.md`. These come up next.

### B. Two columns at once

One TREATAS takes a table expression with both columns, then both target columns in the same order.

```dax
PS Estimate Hours =
CALCULATE (
    SUM ( fact_estimate_ps[Estimate of Effort] ),
    TREATAS (
        ALLSELECTED ( dim_work_item[Company], dim_work_item[Epic Number] ),
        fact_estimate_ps[Company],
        fact_estimate_ps[Epic Number]
    )
)
```

This matches a composite grain (company plus epic) with no key column holding both. For what is
visible on the row, use `SUMMARIZE ( dim_work_item, dim_work_item[Company], dim_work_item[Epic Number] )`
as the table expression (the same choice as form C).

Two separate TREATAS arguments are not the same. Each filters its own column and they combine as an
AND, so companies A and B with epics E1 and E2 also let (A, E2) through even when no selected row
holds that pair. It only bites when the target table holds such a pair, which is why it survives
review. On one real model, two team and service pairs returned 1,635 hours as pairs and 6,405 hours as
two separate arguments, nearly four times as much, with no error. EVALUATE both forms side by side in
DAX query view before you trust either.

### C. VALUES or ALLSELECTED inside TREATAS

This choice is the whole difference between "the estimate for this row" and "the estimate for the
whole page".

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

VALUES for a numerator that walks the rows of a visual. ALLSELECTED for a denominator that holds the
user's full selection while the numerator moves. The pair usually sits a few lines apart and is easy
to mix up later, so name them so the difference is visible.

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

The VAR lets the same set feed a filter and a residual calculation in one measure without being typed
twice.

## Fact to fact, at different grains

TREATAS can join two facts at different grains, for example a work item grain effort table against a
company and month grain estimate table. Try shared dimensions first (the three many to many cases are
in `powerbi-modeling`). TREATAS is the route when no shared dimension can be built. A physical
relationship would need a synthetic key stored on both tables. The virtual one costs query time
instead of model size and adds no ambiguous path to the model.

## Building a composite key in memory, then joining with it

The estimate table is keyed on a company plus month plus year string. The effort table has a sprint,
not a month. The key is built at query time and used as the relationship.

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

1. GENERATE crosses every sprint in context with every company in context.
2. The scalar CALCULATE turns a sprint into its start date, then a month and a year. This is the
   grain change.
3. ADDCOLUMNS and SELECTCOLUMNS materialize a one column table of key strings.
4. TREATAS applies it as a filter on the estimate table's key column.

## KEEPFILTERS, or a silently wrong number

A CALCULATE predicate on a column REPLACES any existing filter on that column, including the user's
slicer. Owners the user excluded are quietly back in the numbers, and nothing looks broken.

```dax
CALCULATE (
    SUM ( 'fact_effort'[Effort (Hours)] ),
    KEEPFILTERS ( 'fact_effort'[Owner] = ThisOwner )
)
```

KEEPFILTERS makes the predicate intersect with the existing filter. Leaving it out gives a plausible
wrong number, so check this one by hand.

## LOOKUPVALUE for a column across a non relationship

RELATED needs a relationship. When there is none and the value must sit on the row, use LOOKUPVALUE.

```dax
Planned Capacity (Hours) =
LOOKUPVALUE (
    fact_planning[Planned Capacity (Hours)],
    fact_planning[Sprint], fact_effort[Sprint],
    fact_planning[Team Member], fact_effort[Owner]
)
```

Pairs after the first argument are (search column, search value), and they intersect. Only do this
when the value has to be groupable or sliceable.

## Composite string keys when the source has no surrogate key

Build integer surrogate keys upstream when you control the source (`powerbi-modeling`). A ticketing
API or a hand maintained workbook gives you none. When the key has to be a concatenated string:

- Let a duplicate fail the refresh, and resist `Table.Distinct`. The rule and its one exception are
  in `relationships.md` in the `powerbi-modeling` skill.
- TRIM every part of the key on both sides. A trailing space from a hand maintained sheet is
  invisible in the data view and produces a silent non match.

  ```dax
  CompanyMonthYearKey =
  TRIM ( fact_estimate_company_month[Company] ) & " - "
      & TRIM ( fact_estimate_company_month[Month] ) & " - "
      & FORMAT ( fact_estimate_company_month[Year], "0000" )
  ```

- Format numbers explicitly. `FORMAT ( [Year], "0000" )` gives the same string on both sides. An
  implicit integer to text conversion can differ between a DAX column and an M step or a locale.

An integer surrogate key is still better whenever the source can produce one.
