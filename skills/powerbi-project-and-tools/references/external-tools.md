# External tools

The free tools worth having around a Power BI model on Pro. All of them edit your LOCAL pbip or
pbix, which is fine on Pro. Read the XMLA boundary below before pointing one at a published model.

## Tabular Editor 2 (free, open source)

https://tabulareditor.com/

- Create, rename, and bulk edit measures, columns, and display folders far quicker than in Desktop.
- Reads and writes TMDL. Works on the pbip `definition` folder, or connected to the local Analysis
  Services model that Desktop runs while it is open.
- Best Practice Analyzer (BPA). Load the community Microsoft BestPracticeRules JSON from the
  `microsoft/Analysis-Services` repo for a default rule set.
- Tabular Editor 3 is paid. You do not need it for BPA or TMDL editing.

Expect the Microsoft rule set to flag some conventions the skills use. A noisy report gets ignored, and an
agent may "fix" a deliberate choice, so read hits on these rules as expected. This list is from
reading rule names against the conventions, and has not been run yet.

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

- Author and run DAX queries. The place to test a measure in isolation.
- Server Timings and Query Plan show storage engine versus formula engine time.
- VertiPaq Analyzer is built in: column level size, cardinality, and encoding. Use it when the
  model is near the 1 GB Pro cap or refresh is slow, to find the column or table to attack.

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
    his post reports errors in some cases. The skills lean on TREATAS, so rerun those measures.

  Sources: https://docs.tabulareditor.com/en/kb/bpa-set-isavailableinmdx-false.html,
  https://blog.crossjoin.co.uk/2018/07/02/isavailableinmdx-ssas-tabular/, and
  https://data-mozart.com/hidden-little-gem-that-can-save-your-power-bi-life/

## Bravo for Power BI (free)

https://bravo.bi/

- Model size, a lighter view than VertiPaq Analyzer.
- Format DAX in place with the DAX Formatter engine.
- Generate a Date table and wire it into the model.

## Measure Killer (free single file tier)

https://measurekiller.com/

- Finds unused measures and columns across the model and the report.
- The free tier works on a single local file. Tenant wide or multi report analysis is paid.

## The modeling MCP (optional, read only first)

https://learn.microsoft.com/en-us/power-bi/developer/mcp/power-bi-authoring-mcp

Microsoft's local Power BI Authoring MCP server lets an agent read and edit a model open in Desktop or
a PBIP on disk, and run DAX. This is from Microsoft docs and the README, and has not yet been run here.

- Start read only. `--readonly` blocks writes. Time a measure audit against a TMDL grep, then check
  `git status` shows no changes before you consider write access.
- A person reads and accepts the EULA. The repo's LICENSE file says MIT, but its README says use of the
  software is subject to a separate proprietary EULA, and the server blocks its tools until someone
  accepts. An agent can call `accept_eula`, and `--accepteula` skips the prompt. Do not let an agent
  decide that.
- Work in a PBIP under git, so every agent change is a diff you can review.
- Model metadata and query results reach your LLM provider.
- Modeling only, no report pages or diagram layouts. DAX queries stop at 100,000 rows. Not on
  macOS. Connecting the local server to a workspace model needs the XMLA endpoint at Read Write on a
  capacity, which is not Pro.
- The local server is GA. A hosted server (preview, September 2026) at
  `https://api.fabric.microsoft.com/v1/mcp/powerbi/authoring` works on workspace models without
  XMLA and needs a tenant setting and Write on the model. Its page names no capacity, so whether it
  reaches a Pro workspace model is untested. It cannot see Desktop or files on disk. Register one
  server or the other, never both.

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

Agent tools run code on your machine and can see your model.

- Pin versions. No `@latest` and no bare `npx -y <package>`, which fetches whatever is newest on each
  start.
- Read hooks before enabling them. A hook runs without being asked, and one that skips quietly looks
  the same as a check that passed.
- Install at project scope, not machine wide.
- No auto update on work machines.
- A person accepts any EULA, never an agent.

## The XMLA boundary

Pointing a tool at a model PUBLISHED in a Pro workspace and saving changes needs the XMLA write
endpoint, which is Premium, Premium Per User, or Embedded. That save fails on Pro. So with a tool:

1. Edit the local pbip or pbix.
2. Save the file.
3. Republish from Power BI Desktop.

Web modeling in the Service is the one documented Pro route to edit a published model, with no
undo. See
`pro-vs-premium-facts.md`.

## Which tool for which job

- Bulk edit measures, apply naming, run the Best Practice Analyzer: Tabular Editor 2.
- Find the column blowing up model size, profile a slow measure, tune refresh: DAX Studio with
  VertiPaq Analyzer.
- Quick size check, format DAX, generate a Date table: Bravo.
- Find and remove unused measures and columns: Measure Killer.
- Let an agent run DAX and read the model: the modeling MCP, read only first.
- Check an agent's report edit rendered and the numbers hold: the loop in `agent-verification.md`.

## See also

- `pbip-and-tmdl.md`: the files these tools read and write.
- `powerbi-data-and-refresh`: the refresh playbook once VertiPaq Analyzer names the culprit.
