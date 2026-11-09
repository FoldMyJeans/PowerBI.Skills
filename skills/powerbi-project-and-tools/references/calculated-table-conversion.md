# Converting an import table to a calculated table

Flipping a table from an M partition to a DAX calculated partition by editing TMDL, and the two
lineage traps that stop the model opening.

Why: a derivative table (one that only reshapes or rolls up tables already in the model) as an M
partition re-runs its whole upstream pull chain on every refresh. As a calculated table it computes
from data already loaded, so each conversion removes a chain rather than a query. Convert only
derivative tables. See the `powerbi-data-and-refresh` skill for how to count the fan out first.

## Why it fails if you just swap the partition

Swap the partition and reopen with the cache in place, and Desktop rejects the whole project:

```text
Changing the partition type from or to PartitionType.Calculated is not allowed
```

The error code is `PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC`. The trigger is the diff against
`.pbi\cache.abf`, not the TMDL. Power BI tries to morph the cached model, and that change is not a
legal in place edit. With no cache, Desktop builds fresh from the TMDL, the same cold load a fresh
git clone takes.

## The procedure

1. Close Desktop. Back up the project folder, or confirm it is committed.
2. Edit the table's `.tmdl` file:
   - Change `partition <Table> = m` to `partition <Table> = calculated`.
   - Keep `mode: import`.
   - Replace the M `source =` with a DAX `source =` expression.
   - REMOVE the `queryGroup:` line. On a calculated partition it is invalid.
   - Give every column `isNameInferred` and `sourceColumn: [Name]` matching a column the DAX
     returns.
   - Keep the existing table and column `lineageTag` values so relationships, measures, and
     visuals stay bound to it.
3. Delete `.pbi\cache.abf`. Keep `localSettings.json`, it holds the publish target binding.
4. Reopen the pbip. The partition type is now set rather than changed, so there is no error. The
   report opens empty.
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

`isNameInferred` tells the engine the column name comes from the DAX. `sourceColumn: [Name]` must
match the name the DAX emits, exactly.

## Trap one: passthrough columns keep their source lineage

When a calculated table column is a bare reference to another table's column, for example
`"Sprint", src[Sprint]` inside `SELECTCOLUMNS`, the engine keeps that column's lineage back to
the source column. It then will not accept your `sourceColumn: [Sprint]` declaration on the new
table, the declared column drops, and any relationship built on it fails to load:

```text
Relationship '...' uses an invalid column ID 300
```

error code `PFE_TM_RELATIONSHIP_END_COLUMN_INVALID`.

The fix is to make every passthrough column an expression, so it carries no lineage:

- Text and dates: `IF ( TRUE (), src[Sprint] )`. Same value and type, but a fresh computed column.
- Numbers: `src[Effort] + 0` does the same job and is shorter.

Comment why in the partition, or the next person "simplifies" the wrapper away and breaks the model:

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

The `@` prefix marks intermediate columns. The outer layer only produces lineage free columns
matching the declarations.

## What changes semantically when M becomes DAX

- Case sensitivity flips. M comparisons are case sensitive (`List.Contains`, `=` on text). DAX
  text comparison and `IN` are case insensitive. A membership test on mixed case keys (emails are
  the classic) can match more rows, so a coverage percent ticks up. Explain the delta rather than
  chasing a phantom bug.
- Null handling is yours to design. An unguarded M row expression, for example
  `#date([Year], [Month], 1)` on a row where those fields are null, fails the whole refresh with
  "cannot convert null to type Number". Guard or exclude those rows in the DAX, and the conversion
  fixes that refresh crash too.

## What you are trading

Cost moves from the data phase into the recalc phase, where the table is rebuilt in full on every
refresh. It wins when the source pull dominates, the usual shape of a multi hour Pro refresh.
Microsoft's documented fix for fan out is a dataflow, which on Pro means Dataflow Gen1 with its own
orchestration problems. The Best Practice Analyzer flags heavy use of calculated tables as
technical debt. After converting, clean up the recalc phase, starting with auto date/time. See the
`powerbi-data-and-refresh` skill for the two phase cost model.

## The GUI route

Create a New table in Desktop with the DAX, move relationships, measures, and visuals onto it, then
delete the old one. More clicking and a risk of missing a visual binding, but no cache deletion and
no lineage tricks.
