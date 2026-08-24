# PowerBI.Skills

Task specific agent skills for building Power BI models and reports on Power BI Pro. No
Fabric, no Premium, no capacity.

## Why this exists

1 GB per model. 8 scheduled refreshes a day. 2 hours before the Service kills a refresh mid run.
No XMLA endpoint, no deployment pipelines.

That is Power BI Pro. It is also what most Power BI work actually runs on, because Pro costs a
few dollars a user and capacity does not.

Almost nothing written about Power BI is written for those limits. Most of it assumes you can
solve a performance problem by adding capacity. So the answer you find is often the answer for
a licence you do not have.

Here is what that looks like. A refresh takes 3 hours and keeps failing. With a capacity behind
you, the fix is a lakehouse or a Gen2 dataflow. On Pro, the fix is to find the derivative tables
that re-run their entire upstream pull on every refresh, and convert them to calculated tables
so they compute in memory from data already loaded. Both answers are correct. Only one is
available to you.

This repo is the second kind of answer, collected in one place. Where something genuinely needs
Premium or Fabric, it says so and gives the Pro alternative instead of pretending the ceiling is
not there.

Three things follow from working inside a constraint, and together they are the reason to load
these skills rather than point an agent at the official documentation.

**It says do not.** Do not use `SharePoint.Files` to read a single file. Do not name a table
`Measures`. Do not leave auto date/time on. A theme whose values are also written into every
visual is not a theme. Vendor documentation rarely calls a feature a trap, because it has to
support every feature it ships. Knowing which door not to open is the part you cannot get from
a reference.

**It is organized around silent failure.** Most sections have a "nothing errors" clause,
because in Power BI most mistakes do not error. The total is wrong while every row is right. The
relationship fans out and doubles the numbers. The refresh goes green on a table that lost half
its rows. That matters more when an agent is writing the code, because an agent reading the
documentation produces something plausible that fails quietly, and plausible is what gets
through review.

**It has defaults.** One theme, one grid, one naming taxonomy, measures in `_Measures`. Official
guidance cannot ship opinions, so it ships "it depends", and an agent facing "it depends"
invents one. A stated default is what stops the invention.

Everything here assumes Pro. If that is what you are working with, this was written for you,
and those limits are the starting point for every answer in it rather than a caveat at the
end of one.

## The skills

| Skill | What it does | Example trigger |
| --- | --- | --- |
| `powerbi-build-playbook` | The phase order for a whole build, the manual Desktop steps, and which skill owns which question. Start here. | "where do I start", "build a new power bi report", "create a pbip" |
| `powerbi-data-and-refresh` | The data layer. Power Query M, connecting to REST or ServiceNow or SharePoint, paging, query folding, and fixing slow or failing refreshes. | "my refresh keeps failing", "connect power bi to this api" |
| `powerbi-modeling` | Star schema, dimensions vs facts, grain, relationships, and naming including the `_Measures` table. | "how should I model this", "star schema" |
| `powerbi-dax` | Measures vs calculated columns and tables, context, and reusable DAX patterns. | "write a year over year measure", "running total" |
| `powerbi-pbir-builder` | Write real report pages and visuals into an existing PBIP by authoring PBIR JSON directly. | "add a page to the report", "build a KPI card in code" |
| `powerbi-report-design` | Layout, chart selection, color and theme JSON, fonts, slicers, navigation, and accessibility. | "design this report", "pick colors", "which chart" |
| `powerbi-project-and-tools` | The pbip and TMDL project format, safe hand editing, free external tools, and the Pro vs Premium boundary. | "edit the TMDL", "what needs Premium", "Tabular Editor" |
| `powerbi-doc-repo` | Document a finished model into a redacted, shareable git repo. | "document this pbi", "I have another PBI I want to do the same with" |

## Shared reference material

Shared facts live inside the skill that owns them, so every skill folder stays portable:

- `skills/powerbi-project-and-tools/references/pro-vs-premium-facts.md`, the verified license
  limits and what is Premium or Fabric only. Other skills point at it by skill name.
- `skills/powerbi-report-design/references/design-principles.md`, the situational report design
  rules of thumb.
- `skills/powerbi-report-design/references/house-default-theme.json`, an accessible Power BI
  theme (Okabe-Ito colorblind safe palette, Segoe UI, a blue to orange diverging scale) to
  start every report from.
