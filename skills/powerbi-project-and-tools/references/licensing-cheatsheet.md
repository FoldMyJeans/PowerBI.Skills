# Licensing cheat sheet

A compact quick reference for what runs on Pro versus what needs Premium, Premium Per User (PPU),
or Fabric. This is a summary. For the full detail and the Microsoft Learn sources, read
`pro-vs-premium-facts.md` in this skill. Re-verify yearly, because these limits move.

| Capability | Pro | Premium, PPU, or Fabric |
| --- | --- | --- |
| Model size per semantic model | Up to 1 GB | Larger, with large models on |
| Scheduled refreshes per day | Up to 8, at least 30 min apart | Up to 48 |
| Single refresh run time cap | 2 hours | 5 hours on capacity, no cap when XMLA triggered |
| Incremental refresh, import part | Yes | Yes |
| Real time or hybrid DirectQuery part of incremental refresh | No | Yes |
| Manage refresh partitions over XMLA (custom incremental partitions) | No | Yes |
| XMLA endpoint on a published dataset (read or write) | No | Yes |
| Edit a published dataset with an external tool | No | Yes |
| Dataflow Gen1 | Yes, legacy and unreliable if mixed into a scheduled model | Yes |
| Dataflow Gen2, enhanced compute, computed entities | No | Needs Fabric or Premium |
| Deployment pipelines (dev, test, prod stages) | No | Yes |
| Publish, workspaces, apps, sharing | Yes | Yes |

## Notes that matter

- Incremental refresh. The import part works on Pro. You set RangeStart and RangeEnd parameters
  plus a date filter, and it only saves work if that filter folds to the source. The real time
  or hybrid part, and any partition management over XMLA, are Premium. See
  `powerbi-data-and-refresh` for the folding detail.
- XMLA. On Pro, external tools like Tabular Editor and DAX Studio edit your LOCAL pbip or pbix,
  which is fine. Writing back to a dataset already published in a Pro workspace needs the XMLA
  write endpoint, which is Premium. On Pro, edit locally then republish from Desktop. See
  `external-tools.md`.
- Dataflow Gen1. It runs in Pro workspaces, but do not push a Gen1 dataflow into a model that
  also refreshes on a schedule. On Pro there is no orchestration between the two, so the model
  can read stale or partial data or the refresh can fail. The clean fix is Gen2, which needs
  Fabric or Premium.

## Full detail

`pro-vs-premium-facts.md` has the verified facts and the Microsoft Learn links behind
every row above.
