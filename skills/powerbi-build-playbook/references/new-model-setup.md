# Creating the project and setting the day one defaults

Manual Power BI Desktop steps that need a person with Desktop open. Hand them over as a checklist.

## Check the project format, once per machine

PBIP and PBIR are generally available (September 2026), so a current build offers Power BI Project
(.pbip) under File, Save as. If it does not, or you get no TMDL `definition/` folder, look under
File, Options and settings, Options, Preview features for:

- Power BI Project (.pbip) save option
- Store semantic model using TMDL format

Restart Desktop after changing them. Options are per machine, so check a new laptop too.

## Turn auto date/time off, once per machine and once per file

File, Options and settings, Options, then Time intelligence. The setting appears on 2 pages:

- GLOBAL, labelled "Auto date/time for new files". This is the one that matters. Turn it off and
  every new file starts clean.
- CURRENT FILE. Applies only to the file open right now.

Both default to on. Do this before loading a single table. Left on, Power BI generates a hidden
calculated date table for every date column in every import table, each with 6 calculated columns,
and rebuilds all of them on every refresh. See the `powerbi-data-and-refresh` skill for the
measured cost.

There is no tenant level enforcement. For a team, the options are the per machine global setting, a
`.pbit` template with it already off, or a Best Practice Analyzer rule as a review gate.

## Create the project

1. Open Desktop, connect to the first data source, and load something. Desktop will not save a
   project with nothing in it.
2. File, Save as, choose Power BI Project (.pbip).
3. Save to a SHORT local path, not OneDrive and not a SharePoint synced folder. `C:\src\<project>`
   is a fine root. OneDrive plus git can corrupt the repo, and PBIR's nesting can push a moved
   project past the 260 character path limit so it fails to open. Both traps are in
   `pbip-and-tmdl.md` in the `powerbi-project-and-tools` skill.

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

No `definition/` folder full of `.tmdl` files means the project saved in another format. Check the
TMDL option above and save again.

## Initialise git before the first real change

```powershell
cd C:\src\MyReport
git init
git add -A
git commit -m "Initial pbip from Desktop"
```

Desktop writes a `.gitignore` that excludes `.pbi\cache.abf` and `localSettings.json`. Check it
exists before the first commit, because committing `cache.abf` puts the whole dataset in git
history. From here, work on a branch and open a pull request per change.

## Set the report level switch for container styling

Turn on the modern visual header so subtitles, dividers, shadows, and header tooltips work at all.
In Desktop this is under File, Options and settings, Options, Report settings, and it writes
`"useStylableVisualContainerHeader": true` into `report.json`. Without it, every container styling
property is accepted and silently ignored. See the `powerbi-pbir-builder` skill.

Check `report.json` first. Whether a new report on the Fluent 2 base theme has it on by default is
not known yet. If the setting is already true, there is nothing to do.

## Apply a theme before building pages

If the report has a look of its own, keep it. Otherwise View, Themes, Browse for themes, and pick
the default theme JSON from the `powerbi-report-design` skill. Do this before adding visuals, so
everything inherits rather than needing a restyle later.

## The handover checklist

Give the person this list and ask them to confirm each one.

- [ ] Power BI Project type available under Save as, saving TMDL
- [ ] Auto date/time off, GLOBAL page, before any data loaded
- [ ] Project saved as .pbip to a short local path, not OneDrive
- [ ] `definition/` folder contains `.tmdl` files
- [ ] `.gitignore` present, `git init` done, first commit made
- [ ] Modern visual header on (checked in `report.json`)
- [ ] Theme applied (the report's own, or the default)
- [ ] Publish target workspace confirmed