- `guidelines/sources.md`, the curated Pro safe source list per topic. Authoring material for
  maintaining this repo, not loaded by the skills.

## Install

The skills follow the Agent Skills standard (a `SKILL.md` with `name` and `description`
frontmatter plus a `references/` folder), which is an open format, not a Claude one. Any tool
that reads skills picks these up, and any tool that does not can still read them as plain
markdown. Each skill folder is self contained: copy it alone and nothing breaks.

### Claude Code

This repo is a Claude Code plugin. It works anywhere you run Claude Code: the CLI, the VS Code
or JetBrains extension, and the desktop app. The repo is public, so anyone can install it on
any Claude plan.

Terminal, the reliable way that works in every setup:

```
claude plugin marketplace add FoldMyJeans/PowerBI.Skills
claude plugin install powerbi-skills@powerbi-skills
```

Run those from a project folder, not your home directory. A git safety check can otherwise
refuse to clone. Then `claude plugin list` should show `powerbi-skills` as enabled. Restart
your Claude Code session so the skills load.

Inside a Claude Code chat session, the interactive form also works:

```
/plugin marketplace add FoldMyJeans/PowerBI.Skills
/plugin install powerbi-skills@powerbi-skills
```

The `/plugin` command is not available in every surface (the desktop app hides it), so use the
terminal commands above if you do not see it. Update later with
`claude plugin update powerbi-skills` (or `/plugin update` in chat).

### Codex, Cursor, and other agents that read ~/.agents/skills

Codex, Cursor, and a growing number of other agents read skills from `~/.agents/skills/`.
Clone the repo, copy the skill folders there once, and they get picked up.

PowerShell (Windows):

```
git clone https://github.com/FoldMyJeans/PowerBI.Skills
Copy-Item -Recurse -Force PowerBI.Skills/skills/* ~/.agents/skills/
```

macOS or Linux:

```
git clone https://github.com/FoldMyJeans/PowerBI.Skills
mkdir -p ~/.agents/skills && cp -R PowerBI.Skills/skills/* ~/.agents/skills/
```

To update: `git pull` in the clone, then run the copy again. Every skill folder is self
contained, so copying only the skills you want also works.

For project scoped use instead of user wide, copy the skill folders into the project's
`.agents/skills/` folder, which these tools also discover.

### Any other AI tool

There is nothing proprietary here. A skill is a folder of markdown, so anything that can read
markdown can use it, with or without skill support.

If the tool can browse or fetch a URL, give it the repo link and tell it which skill to read,
for example `skills/powerbi-dax/SKILL.md`. If it cannot, open that `SKILL.md`, paste it in, and
paste whichever file under `references/` it points you to.

Grab one skill, not the set. The whole repo is around 93,000 tokens and will not fit in a chat
window. A single `SKILL.md` plus one reference is closer to 3,000 to 6,000, which fits anywhere.
The skills table above tells you which one you want.

What you lose without skill support is only the automatic part. A skill aware tool notices you
asked about a slow refresh and loads the right file on its own. Everywhere else you pick the
file yourself, and the content is identical.

### Native alternatives

- Codex: the `$skill-installer` skill can be prompted with this repo's URL to fetch skills.
- Cursor: Customize, Rules, Add Rule, Remote Rule (GitHub) accepts this repo's URL, and Cursor
  also discovers `.cursor/skills/`.

The clone and copy method above is the one to reach for by default. Use these if you prefer them.

## Authoring changes

To add or change a skill, edit under `skills/` on a branch and open a pull request. Bump the
`version` in `.claude-plugin/plugin.json` so installed copies pick it up on the next
`/plugin update`. See AGENTS.md for the writing rules and the Pro only lens.

Before committing, run the check script. It enforces the writing rules, the file size caps, the
self containment rule, and redaction:

```
pwsh -File tools\check.ps1
```

## Keep it local

Do not put this repo inside a OneDrive synced folder. Git plus OneDrive in one folder can
corrupt the repo.

## Sources

See `guidelines/sources.md`. The anchors are Microsoft Learn, SQLBI and DAX.guide and DAX
Patterns, Chris Webb's blog, Kurt Buhler and Data Goblins, Zebra BI and IBCS, and the
colorblind safe palettes from Okabe-Ito and ColorBrewer.
