# Measure driven columns and field parameters

How to make a visual's columns or axis come from a calculation instead of from a table's
columns. Two techniques, a disconnected column header table and a field parameter, both with
the exact TMDL.

## The disconnected column header table

A table that is neither a fact nor a dimension, related to nothing, whose rows become the
columns of a matrix. It exists only to give the matrix something to put on its column axis.

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

Three details are easy to get wrong by hand.

- DATATABLE needs an explicit type per column, STRING and INTEGER here. It does not infer them
  the way a table constructor does.
- `isNameInferred` on both columns, because the names come from the DAX expression rather than
  from a source query.
- `sortByColumn: SortOrder` on the Service Type column. Without it the matrix orders the
  columns alphabetically, which is never the order the business reads them in.

## The routing measure that fills the columns

The header table is filtered to one row per matrix column, so SELECTEDVALUE reads which column
is being drawn and SWITCH returns the matching number.

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

The point worth making: Actual Internal and Maximum Capacity are arithmetic that exists
nowhere in the data. There is no Service Type value called "Actual Internal". This is how you
build a matrix whose columns are a calculation rather than a field, which no amount of
dragging fields onto the visual will produce.

SWITCH returns blank on no match whether or not you write `BLANK ()`, so the default is there
for the reader, not the engine. Write it anyway: it says out loud that an unmatched column is
expected to come back empty, which is the behaviour the next section depends on.

## The coupling contract

Three sets of strings have to agree here, and nothing checks them:

1. The values in the DATATABLE.
2. The branch labels in the SWITCH.
3. The real values in `fact_effort[Service Type]`, for the branches that filter it.

A typo between 1 and 2 shows an empty column, which is annoying but visible. A typo between 2
and 3 is the dangerous one, and this example shows why. Misspell "Managed Services" in the
CALCULATE and `MSH` comes back blank, so the column reads empty. But `ActualInternal` is
`Cap - MSH - PSH`, so those missing hours do not vanish, they silently move into Actual
Internal. Nothing errors, and the row still totals to capacity, which is exactly what makes it
survive review.

Any residual or balancing column has this property. It absorbs your mistakes and keeps the
totals looking right.

Put the contract in a comment next to the DATATABLE, where the strings are:

```dax
// These strings must match fact_effort[Service Type] exactly.
// A mismatch empties its own column and pushes the hours into Actual Internal,
// which still totals to capacity, so it will not look wrong.
DATATABLE ( "Service Type", STRING, ... )
```

## Field parameters

A field parameter lets the user pick which dimension a visual slices by. It is a calculated
table with a very specific shape, and Power BI Desktop generates it from a wizard. Written by
hand, the metadata block is the part that matters.

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

In order of how easy each part is to get wrong.

- The partition is a table constructor of three element tuples: display name, `NAMEOF(column)`,
  sort order. NAMEOF is what makes the second value a field reference instead of a string. Write
  the column name in quotes and the parameter silently becomes a plain text table.
- Value1 is the visible display name column. This is the one you drop on a visual and the one
  the user sees in a slicer.
- Value2 is the hidden field reference column, and it carries `extendedProperty
  ParameterMetadata` with `"version": 3` and `"kind": 2`. That block alone is what makes Power
  BI treat the table as a field parameter. Without it you get a three column calculated table
  that does nothing at all when you put it on a visual.
- `relatedColumnDetails` with `groupByColumn` on column 1 binds each display name to its field
  reference. Missing, the display name is just text next to an unrelated reference.
- Value3 is the sort key, hidden, and BOTH column 1 and column 2 carry `sortByColumn` pointing
  at it. One of the two is a common half done edit, and the order comes out alphabetical.

For hand editing TMDL safely, including reopening the project after a partition change, see
the `powerbi-project-and-tools` skill.

## When to reach for each

- A field parameter when the user should choose the dimension. One visual replaces four, and
  the slicer is the whole interface.
- A disconnected header table when the columns are a fixed set of calculations, especially when
  some of them are arithmetic that has no column behind it.
- Neither when a plain column would do. Both of these add a table that no relationship
  explains, and the next person has to work out why it is there.
