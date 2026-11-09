# Naming and measures

Where measures live, how tables and measures are named, what gets hidden, and the Date table.

## Put every measure in a `_Measures` table

One dedicated holder table, `_Measures`. Not on the fact, not scattered across data tables. Even
one measure on a data table ties it to that table's lifetime and buries it under the data columns.
The leading underscore sorts the table to the top of the field list.

To make one in Desktop:

1. Home, Enter data, create a table with one throwaway column, load it.
2. Rename it `_Measures`.
3. Create or move your measures into it.
4. Hide the throwaway column. A table holding only measures shows with the calculator icon, pinned
   near the top.

## Never name a table exactly `Measures` (reserved name trap)

The literal name `Measures` is reserved. A model with a table named exactly `Measures` can fail to
open in Desktop with an unsupported table name error, and it has caused service side breakage.
Avoid the old leading space trick (`" Measures"`) too, recent Desktop validation rejects it. Use
`_Measures`.

## Prefix every table with its role

A prefix taxonomy that doubles as a pipeline. This is the default for a new model, not a standard:

| Prefix | Holds |
| --- | --- |
| `stg_` | raw pull from one source, load disabled |
| `int_` | intermediate transform, load disabled |
| `xform_` | a union or reshape that several tables build on |
| `dim_` | dimension |
| `fact_` | fact |
| `cfg_` | config read only by DAX, hidden |
| `_Measures` | the measure holder |

The field list sorts into pipeline order, and a table's role and visibility read from its name. A
`stg_` table showing in the field list is a bug you can spot without opening anything.

SQLBI and Tabular Editor both advise against `dim` and `fact` prefixes, and the cost is a visible
`fact_effort` in report authors' field lists. The prefixes are kept here because an agent or a
reviewer can read a table's role from its name, which is judgement. Follow a model's existing names
when it has them. PBIR field references carry table names, so settle this on a new model and do not
rename an existing one for it.

Mirror the taxonomy in the Power Query query groups. In TMDL, a backslash makes a nested group:

```tmdl
queryGroup 00_Admin
	annotation PBI_QueryGroupOrder = 0
queryGroup 02_Staging
	annotation PBI_QueryGroupOrder = 2
queryGroup 04_Model\Dimensions
	annotation PBI_QueryGroupOrder = 0
```

## Naming conventions

- Friendly business names, renamed in the model so every report inherits them. `SalesAmount`
  becomes `Sales Amount`, `cust_nm` becomes `Customer Name`.
- One casing style for user facing names (Title Case with spaces reads well on a visual). No
  `Sales Amount` next to `unitprice`.
- Measures named for the business question: `Total Sales`, `Sales YTD`, `Open Tickets`, never
  `Measure 1`. The name shows as a column header.
- A column that must keep a technical name for a join gets hidden.

Renaming a measure in a PBIP by hand touches four places: the TMDL definition, every DAX reference
to it, every `visual.json` that uses it (`Property`, `queryRef`, `nativeQueryRef`, and any selector
`metadata`), and the culture file's `ConceptualProperty`. Grep the project for the old name until
only culture term keys remain. Those can stay.

## Give every measure a display folder, a description, and a format string

Set these before a measure ships.

- `DisplayFolder` groups related measures by subject, for example `Sales`, `Sales\YoY`, `Capacity`.
- `Description` is a one line note on what the measure does and any assumption it bakes in. It
  shows as a tooltip on hover. Set it in the Properties pane, or as `///` lines directly above the
  measure: in TMDL, and since July 2026 in DAX query view (`///` lines above `MEASURE` inside
  `DEFINE`, then Update model).
- `FormatString`, set explicitly. A percent measure with no format string shows as a raw decimal
  on a card.

```tmdl
	/// Actual logged effort over the estimate. Returns 0, not blank, when no estimate exists.
	measure 'Effort Ratio' = DIVIDE ( [Total Effort], [Estimated Effort], 0 )
		displayFolder: Ratios
		formatString: 0.0%
		lineageTag: 7d000001-0000-4000-8000-000000000001
```

If you clone that block:

- The third `DIVIDE` argument is what makes the description true. With two arguments it returns
  blank, not 0, and a description that disagrees with its own DAX is worse than none. The 0 is for
  this example, not a default. The `powerbi-dax` skill has the cost of returning a value instead of
  blank.
- `lineageTag` must be unique across the whole model. Generate a fresh GUID per measure. Paste the
  same one twice and the project stops opening, with an error that names a different table than the
  one you broke.

`annotation PBI_FormatHint = {"isGeneralNumber":true}` is not a format string. It records that the
format was left on the default. An audit that greps for any formatting counts those lines and
reports a clean model that has none. Grep for `formatString:` specifically.

