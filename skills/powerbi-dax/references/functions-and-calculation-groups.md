# Functions and calculation groups

Two ways to stop repeating DAX. The docs name no capacity requirement for either, but neither has
been run on a real model here yet, so publish a test copy to a Pro workspace before you build on one.
Neither section shows TMDL, because none of it has been read from a file Desktop wrote. Define them
in Desktop and read the files back.

## How to choose

Judgement, not a documented rule: use a calculation group when a report user picks the calculation,
and a function when the author reuses logic.

## User defined functions

Microsoft lists these as generally available in Desktop and the Service from the June 2026 release.
Neither Microsoft page names a capacity or licence requirement, which is silence rather than a promise
about Pro.

- They need database compatibility level 1702 or higher. Compatibility upgrades are one way, so commit
  or back up first, per Tabular Editor's docs.
- Define them in DAX query view, TMDL view, or Model view. In a PBIP they are stored in
  `functions.tmdl` in the `definition` folder.
- Tabular Editor 2 supports functions, without the `Namespace`, `PackageId`, and `PackageVersion`
  properties that Tabular Editor 3 adds.

What they are good for: logic now repeated across measures, such as min-max scoring, SVG scaling, and
page window maths. An agent editing one function produces a smaller diff than editing nine measures.

### The traps

- **`val` or `expr` decides when an argument is evaluated.** `val`, the default, is evaluated once by
  the caller, in the caller's row and filter context, before the function runs. `expr` is evaluated
  inside the function, can run many times, and inherits only the filter context. The wrong one can
  return an empty table or ignore a CALCULATE filter with no error, so state the mode.
- **There is no automatic context transition.** A measure reference gets one, an `expr` parameter does
  not, so inside an iterator wrap the parameter in CALCULATE. SQLBI covers this.
- **An `expr` inside an iterator can be re-evaluated for every row**, which can be costly. Consider
  computing it once into a column with ADDCOLUMNS.
- **Typed parameters convert each argument.** `CastToInt ( 3.5 )` gives 4 on Microsoft's page, and in
  SQLBI's example an INT64 add of 3.4 and 2.4 returns 5, not 5.8.
- **Limits.** No recursion, no overloads, no explicit return type, no display folders, no translations,
  and they need a model with at least one table. Object level security does not transfer to functions.
  Microsoft's list says a function cannot be hidden, while screenshots on the same page show a hide
  option, so check your build.

### Naming

Display folders are not available, so the name has to carry the grouping. Names may use dots, and
otherwise only letters, digits, and underscores, so the Title Case with spaces used for measures cannot
carry over. SQLBI's convention fits: PascalCase with dots for categories, a `Local.` prefix for
functions tied to this model, a library prefix for portable ones, and camelCase parameters with a
suffix on `expr` kinds such as `metricExpr` or `lookupTable`.

Sources: https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions,
https://www.sqlbi.com/articles/introducing-user-defined-functions-in-dax/, and
https://docs.sqlbi.com/dax-style/dax-naming-conventions

## Calculation groups

Supported at compatibility level 1500 and higher, which Microsoft says covers all Power BI semantic
models. You create them in Desktop from the Model view ribbon or TMDL view, so XMLA is one route, not a
requirement. They cut the measure explosion of YTD, PY, and YoY times every base measure.

### The traps

- **Implicit measures are discouraged the moment you add one.** A group needs that property on, and
  Desktop prompts you to set it. Column aggregations can then no longer be added to visuals. Existing
  ones keep working, and calculation items do not apply to them.
- **Every measure becomes variant in reports.** As soon as one group exists, reports treat all measures
  as variant. That can make a dynamic format string that reuses a measure show an error. Wrap it in
  `FORMAT ( [Dynamic format string], "" )` or move the expression to a function.
- **Math on a text measure errors in the visual.** The error is `Cannot convert value ... of type Text
  to type Numeric`. This hits this pack's own taxonomy directly: `Title <Visual>`, `<X> Color`, and
  `<Component> SVG` are all text measures. Guard every item that does math.

  ```dax
  IF ( ISNUMERIC ( SELECTEDMEASURE () ), SELECTEDMEASURE () * 2, SELECTEDMEASURE () )
  ```

- **Precedence decides the nesting.** The highest precedence group wraps the others, and only its
  dynamic format string applies.
- **An item only applies when exactly one item of its group is in filter context.** With none or
  several, selection expressions and the model's `selectionExpressionBehavior` setting decide the
  result, and the default gives you the plain measure.
- **Limits.** Row level security on the group itself is not supported, and neither is object level
  security or the smart narrative visual.

Add a group to a copy that already holds your title and SVG measures, open every page, and record which
visuals error.

Sources: https://learn.microsoft.com/en-us/power-bi/transform-model/calculation-groups and
https://learn.microsoft.com/en-us/analysis-services/tabular-models/calculation-groups

## A dynamic format string for K units did not scale

The goal was K units only from 1,000 up on a chart. The format `#,0,"K"` printed 9,221K on a data label
instead of 9.2K. A one line `formatStringDefinition` in TMDL stopped the project opening, and the fenced
block form loaded but still did not scale. The fix was fixed display units for the whole chart,
`labelDisplayUnits` 1000 with one decimal, in `powerbi-chart-recipes`.
