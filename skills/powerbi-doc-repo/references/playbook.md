# Power BI documentation repo playbook

Turning a finished Power BI model into a redacted, shareable git repo. Plain engineer voice, no em
or en dashes, no semicolons outside code. Run the redaction checklist on every file before it is
committed.

## Repository structure

```
knowledgebase/
  00_overview.md
  01_data_flow_and_lineage.md
  02_data_sources.md
  03_<cross_cutting_topic>.md
  ...
  0N_data_model_relationships.md
  0N_measures_catalog.md
  reference/                 the verbatim M and DAX, one file per layer
    01_source.md
    02_staging.md
    03_transform.md
    04_facts.md
    05_dimensions_and_calculated.md
    06_measures.md
README.md                    the showcase front door
.gitignore
```

The `reference/` folder holds the real code, redacted, so a reader sees exactly how each layer
works. A repo can also ship the real source instead: TMDL for the model, one `.dax` file per
measure in a few numbered folders, with a single README table (folder, description, count) as the
index.

## The .gitignore (write this before the first commit)

```
# OS junk
.DS_Store
Thumbs.db
desktop.ini

# Editor and IDE
.vs/
*.suo
*.user

# Power BI binaries and the raw project export (real, unredacted data)
*.pbix
*.pbip
*.pbit
*.SemanticModel/
*.Report/

# Local only working files, never pushed
CLAUDE.md
00_PROJECT_SETUP.md
00_LOCAL_REDACTION_MAP.md
```

The pbix, pbip, and exported model folders hold the real, unredacted data and code.

## Redaction checklist (where Power BI hides real data)

- Company name. In host names, and as literal display values inside logic, for example
  `if [Company] = "Real Co"` in M or `IF ( company = "Real Co", ... )` in DAX. Replace with
  an alias like "ABC Company".
- Hosts and tenant URLs. ServiceNow instance hosts, SharePoint site URLs, and personal
  OneDrive paths like `https://yourtenant-my.sharepoint.com/personal/<user>`. Replace with
  placeholder hosts.
- People. Hardcoded rosters in dimension tables, owners named in M filters like
  `each [Owner] <> "Real Name"`, owners named in DAX like `IF ( owner = "Real Name", ... )`,
  and DAX variable names built from a first name like `VAR RealNameCap`, which must be
  renamed too. Replace names with roles or generic labels.
- Clients and customers. In assignment group labels and in table values. Use Client A,
  Client B.
- ServiceNow sys_id GUIDs and tenant identifiers. Replace with readable placeholders like
  `<assignment_group_sid_A>`.
- Secrets. Passwords, tokens, keys, connection strings. Never commit these. Flag and remove.

Keep the real to fake mapping only in a git ignored decoder, `00_LOCAL_REDACTION_MAP.md`.
After writing, verify nothing slipped through, for example
`grep -rniE "\bRealName\b|\bRealCompany\b" .` should return nothing.

## README as a showcase

Structure:

- Title and one paragraph on what the model does.
- The goal, framed so a reader sees why the problem was hard.
- An architecture diagram (a mermaid `flowchart`).
- A data model diagram (a mermaid ER diagram).
- The hard parts. One short subsection per tricky thing, each linking to its deep dive doc
  in the knowledgebase.
- Repository layout, and the tech used.
- One quiet closing line that identifiers are anonymized.

Do not add a "what is and is not in the repo" section or a long redaction explainer. Let the
work speak.

## Verify before publishing

Confirm every structural claim the README makes is true of the files shipped (folder counts,
"the theme drives all styling"). One repo claimed its theme drove all styling but shipped no
custom theme file at all, the styling was inline.

In a source-open repo, do not commit a raw `.pbix`, the TMDL and report JSON already are the
source. Dedupe embedded images by hash so near-identical ones do not ship twice. To read an
existing report, a pbix's PBIR (`definition/`, JSON per page and visual) reads directly from a
plain zip extract. A pbix edited and saved by a September 2026 or later build is PBIR. An older one may still
hold the single file `Report/Layout`, which is UTF-16 and harder to diff. Either way the data model
itself is compressed and needs an external tool.

## Setting up and pushing the repo (Windows)

Run git on the Windows machine, not from a sandbox mount. Write the `.gitignore` first so the
binaries and local files never get staged.

```powershell
cd C:\Users\<you>\source\repos\<ProjectName>
git init -b main
git config user.name  "Your Name"
git config user.email "you@company.com"
git remote add origin https://github.com/<account>/<ProjectName>.git
git add -A
git status               # eyeball that no pbix, pbip, or export folder is staged
git commit -m "Initial commit: redacted <model> knowledgebase"
git push -u origin main
```

Create the GitHub repo as Private first. Never run `git init` twice in the same folder. After
this first push, make each change on a branch and open a pull request, then merge on GitHub
after review.

## Keeping the docs in sync with the model

When the model changes, the reference dump has to follow. A scripted sync overwrote the wrong
block twice. Select the fence to replace by section heading, code language, and index within that
section, never by "the first fence after the heading" and never by "the first fence whose first
line matches". Every M fence starts with `let`, and one table's section can hold an M fence and a
DAX fence side by side, so both shortcuts silently overwrite the wrong block while reporting
success.

A cheap end to end check: extract every code fence from the docs and confirm each one still
appears verbatim in the TMDL. A fence that does not match is drift, either a missed sync or a
block an earlier sync overwrote.

## Gotchas

- Keep the repo local, outside any OneDrive synced path.
- "Save as pbip" in Power BI switches the active file to the pbip. Know which file you are now
  editing.
