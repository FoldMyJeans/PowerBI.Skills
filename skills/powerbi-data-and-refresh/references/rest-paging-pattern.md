# The REST paging pattern

The loop for pulling a paged REST API into Power Query, plus the guards. A loop without the
guards works on the first run and fails quietly on the run that matters. Hosts are placeholders,
keep real ones out of anything shared.

## The loop, complete

```m
let
  // 1 - CONFIG. Everything tunable in one place at the top.
  BaseUrl  = "https://yourinstance.service-now.com",
  RelPath  = "api/now/table/incident",
  PageSize = 10000,     // row ceiling = PageSize * MaxPages. Change one, change the other.
  MaxPages = 20,
  Fields   = "number,sys_id,priority,opened_at,short_description,assignment_group",
  Cols     = {"number","sys_id","priority","opened_at","short_description","assignment_group"},

  // 2 - QUERY. Filter at the source. ^ORDERBYsys_id makes offset paging deterministic.
  FullQuery = "sys_created_on>=javascript:gs.dateGenerate('2025-01-01','00:00:00')"
            & "^ORDERBYsys_id",

  // 3 - FETCH ONE PAGE
  FetchPage = (offset as number) as table =>
    let
      Raw = Web.Contents(BaseUrl, [
        RelativePath = RelPath,
        Timeout      = #duration(0, 0, 10, 0),   // default is 100 seconds, budget this below
        Query = [
          sysparm_display_value          = "true",
          sysparm_exclude_reference_link = "true",
          sysparm_fields                 = Fields,
          sysparm_limit                  = Text.From(PageSize),
          sysparm_offset                 = Text.From(offset),
          sysparm_query                  = FullQuery
        ]
      ]),
      Rows = Json.Document(Raw)[result],
      Tbl  = Table.FromList(Rows, Splitter.SplitByNothing(), {"Record"}),
      // THE EMPTY PAGE GUARD. Read the section below before you remove this.
      Exp  = if Table.RowCount(Tbl) = 0
             then #table(Cols, {})
             else Table.ExpandRecordColumn(Tbl, "Record", Cols, Cols)
    in
      Exp,

  // 4 - LOOP. Stop on a short page without spending a request to discover the end.
  Pages = List.Generate(
    () => [Offset = 0, Data = FetchPage(0)],
    (s) => Table.RowCount(s[Data]) > 0 and s[Offset] < MaxPages * PageSize,
    (s) => [ Offset = s[Offset] + PageSize,
             Data   = if Table.RowCount(s[Data]) < PageSize
                      then #table(Cols, {})
                      else FetchPage(s[Offset] + PageSize) ],
    (s) => s[Data]
  ),

  // 5 - COMBINE. List.Generate returns {} when the FIRST page is empty, and
  // Table.Combine({}) gives a table with no columns, which breaks everything downstream.
  Combined = if List.IsEmpty(Pages)
             then #table(Cols, {})
             else Table.Combine(Pages),

  // 6 - CEILING GUARD. Stopping because we ran out of pages, while the last page was
  // still full, means rows were left behind. Fail loudly instead of shipping a short table.
  HitCeiling = List.Count(Pages) >= MaxPages
               and Table.RowCount(List.Last(Pages)) = PageSize,
  Result = if HitCeiling
           then error "Paging stopped at the " & Text.From(MaxPages * PageSize)
                      & " row ceiling with a full last page, so rows were dropped. "
                      & "Raise MaxPages or narrow the query."
           else Combined
in
  Result
```

## The empty page guard, and why it is not optional

`FetchPage` must return a table with a declared column list when the page is empty.
`Table.ExpandRecordColumn` infers nothing from a zero row table, so a page past the end comes back
with no columns. `Table.Combine` then errors or silently drops columns, and the failure surfaces
much later as a broken relationship or a blank visual.

Declare the list once as `Cols` and use it in all four places (the expand, the empty branch in
`FetchPage`, the empty branch in the loop, the empty branch in `Combined`). A drifted copy of that
list is the usual way this breaks after an edit.

The `FetchPage` guard cannot catch an empty FIRST page (a filter that matched nothing). The loop
condition is false on its first evaluation, `List.Generate` returns `{}`, and `Table.Combine({})`
gives a table with no columns. That is why `Combined` tests `List.IsEmpty` first.

## The row ceiling has to be loud

`PageSize * MaxPages` is a ceiling. Without the guard, a source that grows past it returns a short
table, every visual keeps rendering, and the numbers are quietly incomplete.

The test: did we run out of pages, and was the last page still full? Either alone is fine.
Together they mean there was more data and we did not fetch it, so the refresh fails and says so.

## Stop without a wasted request

The `next` function checks whether the page it already has came back short. If so, the next state
gets an empty table and no request goes out. Fetching first and testing afterwards always spends
one extra round trip discovering the end, which on a 10 minute timeout is worth removing.

## Page size, and the symptom that means lower it

Start at 10000 for a ServiceNow Table API, which is also its default cap for `sysparm_limit`.

Lower it on "the operation was cancelled" or "the exception was raised by the IDbCommand
interface". The source could not assemble the page inside its own transaction limit, which is more
likely with `sysparm_display_value` on and many reference fields. Drop to a few thousand and raise
`MaxPages` by the same factor so the row ceiling does not change.

## Set Timeout on purpose, on every Web.Contents

`Web.Contents` gives up after 100 seconds when you set nothing, so
`Timeout = #duration(0, 0, 10, 0)` raises the limit. It does not protect you from a stall.
https://learn.microsoft.com/en-us/powerquery-m/web-contents

- Budget it. The worst case for one paged query is `Timeout` times `MaxPages`, against 2 hours for
  the whole attempt. The values above allow 10 minutes times 20 pages, 200 minutes, before fan out
  multiplies it (`folding-and-duplication.md`). If the product passes 2 hours, lower one or shrink
  the pull.
- Retries are built in, do not write your own. `Web.Contents` retries 408, 429, 503, 504, and 509
  up to three times with exponential back off, or waits for a `Retry-After` in seconds, from 0.5 to
  120. Those waits come out of the same budget.
  https://learn.microsoft.com/en-us/power-query/handling-status-codes
- Single calls and workbook reads usually get no `Timeout`, and a hung read costs as much, so decide
  it everywhere. Microsoft does not say whether the value covers a whole streaming download or only
  the wait for a first response, so test a large workbook.

## No paging is a decision, not a default

A single `Web.Contents` with no `sysparm_limit` and no loop returns the source's default row cap,
with no error when it truncates. Fine for a small reference table, silently wrong the day it grows.
If you skip paging, write the row count assumption in a comment next to the call.

## Reference fields come back as records

With `sysparm_display_value = "true"` a reference field arrives as a record, and sometimes as a
plain scalar depending on the field and the row. Flatten it before anything else touches it.

```m
  ToDisplayValue = (x as any) as any =>
    if Value.Is(x, type record) then Record.FieldOrDefault(x, "display_value", null) else x,

  RefColsWanted  = {"assigned_to", "assignment_group", "parent"},
  RefColsPresent = List.Intersect({Table.ColumnNames(Expanded), RefColsWanted}),
  FlattenRefs    = Table.TransformColumns(
    Expanded,
    List.Transform(RefColsPresent, each {_, ToDisplayValue, type text})
  ),
```

`Value.Is(x, type record)` handles the mixed case. `List.Intersect` means a field disappearing at
the source does not break the query. Keep `sysparm_exclude_reference_link = "true"` on. It stops
each reference arriving as a `{link, value}` pair and cuts payload.

## Building the filter from a table instead of one long string

Past a handful of filters, hand concatenation stops being reviewable. Hold them as data and
compile the encoded query.

```m
  FilterTable = Table.FromRows({
    {"assignment_group", "=",        "<sys_id>",       "OR"},
    {"assignment_group", "=",        "<sys_id>",       "OR"},
    {"short_description","NOT LIKE", "health check",   "AND"},
    {"parent_incident",  "ISEMPTY",  "",               "AND"}
  }, {"Field", "Operator", "Value", "Logic"}),

  ToFragment = (r as record) as text =>
    if r[Operator] = "ISEMPTY" then r[Field] & "ISEMPTY"
    else r[Field] & r[Operator] & r[Value],

  Encoded = List.Accumulate(
    {0 .. Table.RowCount(FilterTable) - 1},
    "",
    (state, i) =>
      let
        row    = Table.ToRecords(FilterTable){i},
        prefix = if i = 0 then "" else if row[Logic] = "OR" then "^OR" else "^"
      in
        state & prefix & ToFragment(row)
  ),

  FullQuery = Encoded & "^sys_created_on>=javascript:gs.dateGenerate('2025-01-01','00:00:00')"
                      & "^ORDERBYsys_id",
```

Every filter stays server side. It is a query string, not the URL, so the literal first argument
rule for `Web.Contents` is untouched. ServiceNow gotcha: `^OR` binds tighter than `^`, so row order
changes the meaning. Group the OR rows together and put them first, as above.

## What the source should be doing, not you

- `sysparm_fields` projects columns. Never pull a field you drop later.
- `sysparm_query` carries every filter you can express server side. Filtering in M after a full
  pull is the most common reason a REST model is slow.
- A date floor in the query string bounds a pull, but the window grows forever unless someone edits
  it. Keep the date in one named constant at the top. To stop re-pulling closed history,
  `RangeStart` and `RangeEnd` can go in the same query string, see `incremental-refresh.md`.

## Freezing history instead of re-pulling it

For a range that will never change again, a static blob costs nothing on every refresh. Power
Query writes this shape itself for Enter data.

```m
  Frozen = Table.FromRows(
    Json.Document(
      Binary.Decompress(
        Binary.FromText("<base64>", BinaryEncoding.Base64),
        Compression.Deflate)),
    {"Sprint", "Owner", "Planned Hours"})
```

This splits a pull in two: closed periods frozen in the model, a live query covering the open ones.
It is the manual version of incremental refresh, so read `incremental-refresh.md` first. Keep the
freeze for when the republish cost described there is unacceptable, because a frozen range survives
a republish and a partition does not.
