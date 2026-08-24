# Star schema

The star schema is the target shape for a Power BI model. It is a mature dimensional modeling
approach (Ralph Kimball) that the Power BI engine is built around. Get the shape right and the
rest of the model, the relationships, the measures, and the report, all get easier. Names here
are placeholders. Use `ABC Company` and generic column names in anything shared, not real ones.

## Dimensions vs facts

Almost every model table is either a dimension or a fact. Decide which before you do anything
else. A few tables are neither, and that is fine when it is deliberate, see "The third role"
below.

- A dimension table describes a business entity: the things you filter and group by. Product,
  Customer, Store, Employee, and Date are dimensions. A dimension has one key column that
  uniquely identifies a row, plus descriptive columns (name, category, color, region) that
  people slice and group on.
- A fact table stores events or observations: the things you measure. A sale, an order line, a
  stock balance, a ticket. A fact holds the dimension key columns that point at the dimensions,
  plus the numeric columns you aggregate (quantity, amount, cost).

Dimensions filter and group. Facts summarize. A visual picks dimension columns for its axis and
legend, then sums or counts fact columns. Build the model to match that split. Do not mix the
two types in one table. The one narrow exception is a degenerate dimension, an attribute like an
order number that lives on the fact purely for filtering.

## The third role: tables that are neither

Some tables are not dimensions and not facts. They exist to feed the model itself rather than
to be sliced or summed. This is normal. Four kinds turn up in practice.

**Config table.** Holds parameters or weights that DAX reads, and nothing else. Hidden, and
related to nothing. The production example is a customer allocation table of `Customer` and
`Weight`, read only by a calculated table's DAX to prorate shared effort across clients. No
visual ever touches it. Prefix it `cfg_` so the name says what it is.

**Disconnected column header table.** Its rows become the columns of a matrix, and one routing
measure fills the cells. It is related to nothing on purpose, because the matrix groups on its
rows and the measure decides what each cell means. For the `DATATABLE` TMDL and the
`SELECTEDVALUE` plus `SWITCH` measure that drives it, see the `powerbi-dax` skill.

**Field parameter table.** Lets a report user swap which field a visual uses, from a slicer.
Power BI generates it, and it is disconnected too. See the `powerbi-dax` skill for the TMDL.

**Staging or transform table left loaded in the model.** Sometimes legitimate, when several
tables build on one reshape and materializing it once is cheaper than repeating it. Often it is
debt. Say it plainly: if no DAX reads it and no visual uses it, it is costing refresh time and
model size for nothing. Disable load or delete it.

Rule of thumb: these tables are fine, but each one needs a reason you can say in one sentence.
"It holds the weights the allocation calc reads" is a reason. "It was there when I got here" is
not. A disconnected table nobody can explain is usually a leftover from an experiment, and the
cheapest way to find out is to disable load and see what breaks.

Hide all of them. None of these belong in a report author's field list.

## Several fact tables is normal

A star with one fact is the teaching example, not the limit. A real operational model usually
carries several facts at different grains sharing one set of conformed dimensions. Eight fact
tables against a shared dimension core is a correct shape, not a sign the model grew wrong.

The rule that keeps it a star: facts do not relate to each other directly. They relate through
the dimensions they share, so a slicer on customer or period filters all of them at once.
Where no shared dimension exists, do not wire fact to fact just to make one
number appear. Use a virtual relationship at the measure layer instead (`TREATAS`), see the
`powerbi-dax` skill. It gives you the filter without changing the model's shape.

## Define the grain first

The grain is what one row of a fact table means. Write it in one plain sentence before you add
any column. "One row per sales order line." "One row per account per month end." "One row per
ticket state change."

Two rules follow from the grain:
- Every row sits at the same grain. Do not park an order total row next to order line rows in
  the same table.
- Every column must make sense at that grain. If a column only makes sense at a different level,
  it belongs in a different table.

If two sets of numbers have different grains, put them in two fact tables and let them share the
dimensions. A daily sales fact and a monthly budget fact do not go in one table. They each relate
to the Date and Product dimensions at their own grain.

## Why a star suits Power BI and VertiPaq

Power BI stores the model in VertiPaq, an in memory columnar engine that compresses each column
on its own. A star schema plays to that:

- Low repetition compresses well. A fact table of narrow integer keys plus numbers compresses
  hard. Descriptive text sits once in the dimension, not repeated on every fact row.
