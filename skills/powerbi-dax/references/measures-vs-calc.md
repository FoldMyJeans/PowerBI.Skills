# Measures vs calculated columns vs calculated tables

Three things in DAX look similar and are not. Picking the wrong one is the most common way a
model gets slow and bloated. The short rule: default to a measure, compute columns upstream,
and use a calculated table only for something that re-derives from data already in the model.

## Measure

A measure is a calculation run at query time inside the current filter context. It stores no
data and adds nothing to the model file. It recomputes for every cell of every visual as the
user filters.

- Use it for anything that aggregates or reacts to slicing: sums, ratios, counts, time
  intelligence, ranking, running totals.
- A measure has no row it belongs to. It reads the filter context, not "this row".
- The cost is CPU at query time, not model size. This is the cheap option. Reach for it first.

## Calculated column

A calculated column is a DAX expression evaluated once per row during refresh and stored on
the table, like any other column.

- It runs in row context. It sees the current row and can reference other columns on it.
- It is stored, so it costs model size and refresh time. DAX calculated columns also do not
  compress as well in VertiPaq as columns that arrive with the data.
- Prefer computing the column upstream in M (Power Query) or at the source. Those columns
  compress better and do not recompute on every refresh. See
  `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.
- Use a calculated column only when the value must physically exist on the row (to group by it,
  relate on it, or slice on it) AND it needs model or row context that M cannot give. An
  example is a value pulled across a relationship with RELATED, or a rank within the row's
  group.

Rule of thumb: if you can compute it in M, do it in M. If you can express it as a measure, do
that instead. A calculated column is the last resort of the three.

## Calculated table

A calculated table is a table whose rows come from a DAX expression, evaluated on refresh.

- It is common and fine for a Date table (CALENDAR or CALENDARAUTO plus added columns), a small
  bridge or disconnected table, or a filtered copy for a specific need.
- It recomputes on every refresh and does not fold to any source. It is pure model compute.
- Size is not the test. Whether the table re-derives from data already in the model is the
  test. A derivative table that only reshapes, rolls up, or filters tables that are already
  loaded is a good calculated table at any size. The largest fact table in a model can be a
  calculated one on purpose, precisely so it stops re-running its source pulls.
- A table that would otherwise pull from a source is not a calculated table. Shape it in M and
  let it fold.
- A dimension built from a fact (DISTINCT over a fact column) is a legitimate and common
  shape. The values already sit in the model, so nothing is fetched twice.
- For the Date table specifically, build it once and mark it as a date table. See
  `powerbi-modeling`.

## Row context vs filter context, in plain terms

Two different contexts drive every DAX result.

- Filter context is the set of filters active right now: the row and column of a matrix, a
  slicer, a page filter, or a filter you passed to CALCULATE. Measures live here. A measure
  sees the current slice and aggregates over the rows that survive it.
- Row context is the current row while a calculation scans a table. A calculated column has a
  row context automatically (the row it is computing). Iterators like SUMX, AVERAGEX, and RANKX
  create a row context as they walk their table.
- Row context does NOT filter the model by itself. Being on a row does not restrict what a
  measure inside that row can see. That surprises people.

## Context transition, what CALCULATE does

CALCULATE takes the current row context and turns it into filter context. That is context
transition. It is the single most important idea in DAX.

- Inside an iterator, wrapping an expression in CALCULATE makes the current row become a filter
  on the whole model for that one evaluation.
- Every measure reference carries an implicit CALCULATE. So calling a measure from inside SUMX
  already applies context transition on each row. This is why a measure called row by row can
  give a different, usually correct, answer than the same raw expression.
- A filter argument in CALCULATE REPLACES any existing filter on that column, it does not add
  to it. Wrap it in KEEPFILTERS to make it intersect with what is already filtered instead.
  Leaving KEEPFILTERS out inside an iterator gives a wrong number rather than an error. Worked
  example in `virtual-relationships.md`.
- Practical effect: if a total does not equal the sum of the visible rows, context transition
  (or the lack of it) is usually why. Decide whether you want the measure evaluated per row and
  then combined, or evaluated once over the whole visible set.

Keep the wording simple when you explain it. CALCULATE says "take where I am right now and
treat it as a filter".

## Converting an import table into a calculated table

You can convert an existing imported (M) table into a calculated table by editing the TMDL, but only
if you clear the cached data first so Desktop builds the model fresh instead of morphing the loaded
one. Swap the partition and reopen with the cache still there and it fails on open with

```
PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC
```

The trigger is the diff against `.pbi\cache.abf`, not the TMDL. Close Desktop, edit the partition to
`= calculated` with a `source =` DAX expression, delete `.pbi\cache.abf`, reopen, then Refresh to
rebuild. The GUI path (New table, move relationships, delete the old one) also works. The full method
and the column lineage gotcha are in the `powerbi-project-and-tools` skill.

Do this only for derivative tables that roll up or reshape data already in the model. A calculated
table recomputes every refresh and does not fold, so it is the right tool to stop a derivative table
re-running its source pulls, not a way to avoid a real source pull.
