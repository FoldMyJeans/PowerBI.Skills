# Power BI Pro vs Premium: verified facts

This repo assumes Power BI Pro only. No Fabric, no Premium, no Premium Per User. The
facts below are the load-bearing ones. A lot of older blog posts get them wrong, so trust
this file and the linked Microsoft docs over memory or old articles. Re-verify against
Microsoft Learn once a year, because limits move.

## What Pro gives you

- Model size up to 1 GB per semantic model. The pbix upload cap is also 1 GB.
- Scheduled refresh up to 8 times per day, at least 30 minutes apart. Manual refreshes
  from the browser do not count. Refreshes triggered by the REST API do count.
- A single refresh run is capped at 2 hours. If a refresh runs past 2 hours it is
  cancelled and fails. This is the single most common cause of a Pro model that "will not
  refresh" (see the data-and-refresh skill).
- Incremental refresh IS supported on Pro. You do not need Premium for it. Set it up with
  RangeStart and RangeEnd parameters plus a date filter. It only helps if the source folds
  the date filter, so for non-folding REST or SharePoint sources you must inject the date
  range into the source query yourself.

## What needs Premium, Premium Per User, or Fabric (do not rely on these)

- Large models over 1 GB.
- Refresh runs longer than 2 hours (Premium capacity allows up to 5 hours, XMLA-triggered
  refresh has no cap).
- More than 8 scheduled refreshes per day (Premium and PPU allow 48).
- The real time or hybrid DirectQuery partition of incremental refresh ("get the latest
  data in real time"). The import part of incremental refresh works on Pro, the real time
  part does not.
- XMLA endpoint write back. On Pro you cannot connect an external tool to a PUBLISHED
  dataset and write changes to it. Read and write XMLA is Premium, PPU, or Embedded only.
  Practical effect: Tabular Editor, ALM Toolkit, and similar tools work fully against your
  LOCAL pbip or pbix file, but cannot edit a model already published to a Pro workspace.
- Dataflow Gen2, the Enhanced Compute Engine, computed and linked dataflow entities,
  DirectQuery over a dataflow, and dataflow level incremental refresh.

## Dataflow Gen1 on Pro: the trap to avoid

Dataflow Gen1 runs in Pro workspaces. It still works, though Microsoft now calls it Legacy
(end of active innovation, not removed). The problem is what happens when a dataset imports
a Gen1 dataflow:

- There is no transactional link and no orchestration between the dataflow refresh and the
  dataset refresh. The dataset reads whatever the dataflow last stored.
- If the dataflow is mid refresh, partially failed, or has not finished before the dataset
  refresh fires, the dataset pulls stale or partial data, or the refresh fails.
- Without the Premium compute engine, Gen1 transformations do not fold, so its refreshes
  are slow and timing collisions are common.

This is inherent to Gen1 on Pro, not a setting you can fix. Guidance: avoid pushing a Gen1
dataflow into a model that also refreshes on a schedule. If you must use one, sequence it
by hand (refresh the dataflow first, leave a wide gap, then refresh the dataset) and accept
that it is fragile. The clean fix (Gen2, staging in a lakehouse or warehouse) needs Fabric
or Premium, which we do not have.

## Calculated columns and tables: help or hurt

- Prefer computing a column upstream in M or at the source. Those columns compress better
  in VertiPaq and do not recompute on every refresh.
- Calculated columns (DAX columns on a table) do not compress as well and add to model size
  and refresh time. Use them only when the logic truly needs the model context.
- Calculated tables (a Date table, a bridge table) are fine and common, but they recompute
  on every refresh and do not fold. Keep them small.
- You CAN flip an existing table between an import (M) partition and a calculated partition by
  editing the TMDL, but only if you delete `.pbi\cache.abf` first so Desktop builds the model
  fresh instead of morphing the cached one. Skip that step and it rejects the project on open
  with error PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC. The GUI path (create the table fresh
  in Desktop, move relationships, measures, and visuals over, delete the old table) also works.
  Full method and the column lineage gotcha are in `calculated-table-conversion.md` in this skill.

## Analytical and AI visuals: what is Pro safe

The native analytical and AI visuals confuse people, because "AI" sounds like Copilot. It is not.
These run their intelligence in the Power BI engine on the local model, so they are Pro safe.

- Decomposition tree, including its High value and Low value AI splits: Pro. In-engine, not
  Copilot.
- Key influencers: Pro. In-engine machine learning. Limits: it does not run on a DirectQuery model
  or an Analysis Services live connection, and its categorical analysis needs implicit measures, so
  calculation groups disable that mode.
- Native small multiples: Pro. A formatting toggle on the cartesian charts, not a separate visual.
- The new card visual (`cardVisual`, general availability November 2025, replaces the old Card
  and Multi-row card) and the KPI visual: Pro.
- Q&A visual: Pro today, but on a retirement path (around December 2026), replaced by Copilot. Do
  not build new work on it.
- Smart narrative: Custom mode (you author the dynamic text) is Pro. Copilot authored narrative
  needs Fabric or Premium.

The `powerbi-report-design` skill has the how-to and a Pro vs Fabric table for these.

## Sources

- Configure incremental refresh and real-time data: https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview
- Data refresh in Power BI: https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data
- Large semantic models (Premium): https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-large-models
- Semantic model connectivity with the XMLA endpoint: https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools
- Dataflows considerations and limitations (Gen1 legacy): https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-features-limitations
- Differences between Dataflow Gen1 and Gen2: https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview
