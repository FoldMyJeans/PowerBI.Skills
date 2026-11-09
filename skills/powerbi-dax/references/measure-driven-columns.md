# Measure driven columns and field parameters

Two ways to make a visual's columns or axis come from a calculation: a disconnected column header
table and a field parameter, both with the exact TMDL.

## The disconnected column header table

A table related to nothing, whose rows become the columns of a matrix.

```tmdl
table ServiceType_Columns
	column 'Service Type'
		summarizeBy: none
		isNameInferred
		sourceColumn: [Service Type]
		sortByColumn: SortOrder

	column SortOrder
		formatString: 0
		summarizeBy: sum
		isNameInferred
		sourceColumn: [SortOrder]

	partition ServiceType_Columns = calculated
		mode: import
		source =
				DATATABLE (
				    "Service Type", STRING,
				    "SortOrder", INTEGER,
				    {
				        {"Managed Services", 1},
				        {"Professional Services", 2},
				        {"Actual Internal", 3},
				        {"Maximum Capacity", 4}
				    }
				)
```

Easy to get wrong by hand:

- DATATABLE needs an explicit type per column (STRING, INTEGER). It does not infer them like a table
  constructor does.
- `isNameInferred` on both columns, because the names come from the DAX expression.
- `sortByColumn: SortOrder` on Service Type. Without it the matrix orders the columns alphabetically.

## The routing measure that fills the columns

The header table is filtered to one row per matrix column, so SELECTEDVALUE reads which column is
being drawn and SWITCH returns the matching number.

```dax
Matrix Value =
VAR Col = SELECTEDVALUE ( ServiceType_Columns[Service Type] )
VAR MSH = CALCULATE ( SUM ( 'fact_effort'[Effort (Hours)] ), 'fact_effort'[Service Type] = "Managed Services" )
VAR PSH = CALCULATE ( SUM ( 'fact_effort'[Effort (Hours)] ), 'fact_effort'[Service Type] = "Professional Services" )
VAR Cap = [Max Capacity Hours]
VAR ActualInternal = Cap - MSH - PSH
RETURN
    SWITCH (
        Col,
        "Managed Services", MSH,
        "Professional Services", PSH,
        "Actual Internal", ActualInternal,
        "Maximum Capacity", Cap,
        BLANK ()
    )
```

Actual Internal and Maximum Capacity are arithmetic with no Service Type value behind them, which no
amount of dragging fields onto the visual produces. SWITCH returns blank on no match anyway. Write
`BLANK ()` so the reader sees that an unmatched column is expected to come back empty.

## The coupling contract

Three sets of strings must agree, and nothing checks them:

1. The values in the DATATABLE.
2. The branch labels in the SWITCH.
3. The real values in `fact_effort[Service Type]`, for the branches that filter it.

A typo between 1 and 2 shows an empty column, which is visible. A typo between 2 and 3 is the
dangerous one. Misspell "Managed Services" in the CALCULATE and `MSH` is blank, but `ActualInternal`
is `Cap - MSH - PSH`, so those hours silently move into Actual Internal. The row still totals to
capacity, which is what makes it survive review. Any residual or balancing column absorbs mistakes
this way.

Put the contract in a comment next to the DATATABLE:

```dax
// These strings must match fact_effort[Service Type] exactly.
// A mismatch empties its own column and pushes the hours into Actual Internal,
// which still totals to capacity, so it will not look wrong.
DATATABLE ( "Service Type", STRING, ... )
```

## Field parameters

A field parameter lets the user pick which dimension a visual slices by. Desktop generates it from a
wizard. Written by hand, the metadata is the part that matters.

```tmdl
table 'Parameter - fact_effort'
	column 'Legend - Actual vs Estimated Efforts (Hour)'
		summarizeBy: none
		sourceColumn: [Value1]
		sortByColumn: 'Parameter Order'

		relatedColumnDetails
			groupByColumn: 'Parameter Fields'

	column 'Parameter Fields'
		isHidden
		summarizeBy: none
		sourceColumn: [Value2]
		sortByColumn: 'Parameter Order'

		extendedProperty ParameterMetadata =
				{
				  "version": 3,
				  "kind": 2
				}

	column 'Parameter Order'
		isHidden
		formatString: 0
		summarizeBy: sum
		sourceColumn: [Value3]

	partition 'Parameter - fact_effort' = calculated
		mode: import
		source =
				{
				    ("Activity", NAMEOF('dim_activity'[Activity]), 0),
				    ("Team", NAMEOF('dim_team'[Team]), 1)
				}
```

In order of how easy each part is to get wrong:

- The partition is a table constructor of three element tuples: display name, `NAMEOF(column)`,
  sort order. NAMEOF makes the second value a field reference. Write the column name in quotes and
  the parameter silently becomes a plain text table. The one argument NAMEOF is right here. The
  newer component and escaping arguments are in `functions-and-calculation-groups.md`.
- Value1 is the visible display name column, the one you drop on a visual and the user sees in a
  slicer.
- Value2 is the hidden field reference column, and it carries `extendedProperty ParameterMetadata`
  with `"version": 3` and `"kind": 2`. That block alone makes Power BI treat the table as a field
  parameter. Without it the table does nothing on a visual.
- `relatedColumnDetails` with `groupByColumn` on column 1 binds each display name to its field
  reference. Missing, the display name is just text next to an unrelated reference.
- Value3 is the hidden sort key, and BOTH column 1 and column 2 carry `sortByColumn` pointing at it.
  Setting only one is a common half done edit, and the order comes out alphabetical.

For hand editing TMDL safely, including reopening after a partition change, see
`powerbi-project-and-tools`.

## When to reach for each

- A field parameter when the user should choose the dimension. One visual replaces four.
- A disconnected header table when the columns are a fixed set of calculations, especially
  arithmetic with no column behind it.
- Neither when a plain column would do. Both add a table no relationship explains.
