---
name: powerbi-project-and-tools
description: >-
  Work with the Power BI project files and the free external tools around a Pro model: the
  pbip project format, the TMDL model files, safe hand editing of those files, and the tools
  Tabular Editor 2, DAX Studio, VertiPaq Analyzer, Bravo, and Measure Killer. Also draws the
  license line, what runs on Pro versus what needs Premium or Fabric. Use whenever the user
  wants to edit the model files directly, open a pbip or TMDL folder, run the Best Practice
  Analyzer, check model size, find unused measures or columns, connect an external tool over
  XMLA, tidy a tangled model view, or asks what needs Premium. Trigger on phrases like "pbip",
  "TMDL", "edit the model files", "model view", "arrange the model diagram", "diagramLayout", "Tabular Editor", "DAX Studio", "VertiPaq Analyzer", "Bravo", "Measure Killer",
  "Best Practice Analyzer", "model size", "external tools", "XMLA", "what needs Premium",
  "licensing", "Desktop Bridge", "modeling MCP", "verify the edit". Assumes Power BI Pro only, no
  Fabric or Premium.
---

# Power BI project and tools

Checked against Power BI releases through October 2026.

The pbip and TMDL files, the free external tools around a Pro model, and the license line. The
license facts live in `references/pro-vs-premium-facts.md`.

## When to use

- Understand or hand edit the pbip and TMDL files that define a model.
- Pick or use a free tool: Tabular Editor 2, DAX Studio, VertiPaq Analyzer, Bravo, Measure Killer.
- Run the Best Practice Analyzer, check model size, or find unused measures and columns.
- Untangle the model view so the relationships can be read and reviewed.
- Know what is Pro versus Premium versus Fabric, or whether an XMLA tool edit will work.
- Check an agent's edit: conformance validation, reload and screenshot through the Desktop Bridge,
  and the expected numbers asserted with DAX.

For M and refresh use `powerbi-data-and-refresh`. For star schema use `powerbi-modeling`. For
DAX use `powerbi-dax`. For report layout use `powerbi-report-design`. To stand up a documented,
redacted repo for a model use `powerbi-doc-repo`.

## The license fact that trips people up

External tools edit your LOCAL pbip or pbix, and that works on Pro. Writing from a tool to a model
already PUBLISHED in a Pro workspace needs the XMLA write endpoint, which is Premium. So with a tool
the Pro loop is: edit the local file, then republish from Desktop. The Service's own web modeling
can edit a published Pro model, with no undo, and the next republish overwrites it. See
`references/pro-vs-premium-facts.md`.

## Workflow for a hand edit of the model files

1. Back up first. Copy the project folder, or commit to git.
2. Close Power BI Desktop. It writes the TMDL from memory on save, so edits made while it is open
   get clobbered. The Desktop Bridge branch, with its own conditions, is in
   `references/agent-verification.md`.
3. One minimal edit at a time, then verify. Never change a repeated code idiom with a global
   search and replace. Measures share guard blocks, so an identical snippet often appears in four
   places and a replace all rewrites the three you did not mean. Nothing errors, because the
   result is still valid DAX. Split every edit at the measure boundary.
4. Keep UTF-8 without BOM, CRLF line endings, and one tab per indent level.
5. Reopen in Desktop. An invalid edit makes Desktop refuse to open and name the file and line.

## Rules of thumb

- TMDL is the source of truth. `.pbi\cache.abf` is cached data only. Edit the `.tmdl` files.
- Flipping a table between an M partition and a calculated partition needs `.pbi\cache.abf`
  deleted first, or the open fails with `PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC`. This is
  the light way to kill refresh fan out. See `references/calculated-table-conversion.md`.
- Delete `.pbi\cache.abf` after any structural edit too (a column added or dropped, a partition
  source changed). Desktop then builds fresh from the TMDL. The cost is one full refresh.
- Dropping a table means removing its name from every file it appears in. See
  `references/removing-a-table-by-hand.md`.
- Keep the pbip repo out of a OneDrive or SharePoint synced folder.
- Tool for the job: Tabular Editor 2 for bulk measure edits and the Best Practice Analyzer, DAX
  Studio with VertiPaq Analyzer for size and timings, Bravo for a quick size check, DAX formatting
  and a Date table, Measure Killer for unused measures and columns. See
  `references/external-tools.md`.
- A model view nobody can read is a model nobody reviews. Facts in one column, dimensions in one
  row. `scripts/arrange_model_diagram.py` applies it by rewriting box positions only. See
  `references/model-diagram-layout.md`.

## References in this skill

- `references/pbip-and-tmdl.md`: the folder and file layout, TMDL as the source of truth, safe hand
  editing rules, the 2026 PBIR conversion and reload preview, query groups, the lineageTag
  uniqueness rule, and the OneDrive and path length traps.
- `references/calculated-table-conversion.md`: flipping a table from an M partition to a calculated
  one, with the cache deletion step and the two column lineage traps that stop the model opening.
- `references/model-diagram-layout.md`: the facts in a column, dimensions in a row layout and the
  script that applies it to `diagramLayout.json`.
- `references/external-tools.md`: the free Pro friendly tools, Best Practice Analyzer conflicts to
  expect, cutting model size, the modeling MCP, the tool risk policy, and the XMLA write boundary.
- `references/agent-verification.md`: the completion loop for an agent's edit, when Desktop can stay
  open, the fix budget, and the fake data fixture.
- `references/removing-a-table-by-hand.md`: every file a table name lives in, and turning auto
  date/time off in a model that already has it.
- `references/offscreen-render.md`: rendering pages, refreshing over TMSL and saving with no window on
  the person's monitors, plus the UI Automation steps for opening a slicer in a picture.
- `references/licensing-cheatsheet.md`: the short Pro versus Premium versus Fabric table.
- `references/pro-vs-premium-facts.md`: the license facts, web modeling on Pro, and the Microsoft
  sources. Owner of every Pro limit in the skills.

## Related

- `powerbi-data-and-refresh`: the refresh playbook once VertiPaq Analyzer or the per table timer
  shows you the culprit.
- `powerbi-doc-repo`: documenting a model end to end in a redacted, shareable repo.
