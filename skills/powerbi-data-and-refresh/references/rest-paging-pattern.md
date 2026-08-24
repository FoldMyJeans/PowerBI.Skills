# The REST paging pattern

The canonical loop for pulling a paged REST API into Power Query, plus the guards a production
pull needs. The guards are the part worth reading twice. A loop without them works on
the first run and fails quietly on the run that matters.

Hosts are placeholders. Replace `yourinstance` with the real value in your own model and keep
real hosts out of anything shared.

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
        Timeout      = #duration(0, 0, 10, 0),
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

`Table.ExpandRecordColumn` infers nothing from a zero row table, so a page past the end comes
back with no columns at all. `Table.Combine` then either errors or silently produces a table
missing columns, and the failure surfaces much later as a broken relationship or a blank
visual. Returning a hand declared `#table(Cols, {})` keeps every page schema identical, so the
combine is safe.

Declare the column list once as `Cols` and use it in all four places (the expand, the empty
branch inside `FetchPage`, the empty branch in the loop, and the empty branch in `Combined`). A
drifted copy of that list is the usual way this breaks after an edit.

There is one case the guard inside `FetchPage` cannot catch on its own. If the very first page
comes back empty, because a filter matched nothing, the loop's own condition is false on its
first evaluation, so `List.Generate` returns an empty list and no page is ever collected.
`Table.Combine` on an empty list gives a table with no columns, and every downstream step
fails on a column that is not there. That is why `Combined` tests `List.IsEmpty` first. A query
that legitimately matches no rows should produce an empty table with the right shape, not a
broken one.

## The row ceiling has to be loud

`PageSize * MaxPages` is a ceiling, and a ceiling you cross silently is worse than no ceiling.
Without the guard, a source that grows past it returns a short table, every measure keeps
working, every visual keeps rendering, and the numbers are quietly incomplete.

The guard is a single test: did we stop because we ran out of pages, and was the last page
still full? Either alone is fine. A full last page after a natural stop cannot happen, and
running out of pages on a short last page means the data ended where we did. Together they mean
there was more and we did not fetch it, so the refresh should fail and say so.

## Stop without a wasted request

The `next` function checks whether the page it already has came back short. If it did, the
next state is filled with an empty table and no request goes out. The alternative, fetching
first and testing afterwards, always spends one extra round trip discovering the end. On an
endpoint with a 10 minute timeout that one request is worth removing.

Do not write the loop so that it computes the next page before deciding whether to continue.

## Page size, and the symptom that means lower it

Start at 10000 for a ServiceNow Table API, which is also its own default cap for
`sysparm_limit`. That is a working production value, not a guess.

Lower it when you see "the operation was cancelled" or "the exception was raised by the
IDbCommand interface". Those mean the source could not assemble the page inside its own
transaction limit and cancelled it, which is more likely when `sysparm_display_value` is on
and the table has many reference fields. Drop to a few thousand and raise `MaxPages` by the
same factor so the row ceiling does not change. Silently truncating data is worse than a slow
refresh.

## Put a Timeout on every Web.Contents, not just the paged ones

`Timeout = #duration(0, 0, 10, 0)` makes a stalled request fail in 10 minutes instead of
creeping toward the Pro 2 hour cap. Paged pulls usually get one because the loop is where
people are thinking about performance. Single calls and workbook reads usually do not, and a
workbook read that hangs costs exactly as much refresh time. Add it everywhere.

## No paging is a decision, not a default

A single `Web.Contents` with no `sysparm_limit` and no loop returns whatever the source's
default row cap is, with no error when it truncates. That is fine for a small reference table
and silently wrong the day the table grows. If you skip paging, write the row count assumption
in a comment next to the call so the next person can check it.

## Reference fields come back as records

With `sysparm_display_value = "true"` a reference field arrives as a record, not text, and
sometimes as a plain scalar depending on the field and the row. Flatten it before anything
else touches the column.

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

`Value.Is(x, type record)` handles the mixed case. `List.Intersect` against the real column
names means a field disappearing at the source does not break the query.

`sysparm_exclude_reference_link = "true"` is what stops each reference arriving as a
`{link, value}` pair, so keep it on. It cuts payload as well as work.

## Building the filter from a table instead of one long string

Once a pull carries more than a handful of filters, concatenating them by hand stops being
reviewable. Hold them as data and compile the encoded query.

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

Every filter stays server side, which is the whole point. This is a query string and not a
URL, so the literal first argument rule for `Web.Contents` is untouched.

One ServiceNow gotcha to know: `^OR` binds tighter than `^`, so the order of the rows changes
the meaning. Group the OR rows together and put them first, as above.

## What the source should be doing, not you

- `sysparm_fields` projects columns. Never pull a field you drop later.
- `sysparm_query` carries every filter you can express server side. Filtering in M after a
  full pull is the most common reason a REST model is slow, because nothing folds.
- A date floor in the query string is the practical alternative to incremental refresh on a
  non folding source. It works, and the cost is that the window grows forever unless someone
  edits it. Put the date in one named constant at the top so that edit is one line.

## Freezing history instead of re-pulling it

For a range that will never change again, a static blob costs nothing on every refresh.
Power Query writes this shape itself when you use Enter data, and it holds a surprising amount.

```m
  Frozen = Table.FromRows(
    Json.Document(
      Binary.Decompress(
        Binary.FromText("<base64>", BinaryEncoding.Base64),
        Compression.Deflate)),
    {"Sprint", "Owner", "Planned Hours"})
```

Used well, this splits a pull in two: closed periods frozen in the model, and a live query
that only has to cover the open ones. It is the poor version of incremental refresh, and on a
non folding source it is often the only version available.
