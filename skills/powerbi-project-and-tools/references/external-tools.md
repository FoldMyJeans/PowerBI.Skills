# External tools

These are the free tools worth having around a Power BI model on Pro. All of them edit your LOCAL
pbip or pbix file, which is fully allowed on Pro. Read the XMLA note near the end before you try
to point any of them at a published dataset.

## Tabular Editor 2 (free, open source)

https://tabulareditor.com/

- Fast model and measure editing. Create, rename, and bulk edit measures, columns, and display
  folders far quicker than in Desktop.
- Reads and writes TMDL. Works directly on the pbip `definition` folder, or connected to the
  local Analysis Services model that Desktop runs while it is open.
- Best Practice Analyzer. A rules engine that flags modeling problems, for example measures with
  no format string, columns that should be hidden, missing keys on dimension tables, and
  relationships on high cardinality columns. Load the community Microsoft BestPracticeRules JSON
  from the `microsoft/Analysis-Services` repo to get a solid default rule set.
- Note. The free tool is Tabular Editor 2. Tabular Editor 3 is a paid product. You do not need 3
  for BPA or TMDL editing.

## DAX Studio (free)

https://daxstudio.org/

- Author and run DAX queries against a model. The place to develop and test a measure in
  isolation.
- Server Timings and Query Plan. Run a query and see where the time goes, storage engine versus
  formula engine, so you can tell why a measure is slow.
- VertiPaq Analyzer is built in. It shows column level storage: which columns and tables eat the
  model size, their cardinality, and how they encode. This is the tool for size and refresh
  tuning. Find the fat, high cardinality column, then drop it, split it, or lower its precision.
- Use this when the model is near the 1 GB Pro cap or refresh is slow and you need to know which
  column or table to attack.

## Bravo for Power BI (free)

https://bravo.bi/

- Analyze model size. A lighter, friendlier view than VertiPaq Analyzer for a quick look.
- Format DAX. Uses the DAX Formatter engine to clean up measure formatting in place.
- Generate a Date table. Builds a correct Date dimension and can wire it into the model. Handy
  when you need a proper date table fast.

## Measure Killer (free single file tier)

https://measurekiller.com/

- Finds unused measures and columns across the model and the report, so you can strip dead weight
  and shrink the model.
- The free tier works on a single local file. Tenant wide or multi report analysis is paid.

## The XMLA boundary, the critical license note

Repeat this every time, because it is the thing that breaks on Pro. All four tools edit your
LOCAL pbip or pbix file, and that is fully fine on Pro. The moment you point one of them at a
dataset that is already PUBLISHED in a Pro workspace and try to WRITE changes, you need the XMLA
write endpoint. XMLA read and write on a published dataset is Premium, Premium Per User, or
Embedded. It is not on Pro.

So on Pro the loop is:

1. Edit the local pbip or pbix with the tool.
2. Save the file.
3. Republish from Power BI Desktop.

Do not expect to connect Tabular Editor to the Service and save changes to a Pro dataset. That
save will fail. See `licensing-cheatsheet.md` and `pro-vs-premium-facts.md`.

## Which tool for which job

- Bulk edit measures, apply naming, run the Best Practice Analyzer: Tabular Editor 2.
- Find the column blowing up model size, profile a slow measure, tune refresh: DAX Studio with
  VertiPaq Analyzer.
- Quick size check, format DAX, generate a Date table: Bravo.
- Find and remove unused measures and columns: Measure Killer.

## See also

- `pbip-and-tmdl.md`: the files these tools read and write.
- `powerbi-data-and-refresh`: the refresh playbook once VertiPaq Analyzer names the culprit.
