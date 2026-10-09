# PBIP and TMDL

## What the PBIP format is

A `.pbix` is one binary file. Report and model are zipped together and you cannot diff it, merge
it, or edit it in a text editor.

A Power BI Project (PBIP) is the same content saved as a folder of plain text files instead. The
model and report metadata become human readable files in a simple folder tree. That makes them
diffable in git, mergeable, and editable in VS Code or any text editor. PBIP is still a preview
feature in Power BI Desktop. Turn it on under File, Options and settings, Options, Preview
features, then check the pbip save option and the option to store the semantic model using TMDL.

You save a pbip with File, Save as, and pick the Power BI Project type. You can convert a pbix
to a pbip and back through Save as in Desktop.

## The folder layout

A pbip for a project called `ABCSales` looks like this. Names are illustrative.

```text
ABCSales.pbip                      pointer file, opening it opens the report and model
ABCSales.SemanticModel/            the model
  definition.pbism                 model definition pointer and format version (required)
  definition/                      the TMDL model, THIS is the source of truth
    database.tmdl                  database name and compatibility level
    model.tmdl                     model level settings, default culture, and table order refs
    relationships.tmdl             every relationship in the model, one file
    expressions.tmdl               every shared expression, one file (see below)
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

What goes where in the model:

- A regular loaded table's M query lives inside that table's file, in its `partition` block, under
  `tables\<Table>.tmdl`.
- `expressions.tmdl` holds the model level shared expressions. That means parameters, and any
  query that is load disabled or shared as a staging query that other queries reference. These
  are stored once at the model level, not inside a table.
- `relationships.tmdl` holds all relationships, so a relationship change is one file to review.
- Columns, hierarchies, and partitions of a table all live inside that one table file, not in
  separate files.

## TMDL is the source of truth

TMDL (Tabular Model Definition Language) is a text format for the model, similar in feel to
YAML. Indentation with a single tab per level denotes the object tree. The files in the
`definition\` folder are what defines the model. The `cache.abf` in `.pbi\` is only a cached copy
of the data from the last edit, and it is git ignored. When you fix the model, you edit the
`.tmdl` files.

## Safe hand editing rules

1. Back up first. Copy the whole project folder, or commit to git, so you can revert cleanly.
2. Close Power BI Desktop before you edit. Desktop keeps the model in memory and rewrites the
   TMDL files from memory when it saves or applies. Any edit you make while it is open will be
   overwritten. Edit, save, then open Desktop.

   Newer Desktop builds do detect on-disk changes and offer to apply them, which is a preview
   feature. It does not change the rule. The prompt resolves a conflict after the fact, and the
   version in Desktop's memory is the one that wins if you get it wrong. Closing first means
   there is no conflict to resolve.
3. Make minimal, targeted edits. One property or one measure at a time, then verify. A small diff
   is easy to review and easy to revert.
4. Preserve line endings and encoding. Desktop writes CRLF and UTF-8 without BOM. A tool that
   rewrites the file as LF makes the whole file look changed in git and can confuse a merge. Set
   git `autocrlf` so line endings stay consistent.
5. Respect the indentation. TMDL is whitespace significant. One tab per level. A stray space, or
   a tab converted to spaces, breaks the parse.
6. Reopen in Desktop to verify. If an edit is invalid, Desktop refuses to open the project and
   points at the file and location of the error.

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

`__PBI_TimeIntelligenceEnabled = 0` is auto date/time turned off for this file, which is the
single highest value default in a model. See the `powerbi-data-and-refresh` skill for why.

A calculated partition must NOT carry a `queryGroup:` line. See
`calculated-table-conversion.md`.

## Converting a table between M and calculated

You can flip a table between an import (M) partition and a calculated (DAX) partition by editing
TMDL, and it is the light way to kill refresh fan out. It needs `.pbi\cache.abf` deleted first,
plus two lineage tricks, or the model will not open. The full procedure is in
`calculated-table-conversion.md`.

## Every lineageTag must be unique across the model

Every table, column, measure, and hierarchy carries a `lineageTag`, the GUID that binds it to the
report visuals and to relationships. That tag has to be unique across the whole model, not just
within its own table file.

This bites when you hand author a new table by copying an existing table file as a starting
point, because it is easy to rename everything and leave the tag block untouched. Desktop then
refuses to open the project at all:

```text
Failed to add a deserialized Table object into the model - name: 'Dim_Date', detailed error:
An object with lineage-tag '...' already exists in the collection.
```

The trap is the table name in that message. It is the table that deserialized FIRST with the
duplicated tag, not the new one you just added. So the error points at a file you never touched
and sends you debugging an innocent table. Go by the tag in the message, not the name, and find
both files that carry it.

Readable fake GUIDs are fine here, and they review better than real ones, for example
`7d000001-0000-4000-8000-000000000001`. Just give each table its own prefix, `7b...` for one
table and `7c...` for the next, so two hand authored tables can never collide.

Check before you open Desktop. Anything this returns is a duplicate, empty output is clean:

```powershell
Get-ChildItem .\ABCSales.SemanticModel\definition -Recurse -Filter *.tmdl |
  Select-String -Pattern "lineageTag:\s*(\S+)" |
  ForEach-Object { $_.Matches[0].Groups[1].Value } |
  Group-Object | Where-Object Count -gt 1
```

Report side ids follow a different rule, so do not go fixing those to match. The `name` on a
filter in a `visual.json` only has to be unique inside that one visual's `filterConfig`. Desktop
reuses the same id across visuals when you duplicate a visual, so duplicates there are normal.

## Other traps

- OneDrive. Keep the pbip repo out of a OneDrive or SharePoint synced folder. A git repo inside a
  synced folder is a known way to corrupt the repo, because OneDrive and git both churn the many
  small files under `.git`. Desktop also cannot save a pbip straight to OneDrive or SharePoint,
  and saving into a locally synced folder can make the save fail. Keep the working repo on a plain
  local path and push to the remote with git.
- Windows path length. A pbip stores many nested files. The default Windows path limit is 260
  characters. Long table names in a deep folder can push a file path past the limit and fail the
  save. Keep the root folder path short.
- The report side is the deep end of that limit. PBIR nests
  `<project>.Report\definition\pages\<20 hex id>\visuals\<20 hex id>\visual.json`, which adds
  roughly 70 characters beyond the project root before any file name. A project that saved fine
  can fail to OPEN after being moved or copied to a deeper folder (a OneDrive backup folder is
  the classic case). Desktop then shows "Issues were found", says it cannot read a visual.json,
  and names the 260 character limit. The fix is to move the whole project folder to a short
  local root, which also gets it out of OneDrive.
- Restart to see external edits. Newer builds prompt to apply changes they detect on disk, but
  a close and reopen after editing TMDL in VS Code is the path that cannot go wrong.
- Do not hand edit `diagramLayout.json` or the report layout files during preview. Those files
  are not documented for external editing. The one exception is box positions in
  `diagramLayout.json`, which `references/model-diagram-layout.md` covers along with its limits.

## See also

- `external-tools.md`: the tools that read and write these files.
- `licensing-cheatsheet.md`: the Pro versus Premium boundary.
- `powerbi-doc-repo`: turning a TMDL export into a documented, redacted repo.
