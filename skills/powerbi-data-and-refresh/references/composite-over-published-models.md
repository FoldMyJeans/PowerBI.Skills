# A summary report over published semantic models

The case: one summary report that reads a small KPI table from each of several models published
to the same Pro workspace. Each source model keeps its own refresh, and the summary reads them
live through DirectQuery. This is a composite model, and it runs on Pro.

## The shape that works

Each source model publishes one long KPI table as a DAX calculated table: `Date`, `KPI Name`,
`Value`, a few hundred rows. The summary reads each source through one expression:

```m
let
    Source = AnalysisServices.Database("powerbi://api.powerbi.com/v1.0/myorg/<Workspace>", "<SourceModel>"),
    Cubes = Table.Combine(Source[Data]),
    Cube = Cubes{[Id="Model", Kind="Cube"]}[Data]
in
    Cube
```

Desktop writes this into `expressions.tmdl` once a live connection becomes a composite model, for
example after a local table or a second source is added. With small in memory remote tables, a
page view costs a handful of DAX queries.

## Why this over the alternatives

| Option | Refresh order | Main cost |
| --- | --- | --- |
| Composite DirectQuery to each published model | None. A source refresh shows in the summary at once | The author consent prompt below. Viewers need Read on every source model |
| A Dataflow Gen1 holding the KPI rows | Dataflow, then model, no shared transaction, clock gaps slip | The KPI logic lives in DAX over loaded facts. Moving it to M means pulling the raw APIs again |
| Each source writes its rows to a SharePoint file through Power Automate, the summary imports | Source, then flow, then summary | No trigger exists for "semantic model refresh finished", so the chain needs polling or clock gaps |
| One combined model | One refresh | Every raw pull in one run under the 2 hour Pro cap, and a large rebuild |

Pick the SharePoint file route only when the report must go to people with no access to the source
models, or a frozen month end snapshot is needed. It is the only option that removes the Read need.

Whether a Dataflow Gen1 can read a published semantic model on Pro was not tested. Importing from a
semantic model goes through the XMLA endpoint, which Pro does not have, so plan as if it cannot.

## The "Potential security risk" prompt

A Desktop author prompt. Report viewers in the Service never see it.

- It appears when one visual query mixes several DirectQuery sources, and again after the composite
  PBIP is edited outside Desktop.
- The acceptance is stored as a signature in `.pbi/localSettings.json` that covers the file
  content. Any outside edit invalidates it.
- Desktop skips saving an unchanged file. So the author accepts, clicks any visual to make a change,
  then saves. Without the click the consent is lost on the next open.
- Only the report author accepts it. An agent must not click it through UI Automation. Batch edits
  into few rounds so the author accepts once per round.

Keep each measure, and each SVG image measure, reading one source only. A single SVG measure that
read three sources made Desktop stop on the prompt at every view. Split per source, the page
renders with no prompt.

## "Include tables added later" pulls in everything

Each DirectQuery expression carries two annotations in `expressions.tmdl`:

```tmdl
annotation PBI_IncludeFutureArtifacts = True
annotation PBI_RemovedChildren = [{"remoteItemId":{"analysisServicesObject":{"sourceName":null,"sourceLineageTag":"<remote table lineageTag>"}},"objectType":"Table"}]
```

- `True` adds every table the source model gains later, on the next open. In one summary report
  that pulled in 8 unused tables, among them a remote measure table holding 97 measures.
- A remote table whose name clashes with a local one gets a " 2" suffix (`dim_date 2`,
  `_Measures 2`).
- A hidden auto date/time table in a source model comes through too, as a DirectQuery proxy named
  `LocalDateTable_<guid>` with a relationship and a column variation on the local side. Turn auto
  date/time off in the source models.
- `PBI_RemovedChildren` lists remote tables the author chose not to include, keyed by the remote
  lineage tag. A local proxy table's `sourceLineageTag` is that remote tag.
- With the flag left at `True`, deleting an unwanted table by hand only makes Desktop add it back.

To drop unused remote tables: close Desktop and back up. Set `PBI_IncludeFutureArtifacts = False` on
each expression. For each table, read its `sourceLineageTag` and `expressionSource`, then append an
entry to that expression's `PBI_RemovedChildren` array. Then remove the table everywhere its name
appears, using the checklist in `removing-a-table-by-hand.md` in the `powerbi-project-and-tools`
skill. Check first that no visual reads the table.

## Guard against a KPI renamed upstream

Every card filters on a `KPI Name` string, so a renamed row in a source model gives a blank card
and no error. Add one check measure per source, reading only that source, on a hidden maintenance
page or a card the author looks at:

```dax
KPI Check Source A =
VAR __expected = DATATABLE ( "@Name", STRING, { { "<KPI one>" }, { "<KPI two>" } } )
VAR __missing =
    FILTER (
        __expected,
        VAR __n = [@Name]
        RETURN
            ISBLANK (
                CALCULATE (
                    COUNTROWS ( <KPI_TABLE> ),
                    REMOVEFILTERS ( <KPI_TABLE> ),
                    REMOVEFILTERS ( <date_table> ),
                    <KPI_TABLE>[KPI Name] = __n
                )
            )
    )
RETURN
    IF ( ISEMPTY ( __missing ), "All found", "Missing: " & CONCATENATEX ( __missing, [@Name], ", " ) )
```

`COUNTROWS` returns blank, not 0, on no rows, hence `ISBLANK`. One measure per source keeps the
consent prompt away.

## Reading a KPI row for a month

KPI rows sit on their own dates (a scan date, a month end), so a relationship from a month end
calendar often matches nothing. Read the latest row on or before the report month inside the
measure instead. The pattern is in `time-intelligence.md` in the `powerbi-dax` skill.

A related trap: a helper that reads `SELECTEDVALUE ( <KPI_TABLE>[KPI Name] )` under a calendar
filter returns blank once the relationship filters every row out, while the value measure that
removed that filter still shows a number. The label then formats wrong (a percent shown as "0").
Read the name outside the calendar filter, or do not drive formatting from the name.
