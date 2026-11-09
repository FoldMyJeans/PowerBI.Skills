# Functions and calculation groups

Two ways to stop repeating DAX. The docs name no capacity or licence requirement for either (silence,
not a promise about Pro), and neither has been run on a real model here yet, so publish a test copy
to a Pro workspace before you build on one. The TMDL below is Microsoft's documented form, not read
from a file Desktop wrote, so define one in Desktop and read it back before writing many by hand.

How to choose (judgement, not a documented rule): a calculation group when a report user picks the
calculation, a function when the author reuses logic.

## User defined functions

Generally available in Desktop and the Service from the June 2026 release.

- They need database compatibility level 1702 or higher. Compatibility upgrades are one way, so
  commit or back up first, per Tabular Editor's docs.
- Define them in DAX query view, TMDL view, or Model view. In a PBIP they are stored in
  `functions.tmdl` in the `definition` folder.
- Tabular Editor 2 supports functions, without the `Namespace`, `PackageId`, and `PackageVersion`
  properties that Tabular Editor 3 adds.
- Good for logic repeated across measures, such as min-max scoring, SVG scaling, and page window
  maths. Editing one function is a smaller diff than editing nine measures.

### The shape

```dax
/// Score a value between a min and a max, 0 to 1.
FUNCTION Local.MinMax = ( value : SCALAR NUMERIC, lo : SCALAR NUMERIC = 0, hi : SCALAR NUMERIC = 1 ) =>
    DIVIDE ( value - lo, hi - lo )
```

- That is the DAX query view form inside `DEFINE`. In TMDL view and `functions.tmdl` it is
  `function Local.MinMax = ( ... ) => ...`. The `///` lines become the description.
- `= default` makes a parameter optional, in any position, so `Local.MinMax ( x, , 10 )` is legal.
  A default may not reference another optional parameter.
- Up to 256 parameters. Type hints: `AnyVal` (the default), `Scalar` with a subtype (`Int64`,
  `Decimal`, `Double`, `String`, `DateTime`, `Boolean`, `Numeric`, `Variant`), `Table`, and the
  reference types `AnyRef`, `ColumnRef`, `MeasureRef`, `TableRef`, `CalendarRef`. Reference types
  are always `expr`.
- `TABLEOF ( <column, measure or calendar> )` returns the table it lives on. `NAMEOF ( <object>
  [, <component> [, <escaped>]] )` returns a part of its name, and the one argument form still works. Component is `TABLE`, `COLUMN`, `MEASURE`,
  `CALENDAR`, `FULL`, `SELF` or `PARENT`. Escaped is `ESCAPED`, `UNESCAPED` or `MINIMALLYESCAPED`.
  Both make a function that takes a column reference useful. Neither works in a visual calculation,
  a DirectQuery calculated column, or RLS.
- `INFO.USERDEFINEDFUNCTIONS ()` lists the model's functions.

### The traps

- **`val` or `expr` decides when an argument is evaluated.** `val`, the default, is evaluated once
  by the caller, in the caller's row and filter context, before the function runs. `expr` is
  evaluated inside the function, can run many times, and inherits only the filter context. The
  wrong one can return an empty table or ignore a CALCULATE filter with no error, so state the mode.
- **No automatic context transition.** A measure reference gets one, an `expr` parameter does not,
  so inside an iterator wrap the parameter in CALCULATE.
- **An `expr` inside an iterator can be re-evaluated for every row.** Consider computing it once
  into a column with ADDCOLUMNS.
- **Typed parameters convert each argument.** `CastToInt ( 3.5 )` gives 4 on Microsoft's page, and
  in SQLBI's example an INT64 add of 3.4 and 2.4 returns 5, not 5.8.
- **Limits.** No recursion, no overloads, no explicit return type, no enum return, no hiding, no
  display folders, no translations, and the model needs at least one table. Object level security
  does not transfer to functions.

### Naming

No display folders, so the name carries the grouping. Names allow dots, letters, digits, and
underscores only, so measure style Title Case with spaces cannot carry over. SQLBI's convention fits:
PascalCase with dots for categories, a `Local.` prefix for functions tied to this model, a library
prefix for portable ones, and camelCase parameters with a suffix on `expr` kinds such as `metricExpr`
or `lookupTable`.

Sources: https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions,
https://www.sqlbi.com/articles/introducing-user-defined-functions-in-dax/, and
https://docs.sqlbi.com/dax-style/dax-naming-conventions

## Calculation groups

Supported at compatibility level 1500 and higher, which Microsoft says covers all Power BI semantic
models. Create them in Desktop from the Model view ribbon or TMDL view, so XMLA is not required. They
cut the YTD, PY, and YoY times every base measure explosion.

### The traps

- **Implicit measures are discouraged the moment you add one.** Desktop prompts you to set that
  property. Column aggregations can then no longer be added to visuals. Existing ones keep working,
  and calculation items do not apply to them.
- **Every measure becomes variant in reports.** That can make a dynamic format string that reuses a
  measure show an error. Wrap it in `FORMAT ( [Dynamic format string], "" )` or move the expression
  to a function.
- **Math on a text measure errors in the visual** with `Cannot convert value ... of type Text to
  type Numeric`. This pack's own taxonomy has text measures everywhere (`Title <Visual>`,
  `<X> Color`, `<Component> SVG`). Guard every item that does math.

  ```dax
  IF ( ISNUMERIC ( SELECTEDMEASURE () ), SELECTEDMEASURE () * 2, SELECTEDMEASURE () )
  ```

- **Precedence decides the nesting.** The highest precedence group wraps the others, and only its
  dynamic format string applies.
- **An item applies only when exactly one item of its group is in filter context.** With none or
  several, selection expressions and the model's `selectionExpressionBehavior` setting decide, and
  the default gives you the plain measure.
- **Limits.** No row level security on the group itself, no object level security, no smart
  narrative visual.

Add a group to a copy that already holds your title and SVG measures, open every page, and record
which visuals error.

Sources: https://learn.microsoft.com/en-us/power-bi/transform-model/calculation-groups and
https://learn.microsoft.com/en-us/analysis-services/tabular-models/calculation-groups

## Dynamic format strings do not scale to K units

The format `#,0,"K"` printed 9,221K on a data label instead of 9.2K. A one line
`formatStringDefinition` in TMDL stopped the project opening, and the fenced block form loaded but
still did not scale. Use fixed display units for the whole chart instead, `labelDisplayUnits` 1000
with one decimal, in `powerbi-chart-recipes`.
