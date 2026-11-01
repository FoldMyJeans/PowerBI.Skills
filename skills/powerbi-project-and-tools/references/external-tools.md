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

Expect the Microsoft rule set to flag some house conventions. A noisy report gets ignored, and an
agent may "fix" a deliberate choice, so read hits on these rules as expected. This list is from reading
rule names against the conventions, and has not been run yet.

| Rule | What it will flag |
| --- | --- |
| `FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED` | `dim_`, `fact_`, `cfg_`, and `_Measures` names |
| `ENSURE_TABLES_HAVE_RELATIONSHIPS` | `_Measures`, `cfg_`, and other disconnected tables |
| `DATE/CALENDAR_TABLES_SHOULD_BE_MARKED_AS_A_DATE_TABLE` | The unmarked date table on a sprint or period grain model |
| `REDUCE_USAGE_OF_CALCULATED_TABLES` | A calculated table that replaces a re-run M pull |
| `USE_THE_DIVIDE_FUNCTION_FOR_DIVISION` | `/` with a constant denominator |
| `RELATIONSHIP_COLUMNS_SHOULD_BE_OF_INTEGER_DATA_TYPE` | The text key fallback when a source has no surrogate key |
| `LARGE_TABLES_SHOULD_BE_PARTITIONED` | Not useful on a small Pro import model |

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

### Cutting size once VertiPaq Analyzer names the culprit

Beyond dropping, splitting, or lowering the precision of a column:

- Raise the grain of a fact by loading it grouped. Microsoft calls this perhaps the most effective
  reduction. The cost is the detail you group away, and changing a grain later is expensive.
- Turn a prefixed ID into a whole number. `SO123456` becomes `123456`, which moves it from hash to
  value encoding. Set its summarization to Do Not Summarize.
  https://learn.microsoft.com/en-us/power-bi/guidance/import-modeling-data-reduction
- Set `IsAvailableInMdx` to false on hidden columns, which stops an attribute hierarchy being built.
  Set it with Tabular Editor 2 and read the file back, because no TMDL shape has been read here yet.
  Leave it alone on a column used for sort by, a hierarchy, a variation, or a calendar, and check
  relationship keys in your test. Measured on large tables, so expect less on a small model: 381 MB to
  191 MB and 105 s to 81 s on 5 million rows of integers (Chris Webb), and 6.27 GB to 5.53 GB and 143 s
  to 124 s on 100 million rows with only non attribute columns changed (Data Mozart). Neither has been
  reproduced here. The costs:
  - That column can no longer go on the rows or columns of an Excel PivotTable.
  - A single column DISTINCTCOUNT, MIN, or MAX can get slower, per Data Mozart.
  - TREATAS once needed the hierarchy. Chris Webb's 2022 note says that was fixed, and a 2024 comment on
    his post reports errors in some cases. This pack leans on TREATAS, so rerun those measures.

  Sources: https://docs.tabulareditor.com/en/kb/bpa-set-isavailableinmdx-false.html,
  https://blog.crossjoin.co.uk/2018/07/02/isavailableinmdx-ssas-tabular/, and
  https://data-mozart.com/hidden-little-gem-that-can-save-your-power-bi-life/

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

## The local modeling MCP (optional, read only first)

https://learn.microsoft.com/en-us/power-bi/developer/mcp/power-bi-authoring-mcp

Microsoft's local Power BI Authoring MCP server lets an agent read and edit a model open in Desktop or
a PBIP on disk, and run DAX to see results. It is optional. This is from Microsoft docs and the README,
and has not yet been run here.

- Start read only. `--readonly` blocks writes. Time a measure audit against a TMDL grep, then check
  `git status` shows no changes before you consider write access.
- A person reads and accepts the EULA. The repo's LICENSE file says MIT, but its README says use of the
  software is subject to a separate proprietary EULA, and the server blocks its tools until someone
  accepts. An agent can call `accept_eula`, and `--accepteula` skips the prompt. Do not let an agent
  decide that.
- Back up, and work in a PBIP under git, so every agent change is a diff you can review.
- Model metadata and query results reach your LLM provider.
- It does modeling only, no report pages or diagram layouts. DAX queries stop at 100,000 rows. It does
  not run on macOS. Connecting to a workspace model needs the XMLA endpoint at Read Write on a capacity,
  which is not Pro.

Microsoft's sample registers it as `@latest`. Adapted to the policy below, with the version pinned and
writes blocked:

```json
{
  "servers": {
    "powerbi-authoring-local": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@1.0.0", "--start", "--readonly"]
    }
  }
}
```

## Tool risk policy

Agent tools run code on your machine and can see your model. The house line:

- Pin versions. No `@latest` and no bare `npx -y <package>`, which fetches whatever is newest on each
  start.
- Read hooks before enabling them. A hook runs without being asked, and one that skips quietly looks
  the same as a check that passed.
- Install at project scope, not machine wide.
- No auto update on work machines.
- A person accepts any EULA, never an agent.

## The XMLA boundary, the critical license note

Repeat this every time, because it is the thing that breaks on Pro. All these tools edit your
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
- Let an agent run DAX and read the model: the local modeling MCP, read only first.
- Check an agent's report edit rendered and the numbers hold: the loop in `agent-verification.md`.

## See also

- `pbip-and-tmdl.md`: the files these tools read and write.
- `powerbi-data-and-refresh`: the refresh playbook once VertiPaq Analyzer names the culprit.
