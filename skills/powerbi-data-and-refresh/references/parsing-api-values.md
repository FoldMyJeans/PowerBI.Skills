# Parsing the values an API actually sends

APIs send durations as words, choices as display text, and dates as ISO strings with a time and a
zone. Each needs a parser, and each parser needs a check that it ever returns a value. Schema
drift, blanks, and text joins are in `m-hardening.md`.

## A duration written as words

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

Handles "2 days 3 hours 15 minutes" in any order and any subset of units. A chain of
`Text.BeforeDelimiter` calls assumes a fixed unit order and silently returns the wrong number when
the order differs.

## A choice field pulled as a display value

With display values on, a ServiceNow choice comes back as `"1 - Critical"` rather than `1`.

```m
{"Priority", each try Number.FromText(Text.Start(Text.Trim(Text.From(_)), 1)) otherwise null, Int64.Type}
```

## A date sent as ISO text with a time

A training API sent campaign dates as `2026-04-01T13:00:00.000Z`. `Date.From` on that text errors on
every row. The query wrapped it in `try ... otherwise null`, so a fallback due date never filled a
single row for two months, and every on time measure quietly left those records out. Nothing
failed.

When only the date matters, cut the text to its first ten characters before parsing:

```m
sd = try Date.From(Text.Start([start_date], 10)) otherwise null,
```

That also drops the zone, so a value near midnight UTC can land on the neighbouring local day.
Harmless for a campaign start, wrong for an event log.

## A datetime from anywhere

```m
{"Start Date", each try DateTime.From(Text.Replace(Text.From(_), "T", " ")) otherwise null, type datetime}
```

`Text.From` first so a non text input survives. The `T` replacement covers ISO 8601 and the space
separated form. The `Z` suffix and milliseconds are a different shape, so run the diagnostic table
below on one real value before trusting this on a new API.

## Prove the parse returns something

`try ... otherwise null` keeps one bad value from erroring the column, and turns a parse that never
works into a column of nulls with no error. Follow every such parse with a check that fails the
refresh when the whole column came back empty:

```m
Parsed = Table.TransformColumns(Source, {{"start_date", each try Date.From(Text.Start(_, 10)) otherwise null, type nullable date}}),
NonNull = List.Count(List.RemoveNulls(Table.Column(Parsed, "start_date"))),
Checked =
  if Table.RowCount(Parsed) > 0 and NonNull = 0
  then error "start_date parsed to null on every row. First raw value: " & Text.From(Source{0}[start_date])
  else Parsed
```

## A temporary diagnostic table

When a parse fails and the cause is unclear, look at what the API really sends. Add a temporary M
table that pages the same endpoint and returns the raw text next to the parse result or the error
message:

```m
Parse = (v) => if v = null then null else try Text.From(Date.From(v)) otherwise "ERROR " & (try Date.From(v))[Error][Message]
```

Refresh only that table (right click it in the Data pane, or a TMSL table refresh, see
`powerbi-project-and-tools`), query it, then delete it. Removal checklist: the table file, its
`ref table` line in `model.tmdl`, and any visual that bound it. It proved the ISO date cause above
in one small call per page.

## Excluding named items at the source

Test and optional campaigns belong out of the model, not filtered on each page. Keep the names in a
list query in the parameter group, annotated as a list result. In `expressions.tmdl`:

```tmdl
/// Items left out of the report on purpose, in upper case.
expression ExcludedNames = {"NAME ONE", "NAME TWO"}
	lineageTag: <new guid>
	queryGroup: Parameter

	annotation PBI_ResultType = List
```

Use it in every staging query that reads the field, upper cased and trimmed on both sides:

```m
Kept = Table.SelectRows(Source, each not List.Contains(ExcludedNames, Text.Upper(Text.Trim([Campaign] ?? ""))))
```

One list, edited in one place, and the page filters cannot drift apart.
