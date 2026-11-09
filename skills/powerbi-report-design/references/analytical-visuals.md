# Native analytical and AI visuals

Almost all of these are Pro safe, because their AI runs in the Power BI engine, not Copilot. Only
Copilot authored narrative needs a Fabric capacity. Use these before a custom visual from AppSource.

## Decomposition tree

Breaks a measure down level by level, one branch at a time. The High value and Low value AI
options pick the next field that most raises or lowers the number.

- Pro safe, AI included. The High and Low value logic runs in the engine, not Copilot.
- For root cause exploration: which team, then which service, then which priority drives the open
  items.
- Fix the drill path with the analysis, or the reader wanders.

## Key influencers

Ranks what moves a metric, for example priority P1 makes a breach 3.2 times more likely.

- Pro safe. In engine machine learning on the local model.
- Two traps, both silent: it does not run on DirectQuery or an Analysis Services live connection,
  and its categorical analysis is unavailable when the model has calculation groups (they set
  Discourage Implicit Measures). Test it on the actual model.
- Categorical target (breach yes or no) or continuous (average resolve hours). Categorical reads
  easier.

## Native small multiples

A formatting toggle on cartesian charts (bar, column, line, area), not a separate visual. A field
in the Small multiples well splits the chart into a grid on a shared axis.

- Pro safe and core.
- Rows and columns are set in Format, Small multiples, Grid layout, up to 6 by 6. Fluent 2
  reports start new ones at 1 by 4.
- The Analytics pane trend line and forecast are disabled while a chart is split.
- The built in answer to "many series over time".

## The new Card visual

`cardVisual` reached GA in November 2025 and replaces the old Card and Multi-row card. Prefer it
for KPIs.

- Reference labels (a comparison value and a change) live in the visual, which is how the default
  KPI card shows the delta versus the prior month.
- One `cardVisual` holds several cards and renders faster than a row of old cards.
- Pro safe. The JSON shape is in the `powerbi-pbir-builder` skill.

## KPI visual

A value against a goal with a trend behind it, for one tracked metric with a target.

- Pro safe.
- Sort the data by the trend axis before converting to a KPI visual, or the trend line and the
  indicator can read the wrong direction.

## Q&A visual (do not invest here)

Pro safe today, but retiring around December 2026, replaced by Copilot. Do not build new reports
around it. For guided exploration use the decomposition tree.

## Smart narrative

- Custom mode is Pro safe. You write the sentences and bind measures, and the text follows the
  filters.
- Copilot authored narrative needs a Fabric or Premium capacity. Flag it, do not assume it.

## Pro vs Fabric at a glance

| Visual | Pro safe | Needs Fabric or Premium |
| --- | --- | --- |
| Decomposition tree (with High/Low value AI) | Yes | No |
| Key influencers | Yes (not on DirectQuery or AAS live, calc groups limit it) | No |
| Native small multiples | Yes | No |
| New Card visual (`cardVisual`) | Yes | No |
| KPI visual | Yes | No |
| Q&A visual | Yes, but retiring around Dec 2026 | No |
| Smart narrative, Custom mode | Yes | No |
| Smart narrative, Copilot authored | No | Yes |
| Any Copilot feature | No | Yes |

## Sources

Microsoft Learn under https://learn.microsoft.com/en-us/power-bi/visuals/ for each visual above.
