# PBIR structure and safe editing

PBIR (the Power BI Enhanced Report format) is the folder-of-JSON-files layout Power BI
Desktop writes when you save a report as a PBIP project. It is the current format, current
Desktop versions write it by default. This reference covers the folder layout, which files
you write versus which only Desktop can generate, and the safety checklist.

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

## What you write versus what only Desktop can generate

Desktop bakes real, version specific GUIDs and internal settings into `.platform`,
`definition.pbir`, `report.json`, and `version.json`. These are not practical to hand write
and change between Desktop versions. Never try to build a PBIP from scratch by hand writing
these. Always start from a project the user saved from Desktop, then add to it.

You write: `pages.json` (append to `pageOrder`), one `page.json` per new page, and one
`visual.json` per new visual. That is the safe, stable surface.

### pages.json in full

It is a short file, and the whole thing looks like this:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
  "pageOrder": ["pgOverview", "pgDetail"],
  "activePageName": "pgOverview"
}
```

`pageOrder` drives the tab order left to right, and every entry must match a page folder name
exactly. A page folder with no entry here does not appear in the report at all, which is the
usual reason a page you just wrote is missing after a reopen.

There is a fourth key, `landingPageName`, which is optional and overrides `activePageName` for
everyone. `activePageName` only sets a per user default. If you want every reader to land on
the same page, `landingPageName` is the one that does it.

## The safety checklist, every time

1. Confirm Power BI Desktop is closed. If it is open, ask the user to close it first. Desktop
   holds the project's files open and can overwrite or lock them.
2. Back up the `.Report` folder, or confirm it is committed to git, before writing anything.
3. Work out the `$schema` for each file kind. `pages.json`, `page.json` and `visual.json` use
   three different schemas, so take each one from an existing file of the SAME kind, never from
   a different kind. For `visual.json`, scan every one in the project and use the highest
   version present, because a real project carries a mix. Do not hardcode a version.
   `layout-and-schema-versions.md` has the three URLs and the scan command.
4. Write the new folders and files.
5. Parse every JSON file you wrote (a simple `JSON.parse` or equivalent) before telling the
   user it is done. A single missing comma or bracket blocks the whole report from loading in
   Desktop, so catch it before the user sees it.
6. Tell the user the files are written and to reopen the `.pbip` in Desktop.
7. If a visual does not render after reopening, valid JSON does not guarantee rendering. Check
   the field reference `Entity` and `Property` values match the model exactly (case
   sensitive), and that the visual is not sized to zero or cropped by its container.
8. After any Desktop session on the project, re-read a file before editing it again. Desktop
   rewrites every JSON file in its own formatting on save, it re-expands compact JSON, and hand
   dragged visuals come back with fractional positions. Cached file content and string match
   patterns from before the session are stale, and an exact string edit built on them will miss.

## Respect a hand tuned layout

When editing an existing report, patch only the properties the user asked for. Never re-apply
a grid, resize, or restyle pass across visuals or pages as a side effect of another change.
Users iterate on layout by hand in Desktop between sessions, and a scripted pass that rewrites
`position` blocks or font sizes silently destroys that manual work, which is worse than a bug
because nothing errors. The fractional positions from step 8 above are the tell that a layout
has been hand dragged. Read the current values from disk, change the one property requested,
and leave everything else byte for byte as you found it. A full layout pass happens only when
the user explicitly asks for one.

## Formatting: theme first, bespoke second

Formatting is resolved in this order: Power BI defaults, then the theme's wildcard rules,
then the theme's per visual type rules, then whatever is written directly in that visual's
`visual.json`. The last one wins.

Prefer putting color and font choices in the report's theme JSON, see
`house-default-theme.json` in the `powerbi-report-design` skill, over repeating the same formatting object in many
`visual.json` files. A theme change updates every visual at once. A bespoke `visual.json`
override only fixes one visual, and the next visual you add will not inherit it.

## Watch for dead formatting from copy and paste

When a visual is duplicated across pages, its bespoke formatting travels with it, including
conditional formatting `dataPoint` rules whose selector points at a table or column that is not in
this visual's query, or not in the model at all. These are dead overrides. They render nothing, but
they are bespoke hex that fights the theme, and they pile up across a report that grew by copy and
paste. When you inherit a report like this, strip any `dataPoint` or selector rule whose `Entity` is
not a real table in the current model. Check the entity names against the TMDL before you delete, so
you do not remove a rule that is only pointing at a renamed table.

## Why this is worth the caution

The PBIR format has no built in guard rails against a broken reference or a malformed file,
it is plain JSON that Desktop trusts. Treat this skill as a precise tool, not a shortcut.
When in doubt, make the change in Power BI Desktop by hand once, save, then read the
`visual.json` Desktop produced to see the exact shape it expects before writing more by hand.
