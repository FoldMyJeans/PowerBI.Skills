# Removing a table by hand

A table's name lives in several files besides its `.tmdl`. A leftover reference either stops the
project opening or leaves a dangling hierarchy on a visual. This is the checklist, plus turning auto
date/time off in a model that already has it.

## Before you start

Close Desktop. Back up the project folder or confirm it is committed. Grep the `.Report` folder for
the table name. A table some visual uses has to be replaced on that visual before it can go.

## Every file a table name can appear in

1. `definition/tables/<table>.tmdl`. Delete it.
2. `model.tmdl`. Remove its `ref table` line. A name with a space is quoted
   (`ref table 'dim_date 2'`). A name made of letters, digits, hyphens and underscores is not
   (`ref table LocalDateTable_<guid>`). A script that quotes on any non word character gets the
   second one wrong, because a hyphen is not a word character.
3. `relationships.tmdl`. Remove every relationship whose `fromColumn` or `toColumn` names the table.
4. Column `variation` blocks on other tables. A variation names a relationship, and it breaks once
   that relationship is gone. Remove the whole `variation` block.
5. `diagramLayout.json`. Remove the table's node. The node's `nodeIndex` is the table name.
6. `cultures/<culture>.tmdl`. The Q&A linguistic schema holds entities bound to the table, its
   columns and its hierarchies, plus relationships between those entities. Remove both.
7. The report. A field used through a hierarchy has a `queryRef` like
   `<table>.<column>.Variation.Date Hierarchy.Year`. A visual can also keep `expansionStates` that
   point at a table that no longer exists.
8. Grep the whole project, report folder included, for the table name. Nothing should remain.
9. Delete `.pbi\cache.abf` so Desktop builds from the TMDL. The first open then needs a refresh.

For a remote table in a composite model, also add it to `PBI_RemovedChildren` and set
`PBI_IncludeFutureArtifacts` to False first, or Desktop adds it back on the next open. See
`composite-over-published-models.md` in the `powerbi-data-and-refresh` skill.

## Turning auto date/time off in an existing model

Turning the option off in Desktop is the safe route, and it breaks every visual that used a hierarchy
level. By hand it touches all of the files above. One source model had 8 `LocalDateTable_<guid>`
tables and one `DateTableTemplate_<guid>`. The steps:

- `model.tmdl`: set `annotation __PBI_TimeIntelligenceEnabled = 0` and drop each `ref table` line
  for the local date tables and the template.
- `relationships.tmdl`: drop each relationship whose `toColumn` is a `LocalDateTable`. They carry
  `joinOnDateBehavior: datePartOnly`, which makes them easy to find. In that model this left the file
  empty, so it was deleted. Whether Desktop also accepts an empty file was not tried.
- Each date column: drop its `variation Variation` block (`isDefault`, `relationship`,
  `defaultHierarchy`).
- `cultures/<culture>.tmdl`: entities with `"VariationSource"`, `"VariationSet"` and `"Hierarchy"`
  bindings, and the relationships that use them. That model had 35 of each.
- Report visuals: a slicer that used a "Between" date range on the plain column had a `queryRef`
  ending in `.Variation.Date Hierarchy.Year`. It became `<table>.<column>`, and its stale
  `expansionStates` was dropped. A visual that really drills Year, Quarter, Month needs a real date
  table with its own hierarchy first.
- Delete `.pbi\cache.abf`.

A composite model built on a source model with auto date/time on gets each hidden date table as a
DirectQuery proxy, with its own relationship.

## Verify

Reopen in Desktop. A missed reference makes Desktop name the file and the line. The steps above come
from a by hand cleanup not yet reopened in Desktop, so treat the first reopen as the test. Then run
the completion loop in `agent-verification.md`.