## A measure name taxonomy that survives missing folders

Display folders get skipped. A naming pattern does not, because the name is what people read. Use
one that carries the grouping in the name and maps straight onto folders later:

| Pattern | Returns | Folder it maps to |
| --- | --- | --- |
| `Title <Visual>` | a string for a dynamic visual title | `Titles` |
| `<X> Color`, `<X> Heat Font` | a hex string | `Formatting` |
| `<X> %`, `<X> Ratio` | a ratio | `Ratios` |
| `<X> Hours` | a quantity | `Effort` |
| `Alt Text <Visual>` | a narrative string for screen readers | `Accessibility` |
| `<Component> HTML`, `<Component> SVG` | markup for a DAX generated visual | `Components` |

Building the accessibility text and the HTML or SVG is `powerbi-dax` territory. This table only
says where the name and folder land. Two of these are rules:

- One title measure per visual, named after the visual it titles, not the number it computes. When
  the visual is deleted, the measure to delete is obvious.
- Never ship a background color measure without its paired font color measure. On the dark end of
  a color ramp, dark text is unreadable, so the pair always travels together.

## Hide keys and technical columns

The field list should show only what a report author should touch.

- Hide every key column, surrogate keys and the foreign keys on the fact alike.
- Hide sort by columns and other helpers (a `MonthNumber` used only to sort `Month`).
- Left visible: descriptive dimension columns to slice by, and the measures in `_Measures`.

Hiding is not security. It tidies the field list and does not stop anyone who can edit the model.

### `changedProperty = IsHidden` does not hide anything

In TMDL, `changedProperty = IsHidden` only records that the property was touched. Without a
separate `isHidden` line on the column, it is visible. That is how an entire dimension reads as
hidden in a diff and ships fully exposed in the field list.

Count the real hides and compare against what you expect:

```powershell
Select-String -Path .\*.SemanticModel\definition\tables\*.tmdl -Pattern "^\s*isHidden\s*$" |
  Measure-Object
```

A scan for `changedProperty` tells you nothing about what is actually hidden.

## One Date table, marked as a date table

Exactly one Date dimension, marked (Table tools, Mark as date table, point it at the date column).

- Continuous, no gaps, covering the facts' range in full years. A year need not be a calendar year.
  Microsoft requires full years, and Desktop's marking check does not test for them (it tests
  unique, no nulls, contiguous, one timestamp), so a table that stops mid year still passes.
  https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables
- Related to each date key on the facts (order date active, other roles inactive, per
  `relationships.md`).
- Marking makes time intelligence (`TOTALYTD`, `SAMEPERIODLASTYEAR`) behave. See `powerbi-dax`.
- Generate it in M or DAX. A DAX calculated Date table is fine, keep it small.

### When a marked Date table does not apply

If the fact grain is a period the business names (a sprint, a cycle, a billing period) rather than
a date, a marked date table and time intelligence may not apply. A model whose grain is the sprint
can leave its date table unmarked on purpose, use it on a couple of relationships out of dozens,
and never call a time intelligence function.

What replaces it:

- A period dimension with a start and an end date, so a visual can still answer "when".
- Period comparison by an explicit key (a composite month or sprint key), not `SAMEPERIODLASTYEAR`.
- Cumulative windows over an ordered column, `FILTER ( ALLSELECTED ( col ), col <= MAX ( col ) )`.
  See the `powerbi-dax` skill.

Either way:

- Turn auto date/time off. In `model.tmdl` that is `annotation __PBI_TimeIntelligenceEnabled = 0`.
- Do not let an agent or reviewer "fix" a period model by marking the date table. It improves no
  measure. Marking does not add a hierarchy. It stops Desktop auto creating them and removes the
  built in date tables, and anything still bound to those stops working.

## What the report layer needs from the model

Page layout is owned by the `powerbi-report-design` skill. Its default asks little of the model:
clean summary measures for any cards, and a date or period dimension carrying the hierarchy the
page level slicer uses.

## Quick checklist

- All measures in `_Measures`, never in a table named the bare reserved word `Measures`.
- Zero measures on fact or dimension tables.
- Table names carry a role prefix, or follow the model's existing convention.
- Every shipped measure has a display folder, a description, and a format string, checked by
  grepping for `formatString:`, not for a format hint annotation.
- Key, foreign key, and sort by columns hidden with a real `isHidden` line, not just a
  `changedProperty` entry.
- User facing names friendly and consistently cased.
- The Date table decision made deliberately: one marked date table, or a period dimension with auto
  date/time off and no time intelligence.