- Relationships match the engine. A one to many relationship from a dimension to a fact is
  exactly the filter path a visual needs. The "one" side (dimension) filters the "many" side
  (fact).
- Fewer, simpler paths. Filters travel a short, predictable route from dimension to fact, so
  queries are faster and results are easier to reason about.

Microsoft guidance is explicit: model as a star schema for performance and usability. See
https://learn.microsoft.com/en-us/power-bi/guidance/star-schema

## Star vs snowflake

A snowflake splits one dimension across several normalized tables (Product to Subcategory to
Category, as three tables). It is not wrong, but for Power BI prefer the flatter star. Collapse
the snowflake into a single dimension table with Category and Subcategory as columns on the
Product table.

Why flatter is usually better here:
- Fewer tables to load and fewer relationship hops for a filter to cross.
- The field list is cleaner, so report authors are not hunting through one column tables.
- You can build a Category to Subcategory to Product hierarchy inside a single table. You cannot
  build a hierarchy that spans several tables.

Keep a snowflake only when a dimension is genuinely huge and the normalized split saves real
size, or when the source already models it that way and flattening is expensive. That is the
exception, not the default.

## Why one flat table is usually worse than a star

The opposite mistake is dumping everything into one wide table. It feels simple, but it is
usually worse than a star:

- It repeats every dimension's text on every fact row, which compresses worse and grows the
  model.
- It cannot filter two different facts from one shared dimension. With a star, one Date table
  filters sales and budget together. One flat table cannot.
- Slicers get messy. The distinct values of a repeated column are scattered across millions of
  rows instead of sitting in a small clean dimension.
- Any change to a dimension attribute has to be rewritten across every row.

A star is a little more work up front and pays off in size, speed, and clarity. See the SQLBI
"star schema or single table" article:
https://www.sqlbi.com/articles/power-bi-star-schema-or-single-table/

## The three fact types

Kimball describes three kinds of fact table. Knowing which one you are building keeps the grain
honest.

1. Transaction fact. One row per event, at the moment it happens. A sales line, a payment, a
   ticket created. This is the most common type and the default you should reach for.
2. Periodic snapshot fact. One row per entity per regular time slot, capturing a state. An
   account balance at each month end, headcount per department per week. You take a picture at
   set intervals, whether or not anything changed.
3. Accumulating snapshot fact. One row per process instance, with several date columns for the
   milestones, updated in place as the instance moves along. An order with order date, ship
   date, and delivery date on one row, filled in as it progresses.

Do not blend types. A transaction fact and a monthly snapshot are two tables sharing the same
dimensions.

## Worked example: Sales

Say ABC Company wants to analyze sales. The raw export is one wide sheet with order line rows
and repeated customer and product text. Reshape it into a star.

Grain: one row per sales order line.

Fact table, `Sales`:
- Keys: `DateKey`, `ProductKey`, `CustomerKey` (whole number keys pointing at the dimensions).
- Numbers: `Quantity`, `UnitPrice`, `SalesAmount`, `Cost`.
- Degenerate dimension: `SalesOrderNumber` kept on the fact for filtering.

Dimension `Date`: one row per day, with `DateKey`, `Date`, `Year`, `Quarter`, `Month`,
`MonthNumber`, `DayName`. Marked as the model's date table.

Dimension `Product`: one row per product, with `ProductKey`, `ProductName`, `Category`,
`Subcategory`, `Color`. Category and Subcategory are folded in here, not snowflaked out.

Dimension `Customer`: one row per customer, with `CustomerKey`, `CustomerName`, `Segment`,
`City`, `Country`.

Relationships: one to many from each dimension into `Sales`, single cross filter direction, on
the key columns. Measures like `Total Sales = SUM ( Sales[SalesAmount] )` live in a `_Measures`
table, not on `Sales`. See `relationships.md` and `naming-and-measures.md`.

The result: three small dimensions, one narrow fact, clean one to many relationships, and a Date
table that filters everything. That is a star, and it is the shape the rest of the skills assume
you have built.

## Quick checklist

- Is every table clearly a dimension or a fact, with no mixing (bar a degenerate dimension).
- Is the grain of each fact written in one sentence, and does every row hold to it.
- Are dimensions flattened into a star, not left as a snowflake, unless there is a real reason.
- Is descriptive text living once in a dimension, not repeated across a wide flat table.
- Does each fact table hold a single fact type, not a blend of transaction and snapshot rows.
- Can you say in one sentence why each disconnected table exists, and is it hidden.
