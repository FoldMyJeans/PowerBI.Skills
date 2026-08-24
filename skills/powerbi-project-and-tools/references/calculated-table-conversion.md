# Converting an import table to a calculated table

The full method for flipping a table from an M partition to a DAX calculated partition by editing
TMDL, plus the two lineage traps that stop the model opening if you get them wrong.

This is the light way to kill refresh fan out. A derivative table (one that only reshapes or rolls
up tables already in the model) as an M partition re-runs its whole upstream pull chain on every
refresh. As a calculated table it computes in memory from data already loaded, with no extra
source calls, so each conversion removes a chain rather than a query.

Convert only derivative tables. A table that would otherwise pull from a source is not a
candidate. See the `powerbi-data-and-refresh` skill for how to count the fan out first.

## Why it fails if you just swap the partition

Swap the partition and reopen with the cached data still in place and Desktop rejects the whole
project on open:

```text
Changing the partition type from or to PartitionType.Calculated is not allowed
```

The error code is `PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC`. The trigger is the diff against
`.pbi\cache.abf`, not the TMDL. Power BI tries to morph the cached model into the new one, and
that specific change is not a legal in place edit.

The fix is to make Desktop build the model fresh from the TMDL instead of morphing the cache.
That is the same cold load path a fresh git clone takes, since `cache.abf` is git ignored and
absent on a clone.

## The procedure

1. Close Desktop. Back up the project folder, or confirm it is committed.
2. Edit the table's `.tmdl` file:
   - Change `partition <Table> = m` to `partition <Table> = calculated`.
   - Keep `mode: import`.
   - Replace the M `source =` with a DAX `source =` expression.
   - REMOVE the `queryGroup:` line. A calculated partition does not belong to a query group and
     leaving it there is invalid.
   - Give every column `isNameInferred` and `sourceColumn: [Name]` matching a column the DAX
     returns.
   - Keep the existing table and column `lineageTag` values so relationships, measures, and
     visuals stay bound to it.
3. Delete `.pbi\cache.abf`. Keep `localSettings.json`, it holds the publish target binding.
4. Reopen the pbip. With no cache, Desktop creates the database fresh from the TMDL, so the
   partition type is set rather than changed, and there is no error. The report opens empty.
5. Refresh to rebuild the data, validate the numbers against the old table, then publish.

## The column shape

```tmdl
table fact_effort
	lineageTag: 7b000001-0000-4000-8000-000000000001

	column Activity
		dataType: string
		lineageTag: 7b000001-0000-4000-8000-000000000002
		summarizeBy: none
		isNameInferred
		sourceColumn: [Activity]

		annotation SummarizationSetBy = Automatic

	column 'Effort (Hours)'
		dataType: double
		lineageTag: 7b000001-0000-4000-8000-000000000003
		summarizeBy: sum
		isNameInferred
		sourceColumn: [Effort (Hours)]

		annotation SummarizationSetBy = Automatic

	partition fact_effort = calculated
		mode: import
		source =
				SELECTCOLUMNS (
				    xform_workitem_union,
				    "Activity", IF ( TRUE (), xform_workitem_union[Activity] ),
				    "Effort (Hours)", xform_workitem_union[Effort (Hours)] + 0
				)
```

`isNameInferred` tells the engine the column name comes from the DAX rather than from a source
column name. `sourceColumn: [Name]` must match the name the DAX emits, exactly.

## Trap one: passthrough columns keep their source lineage

This is the one that wastes an afternoon.

When a calculated table column is a bare reference to another table's column, for example
`"Sprint", src[Sprint]` inside `SELECTCOLUMNS`, the engine keeps that column's lineage back to
the source column. It then will not accept your `sourceColumn: [Sprint]` declaration on the new
table, the declared column drops, and any relationship built on it fails to load:

```text
Relationship '...' uses an invalid column ID 300
```

error code `PFE_TM_RELATIONSHIP_END_COLUMN_INVALID`.

The fix is to make every passthrough column an expression, so it carries no lineage:

- Text and dates: wrap the reference, `IF ( TRUE (), src[Sprint] )`. Same value and type, but now
  it is a fresh computed column that matches your declaration.
- Numbers: `src[Effort] + 0` does the same job and is shorter.

Put a comment in the partition saying why, because the next person will otherwise "simplify" the
wrapper away and break the model:

```dax
// IF(TRUE(), col) keeps the value but breaks column lineage, so the engine creates
// fresh columns that match the declared sourceColumn [Name] entries
```

## Trap two: aggregation has to happen where row context still exists

If the table aggregates, you cannot just wrap the whole thing in `SELECTCOLUMNS`. Do the
aggregation in an inner `ADDCOLUMNS` over a `SUMMARIZE`, where the row context is intact and
context transition works, then re-emit every column in an outer `SELECTCOLUMNS`:

```dax
SELECTCOLUMNS (
    ADDCOLUMNS (
        SUMMARIZE ( fact_effort, fact_effort[Sprint], fact_effort[Owner] ),
        "@TotalEffort", CALCULATE ( SUM ( fact_effort[Effort (Hours)] ) ),
        "@MaxCapacity", CALCULATE ( MAX ( fact_effort[Planned Capacity (Hours)] ) )
    ),
    "Sprint", IF ( TRUE (), fact_effort[Sprint] ),
    "Owner",  IF ( TRUE (), fact_effort[Owner] ),
    "Total Effort (Hours)", [@TotalEffort],
    "Max Capacity (Hours)", [@MaxCapacity]
)
```

The inner columns are prefixed `@` by convention so it is obvious which are intermediate. The
outer layer does nothing except produce lineage free columns matching the declarations.

## What changes semantically when M becomes DAX

The rewrite is not value neutral. Two deltas to expect:

- Case sensitivity flips. M comparisons are case sensitive (`List.Contains`, `=` on text). DAX
  text comparison and `IN` are case insensitive by default. A membership test on mixed case
  keys, emails are the classic, can match more rows after the conversion, so a coverage
  percent ticks up. Validate against the old numbers and explain the delta rather than
  chasing a phantom bug.
- Null handling is yours to design. This cuts both ways. An unguarded M row expression, for
  example `#date([Year], [Month], 1)` on a row where those fields are null, fails the whole
  refresh with "cannot convert null to type Number". Rebuilding the table in DAX is also the
  natural moment to guard or exclude those rows, which makes the conversion a fix for this
  class of refresh crash, not just for fan out.

## What you are trading

Be honest about it. This moves cost from the data phase into the recalc phase, where the table is
rebuilt in full on every refresh. It wins when the source pull dominates, which is the usual
shape of a multi hour Pro refresh, and it is not free.

Microsoft's documented fix for fan out is a dataflow, which on Pro means Dataflow Gen1 with its
own orchestration problems. The Best Practice Analyzer also flags heavy use of calculated tables
as technical debt.

So after converting, go and clean up the recalc phase you just loaded, starting with auto
date/time. See the `powerbi-data-and-refresh` skill for the two phase cost model.

## If you would rather not touch TMDL

The GUI path works too. Create a New table in Desktop with the DAX, move relationships, measures,
and visuals onto it, then delete the old one. It is more clicking and it risks missing a visual
binding, but it needs no cache deletion and no lineage tricks.
