# Star schema

The target shape for a Power BI model: dimensions that filter and group, facts that hold keys and
the numbers you aggregate, one to many from each dimension into each fact. Microsoft's guidance:
https://learn.microsoft.com/en-us/power-bi/guidance/star-schema. Names here are placeholders. Use
`ABC Company` and generic column names in anything shared.

Decide for every table whether it is a dimension or a fact, and do not mix the two. The narrow
exception is a degenerate dimension, an attribute like an order number kept on the fact purely for
filtering.

## Tables that are neither

Some tables feed the model itself rather than being sliced or summed. That is fine when it is
deliberate.

- **Config table.** Parameters or weights that only DAX reads. Hidden, related to nothing. Example:
  a customer allocation table of `Customer` and `Weight`, read only by a calculated table's DAX to
  prorate shared effort across clients. Prefix it `cfg_`.
- **Disconnected column header table.** Its rows become the columns of a matrix, and one routing
  measure fills the cells. Related to nothing on purpose. The `DATATABLE` TMDL and the
  `SELECTEDVALUE` plus `SWITCH` measure are in the `powerbi-dax` skill.
- **Field parameter table.** Lets a report user swap the field a visual uses from a slicer. Power BI
  generates it, disconnected. TMDL in the `powerbi-dax` skill.
- **Staging or transform table left loaded.** Legitimate when several tables build on one reshape
  and materializing it once is cheaper. Often it is debt: if no DAX reads it and no visual uses it,
  it costs refresh time and model size for nothing. Disable load or delete it.

Each one needs a reason you can say in one sentence. "It holds the weights the allocation calc
reads" is a reason. "It was there when I got here" is not. To find out whether an unexplained one
matters, disable load and see what breaks. Hide all of them.

## Several fact tables is normal

A real operational model often carries several facts at different grains sharing one set of
conformed dimensions. Eight fact tables against a shared dimension core is a correct shape.

Facts do not relate to each other directly. They relate through shared dimensions, so a slicer on
customer or period filters all of them. Where no shared dimension exists, do not wire fact to fact
to make one number appear. Use a virtual relationship in a measure (`TREATAS`, see the
`powerbi-dax` skill), which leaves the model's shape alone.

## Define the grain first

Write what one row of a fact means in one sentence before adding any column. "One row per sales
order line." "One row per account per month end." "One row per ticket state change."

- Every row sits at that grain. No order total row next to order line rows.
- Every column makes sense at that grain, or it belongs in another table.
- Two grains, two fact tables. A daily sales fact and a monthly budget fact share the Date and
  Product dimensions, each at its own grain.

## Star vs snowflake vs one flat table

Flatten a snowflake (Product to Subcategory to Category as three tables) into one dimension with
Category and Subcategory as columns. A hierarchy can only be built inside one table, never across
several, and fewer hops filter faster. Keep a snowflake only when a dimension is huge and the split
saves real size, or flattening is expensive.

One wide flat table is usually worse than a star. It repeats dimension text on every row
(compresses worse), and it cannot filter two facts from one shared dimension, which a single Date
table filtering sales and budget together does. SQLBI's comparison:
https://www.sqlbi.com/articles/power-bi-star-schema-or-single-table/

## The three fact types

Knowing which one you are building keeps the grain honest. Do not blend them in one table.

1. Transaction. One row per event (a sales line, a payment, a ticket created). The default.
2. Periodic snapshot. One row per entity per regular time slot, capturing a state (a balance at
   each month end, headcount per department per week), whether or not anything changed.
3. Accumulating snapshot. One row per process instance, with a date column per milestone, updated
   in place (an order with order, ship, and delivery dates).

## Worked example: Sales

ABC Company's raw export is one wide sheet of order lines with repeated customer and product text.
The star, drawn in this skill's `SKILL.md`:

- Grain: one row per sales order line.
- Fact `Sales`: keys `DateKey`, `ProductKey`, `CustomerKey` (whole numbers), numbers `Quantity`,
  `UnitPrice`, `SalesAmount`, `Cost`, degenerate dimension `SalesOrderNumber`.
- `Date`: one row per day, `DateKey`, `Date`, `Year`, `Quarter`, `Month`, `MonthNumber`, `DayName`.
  Marked as the date table.
- `Product`: one row per product, `ProductKey`, `ProductName`, `Category`, `Subcategory`, `Color`.
  Category and Subcategory folded in, not snowflaked out.
- `Customer`: one row per customer, `CustomerKey`, `CustomerName`, `Segment`, `City`, `Country`.
- Relationships: one to many from each dimension into `Sales`, single direction, on the keys.
  `Total Sales = SUM ( Sales[SalesAmount] )` lives in `_Measures`, not on `Sales`. See
  `relationships.md` and `naming-and-measures.md`.

This is the shape the other skills assume you have built.

## Quick checklist

- Every table is a dimension or a fact, with no mixing (bar a degenerate dimension).
- Each fact's grain is written in one sentence, and every row holds to it.
- Dimensions are flattened into a star unless there is a real reason.
- Descriptive text lives once in a dimension, not repeated across a wide flat table.
- Each fact table holds a single fact type.
- Every disconnected table has a one sentence reason, and is hidden.
