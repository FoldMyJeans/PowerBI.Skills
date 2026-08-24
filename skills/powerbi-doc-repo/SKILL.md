---
name: powerbi-doc-repo
description: >-
  Stand up a redacted, shareable git repo that documents a Power BI model end to end, from
  the M and DAX in a PBIP or TMDL export to a polished knowledgebase and a showcase README.
  Use whenever the user wants to document, write up, or create a repo or knowledgebase for a
  Power BI file, a pbix, a pbip, a PBIP project, a semantic model, a dataset, or the model
  behind a dashboard, or mentions exporting a Power BI model to TMDL, anonymizing a BI model
  for sharing, putting a Power BI model on GitHub, or doing the same thing as a previous
  Power BI repo on a new file. Trigger even without the word documentation, for example
  "I have another PBI I want to do the same with". For building or fixing a model use the
  other powerbi skills, this one is only about documenting a finished model.
---

# Power BI documentation repo

Turn a finished Power BI model into a clean, redacted, shareable git repo: a knowledgebase
that explains the model, a reference dump of the real M and DAX by layer, and a README that
reads like a showcase. The privacy rules are the redaction checklist in this skill, and the
writing voice is plain engineer prose, no em or en dashes, no semicolons outside code.

Read `references/playbook.md` for the full step by step, the exact `.gitignore`, the README
template, and the redaction checklist.

## When to use

Use this to document a model that already exists. To build or troubleshoot a model, use
`powerbi-data-and-refresh`, `powerbi-modeling`, `powerbi-dax`, `powerbi-report-design`, or
`powerbi-project-and-tools`.

## Workflow (8 steps)

1. Get a text export of the model. Save as a PBIP project so the model is TMDL text, or
   export the model to TMDL. The TMDL is the source of truth, trust it over any older summary.
2. Read the model. Walk the M in `expressions.tmdl` and the table partitions, the DAX
   measures, the relationships, and the report pages. Build a mental map of the layers
   (sources, staging, transform, facts, dimensions, measures).
3. Plan the repo. One knowledgebase doc per topic, plus a reference folder that holds the
   verbatim M and DAX per layer.
4. Redact as you write. Run the redaction checklist in the playbook. Keep the real to fake
   mapping only in a git ignored decoder file, never in a committed file.
5. Write the knowledgebase. Numbered docs, plain engineer voice, no em or en dashes, no
   semicolons outside code.
6. Write the reference dump. The real M and DAX, redacted, one file per layer.
7. Write the README as a showcase. Title, the goal, an architecture diagram, a data model
   diagram, the hard parts each linking to its deep dive, the layout, and a quiet closing
   line that identifiers are anonymized.
8. Set up and push the repo on the Windows machine. `.gitignore` first, then init, commit,
   push. After the first push, make further changes on a branch and open a pull request.

## Key rules

- Keep the repo out of a OneDrive synced folder. Git plus OneDrive in one folder can corrupt
  the repo.
- Never commit the pbix, pbip, or the raw TMDL export. The `.gitignore` in the playbook
  excludes them.
- Redact real company, hosts and tenant URLs, people and rosters, clients, and ServiceNow
  sys_id values. See the checklist in `references/playbook.md`.
