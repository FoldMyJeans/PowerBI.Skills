# PBIP and TMDL

## The format, and what 2026 changed

A Power BI Project (PBIP) is a pbix saved as a folder of text files, so git can diff and merge it.
Save with File, Save as, Power BI Project. Save as converts a pbix to a pbip and back. PBIP and PBIR
went GA in September 2026. If a build offers no project type or no TMDL `definition` folder, look
under File, Options and settings, Options, Preview features.

PBIR is now the report format inside a `.pbix` too. Saving a PBIR-Legacy report (a single
`report.json`) converts it silently, with no opt out. Desktop keeps the pre conversion copy for
30 days under `%USERPROFILE%\AppData\Local\Microsoft\Power BI Desktop\TempSaves\Backups`, and the
Service offers Restore as PBIR-Legacy for 28 days. `definition.pbir` `version` 4.0 or higher
allows the `definition` folder.

## The folder layout

Names are illustrative.

```text
ABCSales.pbip                      pointer file, opening it opens the report and model
ABCSales.SemanticModel/            the model
  definition.pbism                 model definition pointer and format version (required)
  definition/                      the TMDL model, THIS is the source of truth
    database.tmdl                  database name and compatibility level
    model.tmdl                     model level settings, default culture, and table order refs
    relationships.tmdl             every relationship in the model, one file
    expressions.tmdl               every shared expression, one file (see below)
    functions.tmdl                 DAX user defined functions, present only when the model has them
    tables/
      Fact_Sales.tmdl              one file per table: its columns, measures, hierarchies, and
      Dim_Date.tmdl                the partition that holds the table's M query
      Dim_Customer.tmdl
    cultures/                      one file per culture, present only with translations
    roles/                         one file per row level security role, present only with RLS
    perspectives/                  one file per perspective
  .pbi/                            local only, git ignored: localSettings.json and cache.abf
  diagramLayout.json               model diagram positions, see model-diagram-layout.md
  .platform                        item metadata, Desktop generates
ABCSales.Report/                   the report
  .platform                        item metadata, Desktop generates
  definition.pbir                  report pointer
  definition/                      report pages and visuals
.gitignore                         created by Desktop, ignores .pbi\cache.abf and localSettings.json
```

- A loaded table's M query lives in that table's `partition` block in `tables\<Table>.tmdl`.
  Columns, hierarchies, and partitions all live in that one table file.
- `expressions.tmdl` holds model level shared expressions: parameters, and load disabled or
  staging queries that other queries reference.
- `relationships.tmdl` holds all relationships, so a relationship change is one file to review.
- TMDL nests by indentation, one tab per level. `.pbi\cache.abf` is only cached data from the last
  edit, and it is git ignored. Fix the model in the `.tmdl` files.

## Safe hand editing rules

1. Back up first. Copy the project folder, or commit to git.
2. Close Power BI Desktop before you edit. Desktop rewrites the TMDL from memory when it saves or
   applies, so an edit made while it is open is overwritten.

   The preview switch "Detect and reload external PBIP changes" (August 2026) shows an Apply
   external changes banner after an outside save. It does not change the rule. Applying reloads
   the whole report or model, discards unsaved Desktop edits, and resets filters. While it is on
   you may not edit `definition.pbir`, `report.json`, `mobileState.json` or
   `semanticModelDiagramLayout.json` from outside, and a leftover `unappliedChanges.json` must be
   applied first or expression edits are lost. Closing first means there is no conflict to
   resolve. An agent running the Desktop Bridge has a second branch, with its own conditions, in
   `agent-verification.md`.
3. One property or one measure at a time, then verify.
4. Preserve line endings and encoding. Desktop writes CRLF and UTF-8 without BOM. A rewrite as LF
   makes the whole file look changed in git. Set git `autocrlf` so line endings stay consistent.
   Python in text mode reads CRLF as `\n`, so a check for `\r\n` is always false, and a rewrite
   can come back LF only. Read and write bytes, or open with `newline=''`. If a TMDL file you meant
   to leave alone differs only in line endings, restore the original instead of committing it.
5. One tab per level. A stray space, or a tab converted to spaces, breaks the parse.
6. Reopen in Desktop. An invalid edit makes it refuse to open and point at the file and location.

## What a Desktop save does to files you wrote

- Desktop rewrites every PBIR file on save, formatting only. Parsed as JSON, hand written files
  came back identical, apart from one empty `visualContainerObjects` it dropped. TMDL files gain
  `lineageTag` lines.
