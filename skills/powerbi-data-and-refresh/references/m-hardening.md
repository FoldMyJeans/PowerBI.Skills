# Hardening an M query

The transforms that keep a query alive when the source drifts, plus the parsing helpers that
come up on every API and every business owned workbook.

A query that works today and breaks in 3 months usually breaks for one of four reasons: a
column disappeared, a value arrived in a shape the query did not expect, a blank came through
as `""` instead of `null`, or a text key stopped matching because of a stray space. Each has a
standard answer below.

## Survive a column that disappears

Three forms, because they solve different problems and only the first is widely known.

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
'opened_at' of the record wasn't found", which at least names the column.

Do not confuse it with "The key did not match any rows in the table". That comes from a record
key lookup, the `Source{[Item = "Sheet1", Kind = "Sheet"]}` shape, and means a worksheet or
table was renamed, not a column.

## Quote a field name that has punctuation in it

A bare `[Effort (Hours)]` is a parse error, not a runtime error, so the query does not fail at
refresh time, the whole `.pbip` refuses to open, reporting `Invalid identifier`. This bites in
`each` expressions and record constructors.

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

A space alone is fine, so `[Initial Owner]` does not need quoting. Parentheses, slashes, and a
leading digit do. When in doubt, quote it, the hash form is always valid.

The `List.Sum({a, b, 0})` shape above is worth stealing on its own. It tolerates a null in
either input and the trailing `0` guarantees a number rather than a blank.

## Normalize blanks before load

An API that returns `""` where it means nothing will give you a column that is neither blank
nor useful. `""` and `null` behave differently in DAX `ISBLANK` and in relationships, so fix it
once at the end rather than in every downstream measure.

```m
NormalizeBlanks = Table.TransformColumns(
  Source,
  List.Transform(
    Table.ColumnNames(Source),
    each {_, (v) => if v is text and Text.Trim(v) = "" then null else v, type nullable any}
  )
),
```

`v is text` guards the columns that are not text. Run this as one of the last steps.

## Catch anything that still errored

```m
Result = Table.ReplaceErrorValues(Final, {
  {"Number", null}, {"Priority", null}, {"Company", null}
})
```

Belt and braces after the typed transforms. It catches errors that slipped past a
`try ... otherwise` earlier in the chain, and it means one bad row does not fail the refresh.

## Parsing the values an API actually sends

### A duration written as words

```m
DurationToHours = (t as any) as nullable number =>
  let
    Txt    = if t = null then null else Text.Lower(Text.Trim(Text.From(t))),
    Tokens = if Txt = null or Txt = "" then {} else List.Select(Text.Split(Txt, " "), each _ <> ""),
    Acc = List.Accumulate(
      {0 .. List.Count(Tokens) - 2},
      [d = 0, h = 0, m = 0, s = 0],
      (st, i) =>
        let
          n = try Number.FromText(Tokens{i}) otherwise null,
          u = Tokens{i + 1}
        in
          if n = null then st
          else if Text.StartsWith(u, "day")    then [d = st[d] + n, h = st[h], m = st[m], s = st[s]]
          else if Text.StartsWith(u, "hour")   then [d = st[d], h = st[h] + n, m = st[m], s = st[s]]
          else if Text.StartsWith(u, "minute") then [d = st[d], h = st[h], m = st[m] + n, s = st[s]]
          else if Text.StartsWith(u, "second") then [d = st[d], h = st[h], m = st[m], s = st[s] + n]
          else st
    )
  in
    if Txt = null then null
    else Number.Round(Acc[d] * 24 + Acc[h] + Acc[m] / 60 + Acc[s] / 3600, 5),
```

Handles "2 days 3 hours 15 minutes" in any order and with any subset of units. The tempting
alternative, a chain of `Text.BeforeDelimiter` calls, assumes the units arrive in a fixed order
and silently returns the wrong number when they do not. Use the accumulator.

### A choice field pulled as a display value

```m
{"Priority", each try Number.FromText(Text.Start(Text.Trim(Text.From(_)), 1)) otherwise null, Int64.Type}
```

With display values on, a ServiceNow choice comes back as `"1 - Critical"` rather than `1`.

### A datetime from anywhere

```m
{"Start Date", each try DateTime.From(Text.Replace(Text.From(_), "T", " ")) otherwise null, type datetime}
```

`Text.From` first so a non text input survives, the `T` replacement covers both ISO 8601 and
the space separated form, and `try ... otherwise null` keeps one bad value from erroring the
whole column.

## Fail loudly where a silent wrong answer would be worse

```m
MonthColsCheck =
  if List.Count(MonthColsPresent) < 10
  then error "Month headers not detected. Found: " & Text.Combine(MonthColsPresent, ", ")
            & " | All columns: " & Text.Combine(Table.ColumnNames(Source), ", ")
  else Source,
```

Use this where an assumption, once broken, would produce a plausible but wrong number rather
than an obvious failure. Put the observed values in the message so the refresh error tells you
what changed instead of just that something did.

The same idea in the small: `try ... otherwise error "a useful sentence"` beats
`try ... otherwise null` when null would quietly propagate.

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

The last step matters more than it looks. Leave the non matches as null and those rows vanish
from every sliced total without anyone noticing. Named buckets show up in a slicer and get
questioned, which is what you want.

If the join key must stay unique for a model relationship, end the query with
`Table.Distinct(Source, {"Task Number"})` and say why in a comment. A duplicate on the one side
turns a relationship many to many at refresh time.

## A join a merge cannot express

Matching a date to the range it falls inside is not an equality join, so `Table.NestedJoin`
cannot do it.

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

`Table.Buffer` is required, not an optimization. Without it the lookup table is re-evaluated
once per fact row. Note the `(row) =>` lambda instead of `each`, so `row[...]` and the inner
`each [...]` unambiguously refer to different tables.

## Turning one row into several

When one source row should become one fact row per participant, and the columns are
heterogeneous rather than a clean unpivot:

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

`List.RemoveNulls` means a row with only one valid participant produces exactly one output row,
not one plus a blank.

## Sorting a numeric suffix

```m
Recent = Table.SelectRows(Source, each
  let n = try Number.FromText(Text.Trim(Text.AfterDelimiter([Sprint], "Sprint "))) otherwise null
  in n <> null and n >= 85),
```

Text comparison puts "Sprint 9" after "Sprint 85". Parse the number. Leaving the upper bound off
means future values keep flowing with no maintenance.

Note the `try ... otherwise` inside the predicate. A `Table.SelectRows` predicate that errors on
a single row kills the whole filter, so the guard is required rather than defensive.
