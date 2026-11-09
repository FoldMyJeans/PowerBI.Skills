# Measures vs calculated columns vs calculated tables

Default to a measure, compute columns upstream in M, and use a calculated table only for something
that re-derives from data already in the model.

## Measure

Runs at query time in the current filter context, stores nothing, adds nothing to model size. Use
it for anything that aggregates or reacts to slicing. The cost is CPU at query time.

## Calculated column

Evaluated once per row during refresh, in row context, and stored.

- It costs model size and refresh time, and compresses worse in VertiPaq than a column that
  arrives with the data. A column computed in M or at the source compresses better and does not
  recompute every refresh (`pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill).
- It earns its place only when the value must physically sit on the row (to group, relate, or
  slice on it) AND it needs model or row context M cannot give, such as RELATED across a
  relationship or a rank within the row's group.
- A sort column cannot read the column it sorts. A calculated `State Order` computed from `State`,
  set as the `sortByColumn` of `State`, failed the refresh with "A circular dependency was
  detected". Repeat the logic from the source columns, or build the order upstream in M.
- Stored is the default. The April 2026 preview column property Expression Context, set to User
  Context, makes a column that is not stored and runs at query time, so it costs speed instead.

## Calculated table

Rows come from a DAX expression evaluated on refresh. It recomputes every refresh and does not fold.

- Size is not the test. Whether the table re-derives from data already in the model is the test. A
  table that only reshapes, rolls up, or filters loaded tables is a good calculated table at any
  size. The largest fact in a model can be calculated on purpose, so it stops re-running its source
  pulls.
- A table that would otherwise pull from a source is not a calculated table. Shape it in M and let
  it fold.
- A dimension built from a fact (DISTINCT over a fact column) is legitimate. Nothing is fetched
  twice.
- A Date table, a small bridge, or a disconnected table are the common cases. Build the Date table
  once and mark it as a date table (`powerbi-modeling`).

## The context facts that cause wrong numbers

- Row context does NOT filter the model. Being on a row inside SUMX or a calculated column does not
  restrict what a measure there sees until CALCULATE turns the row into a filter (context
  transition).
- Every measure reference carries an implicit CALCULATE, so a measure called inside an iterator
  already transitions on each row. The same raw expression without CALCULATE does not, and gives a
  different number.
- A CALCULATE filter argument REPLACES the existing filter on that column. KEEPFILTERS makes it
  intersect. Left out inside an iterator, it gives a plausible wrong number. Worked example in
  `virtual-relationships.md`.
- A total that does not equal the sum of the visible rows usually means the measure should be
  evaluated per row and then combined. See `ratios-and-totals.md`.

## Converting an import table into a calculated table

Editing the TMDL works only if the cached data is cleared first. Swap the partition and reopen with
the cache still there and it fails on open with

```
PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC
```

The trigger is the diff against `.pbi\cache.abf`, not the TMDL. Close Desktop, edit the partition to
`= calculated` with a `source =` DAX expression, delete `.pbi\cache.abf`, reopen, then Refresh. The
GUI path (New table, move relationships, delete the old one) also works. The full method and the
column lineage gotcha are in the `powerbi-project-and-tools` skill.

Do this only for derivative tables that roll up or reshape data already in the model, never to avoid
a real source pull.
