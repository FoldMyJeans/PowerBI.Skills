# Test backlog

Maintainer material, not loaded by the skills. These are things the November 2026 research pass did
not write up, or wrote up only with a caveat, because they need a real test. Each entry has the exact
test. Run it, record the number or the error string, then write the finding into the owning skill
through a pull request and delete the entry.

Run tests on a throwaway PBIP with fake data, in a dev workspace on Pro. Microsoft Learn pages are read
as facts and reworded. Ideas taken from other repos note their license, so check it before reusing any
text. An MIT repo needs attribution. The data-goblin terms ask for attribution and a link even when an
agent rewrites the content, so take no wording or structure from it.

## Refresh

### Refresh execution metrics on Pro (highest value)

- **Question:** Do the refresh details page and Get Refresh Execution Details return attempt level
  metrics on a Pro workspace? `refresh-cost-model.md` says per table timings need XMLA or Log Analytics,
  and `refresh-troubleshooting.md` says the details list per table durations where available. They
  disagree, and neither is tested. Microsoft says the details page shows metrics that previously needed
  Log Analytics, but does not name Pro, and its API sample shows a roughly 5 hour timeout, so it was not
  captured on Pro.
- **Test:** One manual refresh on a Pro workspace model. Open the Refresh details link from the semantic
  model refresh settings and select Show under Execution details. Call Get Refresh History for the
  `requestId`, then Get Refresh Execution Details for that id. Record whether `executionMetrics` comes
  back with `externalQueryExecutionTimeMs` and `vertipaqJobCpuTimeMs`. If it does, compare those two
  before and after a calculated table conversion, and read `approximatePeakMemConsumptionKB` over a week
  of runs. Also record whether the page renders at all in a tenant with no Fabric capacity.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-execution-details

### A parameter as the base URL of Web.Contents

- **Question:** `connecting-to-sources.md` says a parameter in the first argument fails in the Service.
  Microsoft lists a web service URL as a dynamic source, then says queries that reference Power Query
  parameters can also be refreshed. That sentence is general, so the rule stands until tested.
  Concatenating a parameter into a URL is not covered by it either way.
- **Test:** On a dev workspace copy, set `Web.Contents(BaseUrlParam, [RelativePath = ..., Query = ...])`.
  Check Data source settings, Data sources in current file, for the dynamic source warning. Publish, set
  credentials, schedule a refresh. Change the parameter in the semantic model settings and refresh again.
  Record both results.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data

### Does Gen1 fold without the compute engine

- **Question:** `pro-vs-premium-facts.md` says Gen1 transformations do not fold without the Premium
  compute engine. The limitations page ties that engine to linked and computed tables, and does not say
  source folding stops. Left as written until tested.
- **Test:** Build a Pro Gen1 dataflow over a foldable source such as a SQL database. Filter and select
  columns, then trace the query at the source. Record whether the filter arrived in the source query.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-features-limitations

### Per table durations in the Service

- **Question:** `refresh-troubleshooting.md` says the failed run lists "where available, per table
  durations". The non enhanced API sample shows no per table timing, and the `objects` array appears only
  in the enhanced samples.
- **Test:** Same run as the execution metrics test. Record whether any per table figure appears on the
  page or in the API. Fix whichever line turns out wrong.
- **Source:** Microsoft Learn, as above.

### The separate cache quote

- **Question:** `refresh-cost-model.md` and `folding-and-duplication.md` quote Microsoft on each query
  having its own separate cache in a cloud environment. The November 2026 pass did not find that sentence
  on the referencing queries page or the data refresh page. The nearest found was a Microsoft staff forum
  answer. The idea stands, the attribution does not yet.
- **Test:** A source check, not a model test. Search Learn for the exact sentence. Add its URL, or
  reattribute it to https://community.fabric.microsoft.com/t5/Power-Query/Persistent-Cache-in-Power-BI-Service/m-p/2306003
- **Source:** Microsoft Learn and Microsoft Fabric community.

### The 30 minute gap

- **Question:** `pro-vs-premium-facts.md` and `refresh-troubleshooting.md` say scheduled refreshes must be
  at least 30 minutes apart. The two Microsoft pages that give the limit of 8 do not say it. It is probably
  the time slot granularity in the settings page.
- **Test:** In the Service, try to add two slots less than 30 minutes apart, and call the refresh schedule
  API with the same values. Record what each allows, then source the line or drop it.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh

### What the client Timeout really does

