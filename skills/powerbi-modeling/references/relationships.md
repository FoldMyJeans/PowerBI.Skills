# Relationships

Relationships are the model. They decide how a filter on one table reaches another, and they are
what makes a table a dimension or a fact. Get them right and the numbers are predictable. Get
them wrong and you get blanks, doubled totals, or filters that do nothing.

## Cardinality: one to many is the default and the goal

Cardinality is how many rows on each side of a relationship share a key value.

- One to many is what you want almost every time. The "one" side is a dimension with unique keys.
  The "many" side is a fact where the key repeats. The dimension filters the fact. A star schema
  is a set of one to many relationships from dimensions into facts.
- One to one is rare. It usually means two tables should be one, or that you are looking at a
  degenerate dimension. Merge them unless you have a specific reason.
- Many to many cardinality (both sides can hold duplicates) is rare and has real costs. One case
  calls for it, a fact at a higher grain than its dimension. Between two dimensions, prefer a bridge
  table. See `many-to-many.md`.

Power BI decides the table type from cardinality. The "one" side is always a dimension, the
"many" side is always a fact. If a relationship you expected to be one to many comes up many to
many, your "one" side has duplicate or blank keys. Fix the key, do not accept the many to many.

## Cross filter direction: single is safer than both

Every relationship has a cross filter direction, single or both.

- Single means the filter flows one way, from the "one" side (dimension) to the "many" side
  (fact). This is the safe default and it is what a star schema wants. A slice on Product filters
  Sales. That is all you usually need.
- Both (bidirectional) lets the filter flow the other way too, from the fact back up into the
  dimension. It is occasionally useful but dangerous as a default.

Why single is safer:
- Predictable numbers. Filters travel one known path, so a measure returns what you expect.
- No ambiguity. With several dimensions on one fact, bidirectional filters can create more than
  one path between two tables. The engine then cannot tell which path to use, and you get
  ambiguous or wrong results. Power BI will even block some bidirectional relationships that
  would make the model ambiguous.
- Speed. Every extra filter direction is more work per query.

Leave cross filter direction on single. Turn on both only for a deliberate reason, almost always
a bridge table for a genuine many to many, and only once you know the filter paths it opens. Do
not flip a dimension to fact relationship to both just to make one visual work. That fix usually
breaks another number quietly.

## Active vs inactive relationships and USERELATIONSHIP

Between any two tables, only one relationship can be active at a time. The active one is the
default filter path (a solid line in the diagram). Extra relationships between the same two
tables must be inactive (a dashed line).

The classic case is role playing dates. A `Sales` fact has an order date, a ship date, and a
delivery date, all pointing at one `Date` table. Only one of those relationships can be active,
usually order date. The others sit inactive.

To use an inactive relationship, turn it on for a single measure with `USERELATIONSHIP`:

```dax
Sales by Ship Date =
CALCULATE (
    [Total Sales],
    USERELATIONSHIP ( Sales[ShipDateKey], 'Date'[DateKey] )
)
```

Two ways to handle role playing dimensions:
- Keep one Date table and write a measure per role with `USERELATIONSHIP`. Fewer tables, but a
  measure for every date role.
- Add a separate dimension table per role (a `Ship Date` table, a `Delivery Date` table), each
  with its own active relationship. More tables, but no special measures, and you can filter by
  two roles at once.

Microsoft leans toward the second, active relationships with the dimension duplicated, because it
widens what report authors can do. It treats inactive relationships as fine when no visual has to
filter by two roles at once. Two costs to check:

- A clone made as a calculated table carries columns only. Formats, descriptions, and hierarchies do
  not come across.
- `USERELATIONSHIP` errors when row level security is defined on the table involved, for example on
  the dimension named in the function. If the model uses RLS, check this before choosing the first
  option.

For DAX detail on `USERELATIONSHIP` and measure patterns, see `powerbi-dax`.

## Many to many

There are three different cases and the answer differs. Two dimensions get a bridge table, two facts
get shared dimensions, and a fact at a higher grain can take a single direction many to many
relationship with a grain guard in its measures. A many to many cardinality relationship is always
limited, which hides unmatched rows. The full treatment is in `many-to-many.md`.

## When the one to many rule bends

Everything above is the default and it holds most of the time. It does not hold always. A
model of twenty five relationships can easily have four that fail this file's own checklist,
all four working, all four deliberate.

The four shapes, in rising order of risk:

- **Dimension to dimension.** A date column on a dimension related to the date or period table,
  for example a last updated month on a work item dimension. Legitimate. Nothing says a
  dimension cannot carry a date you want to filter on.
- **Fact to fact, single direction.** A plan table filters a transaction table, because the plan
  sets the scope and the transactions report against it. Single direction keeps the filter path
  readable and the totals predictable.
