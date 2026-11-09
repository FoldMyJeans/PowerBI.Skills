# Connecting to sources

Which connector for which source, and the shape of a clean staging query. Hosts are
placeholders. Keep real hosts out of any shared or committed file. The paging loop is in
`rest-paging-pattern.md`, drift tolerant transforms in `m-hardening.md`.

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

For the direct URL, use the path from the browser or the Path field in the file details pane.
Not the share link with `?e=`, which is not a clean path. Percent encode spaces
(`Shared%20Documents`). Literal spaces also work, but one form per model keeps URLs greppable.

```m
// AVOID: REST GetFileById. The file id survives a move, but the credential test is fragile
// and often fails with a 400 on the data source setup.
Web.Contents("https://yourtenant.sharepoint.com/sites/Site",
  [RelativePath = "_api/web/GetFileById('<file-id>')/$value"])
```

Set a `Timeout` on a workbook read as on an API call. A hung download costs the same refresh
minutes. The default and the budget are in `rest-paging-pattern.md`.

### Kind is Sheet or Table, and they differ

`Excel.Workbook` returns both. A `Table` (a real Excel table object) arrives with correct headers.
A `Sheet` is the raw grid, so you promote headers yourself and own any title rows above the data.
Prefer a `Table` when the file has one.

### Sheet layout and file format change the read time

Chris Webb's measurements, not over SharePoint, so trust the direction more than the factor. From
local disk, a small Excel table on a sheet shared with a lot of other data took 4,918 ms against
63 ms on its own sheet, and being a real Excel table did not avoid it
(https://blog.crossjoin.co.uk/2023/11/12/excel-workbook-layout-and-the-performance-of-reading-data-with-power-query-in-power-bi/).
In an older test, the same data took 59 seconds from xlsx and 9 from CSV
(https://blog.crossjoin.co.uk/2018/08/02/comparing-the-performance-of-csv-and-excel-data-sources-in-power-query/).
Keep each source table on its own sheet, and when a process you control writes the file, write CSV.

### Parquet is not a Pro speed fix

The Parquet connector reads only from the local filesystem, Azure Blob Storage, and Azure Data Lake
Storage Gen2. Small files from elsewhere may work through `Binary.Buffer`, and larger ones fail with
`Parquet.Document cannot be used with streamed binary values`
(https://learn.microsoft.com/en-us/power-query/connectors/parquet). Chris Webb's 2021 tests against
ADLS Gen2 found combining files faster on CSV than on Parquet, with the Parquet gain coming only from
loading some columns, and no predicate pushdown
(https://blog.crossjoin.co.uk/2021/04/11/importing-data-from-adlsgen2-into-power-bi-summary-of-findings/).
For a generated extract on Pro, write CSV.

### Do not hardcode a sheet or table name a business user can edit

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
table. `Table.TransformColumnNames(..., each Text.Trim(_))` fixes headers with a trailing space.

Columns too. A business user inserts one worksheet column, every positional mapping to its right
(`Column8`, `Column9` renames) shifts by one, and nothing errors. The model reads wrong numbers
until somebody questions a total, which can take months. Map by header name whenever a header
exists. Where a headerless block forces positional names, assert that a known marker value sits
in its expected column and raise a clear `error` when it does not (the fail loud pattern in
`m-hardening.md`).

## OData

Use `OData.Feed` when the service really is OData, from the service root so Power Query can
navigate and filter from there. From Microsoft docs, not yet run on a real model here.

- `Timeout` defaults to 600 seconds on `OData.Feed`, not the 100 seconds of `Web.Contents`.
- `Concurrent` follows the service's `AsynchronousRequestsSupported` annotation, and runs
  sequentially if the service does not say.
- `OmitValues = ODataOmitValues.Nulls` and `Implementation = "2.0"` are worth testing one at a
  time. No published benchmark for either.
- If the URL is more than the service root, select Skip Test Connection when you set up refresh.
  The Service's credential test ignores the query options in the M.
- Joins with OData or Web sources can be slow enough for the host to close the connection, with
  `An existing connection was forcibly closed by the remote host`. Use a navigation column when
  you can, otherwise `Table.Buffer` the smaller query before the merge.
- On a SharePoint list or Project Online, a URL past about 2,100 characters fails with a 401.
  Start from the root endpoint and filter in Power Query.
- Microsoft Graph is not supported through this connector.

Sources: https://learn.microsoft.com/en-us/powerquery-m/odata-feed and
https://learn.microsoft.com/en-us/power-query/connectors/odata-feed

## Authentication notes (Pro)

- ServiceNow REST: Basic (user and password) or OAuth. Set it in Desktop, and again in the
  Service under the model's data source credentials.
- SharePoint, SharePoint files, Excel on SharePoint: Organizational account (OAuth).
- Set privacy levels consistently. Mismatched levels on two sources combined in one query throw a
  Formula.Firewall error. For a single tenant, Organizational on all sources is usually right, and
  it does not cause the "operation cancelled" timeout. The model level override and Desktop's July 2026
  preview firewall option are in `refresh-troubleshooting.md`.

## The literal first argument rule

The first argument to `Web.Contents` must be a constant. That is what lets the Service bind one
credential to one host and refresh on a schedule.

```m
Web.Contents("https://yourinstance.service-now.com", [RelativePath = ..., Query = ...])   // fine
WorkbookUrl = "https://yourtenant.sharepoint.com/sites/Site/File.xlsx",
Web.Contents(WorkbookUrl)                                                                  // also fine
Web.Contents("https://" & host & "/api/" & table)                                          // breaks in the Service
```

A `let` binding to a string constant is safe. What breaks is a URL the Service cannot resolve
without running the query: anything concatenated or read out of data. Keep everything variable in
`RelativePath` and `Query`.

## Parameters, and the one place they bite

Power Query parameters (Home, Manage Parameters) stop a host being hardcoded in 6 queries, and the
Service lets you change a parameter value in the semantic model settings without republishing.

Parameterize freely: page size, row limits, any `Query` record value, filter values, cutoff
dates, thresholds, the relative path when one host serves several tables, and `RangeStart` and
`RangeEnd`, which incremental refresh requires by name.

The exception: a parameter in the first argument to `Web.Contents`, or concatenated into the URL,
fails in the Service because the host cannot be resolved without running the query. It fails at
scheduled refresh, not in Desktop, so you will not see it while building. To swap environments,
branch across whole literal calls:

```m
// Each branch hands Web.Contents a literal, so the Service can still resolve both hosts.
Source = if UseTest
         then Web.Contents("https://test-instance.example.com", [RelativePath = RelPath, Query = Q])
         else Web.Contents("https://prod-instance.example.com", [RelativePath = RelPath, Query = Q])
```

## A clean staging query

Keep the raw pull in its own query, load disabled, do the reshape there, and let the model tables
build from it. Then count how many things reference it, because each reference re-runs it in full,
network calls included. The method is in `folding-and-duplication.md`.
