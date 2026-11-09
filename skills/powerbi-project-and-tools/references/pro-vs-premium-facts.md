# Power BI Pro vs Premium: verified facts

The skills assume Power BI Pro only. No Fabric, no Premium, no Premium Per User. Trust this file and
the linked Microsoft docs over memory or old blog posts, and check it against each month's release
(https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new), because limits move.

## What Pro gives you

- Model size up to 1 GB per semantic model. The pbix upload cap is also 1 GB.
- Scheduled refresh up to 8 times per day, at least 30 minutes apart. Manual refreshes
  from the browser do not count. Refreshes triggered by the REST API do count.
- A refresh is capped at 2 hours per attempt, across all the work in the attempt. Past 2 hours it
  is cancelled and fails. This is the most common cause of a Pro model that "will not refresh"
  (see the `powerbi-data-and-refresh` skill).
- Incremental refresh IS supported on Pro. Set it up with RangeStart and RangeEnd parameters plus
  a date filter. It only helps if the filter reaches the source, so for non-folding REST or
  SharePoint sources you must inject the date range into the source query yourself. A republish
  wipes the partitions, and the metadata only way round that is Premium. See
  `incremental-refresh.md` in the `powerbi-data-and-refresh` skill.
- Web modeling on a published model (2026). See below.

## Web modeling on Pro

The Service's web modeling edits a published model in a Pro workspace, and through 2026 it grew to
cover relationships, DAX, Model Options, TMDL view on the web (preview), DirectQuery and composite storage modes, and a refresh of
one table or of data only.

- It needs Write on the model and the tenant setting for editing models in the Service.
- Edits save at once with no undo. Workspace version history is the only rollback.
- The next republish from Desktop overwrites them. Decide which copy is the source of truth. For a
  PBIP in git, that is the local copy, so a web edit has to be made again locally.
- Not supported: live connections, automatic aggregations, models not yet in enhanced metadata
  format. Power Query on the web is not available for incremental refresh models.
- External tools still cannot write to a published Pro model. That is the XMLA rule below.

## What needs Premium, Premium Per User, or Fabric (do not rely on these)

- Large models over 1 GB.
- Refresh runs longer than 2 hours (Premium capacity allows up to 5 hours, XMLA-triggered
  refresh has no cap).
- More than 8 scheduled refreshes per day (Premium and PPU allow 48).
- The real time or hybrid DirectQuery partition of incremental refresh ("get the latest
  data in real time"). The import part works on Pro, the real time part does not.
- XMLA endpoint write back. Read and write XMLA is Premium, PPU, or Embedded only. Tabular
  Editor, ALM Toolkit, and similar tools work fully against your LOCAL pbip or pbix file, but
  cannot edit a model already published to a Pro workspace.
- Dataflow Gen2, the Enhanced Compute Engine, computed and linked dataflow entities,
  DirectQuery over a dataflow, and dataflow level incremental refresh.
- Copilot, Direct Lake, Fabric Apps, translytical task flows, and deployment pipelines.

## Dataflow Gen1 on Pro: the trap to avoid

Dataflow Gen1 runs in Pro workspaces. Microsoft now calls it Legacy (end of active innovation, not
removed). The problem is a dataset that imports a Gen1 dataflow:

- There is no transactional link between the dataflow refresh and the dataset refresh. The
  dataset reads whatever the dataflow last stored.
- If the dataflow is mid refresh, partially failed, or not finished before the dataset refresh
  fires, the dataset pulls stale or partial data, or the refresh fails.
- Without the Premium compute engine, Gen1 transformations do not fold, so its refreshes are slow
  and timing collisions are common.

Sequencing is possible with Power Automate. A cloud flow triggers on "When a dataflow refresh
completes", checks that Refresh Status equals Success, and calls "Refresh a dataset". Both
connectors are Standard class. Microsoft names this as a scenario, though its walkthrough covers
the dataflow to dataflow case, so this is from Microsoft docs and not yet run on a real model.
Add a failure branch that tells someone. The costs:

- The dataset refresh is API triggered, so it counts against the 8 per day.
- It sends no failure email. Power BI does not email for refreshes started this way.
- There is still no transaction. A failed dataset refresh leaves new dataflow data under an old
  model.
- A shared dataflow times out at 2 hours per table and 3 hours per dataflow.
- Transferring ownership of a Gen1 dataflow invalidates its connections, and a new or renamed
  column does not reach the model until it is refreshed in Desktop and republished.

Guidance: avoid pushing a Gen1 dataflow into a model that also refreshes on a schedule unless the
fan out it removes is worth those costs. Do not sequence it on a clock gap, because scheduled
starts can slip by up to an hour. The clean fix (Gen2, staging in a lakehouse or warehouse) needs
Fabric or Premium.

A summary that feeds on several published models needs no dataflow and no sequencing. DirectQuery
to a published semantic model is Pro, and each source refresh shows up in the summary at once. See
`composite-over-published-models.md` in the `powerbi-data-and-refresh` skill.

## Calculated columns and tables: help or hurt

- Prefer computing a column upstream in M or at the source. Those columns compress better
  in VertiPaq and do not recompute on every refresh.
- Calculated columns compress worse and add to model size and refresh time. Use them only when the
  logic truly needs the model context.
- Calculated tables (a Date table, a bridge table) recompute on every refresh and do not fold.
  The test is whether the table re-derives from data already in the model, not its size. See the
  `powerbi-dax` skill.
- You CAN flip an existing table between an import (M) partition and a calculated partition by
  editing the TMDL, but only after deleting `.pbi\cache.abf`. Skip that and Desktop rejects the
  project on open with PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC. The GUI path (create the
  table fresh in Desktop, move relationships, measures, and visuals over, delete the old table)
  also works. Full method in `calculated-table-conversion.md` in this skill.

## Analytical and AI visuals: what is Pro safe

These run in the Power BI engine on the local model, not in Copilot, so they are Pro safe.

- Decomposition tree, including its High value and Low value AI splits: Pro.
- Key influencers: Pro. Limits: it does not run on a DirectQuery model or an Analysis Services
  live connection, and its categorical analysis needs implicit measures, so calculation groups
  disable that mode.
- Native small multiples: Pro. A formatting toggle on the cartesian charts, not a separate visual.
- The new card visual (`cardVisual`, general availability November 2025, replaces the old Card
  and Multi-row card) and the KPI visual: Pro.
- Q&A visual: deprecated in January 2026 and retiring in December 2026, replaced by Copilot,
  which Pro does not get. Do not build new work on it. Narrative values built with Q&A became read
  only in September 2026.
- Smart narrative: Custom mode (you author the dynamic text) is Pro. Copilot authored narrative
  needs Fabric or Premium.

The `powerbi-report-design` skill has the how-to and a Pro vs Fabric table for these.

## Sources

- What's new in Power BI: https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new
- Configure incremental refresh and real-time data: https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview
- Data refresh in Power BI: https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data
- Large semantic models (Premium): https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-large-models
- Semantic model connectivity with the XMLA endpoint: https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools
- Dataflows considerations and limitations (Gen1 legacy): https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-features-limitations
- Differences between Dataflow Gen1 and Gen2: https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview
- Trigger dataflows and semantic models in sequence: https://learn.microsoft.com/en-us/power-query/dataflows/trigger-dataflows-and-power-bi-dataset-sequentially
