# Verifying an agent's edit

An edit is not done when the JSON parses. Valid PBIR can render wrong, and a page that renders can
show a wrong number. This file is the loop that closes that gap, and it owns the rule for when
Desktop can stay open.

Status: the loop comes from Microsoft docs and the CLI READMEs, and has not yet been run on a real
report here. The local prerequisites list no capacity (Windows, Desktop, one security option), but
nothing says Pro outright, so prove it once on a Pro machine. Microsoft called the bridge preview in
June 2026 and listed it under the agentic experiences that went GA in September 2026. Its Learn page
(September 2026) no longer carries a preview label. The CLI is at version 1.0.0.

## Install, pinned

```powershell
npm install -g @microsoft/powerbi-report-authoring-cli@0.5.0
npm install -g @microsoft/powerbi-desktop-bridge-cli@1.0.0
```

The report authoring CLI is a public preview, and its README says to pin exact versions or expect
breaks. Read the current versions first, and see the tool risk policy in `external-tools.md`.

The bridge needs Desktop on Windows, with File, Options and settings, Options, Security, Desktop
Bridge, Enable external tool access to Power BI Desktop through secure local APIs. That is on by
default, and an administrator can turn it off with a registry policy.

## Desktop open or closed

Two branches, and this is the only place that says so.

**No bridge in this session.** Close Desktop, edit, reopen. That is the rule in `pbip-and-tmdl.md`,
and nothing below changes it. To render and refresh a copy without the bridge and without touching the
person's screen, see `offscreen-render.md`.

**With the bridge.** Desktop can stay open, on these conditions:

1. The person saves in Desktop first. Desktop does not write its changes to the files until it saves.
2. Run `powerbi-desktop status` to see which file is open, its PID, and its unsaved state. Check it is
   the right project. Do not rely on the flag alone. The README says that on Desktop 2.157.627.0,
   `hasUnsavedChanges` reads true for an untouched PBIP and never clears, so a strict gate would block
   every time. Ask the person instead.
3. `reload` discards unsaved edits in Desktop, with no check and no warning. Never run it while someone
   may be working in that window.

A reload also resets filters and some of the interface, and it does not reload `cache.abf`.

## The loop

### 1. Source checks

Parse every JSON file you wrote. Each `Entity` and `Property` must match the model exactly. A
mismatch parses fine and renders an empty visual. If you touched TMDL, run the lineageTag
check in `pbip-and-tmdl.md`.

### 2. Conformance validation

```powershell
powerbi-report-author validate .\ABCSales.Report --out validate.json
```

This covers JSON Schema, IDs, formatting, theme, and layout, and reports each problem by code, file,
and dotted JSON path. It exits with 1 when the result is failed. Unknown visual types stay warnings,
so a custom visual does not fail it. Run it once over a report Desktop wrote, so you know its noise
level before you trust a failure.

Look up roles and properties instead of guessing them: `powerbi-report-author catalog describe
<visualType>` and `powerbi-report-author formatting describe-object <visualType> <object>`.

### 3. Reload and screenshot through the bridge

```powershell
powerbi-desktop status
powerbi-desktop reload --pid <pid>
powerbi-desktop screenshot-all --pid <pid> --output-dir .\shots
```

Run these one at a time. The bridge handles one operation at a time per Desktop process, and
overlapping calls can be cancelled. Use `--wait-seconds` right after a reload. Never review a screenshot
taken before the latest reload. The page list comes from `pages.json` on disk, so a page you added but
did not reload fails with a per page error.

`powerbi-report-author preview <folder> --host desktop --reload` goes through the same bridge. Judgement:
pick one route per project rather than mixing them.

After a TMDL change, reopen the PBIP in Desktop. The sources disagree on whether a reload reapplies the
model. Microsoft's bridge page says it does by default, the CLI README says to reopen if the changes do
not show, and the report CLI has a separate `--reload-with-model` flag. The bridge also has no refresh
method. When data has to change, send a TMSL refresh to Desktop's local engine and save through UI
Automation, as in `offscreen-render.md`, or ask the person to press Refresh.

### 4. Review each page

A screenshot includes the filter pane when it is open, so review that too. Check:

- Visuals fully inside their frame, with nothing clipped or overlapping.
- Titles, labels, legends, and card values that are readable and not cut off or ending in an ellipsis.
- Charts with marks rather than empty frames, and tables with rows rather than only headers.
- No error icons, and no message asking for more fields.
- Blanks and dashes only where you expect them.
- Slicers that show selectable values.
- The theme applied, with text that contrasts with its background.

Whether the page is any good is the `powerbi-report-design` skill's question.

After a batch of visual edits, hand the files, the rules, and the theme schema to a separate reviewer
agent that did not write them. On one batch of slicer edits it found a missing row padding, a row
height never measured from a render, two drawers that opened past the page edge, a title colour and a
font that did not match the classic slicers beside them, and a pill with no room.

Write multi file edit scripts so every assertion runs before any file is written. A script that
asserted file by file half applied once and could not be rerun.

### 5. Assert the numbers with DAX

A screenshot of a wrong total looks fine. Before the change, write a short list of expected values taken from the source, not from the model: a few totals, one
filtered slice, and every ratio at the total level. After the change, run them in DAX query view, DAX
Studio, or the local modeling MCP in read only mode.

```dax
EVALUATE
ROW ( "Total Sales", [Total Sales], "Margin %", [Margin %] )
```

A value that does not match fails the edit, however good the page looks. A fan out or a broken
relationship shows up here and not in the picture.

## Stop rules

- **Bound the fix loop.** Judgement: allow one round of fixes, rerun the whole loop, then report what you
  saw instead of trying again. An unbounded loop can hide that the fault is not fixable from the
  files. If nothing changed in the project, skip the loop. The idea of a fix budget and named
  failures follows Agentic-PBIP-Template (MIT): https://github.com/Mofaji/Agentic-PBIP-Template
- **Blocked is not done.** If Desktop is not running, the bridge is off, another project is open, or the
  reload failed, say which, and report the check as blocked. Do not claim the edit is complete.

## Use a fake data fixture

Screenshots, query results, and model metadata reach whichever model provider the agent uses (the MCP
page says so for metadata and query results). PBIR files can also hold data values, for example a
filter value in a `visual.json`.

So run the loop on a small fixture PBIP with fake data (ABC Company) and the same table and column names
as the real model. Use real data only when the person responsible for that data has decided to allow
it. Deleting the screenshots afterwards is tidy, but it does not recall what was already sent.

Sources:

- Desktop Bridge: https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-desktop-bridge-overview
- Editing project files: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-external-editing
- Bridge CLI: https://www.npmjs.com/package/@microsoft/powerbi-desktop-bridge-cli
- Report authoring CLI: https://www.npmjs.com/package/@microsoft/powerbi-report-authoring-cli
- Microsoft's report skill, the same loop in its own words (MIT): https://github.com/microsoft/skills-for-fabric
