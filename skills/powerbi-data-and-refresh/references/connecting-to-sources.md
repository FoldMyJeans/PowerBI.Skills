# Connecting to sources

Which connector for which source, and the shape of a clean staging query. Hosts and names here
are placeholders. Replace `yourinstance` and `yourtenant` with the real values in the model, and
keep real hosts out of any shared or committed file.

For a paged REST API, the loop and its guards live in `rest-paging-pattern.md`. For
the defensive transforms that keep a query alive when a source drifts, see
`m-hardening.md`.

## Picking the connector

| Source | Use | Not |
| --- | --- | --- |
| REST or ServiceNow Table API | `Web.Contents` with a literal base URL, `RelativePath`, and `Query`, wrapped in the paging loop | One long concatenated URL string, which breaks credential binding in the Service |
| One Excel file on SharePoint | `Excel.Workbook(Web.Contents("<direct file url>"), null, true)` | `SharePoint.Files`, which crawls every file in the site first |
| Many files in one folder | `SharePoint.Files` filtered early, or `Folder.Files` on a synced path | A direct read per file, which does not scale |
| A file that moves or gets renamed | `SharePoint.Files`, accepting the crawl cost | A fixed path that breaks silently |
| An OData service | `OData.Feed` from the service root, see below | A hand paged `Web.Contents` |
| Closed history you do not want to re-pull | Incremental refresh with the range in the request (`incremental-refresh.md`), or a static blob when the republish cost is unacceptable | Re-pulling closed history on every refresh |

## Reading an Excel file on SharePoint

Read the file directly. Do not enumerate the site.

```m
// GOOD: direct file read, fast
let
  Source = Excel.Workbook(
    Web.Contents("https://yourtenant.sharepoint.com/sites/YourSite/Shared%20Documents/Folder/File.xlsx"),
    null, true),
  Table1 = Source{[Item = "TableName", Kind = "Table"]}[Data]
in
  Table1
```

```m
// BAD for a single file: SharePoint.Files crawls every file in the whole site first,
// which can run for many minutes and cause a multi hour refresh.
let
  Source = SharePoint.Files("https://yourtenant.sharepoint.com/sites/YourSite", [ApiVersion = 15]),
  File   = Source{[Name = "File.xlsx"]}[Content]
in
  File
```

To get the exact direct URL, open the file location in the browser and use the path, or in the
file details pane copy the Path field. Avoid the share link with the `?e=` parameter, it is not
a clean path. Percent encode the spaces (`Shared%20Documents`). Literal spaces also work in
practice, but one form per model keeps the URLs greppable.

Do not use the SharePoint REST API for a normal file read:

```m
// AVOID: REST GetFileById. The file id survives a move, but the credential test is fragile
// and often fails with a 400 on the data source setup.
Web.Contents("https://yourtenant.sharepoint.com/sites/Site",
  [RelativePath = "_api/web/GetFileById('<file-id>')/$value"])
```

Set a `Timeout` on a workbook read the same way you would on an API call. A hung download costs
the same refresh minutes as a hung request. The default and the budget are in
`rest-paging-pattern.md`.

### Kind is Sheet or Table, and they differ

`Excel.Workbook` returns both. A `Table` (a real Excel table object) arrives with headers already
correct. A `Sheet` is the raw grid, so you promote headers yourself and you own whatever title
rows sit above the data. Prefer a `Table` when the file has one.

### Sheet layout and file format change the read time

