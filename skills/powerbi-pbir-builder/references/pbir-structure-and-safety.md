# PBIR structure and safe editing

PBIR is the folder of JSON files Desktop writes for a report saved as a PBIP. It is the format
current Desktop writes, generally available since September 2026.

## Folder layout

```
ProjectName.Report/
  .platform                        Desktop generates. Report type and a real GUID.
  definition.pbir                  Desktop generates. Links this report to its semantic
                                    model, either byPath (local pbip) or byConnection
                                    (a published dataset).
  definition/
    version.json                   Desktop generates. The PBIR version.
    report.json                    Desktop generates. Report level settings: theme,
                                    report level filters, resource packages.
    reportExtensions.json          Report level or visual level DAX that is not in the
                                    model (extension measures, visual calculations). Use
                                    sparingly, prefer a real model measure when you can.
    pages/
      pages.json                   WE EDIT. Page order and the active page.
      pgOverview/                  WE CREATE. One folder per page.
        page.json                  WE CREATE. Page size, background, page level filters.
        visuals/
          vSalesBarChart/          WE CREATE. One folder per visual.
            visual.json            WE CREATE. The visual type, its data bindings, and
                                    its formatting.
  StaticResources/
    RegisteredResources/           Custom theme JSON lives here if registered by Desktop.
```

## What you write

- You write: `pages.json` (append to `pageOrder`), one `page.json` per new page, one
  `visual.json` per new visual.
- Only Desktop writes: `.platform`, `definition.pbir`, `report.json`, `version.json`. They carry
  version specific GUIDs and settings. Never hand build them.

### pages.json in full

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
  "pageOrder": ["pgOverview", "pgDetail"],
  "activePageName": "pgOverview"
}
```

- `pageOrder` is the tab order, left to right. Each entry must equal a page folder name. A page
  folder with no entry here does not appear at all, the usual reason a new page is missing after
  a reopen.
- `landingPageName` (optional) overrides `activePageName` for everyone. `activePageName` is only a
  per user default.

## The safety checklist, every time

1. Desktop is closed. If it is open, ask the user to close it. The exception is the bridge branch
   in `agent-verification.md` in the `powerbi-project-and-tools` skill.
2. Back up the `.Report` folder, or confirm it is committed to git.
3. Take each `$schema` from an existing file of the SAME kind (`pages.json`, `page.json` and
   `visual.json` use three different schemas). For `visual.json`, scan every one and use the
   highest version present. `layout-and-schema-versions.md` has the URLs and the scan command.
4. Check the formatting names you write (everything under `objects` and
   `visualContainerObjects`) against the report theme schema for the installed Desktop version
   (`reportThemeSchema-<version>.json` in microsoft/powerbi-desktop-samples, for example 2.159 for
   October 2026). Its per visual definitions (named like `visual-listSlicer`, confirm in the file)
   list every card, property and enum value, so a misspelled name or a value from memory shows up
   before Desktop ignores it in silence. The schema does not cover `query`, `filterConfig` or sync
   groups. Write the new folders and files.
5. Parse every JSON file you wrote. One missing comma blocks the whole report from loading.
6. Run the completion loop in `agent-verification.md` in the `powerbi-project-and-tools` skill.
   Without the bridge, tell the user to reopen the `.pbip`.
7. A visual that parses but does not render: check `Entity` and `Property` match the model
   exactly (case sensitive), and that the visual is not sized to zero or cropped by its container.
8. After any Desktop session, re-read a file before editing it again. Desktop rewrites every JSON
   file in its own formatting on save, re-expands compact JSON, and gives hand dragged visuals
   fractional positions. Cached content and string match patterns from before the session miss.

## Respect a hand tuned layout

When editing an existing report, patch only the properties the user asked for. Never re-apply a
grid, resize, or restyle pass as a side effect of another change. Users tune layout by hand in
Desktop between sessions, and a scripted pass over `position` blocks or font sizes destroys that
work with no error. Fractional positions (step 8) are the tell. Read the current values from disk,
change the one property, leave the rest byte for byte. A full layout pass only when the user asks.

## Formatting order

Power BI defaults, then the theme's wildcard rules, then the theme's per visual type rules, then
the visual's own `visual.json`. The last one wins. A theme change reaches every visual. A bespoke
override fixes one visual, and the next visual you add will not inherit it.

## Dead formatting from copy and paste

A duplicated visual carries its bespoke formatting, including `dataPoint` rules whose selector
points at a table or column that is not in this visual's query, or not in the model. They render
nothing but pile up as hex that fights the theme. When you inherit such a report, strip any
`dataPoint` or selector rule whose `Entity` is not a real table in the current model. Check the
names against the TMDL first, so you do not delete a rule that points at a renamed table.

## When unsure of a shape

PBIR has no guard rails. Desktop trusts the JSON. Make the change once in Desktop, save, and read
the `visual.json` it wrote before writing more by hand.
