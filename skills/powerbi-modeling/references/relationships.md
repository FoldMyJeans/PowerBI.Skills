# Relationships

Relationships decide how a filter on one table reaches another. Wrong ones give blanks, doubled
totals, or filters that do nothing.

## Cardinality: one to many is the default

- One to many almost every time. The "one" side is a dimension with unique keys, the "many" side a
  fact where the key repeats.
- One to one is rare. It usually means two tables should be one. Merge them unless you have a
  specific reason.
- Many to many cardinality has real costs. One case calls for it, a fact at a higher grain than its
  dimension. Between two dimensions, use a bridge. See `many-to-many.md`.

If a relationship you expected to be one to many comes up many to many, the "one" side has
duplicate or blank keys. Fix the key, do not accept the many to many.

## Cross filter direction: single is the default

Single flows the filter from the "one" side to the "many" side, which is what a star wants. Both
also flows it back from the fact into the dimension.

Both is risky as a default. With several dimensions on one fact it can create more than one path
between two tables, and the engine then gives ambiguous or wrong results (Power BI blocks some of
these outright). It is also more work per query. Turn on both only for a deliberate reason, almost
always one leg of a bridge, once you know the paths it opens. Flipping a dimension to fact
relationship to both to make one visual work usually breaks another number quietly.

## Active vs inactive relationships and USERELATIONSHIP

Only one relationship between two tables can be active (solid line in the diagram). Extras are
inactive (dashed). The classic case is role playing dates: order, ship, and delivery date on
`Sales`, all pointing at one `Date` table, order date active.

Turn an inactive one on for a single measure:

```dax
Sales by Ship Date =
CALCULATE (
    [Total Sales],
    USERELATIONSHIP ( Sales[ShipDateKey], 'Date'[DateKey] )
)
```

Two ways to handle role playing dimensions:

- One Date table and a `USERELATIONSHIP` measure per role. Fewer tables, a measure for every role.
- A dimension per role (`Ship Date`, `Delivery Date`), each with its own active relationship. More
  tables, no special measures, and you can filter by two roles at once.

Microsoft leans toward the second because it widens what report authors can do, and treats
inactive relationships as fine when no visual has to filter by two roles at once. Two costs to
check:

- A clone made as a calculated table carries columns only. Formats, descriptions, and hierarchies
  do not come across.
- `USERELATIONSHIP` errors when row level security is defined on the table involved, for example on
  the dimension named in the function. With RLS, check this before choosing the first option.

When the relationship should not exist in the model at all, filter through one in a single measure
instead (TREATAS, `virtual-relationships.md` in the `powerbi-dax` skill).

## When the one to many rule bends

A model of twenty five relationships can have four that fail this file's checklist, all working
and all deliberate. The four shapes, in rising order of risk:

- **Dimension to dimension.** A date column on a dimension related to the date or period table,
  for example a last updated month on a work item dimension. Legitimate.
- **Fact to fact, single direction.** A plan table filters a transaction table, because the plan
  sets the scope. Single direction keeps the path readable and the totals predictable.
- **Dimension to fact declared with the dimension on the "from" side.** Works only because the
  "to" side happens to be unique today. One duplicate row from the source then fails the whole
  refresh. Fragile, so note it in the model.
- **Fact to fact, bidirectional, on a composite string key.** Two facts at different grains (work
  item versus company month) with no surrogate key to hang a dimension off. The genuinely risky
  one. Test the totals from both directions, and prefer a virtual relationship (`TREATAS` in a
  measure, see the `powerbi-dax` skill), which does not change the filter graph at all.

A bidirectional fact to fact join can turn ambiguous later, when someone adds a third table that
closes a loop nobody was watching. Break the default on purpose, with the reason written down, or
not at all.

## Relationship columns must be clean keys

The "one" side key must be:

- Unique. A duplicate stops you declaring one to many, and once declared, a duplicate arriving in a
  refresh fails the whole refresh.
- Non blank. On a regular one to many, a blank or unmatched key lands in a single blank member. On
  a limited relationship (see `many-to-many.md`) the row drops out of the join instead.
- One data type on both ends. Text on one side and a number on the other will not match, or will
  match slowly. Whole number keys compress and join fastest.

Habits:

- Join on a dedicated key column, not a display name. Two customers can share a name.
- Remove the time from a date key in Power Query. The engine stores every date as DateTime even when
  formatted as Date, so a time portion stops two equal looking dates from matching.
- For an ID that must never be missing, turn off `Is Nullable` in the column properties, and the
  refresh fails when a missing value arrives (from Microsoft docs, not yet run on a real model). Set
  it in Desktop and read the TMDL back if you need the file shape.
- Build surrogate integer keys upstream in M or at the source when the source has no clean key, not
  in DAX calculated columns.
- Check the fact for orphan keys (no matching dimension row). They show as a blank member and are
  usually a data load bug.
- Rename relationships Desktop auto detected. A shipped model whose one real relationship still
  carried the default `AutoDetected_` name also had auto date/time on and no marked Date table. Both
  come from shipping whatever Desktop wired up without reviewing it.

### When the source cannot give you a surrogate key

A ticketing API hands you a text ticket number, a hand maintained workbook hands you whatever was
typed. You still need the join:

- Accept a text key, but make it deterministic. Trim both sides, and normalize case if the source
  is inconsistent.
- For a composite key, format every part explicitly so both sides concatenate identically.
  `FORMAT ( Year, "0000" )`, not however an integer happens to stringify. Same for the month part
  and any padded id.
- Let a duplicate on the "one" side fail the refresh. That tells you the key or the grain is wrong
  while the old data is still in place. Do not "fix" it with `Table.Distinct`, which keeps one
  arbitrary row per key, so the refresh goes green while the data goes wrong.

```m
// Only when you have checked the duplicates are byte identical rows, for example a source
// that returns the same record twice. Then losing one costs nothing.
Deduped = Table.Distinct(Source, {"Task Number"})
```

If the duplicates are not identical, the key is wrong, not the data. Widen it until it is unique,
or take the grain question back to whoever owns the source.

Text keys are a fallback. They compress worse, join slower, and depend on a cleaning step that has
to keep working. Use a stable integer surrogate whenever the source can give one.

## Quick checklist

- Every relationship is one to many from a dimension into a fact, or a written down exception.
- Cross filter direction is single everywhere, except a deliberate, tested bridge.
- Where a table pair has several relationships, the right one is active and the others are driven
  by `USERELATIONSHIP`.
- Every "one" side key is unique, non blank, one data type, and re-checked after every source
  change.
- Many to many between dimensions goes through a bridge, and any direct many to many is a
  deliberate higher grain case with a grain guard in its measures.
- No orphan keys on the facts showing up as a blank member.
