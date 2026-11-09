# Licensing cheat sheet

The short table. `pro-vs-premium-facts.md` in this skill owns the detail and the Microsoft sources,
and is the file to check against each month's release.

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
| Edit a published dataset in the browser (web modeling, TMDL view on the web in preview) | Yes | Yes |
| Copilot, Direct Lake, Fabric Apps, translytical task flows | No | Fabric or Premium capacity |
| Dataflow Gen1 | Yes, legacy and unreliable if mixed into a scheduled model | Yes |
| Dataflow Gen2, enhanced compute, computed entities | No | Needs Fabric or Premium |
| Deployment pipelines (dev, test, prod stages) | No | Yes |
| Publish, workspaces, apps, sharing | Yes | Yes |

## Where the catches are

- Incremental refresh only saves work if the date filter folds. See `pro-vs-premium-facts.md` and
  the `powerbi-data-and-refresh` skill.
- XMLA: edit the local file with the tool, then republish from Desktop. See `external-tools.md`.
- Web modeling: no undo, and the next republish overwrites it. See `pro-vs-premium-facts.md`.
- Dataflow Gen1 into a scheduled model: sequence it or avoid it. See `pro-vs-premium-facts.md`.
