---
name: powerbi-project-and-tools
description: >-
  Work with the Power BI project files and the free external tools around a Pro model: the
  pbip project format, the TMDL model files, safe hand editing of those files, and the tools
  Tabular Editor 2, DAX Studio, VertiPaq Analyzer, Bravo, and Measure Killer. Also draws the
  license line, what runs on Pro versus what needs Premium or Fabric. Use whenever the user
  wants to edit the model files directly, open a pbip or TMDL folder, run the Best Practice
  Analyzer, check model size, find unused measures or columns, connect an external tool over
  XMLA, or asks what needs Premium. Trigger on phrases like "pbip", "TMDL", "edit the model
  files", "Tabular Editor", "DAX Studio", "VertiPaq Analyzer", "Bravo", "Measure Killer",
  "Best Practice Analyzer", "model size", "external tools", "XMLA", "what needs Premium",
  "licensing". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI project and tools

This skill covers the Power BI project files (pbip and TMDL) and the free external tools you
use around a model on Pro. It also draws the license line: what runs on Pro versus what needs
Premium or Fabric. This is the skill where the license boundary matters most. For the hard
facts, read `references/pro-vs-premium-facts.md` in this skill.

## When to use

Use this when the user wants to:

- Understand or hand edit the pbip and TMDL files that define a model.
- Pick or use a free tool: Tabular Editor 2, DAX Studio, VertiPaq Analyzer, Bravo, Measure Killer.
- Run the Best Practice Analyzer, check model size, or find unused measures and columns.
- Know what is Pro versus Premium versus Fabric, or whether an XMLA tool edit will work.

For M and refresh use `powerbi-data-and-refresh`. For star schema use `powerbi-modeling`. For
DAX use `powerbi-dax`. For report layout use `powerbi-report-design`. To stand up a documented,
redacted repo for a model use `powerbi-doc-repo`.

## The one license fact that trips people up

All the tools here edit your LOCAL pbip or pbix, and that works on Pro. Writing changes back to
a dataset already PUBLISHED in a Pro workspace needs the XMLA write endpoint, and XMLA write is
Premium, not Pro. So on Pro the loop is always: edit the local file with the tool, then
republish from Power BI Desktop. See `references/licensing-cheatsheet.md`.

## Workflow for a hand edit of the model files

1. Back up first. Copy the whole project folder, or commit to git, so you can revert.
2. Close Power BI Desktop before you touch the files. Desktop holds the model in memory and
   writes the TMDL files from memory when it saves. Edits made while it is open get clobbered.
   Newer builds prompt to apply edits they spot on disk, but closing first avoids the conflict
   rather than resolving it.
3. Make one minimal, targeted edit at a time. Change a single property or measure, then verify.
   Never change a repeated code idiom with a global search and replace. Measures share guard
   blocks, so an identical snippet often appears in four places and a replace all rewrites the
   three you did not mean. Nothing errors, because the result is still valid DAX. Split every
   edit at the measure boundary.
4. Keep the encoding UTF-8 without BOM and keep the CRLF line endings. Preserve the tab
   indentation. TMDL structure is whitespace significant, one tab per level.
5. Reopen in Desktop to verify. If an edit is invalid, Desktop refuses to open and names the
   file and the line of the error.

## Rules of thumb

- TMDL is the source of truth for the model. The `.pbi\cache.abf` is just cached data, not the
  definition. Edit the `.tmdl` files, not the cache.
- You can flip a table between an import (M) partition and a calculated (DAX) partition by editing
  TMDL, but only if you delete `.pbi\cache.abf` first so Desktop rebuilds fresh from the TMDL.
  Reopening with the cache in place fails on open with
  `PFE_TM_DDL_CHANGED_PARTITION_FROM_OR_TO_CALC`. This is the light way to kill refresh fan out. See
  `references/pbip-and-tmdl.md`.
- Deleting `.pbi\cache.abf` is also the safe move after any structural edit, adding or dropping
  a column or changing a partition source. Desktop then builds fresh from the TMDL instead of
  morphing stale cached data. The cost is one full refresh on the next open.
- Keep the pbip repo out of a OneDrive or SharePoint synced folder. OneDrive plus git in one
  folder can corrupt the repo, and Desktop cannot save a pbip cleanly into a synced folder.
- Pick the tool for the job. Bulk measure edits and the Best Practice Analyzer go to Tabular
  Editor 2. Model size and query timings go to DAX Studio with VertiPaq Analyzer. Quick size
  check, DAX formatting, and a Date table go to Bravo. Unused measures and columns go to
  Measure Killer. See `references/external-tools.md`.
- On Pro these tools edit the LOCAL file, then you republish. Connecting a tool to WRITE to a
  published dataset over XMLA is Premium.

## References in this skill

- `references/pbip-and-tmdl.md`: what the pbip format is, the folder and file layout, TMDL as
  the source of truth, safe hand editing rules, query groups, the lineageTag uniqueness rule,
  and the OneDrive and path length traps.
- `references/calculated-table-conversion.md`: the full procedure for flipping a table from an M
  partition to a calculated one to kill refresh fan out, with the cache deletion step and the two
  column lineage traps that stop the model opening.
- `references/external-tools.md`: the free Pro friendly tools, what each is for, and the XMLA
  write boundary repeated clearly.
- `references/licensing-cheatsheet.md`: a compact Pro versus Premium versus Fabric table.

## Related

- `references/pro-vs-premium-facts.md`: the full, verified license facts with Microsoft sources.
- `powerbi-data-and-refresh`: the refresh troubleshooting playbook once VertiPaq Analyzer or the
  per table timer shows you the culprit.
- `powerbi-doc-repo`: documenting a model end to end in a redacted, shareable repo.