- **Question:** Microsoft gives the 100 second default, but does not say whether a timed out call is
  retried, or whether the value covers a whole streaming download. `rest-paging-pattern.md` attributes "the
  operation was cancelled" to the source, which may be only partly right.
- **Test:** Remove `Timeout` from one slow paged query and from one large workbook read. Refresh in Desktop
  and in the Service. Record the error string and the time it fails. Compare with `Timeout` at 10 minutes.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/powerquery-m/web-contents

### Incremental refresh on a real REST source

- **Question:** `incremental-refresh.md` is from docs. Does the policy dialog enable with the parameters
  only in a `Query` record, how many requests does a paged pull make per partition, and how long does a
  republish reload take?
- **Test:** Add the bounds to one paged fact query, with a 2 day Desktop window. Check with Query
  Diagnostics that `sysparm_query` carries the dates. Publish a copy, run a manual first refresh, and compare
  the second refresh duration and request count with the full pull. Then make a trivial model edit, republish,
  and record that history is gone and how long the reload takes. Partition on the open date, update a ticket
  after its partition left the window, and check for the stale value. Delete a row inside and outside the
  window and record what the model shows. Publish a thin report separately, edit only the report, and check
  the partitions survive.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview.
  The deleted rows point in the research notes cited Tabular Editor's docs, and that page does not cover it,
  so the file reasons from partition behaviour instead.

### Dataflow chained with Power Automate

- **Question:** How stable is the chain on Pro in daily use? Microsoft's walkthrough covers dataflow to
  dataflow only.
- **Test:** Move the staging query with the worst runs per refresh count into a Gen1 dataflow. Add the flow
  with a failure branch. Compare request count and Service duration over a week, including one forced dataflow
  failure. Check the model refresh counts against the 8.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-query/dataflows/trigger-dataflows-and-power-bi-dataset-sequentially

### Schedule and failure behaviour

- **Test:** In a dev workspace, force 4 failures with a bad parameter. Record the deactivation and the email.
  Scan refresh history through the API for credential errors and how long each attempt ran. Clustering around
  60 minutes is the token expiry signature. Check whether it happens on a `Web.Contents` workbook read.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios

### Excel and SharePoint.Contents timing

- **Question:** The sheet layout measurement was on local disk. A claim that `SharePoint.Contents` avoids
  enumerating a whole site has only forum support, so it is not in the skill.
- **Test:** Copy a business owned workbook, move the source table to its own sheet, and time it in the Desktop
  refresh dialog over a direct SharePoint URL. Time `SharePoint.Files` against `SharePoint.Contents` for the same
  folder on a large site.
- **Source:** Chris Webb, https://blog.crossjoin.co.uk/2023/11/12/excel-workbook-layout-and-the-performance-of-reading-data-with-power-query-in-power-bi/,
  and a Microsoft Fabric community thread, https://community.fabric.microsoft.com/t5/Power-Query/SharePoint-to-Power-BI-API-15/m-p/4790091

### OData options

- **Test:** On any OData source, compare the default against `OmitValues = ODataOmitValues.Nulls`, then
  `Implementation = "2.0"`, then `Concurrent = true`, on one table. Use the Desktop timer and the Content length
  column in Query Diagnostics.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/powerquery-m/odata-feed

### Query Diagnostics on a full refresh

- **Question:** Microsoft's page speaks of full refresh support as future, while its options text implies a full
  refresh trace works unless the non admin setting is selected.
- **Test:** Run diagnostics during a Desktop model refresh with the setting on and off, with parallel loading on and
  off. Count requests per query against the grep count in `folding-and-duplication.md`.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-query/query-diagnostics

## Modelling and DAX

### Duplicate and blank keys

- **Test:** Append one duplicate key row to a dimension source on a copy, refresh in Desktop, and capture the exact error
  string for `relationships.md`. Repeat with a null key and `Is Nullable` off, then read the TMDL back to get the real
  shape.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many

### ISINSCOPE and custom totals

- **Test:** Take the capacity ratio measure, slice to one sprint, and put it on a card and in a matrix grouped by something
  else. Compare the HASONEVALUE and ISINSCOPE variants. Then try the Average custom total on the matrix against the AVERAGEX
  branch.
- **Source:** SQLBI, https://www.sqlbi.com/articles/distinguishing-hasonevalue-from-isinscope/

### Functions and calculation groups on a Pro workspace

