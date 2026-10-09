# Model diagram layout

The model view is where a model gets reviewed. When the relationship lines cross in every
direction nobody traces them, including the person who built the model. This reference owns one
layout that fixes that, and the script that applies it to a pbip project.

Nothing in the model changes. Same tables, same relationships. Only the boxes move.

## The layout

Facts go in one column on the left. Dimensions go in one row across the top. Tables with no
relationship at all (the measures table, field parameters, config tables) sit in their own row
above the dimensions, out of the way of every line.

```text
              _Measures   Field parameter   Config table        no relationships
              Dim_Date    Dim_Customer      Dim_Product   ...    dimensions, one row

Fact_Sales
Fact_Orders                                                      facts, one column
Fact_Stock
```

Every line now leaves a fact sideways and turns up into a dimension, so the area between the
column and the row reads like a grid. What that makes visible:

- A dimension with a line from every fact is shared. A dimension with one line serves one fact.
- A box in the dimension row with no line is disconnected. Either it is driven by `TREATAS` or
  a field parameter on purpose, or a relationship is missing.
- A line between two boxes in the fact column is a fact to fact relationship. Those deserve a
  second look.
- A fact with more lines than you expected, or a dimension joined to something it has no
  business filtering, stands out because no other line hides it.
- A dotted line is an inactive relationship. In a tangle they disappear under the solid ones.

Inside each group the tables with the most relationships sit nearest the corner, so the busiest
lines are the shortest ones.

## By hand or by script

By hand is the supported route. Open the model view in Desktop and drag. For a model with a
handful of tables that takes about a minute.

Use the script when the model has many tables, or when the model was built by code. A model
built by writing TMDL has a diagram file that has never seen most of its tables, so Desktop
drops each new one wherever it finds room.

```powershell
python scripts\arrange_model_diagram.py "C:\pbi\ABCSales\ABCSales.SemanticModel" --dry-run
python scripts\arrange_model_diagram.py "C:\pbi\ABCSales\ABCSales.SemanticModel"
```

1. Close Power BI Desktop. It writes the diagram file from memory on save and would overwrite
   the edit.
2. Copy `diagramLayout.json` somewhere outside the project as a backup.
3. Run with `--dry-run` and read the three lists it prints: fact, dim, other. A table in the
   wrong list means its name and its relationships disagree, which is worth knowing by itself.
4. Run it for real, then open the project and look at the model view.

The edit lands in the project file, so there is nothing to save afterwards and nothing to
refresh. If somebody arranged the diagram by hand already, ask before running. The script
replaces every position.

## How the script decides

- Name first. A table named `fact_x` or `Fact x` is a fact. A table named `dim_x`, `Dim x`, or
  `Dimension x` is a dimension.
- Otherwise `relationships.tmdl` decides. A table on the one side of any relationship is a
  dimension. A table that only ever sits on the many side is a fact. A table in no
  relationship goes to the top row.
- Box sizes are never changed.
- A table that has a TMDL file but no box yet gets one, in the first diagram only (the one
  Desktop names All tables). Other diagrams are subsets somebody chose, so they are rearranged
  but nothing is added to them. Auto date/time tables are skipped, Desktop never draws them.
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

- `nodeIndex` is the table name. `nodeLineageTag` is the table's `lineageTag` from its TMDL
  file. Desktop itself leaves the tag off some boxes, so it is not required.
- `location` can be an empty object on a box Desktop has not placed yet.
- The size the script gives a new box is a guess at Desktop's default: width 234, height 80
  plus 24 for each column or measure, capped at 300. That is read off boxes Desktop sized
  itself (one field 104, two fields 128, five fields 200, eight fields 272), not from any
  documentation. If a new box looks wrong, resize it by hand.

## Limits

- Microsoft's project documentation says this file does not support external editing
  (https://learn.microsoft.com/power-bi/developer/projects/projects-dataset). The file holds
  nothing but the diagram, so a bad edit cannot reach the model or the data. If Desktop objects
  when it opens the project, put the backup copy back.
- It works on a pbip project only. For a pbix, save it as a project first.
- It does not judge the model. A snowflaked dimension lands in the dimension row next to its
  parent and looks fine. Reading the lines is still the reviewer's job.
