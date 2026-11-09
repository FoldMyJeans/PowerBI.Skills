# Hardening an M query

Transforms that keep a query alive when the source drifts. A query that works today and breaks in
3 months usually breaks for one of four reasons: a column disappeared, a value arrived in an
unexpected shape, a blank came through as `""` instead of `null`, or a text key stopped matching
because of a stray space. Parsing API values is in `parsing-api-values.md`.

## Survive a column that disappears

```m
// A. Selecting or renaming: intersect what you want with what is there
Wanted  = {"number", "sys_id", "priority", "opened_at"},
Present = List.Intersect({Table.ColumnNames(Source), Wanted}),
Kept    = Table.SelectColumns(Source, Present, MissingField.Ignore),
```

```m
// B. A whole STEP depends on a column existing. MissingField.Ignore cannot help here,
//    because Table.SelectRows evaluates the reference itself.
Filtered =
  if List.Contains(Table.ColumnNames(Source), "opened_at")
  then Table.SelectRows(Source, each Date.From([opened_at]) >= CutoffDate)
  else Source,
```

```m
// C. Drop columns the source populated in dev and stopped populating in production
NonEmpty =
  let
    cols = Table.ColumnNames(Source),
    keep = List.Select(cols, each List.NonNullCount(Table.Column(Source, _)) > 0)
  in
    Table.SelectColumns(Source, keep),
```

Form B is the one people miss. `MissingField.Ignore` only applies to the select and rename
functions. A `Table.SelectRows` predicate that names a vanished column throws "The field
'opened_at' of the record wasn't found".

Different error: "The key did not match any rows in the table" comes from a record key lookup, the
`Source{[Item = "Sheet1", Kind = "Sheet"]}` shape, and means a worksheet or table was renamed, not
a column.

## Quote a field name that has punctuation in it

A bare `[Effort (Hours)]` is a parse error, not a runtime error. The whole `.pbip` refuses to open,
reporting `Invalid identifier`. It bites in `each` expressions and record constructors.

```m
// wrong, will not parse
each List.Sum({[Days Unavailable (Days)], [Sick Days (Days)], 0})

// right
each List.Sum({[#"Days Unavailable (Days)"], [#"Sick Days (Days)"], 0})
```

```m
// also needs it inside a record constructor
[ Owner = [Initial Owner], #"Effort (Hours)" = [#"Initial Effort (Hours)"] ]
```

A space alone is fine (`[Initial Owner]`). Parentheses, slashes, and a leading digit need the hash
form, which is always valid, so quote when in doubt. The `List.Sum({a, b, 0})` shape tolerates a
null in either input, and the trailing `0` guarantees a number rather than a blank.

## Normalize blanks before load

`""` and `null` behave differently in DAX `ISBLANK` and in relationships. Fix it once, as one of the
last steps, rather than in every downstream measure.

```m
NormalizeBlanks = Table.TransformColumns(
  Source,
  List.Transform(
    Table.ColumnNames(Source),
    each {_, (v) => if v is text and Text.Trim(v) = "" then null else v, type nullable any}
  )
),
```

`v is text` guards the columns that are not text.

## Catch anything that still errored

```m
Result = Table.ReplaceErrorValues(Final, {
  {"Number", null}, {"Priority", null}, {"Company", null}
})
```

Catches errors that slipped past a `try ... otherwise` earlier, so one bad row does not fail the
refresh.

## Fail loudly where a silent wrong answer would be worse

```m
MonthColsCheck =
  if List.Count(MonthColsPresent) < 10
  then error "Month headers not detected. Found: " & Text.Combine(MonthColsPresent, ", ")
            & " | All columns: " & Text.Combine(Table.ColumnNames(Source), ", ")
  else Source,
```

Use it where a broken assumption would produce a plausible but wrong number. Put the observed
values in the message so the refresh error says what changed. In the small:
`try ... otherwise error "a useful sentence"` beats `try ... otherwise null` when null would
quietly propagate.

## Joining on text people typed

Trim both sides before the join, then bucket the non matches deliberately.

```m
Clean = Table.TransformColumns(Lookup, {
  {"Team Member", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
  {"Sprint",      each if _ = null then null else Text.Trim(Text.From(_)), type nullable text}
}),
Merged   = Table.NestedJoin(Source, {"Sprint", "Owner"}, Clean, {"Sprint", "Team Member"}, "T", JoinKind.LeftOuter),
Expanded = Table.ExpandTableColumn(Merged, "T", {"Team", "Role"}, {"Team", "Role"}),
Filled   = Table.TransformColumns(Expanded, {
  {"Team", each if _ = null or Text.Trim(Text.From(_)) = "" then "Other" else _, type text},
  {"Role", each if _ = null or Text.Trim(Text.From(_)) = "" then "Other" else _, type text}
}),
```

Leave the non matches as null and those rows vanish from every sliced total without anyone
noticing. Named buckets show up in a slicer and get questioned.

If the join key must stay unique for a model relationship, `Table.Distinct(Source, {"Task Number"})`
is safe only when the duplicates are identical rows. A duplicate on the one side fails the refresh,
and that rule, with when not to dedupe, is in the `powerbi-modeling` skill.

## A join a merge cannot express

Matching a date to the range it falls inside is not an equality join, so `Table.NestedJoin` cannot
do it.

```m
Buffered = Table.Buffer(dim_sprint),
WithSprint = Table.AddColumn(Source, "Sprint",
  (row) =>
    if row[Start Date] = null then null
    else
      let
        match = Table.SelectRows(Buffered,
          each row[Start Date] >= [Sprint Start Date] and row[Start Date] <= [Sprint End Date])
      in
        if Table.RowCount(match) > 0 then match{0}[Sprint Name] else null,
  type text),
```

`Table.Buffer` is required, not an optimization. Without it the lookup table is re-evaluated once
per fact row. The `(row) =>` lambda instead of `each` keeps `row[...]` and the inner `each [...]`
pointing at different tables.

## Turning one row into several

When one source row should become one fact row per participant, and the columns are heterogeneous
rather than a clean unpivot:

```m
WithList = Table.AddColumn(Source, "OwnerEffort", each List.RemoveNulls({
  if [Initial Owner] <> null and [#"Initial Effort (Hours)"] <> null
    then [Owner = [Initial Owner], #"Effort (Hours)" = [#"Initial Effort (Hours)"]] else null,
  if [Escalated Owner] <> null and [#"Escalated Effort (Hours)"] <> null
    then [Owner = [Escalated Owner], #"Effort (Hours)" = [#"Escalated Effort (Hours)"]] else null
})),
Exploded = Table.ExpandListColumn(WithList, "OwnerEffort"),
Final    = Table.ExpandRecordColumn(Exploded, "OwnerEffort", {"Owner", "Effort (Hours)"}, {"Owner", "Effort (Hours)"}),
```

`List.RemoveNulls` means a row with one valid participant produces exactly one output row, not one
plus a blank.

## Sorting a numeric suffix

```m
Recent = Table.SelectRows(Source, each
  let n = try Number.FromText(Text.Trim(Text.AfterDelimiter([Sprint], "Sprint "))) otherwise null
  in n <> null and n >= 85),
```

Text comparison puts "Sprint 9" after "Sprint 85", so parse the number. No upper bound means future
values keep flowing. The `try ... otherwise` is required: a `Table.SelectRows` predicate that errors
on one row kills the whole filter.