- **Test:** On a copy, define one function in DAX query view and call it from a measure. Save, then read `functions.tmdl` and
  the compatibility level back. Open it in Tabular Editor 2. Publish to a Pro workspace, open the report, and schedule a
  refresh. Check whether a function can be hidden. Separately, add a two item calculation group to a copy with SVG and title
  measures present, open every page, and record which visuals error. Read the TMDL back.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions.
  daxlib/daxlib (MIT per GitHub) for ideas only: https://github.com/daxlib/daxlib

### Value filter behavior

- **Test:** Read `model.tmdl` on a new and an old project for the property, by toggling it in Desktop and reading it back.
  Snapshot a set of measures with two same table slicers in DAX query view, switch to Independent, and diff the results.
  Settle which default a new model gets.
- **Source:** Microsoft Learn and SQLBI, which disagree, https://learn.microsoft.com/en-us/power-bi/transform-model/value-filter-behavior
  and https://www.sqlbi.com/articles/understanding-value-filter-behavior-in-summarizecolumns/

### Date table and time intelligence

- **Test:** Trim a date table to mid year, check marking still passes, then compare a YTD and a prior year total against a full
  year table. Remove a date from a marked table and record whether classic functions throw an error or return blank, because
  `patterns.md` says blank or wrong and Microsoft says an error. Run `Sales PY (Fair)` from `time-intelligence.md` on data ending
  mid month. Add RLS on a dimension and call USERELATIONSHIP, capturing the error.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-time-intelligence, and for the
  idea, https://www.daxpatterns.com/standard-time-related-calculations/ (all rights reserved, write our own form).

### Limited relationships

- **Test:** Build a category grain target two ways on a copy, many to many and TREATAS. Compare totals with an orphan row present,
  where the limited relationship should drop it silently, and compare Server Timings in DAX Studio.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand

### RANK, window functions, visual calculations

- **Test:** Rerun the leaderboard rank in `scoring-and-pagination.md` on tied data with RANK and RANKX. Count rows per page and compare
  Server Timings. Create one visual calculation in Desktop, read `visual.json` back, and export the visual's data to check the column
  is absent.
- **Source:** SQLBI, https://www.sqlbi.com/articles/introducing-the-rank-window-function-in-dax/, and Microsoft Learn.

### Calendar based time intelligence

- **Test:** Only once it is generally available, or on a throwaway copy. Define a calendar on a sprint model in Desktop, read the TMDL
  back, and compare a prior period result with the current explicit key measure.
- **Source:** Microsoft Learn, https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-time-intelligence

### Model size and Best Practice Analyzer

- **Test:** Run VertiPaq Analyzer before and after setting `IsAvailableInMdx` false on hidden fact columns. Record hierarchy size, total
  size, and refresh time. Check Desktop keeps the property after a save, and rerun TREATAS measures and relationship keys. Run the full
  rule set in Tabular Editor 2 on real projects, tabulate hits by rule, and separate true faults from convention noise, then replace the
  expected list in `external-tools.md` with the result.
- **Source:** microsoft/Analysis-Services (MIT), https://github.com/microsoft/Analysis-Services/tree/master/BestPracticeRules.
  TabularEditor/BestPracticeRules has a Power BI rule file but no license reported, so reference only.

### Naming

- **Test:** Count visible objects with prefixes on a real model. Have a report author and an agent each find five fields. Log misses.
- **Source:** SQLBI and Tabular Editor, opinion on both sides.

## Agent tooling

### The completion loop

- **Test:** On a throwaway PBIP with fake data, break one visual on purpose (overlap, missing role). Check JSON parse passes, the screenshot
  shows the fault, and the agent fixes it from the picture. Introduce a fan out and check the DAX assertion fails while the visual still
  renders. Run with Desktop closed, and with an unfixable fault, and check it stops after one round. Do all of this on a Pro machine and
  record it, since the loop's Pro status rests on the prerequisites listing no capacity.
- **Source:** microsoft/skills-for-fabric (MIT), Mofaji/Agentic-PBIP-Template (MIT).

### What the CLIs do

- **Test:** Run `powerbi-report-author validate` over a report Desktop wrote, to measure false positives. Seed a bad property, a wrong enum,
  and a bad selector, and record which it catches. Run once with the network off. Mofaji says filter expression faults pass under `--no-schema`,
  which is untested. For `reload` on a TMDL change, compare the bare command, `--reload-with-model`, and a reopen, because the sources disagree.
  Check whether the bridge needs the Detect and reload external PBIP changes preview option. Read the `hasUnsavedChanges` flag on your build.
  Microsoft's report skill page also describes a headless browser fallback when Desktop is not installed. Check what that host needs, and whether
  it works with no workspace on Pro.