- **Dimension to fact declared with the dimension on the "from" side.** It works only because
  the "to" side happens to be unique today. One duplicate row from the source then fails the whole
  refresh. Fragile, and worth a note in the model.
- **Fact to fact, bidirectional, on a composite string key.** Used when two facts sit at
  different grains (work item grain versus company month grain) and neither side has a surrogate
  key to hang a dimension off. This is the one genuinely risky case. Test the totals from both
  directions before you ship it, and prefer a virtual relationship (`TREATAS` in a measure, see
  the `powerbi-dax` skill) if you can, because a virtual relationship does not change the
  model's filter graph at all.

Each of these costs something. A bidirectional fact to fact join makes the filter graph harder
to reason about, and it can produce ambiguity later, when someone adds a third table that closes
a loop nobody was looking for. The checklist below is still the default. Break it on purpose,
with a reason written down, or not at all.

## Relationship columns must be clean keys

A relationship is only as good as the columns it joins on. The key on the "one" side must be:
- Unique. No duplicate values. Duplicates stop you declaring one to many in the first place, and
  once it is declared, a duplicate arriving in a refresh fails the whole refresh.
- Non blank. On a regular one to many relationship, a blank or unmatched key lands in a single blank
  member. On a limited relationship (see `many-to-many.md`) the row drops out of the join instead.
- One data type on both ends. A text key on one side and a number on the other will not match, or
  will match slowly. Whole number keys are best, they compress and join fastest.

Practical habits:
- Join on a dedicated key column, not on a display name. Two customers can share a name.
- Remove the time from a date key in Power Query. The engine stores every date as DateTime even when
  it is formatted as Date, so a time portion stops two equal looking dates from matching.
- Fail fast on blanks. For an ID that must never be missing, turn off `Is Nullable` in the column
  properties, and the refresh fails when a missing value arrives (from Microsoft docs, not yet run
  on a real model). Set it in Desktop and read the TMDL back if you need the file shape.
- Build surrogate integer keys upstream in M or at the source when the source has no clean key.
- Check the fact for orphan keys (a key with no matching dimension row). Those show up as a blank
  member in visuals and are usually a data load bug.
- Keep the key work in M or the source, not in DAX calculated columns. See
  `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.

### When the source cannot give you a surrogate key

Plenty of sources cannot. A ticketing API hands you a text ticket number, and a workbook a
person maintains by hand hands you whatever they typed. You still need the join, so:

- Accept a text key, but make it deterministic. Trim both sides. Normalize case as well if the
  source is inconsistent about it, that is cheaper than debugging one unmatched row next month.
- When you must build a composite key, format every part explicitly so both sides concatenate
  identically. `FORMAT ( Year, "0000" )` rather than letting an integer stringify however it
  happens to. Same for the month part, same for any padded id.
- Let a duplicate on the "one" side fail the refresh. Microsoft is plain about it: if a refresh tries
  to load duplicates into a "one" side column, the entire refresh fails. That is the behaviour you
  want, because it tells you the key or the grain is wrong while the old data is still in place.

  Resist the urge to "fix" it upstream with `Table.Distinct`. That silently keeps one arbitrary row
  per key and throws the rest away, so the refresh goes green while the data goes wrong.

```m
// Only when you have checked the duplicates are byte identical rows, for example a source
// that returns the same record twice. Then losing one costs nothing.
Deduped = Table.Distinct(Source, {"Task Number"})
```

  If the duplicates are not identical, the key is wrong, not the data. Widen it until it is unique,
  or take the grain question back to whoever owns the source.

The honest trade: this is a fallback, not an equal option. Text keys compress worse, join
slower, and depend on a cleaning step that has to keep working. An integer surrogate key is
still better whenever the source can give you a stable one.

The common shape is a model that shipped with auto date/time still on and no marked Date table
(the rule for that lives in `naming-and-measures.md`), so its time based logic runs on `FILTER`
and `ALL` over a plain date column instead. Its one real relationship still carried the default `AutoDetected_`
name Desktop generates, never renamed to say what it joins. Both come from the same habit,
shipping whatever Desktop wired up instead of reviewing it.

## Quick checklist

- Is every relationship one to many from a dimension into a fact.
- Is cross filter direction single everywhere, except a deliberate, tested bridge.
- Does any table pair have more than one relationship. If so, is the right one active, and are the
  others driven by `USERELATIONSHIP`.
- Is every "one" side key unique, non blank, and a single data type.
- Is that uniqueness re-checked after every source change, not just on the day you created the
  relationship.
- Is any many to many between dimensions wired through a bridge table, and is any direct many to many
  relationship a deliberate higher grain case with a grain guard in its measures.
- Are there orphan keys on the facts showing up as a blank member.
