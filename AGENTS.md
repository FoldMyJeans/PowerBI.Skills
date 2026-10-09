# AGENTS.md

Operating rules for this repo, for any coding agent (Claude Code, Codex, Cursor) and any
human editing it. This file is committed on purpose, because the repo is the instructions.

## What this repo is

A pack of agent skills plus shared guidelines for building Power BI models and reports. This
repo is where they are authored, versioned, and evolved.

When you add something, prefer a pattern you have seen work in a real file over one that should
work in theory. Where the difference matters to the reader, show it through the detail (the
exact error, the number that was wrong) rather than by labelling the claim. See the evidence
rule below.

The skills follow the Agent Skills standard, which is an open format. Any tool that reads
skills loads them directly, and any tool that does not can read them as plain markdown. See
README.md for the install paths. Each skill auto triggers on its own Power BI work.

## The one constant: Power BI Pro only

Every skill and guideline assumes Power BI Pro. No Fabric, no Premium, no Premium Per User,
only Dataflow Gen1. When you add or change content, keep this lens. If something needs
Premium or Fabric, say so plainly and give the Pro friendly alternative. The verified limits
live in `skills/powerbi-project-and-tools/references/pro-vs-premium-facts.md`. Trust that
file over memory or old blog posts, and re-verify against Microsoft Learn about once a year.

## Writing rules (apply to every file here)

These govern files in this repo. They are not style advice for your own project's docs, and
nothing here should be applied to a user's report, code, or writing unless they ask for it.

- Plain engineer voice. Short direct sentences. Explain the why, not marketing filler.
- Never use an em dash or an en dash. Use commas, periods, or parentheses.
- Never use a semicolon outside a fenced code block. Split into two sentences.
- No real company name. Use "ABC Company". No real people names, use a role. Use placeholder
  hosts like `yourtenant.sharepoint.com` and `yourinstance.service-now.com`. No secrets, ever.
- Never state a count of things this repo contains. Not the number of skills, not the number of
  references, not "the full 23 rules". Every such number is a promise to come back and edit it,
  and the edit gets missed, so the number goes stale and quietly lies. Say "the skills" and
  "the full list" instead. The same goes for cross references: point at a rule by its name, not
  by its position in a numbered list, because inserting one renumbers everything after it.

## How the skills are structured

- One folder per skill under `skills/`, each with a `SKILL.md` and a `references/` folder. A
  skill that ships a runnable helper keeps it in its own `scripts/` folder, and a reference in
  that skill says when and how to run it.
- `SKILL.md` has YAML frontmatter with two keys, `name` (matching the folder name) and
  `description`. The description is the trigger, so make it pushy: say what the skill does
  and when to use it, packed with trigger phrases and synonyms. Keep it under 1024
  characters.
- Keep `SKILL.md` short, under 150 lines: when to use, a short workflow, rules of thumb, and
  pointers. Put the depth in `references/`.
- Keep each reference under 250 lines, which is roughly one focused read on top of a SKILL.md.
  The cap is a proxy for the real rule, which is ONE TOPIC PER REFERENCE. A file that wants
  more than 250 lines is usually covering two topics, so split it by topic rather than by size.
- Every skill folder is self contained. Never reference a path outside the skill folder.
  Shared facts live in the `references/` of the skill that owns them
  (`pro-vs-premium-facts.md` in `powerbi-project-and-tools`, `design-principles.md` and
  `house-default-theme.json` in `powerbi-report-design`), and other skills point at them by
  skill name, not by path. A skill folder is shipped on its own, so it also cannot link to
  `guidelines/sources.md`. Inline the two or three URLs a file needs instead.
- `guidelines/sources.md` at the repo root is authoring material for maintainers, not loaded
  by the skills.

## One owner per fact

Every fact has exactly one file that owns it. Other files may carry a ONE OR TWO LINE summary
plus a pointer to the owning skill. They may not restate it in full.

This is the rule that keeps the repo honest, and it is the one most easily broken, because
restating something feels helpful. It is not. When the house page layout preference lived in
five files, a change to it meant five edits and four chances to leave a stale copy behind.

The test: if you are about to write a third sentence about something another file already
covers, stop and write a pointer instead. A summary exists so the reader can act without
loading the other file. If they need the detail, they should load the owner.

## Show the evidence, do not announce it

Never write that something is confirmed, verified, battle tested, or drawn from a real
production model. Those sentences add no information, and a reader who has done this work reads
them as filler at best and as a machine padding for credibility at worst. Trust is earned by
being specific, not by claiming to be trustworthy.

So instead of "confirmed in a live production model", give the detail that only somebody who hit
the problem would know: the exact error string, the number that was wrong, what it looked like
before anyone noticed. Concrete beats certified.

Two places a source note is still doing real work, and both are about what the reader should do
next rather than about how much to be impressed:

- When a shape is a guess, say so, because the reader needs to verify it before relying on it.
  The Confirmed column in `visual-types-and-patterns.md` is the pattern.
- When something is judgement rather than fact, label it as judgement, as `refresh-cost-model.md`
  does with its ranking.

Never present a guessed JSON shape or TMDL block as if it were read from a real file. If a shape
has not been seen in a file Desktop wrote, say to generate one in Desktop and read it back.

## Adding or updating a skill

1. Create or edit `skills/<name>/SKILL.md` and its `references/`. The folder name must match
   the `name` in the frontmatter.
2. Follow the writing rules above and keep the Pro lens.
3. A brand new skill folder needs no manifest change, the `skills` path in
   `.claude-plugin/plugin.json` already exposes every folder under `skills/`. Bump the
   `version` in plugin.json so installed copies pick it up on the next `/plugin update`.
4. Make the change on a branch and open a pull request, using the workflow below.

## Daily changes via pull request

Make each change on a branch and open a pull request. Do not commit straight to main.

```powershell
git checkout -b my-change
# make your edits
git add -A
git commit -m "what changed"
git push -u origin my-change
gh pr create
```

Merge on GitHub after review.

## Verify before committing

Run the check script. It enforces every rule above that can be enforced mechanically.

```powershell
pwsh -File tools\check.ps1
```

It fails the build on: an em or en dash or a semicolon in prose (code fences are exempt), a
`SKILL.md` frontmatter `name` that does not match its folder, a description over 1024
characters, a `SKILL.md` over 150 lines, a reference over 250 lines, any path reference that
leaves its own skill folder, a real company name or tenant or instance host, a reference file
that its own `SKILL.md` never mentions, and any JSON in the repo that does not parse.

Exit code 0 means clean. Do not commit on a red check.

Two things the script cannot check, so check them yourself:

- `skills/powerbi-report-design/references/house-default-theme.json` still validates against the
  official report theme schema (from microsoft/powerbi-desktop-samples) if you changed it.
- The one owner per fact rule. A new full restatement of something another file owns will pass
  the script and still be wrong.

## Keep it local

Do not put this repo in a OneDrive synced folder. Git plus OneDrive can corrupt the repo.