- **Source:** npm READMEs for @microsoft/powerbi-report-authoring-cli and @microsoft/powerbi-desktop-bridge-cli (both MIT).

### The modeling MCP

- **Test:** `--readonly` against a local PBIP. Time a measure audit against a TMDL grep, then check `git status` shows no changes. Check how it
  reports a TMDL syntax error on load.
- **Source:** microsoft/powerbi-modeling-mcp (LICENSE file MIT, separate proprietary EULA).

### A reviewed page spec before a build

- **Test:** Run the same brief with and without the review step on a fake model. Count rework edits.
- **Source:** microsoft/skills-for-fabric (MIT), Mofaji/Agentic-PBIP-Template (MIT), RuiRomano/pbip-demo-agentic (MIT).

### Write hook, off by default

- **Idea:** A fail open hook that catches a bad file at write time, inert outside a Power BI project, and that prints when it skipped a check.
- **Test:** On Windows with a project scoped hook, make 50 unrelated edits. Record noise, delay, and whether a bad `visual.json` gets flagged.
- **Source:** data-goblin/power-bi-agentic-development (GPL-3.0 plus an attribution notice, idea only, write our own). Its README lists open
  Claude Code Windows hook bugs. Mofaji/Agentic-PBIP-Template (MIT).

### Trigger evals

- **Idea:** Queries with an expected trigger, including near misses, for skill pairs that collide such as `powerbi-report-design` and
  `powerbi-pbir-builder`, or `powerbi-modeling` and `powerbi-dax`. Check whether `claude plugin eval` covers this before building a harness.
- **Test:** About 20 queries per skill, half near misses. Record the trigger rate, tighten descriptions, and rerun.
- **Source:** data-goblin/power-bi-agentic-development (GPL-3.0 plus an attribution notice, copy the idea of the shape only).

### A generalised static preflight script

- **Idea:** A script in `powerbi-project-and-tools/scripts` that catches load failures from source, because Desktop cannot serve a failed load
  over the bridge. Measure and column name collisions, duplicate names, relationship endpoints that do not exist, unresolved qualified DAX
  references, malformed filter expression keys, unregistered resources, duplicate page IDs, and every `Entity` and `Property` in `visual.json`
  existing in the TMDL. Split per edit checks from whole model checks.
- **Test:** Seed each fault into a copy of a PBIP, check the script names it, then check Desktop rejects the same copy.
- **Source:** Mofaji/Agentic-PBIP-Template (MIT), MinaSaad1/pbi-cli (MIT). Write our own.

### fab-inspector

- **Idea:** Deterministic report rules run locally, which could turn the accessibility greps into rules.
- **Test:** Run the base rules on a report with known alt text gaps. Add one house rule, such as hex colors in `visual.json`.
- **Source:** NatVanG/fab-inspector (MIT), https://github.com/NatVanG/fab-inspector. Community project, local mode only for us.

### Headless Tabular Editor 2 Best Practice Analyzer

- **Idea:** Let an agent run the rules instead of a person. The demo script downloads latest releases unpinned, so pin versions and hashes in ours.
  The newer `te` CLI is a limited preview that will need a license, so it is out.
- **Test:** Run Tabular Editor 2 headless against a PBIP `definition` folder and compare results with the GUI. Check whether exit codes can gate a
  script.
- **Source:** RuiRomano/pbip-demo-agentic (MIT), TabularEditor/TabularEditor (MIT), microsoft/Analysis-Services (MIT).

### Template drift check

- **Idea:** Use the official visual catalog in `tools/check.ps1` to catch drift in the PBIR templates, with a dev dependency kept out of the shipped
  skill folders.
- **Test:** Validate every template against its declared schema, and list roles missing from the catalog.
- **Source:** @microsoft/powerbi-core-visual-schema (MIT), microsoft/json-schemas (MIT).

### Backup mechanics

- **Idea:** Turn "back up first" into a rule set: require a clean git tree before a batch, validate ID names, and re-read after writing. Any write
  guard needs an exception for the deliberate `cache.abf` delete.
- **Test:** Feed the check names with `..`, `CON`, and spaces, and a dirty tree.
- **Source:** HorizunGroup/horizun-pbi-mcp (Apache-2.0, ideas only, new and unproven), Mofaji/Agentic-PBIP-Template (MIT).
