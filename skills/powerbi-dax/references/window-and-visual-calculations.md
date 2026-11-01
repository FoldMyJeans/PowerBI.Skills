# RANK, window functions, and visual calculations

Two newer tools for position based logic. All of this comes from docs and SQLBI, and none of it has
been run on a real model here yet. Neither Microsoft page names a capacity requirement.

## RANK and RANKX

`patterns.md` and `scoring-and-pagination.md` use RANKX. RANK is usually the better choice, per SQLBI.

- ORDERBY takes several columns, so a tie break needs no helper. On a leaderboard, DENSE ties can
  overfill a page, and adding a name column to ORDERBY gives exact page sizes (reasoning, not measured).
- It returns blank on total rows. RANKX repeats a rank there, which reads as a real value.
- If you omit the relation, it defaults to ALLSELECTED of the ORDERBY and PARTITIONBY columns. Ties
  default to SKIP, so ask for DENSE when you want no gaps.
- Keep RANKX for ranking a value against a separate table, such as a configuration table. RANK does not
  do that. SQLBI also notes a rare floating point problem with RANKX on decimals.

```dax
Product Rank =
RANK (
    DENSE,
    ALLSELECTED ( Product[Product Name] ),
    ORDERBY ( [Total Sales], DESC, Product[Product Name], ASC )
)
```

## OFFSET, WINDOW, and INDEX

These navigate a sorted, partitioned table instead of filtering on values. OFFSET returns the row a
given number of places from the current one, which can replace a FILTER and MAX shape for previous
row logic. WINDOW returns a slice of rows, and INDEX a row by position. OFFSET gives back an empty
table when the row does not exist, so the first row of a partition returns blank. If the ORDERBY and
PARTITIONBY columns cannot identify every row, it looks for extra columns to add and errors if it
finds none, so give it a unique sort.

```dax
Sales Previous Year =
CALCULATE ( [Total Sales], OFFSET ( -1, , ORDERBY ( 'Date'[Year] ) ) )
```

Sources: https://learn.microsoft.com/en-us/dax/rank-function-dax,
https://learn.microsoft.com/en-us/dax/offset-function-dax, and
https://www.sqlbi.com/articles/introducing-the-rank-window-function-in-dax/

## Visual calculations

Microsoft lists these as generally available from May 2026. A visual calculation is DAX stored on one
visual that runs over the visual's aggregated grid, and Microsoft says it often performs better than
the equivalent measure. Good fits are running sums, percent of parent, and versus previous.

The limits matter more than the syntax:

- It lives on the visual. It cannot be copied or reused across visuals.
- It does not work on custom visuals, slicers, Python or R visuals, Key Influencers, Decomposition Tree,
  or Smart Narrative. `USERELATIONSHIP`, `RELATED`, and `RELATEDTABLE` are not available.
- No dynamic format strings and no data categories, so an SVG measure's Image URL route (see
  `svg-from-dax.md`) is out. No show items with no data, and no filtering or sorting on the result.
- Data exports leave out the results. The visual cannot be pinned to a dashboard or used with Publish
  to web.

Judgement: use a measure by default, and a visual calculation only when one visual owns the logic and
exporting that number does not matter. When you need to see how one is stored, create it in Desktop and
read `visual.json` back, do not write the shape by hand.

Custom totals are built on this feature, see `ratios-and-totals.md`.

Source: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-visual-calculations-overview
