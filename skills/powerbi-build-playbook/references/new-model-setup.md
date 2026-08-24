# Creating the project and setting the day one defaults

The manual Power BI Desktop steps that come before any skill can help. An agent cannot do these,
they need a person with Desktop open. Hand them over as a checklist.

## Turn on the project format, once per machine

File, Options and settings, Options, Preview features. Check:

- Power BI Project (.pbip) save option
- Store semantic model using TMDL format

Restart Desktop. These are per machine, so a new laptop needs them again, and a colleague who
opens your project without them will save it back as a pbix.

## Turn auto date/time off, once per machine and once per file

File, Options and settings, Options, then Time intelligence. The setting appears on 2 pages:

- GLOBAL, labelled "Auto date/time for new files". This is the one that matters. Turn it off and
  every new file starts clean.
- CURRENT FILE. Applies only to the file open right now.

Both default to on. Do this before loading a single table.

Why it matters in one line: left on, Power BI generates a hidden calculated date table for every
date column in every import table, each with 6 calculated columns, and rebuilds all of them on
every refresh. See the `powerbi-data-and-refresh` skill for the measured cost.

There is no tenant level enforcement. For a team, the realistic options are the per machine
global setting, a `.pbit` template with it already off, or a Best Practice Analyzer rule as a
review gate.

## Create the project

1. Open Desktop, connect to the first data source, and load something. Desktop will not save a
   project with nothing in it.
2. File, Save as, choose Power BI Project (.pbip).
3. Save to a SHORT local path. Not OneDrive, not a SharePoint synced folder.

On the path, two separate traps:

- OneDrive plus git in one folder can corrupt the repo, and Desktop cannot save a pbip cleanly
  into a synced folder.
- Windows caps a path at 260 characters by default. PBIR nests
  `<project>.Report\definition\pages\<20 hex>\visuals\<20 hex>\visual.json`, which adds roughly
  70 characters before any file name. A project that saved fine can fail to OPEN after being
  moved somewhere deeper, with Desktop reporting that it cannot read a `visual.json`.

`C:\src\<project>` is a fine root. A path under a synced Documents folder is not.

## What you should end up with

```text
MyReport.pbip                      pointer file, open this
MyReport.SemanticModel/
  definition.pbism
  definition/
    database.tmdl
    model.tmdl
    relationships.tmdl
    expressions.tmdl
    tables/
      <one file per table>
  .pbi/                            git ignored, holds cache.abf and localSettings.json
MyReport.Report/
  definition.pbir
  definition/
    report.json
    version.json
    pages/
      pages.json
  StaticResources/
.gitignore                         Desktop writes this
```

If you do not see a `definition/` folder full of `.tmdl` files, the TMDL preview flag was not on
when you saved. Turn it on and save again.

## Initialise git before the first real change

```powershell
cd C:\src\MyReport
git init
git add -A
git commit -m "Initial pbip from Desktop"
```

Desktop writes a `.gitignore` that excludes `.pbi\cache.abf` and `localSettings.json`. Check it
exists before the first commit, because committing `cache.abf` puts the whole dataset in git
history and it is painful to remove later.

From here, work on a branch and open a pull request per change.

## Set the report level switch for container styling

Once the report exists, turn on the modern visual header so subtitles, dividers, shadows, and
header tooltips work at all. In Desktop this is under File, Options and settings, Options, Report
settings, and it writes `"useStylableVisualContainerHeader": true` into `report.json`.

Without it, every container styling property is accepted and silently ignored. See the
`powerbi-pbir-builder` skill.

## Apply the theme before building pages

View, Themes, Browse for themes, and pick the house theme JSON. Do this before adding visuals,
so everything inherits rather than needing a restyle later. The theme lives in the
`powerbi-report-design` skill.

## The handover checklist

Give the person this list and ask them to confirm each one.

- [ ] pbip and TMDL preview options on, Desktop restarted
- [ ] Auto date/time off, GLOBAL page, before any data loaded
- [ ] Project saved as .pbip to a short local path, not OneDrive
- [ ] `definition/` folder contains `.tmdl` files
- [ ] `.gitignore` present, `git init` done, first commit made
- [ ] Modern visual header on
- [ ] House theme applied
- [ ] Publish target workspace confirmed