These are Chris Webb's measurements, not taken over SharePoint, so trust the direction more than
the factor. Read from local disk, a small Excel table on a sheet shared with a lot of other data
took 4,918 ms against 63 ms on its own sheet, and being a real Excel table did not avoid it
(https://blog.crossjoin.co.uk/2023/11/12/excel-workbook-layout-and-the-performance-of-reading-data-with-power-query-in-power-bi/).
In an older test that does not say where the files sat, the same data took 59 seconds from xlsx and
9 from CSV (https://blog.crossjoin.co.uk/2018/08/02/comparing-the-performance-of-csv-and-excel-data-sources-in-power-query/).
So keep each source table on its own sheet, and when a process you control writes the file, write
CSV.

### Parquet is not a Pro speed fix

Microsoft documents the Parquet connector as reading only from the local filesystem, Azure Blob
Storage, and Azure Data Lake Storage Gen2. Small files from elsewhere may work through
`Binary.Buffer`, at a possible performance cost, and larger ones fail with `Parquet.Document cannot
be used with streamed binary values` (https://learn.microsoft.com/en-us/power-query/connectors/parquet).
So Parquet on SharePoint is a small file trick. Chris Webb's 2021 tests, run against ADLS Gen2 rather
than local disk, found the generated code for combining files faster on CSV than on Parquet, and the
Parquet gain coming from loading only some columns, with no predicate pushdown
(https://blog.crossjoin.co.uk/2021/04/11/importing-data-from-adlsgen2-into-power-bi-summary-of-findings/).
For a generated extract on Pro, write CSV.

### Do not hardcode a sheet or table name a business user can edit

Four patterns for a workbook someone else maintains.

```m
// Pick the sheet by a predicate on its name, not by literal match
ActiveSheet = Table.SelectRows(Source,
  each [Kind] = "Sheet" and Text.Contains(Text.Lower([Name]), "active")){0}[Data],
```

```m
// Take the newest table when a new one appears each year (EPS_2026, EPS_2027, ...)
EPSNames  = Table.SelectRows(Source, each [Kind] = "Table" and Text.StartsWith([Item], "EPS_")),
TableName = List.Max(EPSNames[Item]),
Data      = Source{[Item = TableName, Kind = "Table"]}[Data],
Year      = try Number.FromText(Text.AfterDelimiter(TableName, "_"))
            otherwise error "Table name must end with a year like EPS_2026",
```

```m
// Find the header row inside a messy sheet instead of Table.Skip(n)
WithIndex = Table.AddIndexColumn(sheetData, "__idx", 0, 1, Int64.Type),
HeaderRow = Table.SelectRows(WithIndex,
              each Text.Trim(Text.From(Record.Field(_, Table.ColumnNames(sheetData){0}))) = "Company"),
HeaderIdx = if Table.RowCount(HeaderRow) = 0
            then error "Could not find a header row starting with 'Company'."
            else HeaderRow{0}[__idx],
Promoted  = Table.PromoteHeaders(Table.Skip(sheetData, HeaderIdx), [PromoteAllScalars = true]),
Trimmed   = Table.TransformColumnNames(Promoted, each Text.Trim(_)),
```

```m
// One sheet per year or region: fan out and combine in one workbook read
YearSheets  = Table.SelectRows(Source, each [Kind] = "Sheet" and IsYearSheet(Text.From([Item]))),
WithYear    = Table.AddColumn(YearSheets, "YearValue", each YearFromSheetName([Item]), Int64.Type),
Transformed = Table.AddColumn(WithYear, "Data2", each TransformSheet([Data], [YearValue]), type table),
Final       = Table.Combine(Transformed[Data2]),
```

`Table.Skip` with a hard coded number breaks the first time someone inserts a row above the
table. `Table.TransformColumnNames(..., each Text.Trim(_))` is the companion fix for headers
that carry a trailing space.

The same goes for columns. A business user inserts one worksheet column, every positional
mapping to its right (`Column8`, `Column9` renames) shifts by one, and nothing errors. The
model reads wrong numbers until somebody questions a total, which can take months. Map by
header name whenever a header exists. Where a headerless block forces positional names, assert
that a known marker value sits in its expected column and raise a clear `error` when it does
not, the fail loud pattern in the m-hardening reference of this skill.

## OData

Use `OData.Feed` when the service really is OData, and start from the service root so Power Query
can navigate and filter from there. This comes from Microsoft docs and has not yet been run on a
real model here.

- `Timeout` defaults to 600 seconds on `OData.Feed`, not the 100 seconds of `Web.Contents`.
- `Concurrent` follows the service's `AsynchronousRequestsSupported` annotation, and runs
  sequentially if the service does not say.
- `OmitValues = ODataOmitValues.Nulls` and `Implementation = "2.0"` are options worth testing one at
  a time. No published benchmark turned up for either.
- If the URL is more than the service root, select Skip Test Connection when you set up refresh. The
  Service's credential test ignores the query options in the M.
- Joins with OData or Web sources can be slow enough for the host to close the connection, with `An
  existing connection was forcibly closed by the remote host`. Use a navigation column when you can,
  otherwise `Table.Buffer` the smaller query before the merge.
- On a SharePoint list or Project Online, a URL past about 2,100 characters fails with a 401. Start
  from the root endpoint and filter in Power Query.
- Microsoft Graph is not supported through this connector.

Sources: https://learn.microsoft.com/en-us/powerquery-m/odata-feed and
https://learn.microsoft.com/en-us/power-query/connectors/odata-feed

## Authentication notes (Pro)

- ServiceNow REST: Basic (user and password) or OAuth. Set it once in Desktop, and again in the
  Service under the dataset's data source credentials.
- SharePoint and SharePoint files and Excel on SharePoint: Organizational account (OAuth).
- Set privacy levels consistently. When two sources are combined in one query, mismatched
  privacy levels throw a Formula.Firewall error. For a single tenant, Organizational on all
  sources is usually right, and it does not cause the "operation cancelled" timeout error. The
  model level override is in `refresh-troubleshooting.md`.

## The literal first argument rule, and its one safe exception

The first argument to `Web.Contents` must be a constant. That is what lets the Service bind one
credential to one host and refresh on a schedule.

```m
Web.Contents("https://yourinstance.service-now.com", [RelativePath = ..., Query = ...])   // fine
WorkbookUrl = "https://yourtenant.sharepoint.com/sites/Site/File.xlsx",
Web.Contents(WorkbookUrl)                                                                  // also fine
Web.Contents("https://" & host & "/api/" & table)                                          // breaks in the Service
```

A `let` binding to a string constant is safe, and it reads better when the same URL is used
twice. What breaks the Service is a URL it cannot resolve without running the query, which
means anything built by concatenation or read out of data. Keep everything variable in
`RelativePath` and `Query`.

## Parameters, and the one place they bite

Hardcoding a host in 6 queries means changing it in 6 places, and it guarantees that the
day you point at a test instance you will miss one. Power Query parameters (Home, Manage
Parameters) fix that, and the Service lets you change a parameter value in the semantic model
settings without republishing the file, which is the part that makes them worth setting up.

Parameterize freely:

- Page size, row limits, and any `Query` record value.
- Filter values, cutoff dates, and thresholds used in transformations.
- The relative path, when the same host serves several tables.
- `RangeStart` and `RangeEnd`, which incremental refresh requires by name.

The exception is the one the rule above already describes. A parameter in the first argument to
`Web.Contents` is the case that fails in the Service, because the analyzer cannot resolve the
host without running the query. Concatenating a parameter into the URL fails the same way, and
it fails at scheduled refresh rather than in Desktop, so you will not see it while building.

When you need to swap environments, branch across whole literal calls instead of
building a string:

```m
// Each branch hands Web.Contents a literal, so the Service can still resolve both hosts.
Source = if UseTest
         then Web.Contents("https://test-instance.example.com", [RelativePath = RelPath, Query = Q])
         else Web.Contents("https://prod-instance.example.com", [RelativePath = RelPath, Query = Q])
```

The repetition is the point. Each branch hands `Web.Contents` a literal it can resolve, which
is what a concatenated URL cannot do.

## A clean staging query

Keep the raw pull in its own query, load disabled, do the reshape there, then let the model
tables build from it.

Then count how many things reference it. A referenced query re-runs in full every time,
including its network calls, and that count is the number that decides your refresh time. The
counting method and what to do about it are in `folding-and-duplication.md`.
