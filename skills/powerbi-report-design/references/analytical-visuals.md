# Native analytical and AI visuals

Power BI ships several analytical and AI driven visuals in the box. The headline for this repo:
almost all of them are Pro safe, because their AI runs inside the Power BI engine, not in
Copilot. The only thing here that needs a Fabric capacity is Copilot authored narrative. Use
these before reaching for a custom visual from AppSource.

## Decomposition tree

Breaks a measure down level by level. You pick the measure, then add fields to drill by, and the
tree expands one branch at a time. The two AI options, High value and Low value, let the visual
choose the next field that most increases or decreases the number.

- Pro safe, including the AI. The High and Low value logic runs in the engine, it is not Copilot
  and needs no Fabric.
- Use it for root cause exploration: which team, then which service, then which priority is
  driving the open items.
- It is an exploration visual. Fix the drill path with the analysis, or the reader can wander.

## Key influencers

Ranks what actually moves a metric. You give it a metric to Analyze and fields to explain by, and
it reports, for example, that priority being P1 makes a breach 3.2 times more likely.

- Pro safe. The ranking runs on the local model with in engine machine learning, not Copilot.
- Two real traps to document: it does not run on a DirectQuery model or an Analysis Services live
  connection, and its categorical analysis is unavailable when the model has calculation groups
  (they set Discourage Implicit Measures). Both fail quietly, so test it on the actual model.
- Works for a categorical target (breach yes or no) and a continuous target (average resolve
  hours). Categorical is the easier read.

## Native small multiples

Not a separate visual, a formatting toggle on the cartesian charts (bar, column, line, area).
Drop a field into the Small multiples well and the one chart becomes a grid of small charts on a
shared axis.

- Pro safe and core.
- Grid size runs from 2 by 2 up to 6 by 6, set in Format, Small multiples, Grid layout.
- One limit to know: the Analytics pane trend line and forecast are disabled while a chart is
  split into small multiples.
- This is the built in answer to "many series over time". Prefer it over five overlapping lines.

## The new Card visual

The card was rebuilt. The new `cardVisual` reached general availability in November 2025 and
replaces both the old Card and the old Multi-row card. Prefer it for KPIs.

- It carries reference labels (a comparison value and a change) in the visual itself, which is
  how the house KPI card shows the delta versus the prior month.
- One `cardVisual` can hold multiple cards, which renders and refreshes faster than a row of
  separate old cards.
- Pro safe. See the `powerbi-pbir-builder` skill for its JSON shape.

## KPI visual

Shows a value against a goal with a trend behind it. Good for a single tracked metric with a
target.

- Pro safe.
- Gotcha: sort the underlying data by the trend axis before you convert to a KPI visual, or the
  trend line and the indicator can read the wrong direction.

## Q&A visual (do not invest here)

The natural language Q&A visual lets a reader type a question and get a generated visual. It is
Pro safe today, but Microsoft has it on a retirement path, replaced by the Copilot experience,
with removal slated for around December 2026. Do not build new reports around it. If a report
needs guided exploration, use the decomposition tree instead.

## Smart narrative

Generates a text summary of a visual or a page.

- Custom mode is Pro safe. You author the dynamic sentences and bind measures into them, and the
  text updates with the filters. This is fine to use.
- Copilot authored narrative (let the AI write the summary) needs a Fabric or Premium capacity.
  Flag it, do not assume it is available.

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

Microsoft Learn on the decomposition tree, key influencers, small multiples, the card visual, the
KPI visual, the Q&A visual, and smart narrative, all under
https://learn.microsoft.com/en-us/power-bi/visuals/