- So when shipping a working copy into the real project, compare by parsed JSON content, not by
  bytes. Copy new and changed files, delete the files removed in the copy, and leave the rest.
- Deleting a `visual.json` is safe. Desktop opens the page and removes the empty visual folder on
  its next save. Empty page or visual folders left behind do not stop the report opening.

## Expressions that stopped a project opening

Two hand written shapes made Desktop refuse to open a project: a calculated column expression split
over several lines, and a one line `formatStringDefinition` on a measure. The fenced block form of
`formatStringDefinition` loaded. Write a calculated column on one line, a format string definition
in the fenced form, and copy any other multi line shape from a file Desktop wrote.

## Query groups organize the model files

`model.tmdl` declares the Power Query query groups, and each partition names the group it belongs
to. A backslash makes a nested group, and `PBI_QueryGroupOrder` restarts at 0 inside a nest.

```tmdl
queryGroup 00_Admin
	annotation PBI_QueryGroupOrder = 0
queryGroup 02_Staging
	annotation PBI_QueryGroupOrder = 2
queryGroup 04_Model\Dimensions
	annotation PBI_QueryGroupOrder = 0
queryGroup 04_Model\Facts
	annotation PBI_QueryGroupOrder = 1

annotation __PBI_TimeIntelligenceEnabled = 0
```

`__PBI_TimeIntelligenceEnabled = 0` is auto date/time off for this file. See the
`powerbi-data-and-refresh` skill for why it matters.

A calculated partition must NOT carry a `queryGroup:` line. Flipping a table between M and
calculated needs `.pbi\cache.abf` deleted and two lineage tricks. See
`calculated-table-conversion.md`.

## Every lineageTag must be unique across the model

Every table, column, measure, and hierarchy carries a `lineageTag`, the GUID that binds it to
visuals and relationships. It must be unique across the whole model, not just its own table file.

This bites when you copy an existing table file to start a new one and leave the tag block
untouched. Desktop then refuses to open the project:

```text
Failed to add a deserialized Table object into the model - name: 'Dim_Date', detailed error:
An object with lineage-tag '...' already exists in the collection.
```

The table named is the one that deserialized FIRST with the duplicated tag, not the new one. So
the error points at a file you never touched. Go by the tag in the message and find both files
that carry it.

Readable fake GUIDs are fine, for example `7d000001-0000-4000-8000-000000000001`. Give each table
its own prefix (`7b...`, `7c...`) so two hand authored tables can never collide.

Check before you open Desktop. Anything this returns is a duplicate, empty output is clean:

```powershell
Get-ChildItem .\ABCSales.SemanticModel\definition -Recurse -Filter *.tmdl |
  Select-String -Pattern "lineageTag:\s*(\S+)" |
  ForEach-Object { $_.Matches[0].Groups[1].Value } |
  Group-Object | Where-Object Count -gt 1
```

Report side ids follow a different rule, so do not fix those to match. A filter `name` in a
`visual.json` only has to be unique inside that visual's `filterConfig`. Desktop reuses the same id
when you duplicate a visual, so duplicates there are normal.

## Other traps

- OneDrive. Keep the pbip repo out of a OneDrive or SharePoint synced folder. OneDrive and git both
  churn the small files under `.git`, which can corrupt the repo. Desktop also cannot save a pbip
  straight to OneDrive or SharePoint, and saving into a locally synced folder can make the save
  fail. Work on a plain local path and push with git.
- Windows path length. The default limit is 260 characters. PBIR nests
  `<project>.Report\definition\pages\<20 hex id>\visuals\<20 hex id>\visual.json`, roughly 70
  characters beyond the project root before any file name. A project that saved fine can fail to
  OPEN after being moved to a deeper folder (a OneDrive backup folder is the classic case). Desktop
  shows "Issues were found", says it cannot read a visual.json, and names the 260 character limit.
  Move the whole project to a short local root. Long table names in a deep folder can also fail
  the save, so keep the root path short from the start.
- Do not hand edit `diagramLayout.json`, `semanticModelDiagramLayout.json`, `mobileState.json`, or a
  PBIR-Legacy `report.json`. Microsoft lists those as not supported for external editing. The one
  exception is box positions in `diagramLayout.json`, covered with its limits in
  `model-diagram-layout.md`.

## See also

- `external-tools.md`: the tools that read and write these files.
- `pro-vs-premium-facts.md`: the Pro versus Premium boundary.
- `powerbi-doc-repo`: turning a TMDL export into a documented, redacted repo.
