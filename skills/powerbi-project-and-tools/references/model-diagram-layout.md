# Model diagram layout

One model view layout that makes relationship lines traceable, and the script that applies it to a
pbip project. Nothing in the model changes, only the boxes move.

## The layout

Facts in one column on the left. Dimensions in one row across the top. Tables with no relationship
(the measures table, field parameters, config tables) in their own row above the dimensions.

```text
              _Measures   Field parameter   Config table        no relationships
              Dim_Date    Dim_Customer      Dim_Product   ...    dimensions, one row

Fact_Sales
Fact_Orders                                                      facts, one column
Fact_Stock
```

Every line leaves a fact sideways and turns up into a dimension, so the area between reads like a
grid. What that makes visible:

- A dimension with a line from every fact is shared. A dimension with one line serves one fact.
- A box in the dimension row with no line is disconnected. Either it is driven by `TREATAS` or
  a field parameter on purpose, or a relationship is missing.
- A line between two boxes in the fact column is a fact to fact relationship. Look twice.
- A fact with more lines than expected, or a dimension joined to something it has no business
  filtering, stands out.
- A dotted line is an inactive relationship. In a tangle they disappear under the solid ones.

Inside each group the tables with the most relationships sit nearest the corner, so the busiest
lines are the shortest.

## By hand or by script

By hand is the supported route: drag in the model view. For a handful of tables that takes a
minute.

Use the script when the model has many tables, or was built by code. A model built by writing TMDL
has a diagram file that has never seen most of its tables, so Desktop drops each new one wherever
it finds room.

```powershell
python scripts\arrange_model_diagram.py "C:\pbi\ABCSales\ABCSales.SemanticModel" --dry-run
python scripts\arrange_model_diagram.py "C:\pbi\ABCSales\ABCSales.SemanticModel"
```

1. Close Power BI Desktop. It writes the diagram file from memory on save.
2. Copy `diagramLayout.json` outside the project as a backup.
3. Run with `--dry-run` and read the three lists it prints: fact, dim, other. A table in the
   wrong list means its name and its relationships disagree, which is worth knowing by itself.
4. Run it for real, then open the project and look at the model view.

Nothing to save or refresh afterwards. If somebody arranged the diagram by hand already, ask before
running, because the script replaces every position.

## How the script decides

- Name first. `fact_x` or `Fact x` is a fact. `dim_x`, `Dim x`, or `Dimension x` is a dimension.
- Otherwise `relationships.tmdl` decides. A table on the one side of any relationship is a
  dimension. A table only ever on the many side is a fact. A table in no relationship goes to the
  top row.
- Box sizes are never changed.
- A table with a TMDL file but no box gets one, in the first diagram only (the one Desktop names
  All tables). Other diagrams are subsets somebody chose, so they are rearranged but nothing is
  added. Auto date/time tables are skipped, Desktop never draws them.
- Before writing, it asserts that every existing box kept its name and size, that no two boxes
  overlap, and that the output parses. It keeps the file's line endings and encoding.

## The file

`diagramLayout.json` sits in the `.SemanticModel` folder. One box, as Desktop writes it:

```json
{
  "location": { "x": 782, "y": 350 },
  "nodeIndex": "Dim_Customer",
  "nodeLineageTag": "1a2b3c4d-0001-4aaa-8bbb-100000000001",
  "size": { "height": 128, "width": 234 },
  "zIndex": 0
}
```

- `nodeIndex` is the table name. `nodeLineageTag` is the table's `lineageTag`. Desktop leaves the
  tag off some boxes, so it is not required.
- `location` can be an empty object on a box Desktop has not placed yet.
- The size the script gives a new box is a guess at Desktop's default: width 234, height 80
  plus 24 for each column or measure, capped at 300. That is read off boxes Desktop sized
  itself (one field 104, two fields 128, five fields 200, eight fields 272), not from any
  documentation. If a new box looks wrong, resize it by hand.

## Limits

- Microsoft's project documentation says this file does not support external editing
  (https://learn.microsoft.com/power-bi/developer/projects/projects-dataset). It holds only the
  diagram, so a bad edit cannot reach the model or the data. If Desktop objects on open, put the
  backup back.
- pbip only. Save a pbix as a project first.
- It does not judge the model. A snowflaked dimension lands in the dimension row next to its
  parent and looks fine. Reading the lines is still the reviewer's job.
