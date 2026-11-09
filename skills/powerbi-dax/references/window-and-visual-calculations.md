# RANK, window functions, and visual calculations

From docs and SQLBI, not yet run on a real model here. Neither Microsoft page names a capacity
requirement.

## RANK and RANKX

`patterns.md` and `scoring-and-pagination.md` use RANKX. RANK is usually the better choice, per SQLBI.

- ORDERBY takes several columns, so a tie break needs no helper. On a leaderboard, DENSE ties can
  overfill a page, and adding a name column to ORDERBY gives exact page sizes (reasoning, not
  measured).
- It returns blank on total rows. RANKX repeats a rank there, which reads as a real value.
- With no relation it defaults to ALLSELECTED of the ORDERBY and PARTITIONBY columns. Ties default
  to SKIP, so ask for DENSE when you want no gaps.
- Keep RANKX for ranking a value against a separate table, such as a configuration table. RANK
  does not do that. SQLBI also notes a rare floating point problem with RANKX on decimals.

```dax
Product Rank =
RANK (
    DENSE,
    ALLSELECTED ( Product[Product Name] ),
    ORDERBY ( [Total Sales], DESC, Product[Product Name], ASC )
)
```

## OFFSET, WINDOW, and INDEX

They navigate a sorted, partitioned table instead of filtering on values. OFFSET returns the row a
given number of places away, which can replace a FILTER and MAX shape for previous row logic. WINDOW
returns a slice, INDEX a row by position.

- OFFSET returns an empty table when the row does not exist, so the first row of a partition is
  blank.
- If ORDERBY and PARTITIONBY cannot identify every row, it looks for extra columns to add and errors
  if it finds none. Give it a unique sort.

```dax
Sales Previous Year =
CALCULATE ( [Total Sales], OFFSET ( -1, , ORDERBY ( 'Date'[Year] ) ) )
```

Sources: https://learn.microsoft.com/en-us/dax/rank-function-dax,
https://learn.microsoft.com/en-us/dax/offset-function-dax, and
https://www.sqlbi.com/articles/introducing-the-rank-window-function-in-dax/

## Visual calculations

Generally available from May 2026. DAX stored on one visual that runs over the visual's aggregated
grid, and Microsoft says it often performs better than the equivalent measure. Good fits: running
sums, percent of parent, versus previous.

The limits matter more than the syntax:

- It lives on the visual. It cannot be copied or reused across visuals.
- Not on custom visuals, slicers, Python or R visuals, Key Influencers, Decomposition Tree, or Smart
  Narrative. `USERELATIONSHIP`, `RELATED`, and `RELATEDTABLE` are not available.
- No dynamic format strings and no data categories, so an SVG measure's Image URL route
  (`svg-from-dax.md`) is out. No show items with no data, and no filtering or sorting on the result.
- Data exports leave out the results. The visual cannot be pinned to a dashboard or used with
  Publish to web.

Newer than the GA:

- Small multiples work (September 2026). The small multiples field is the `ROWPAGES` axis, so
  `RUNNINGSUM ( [Sales], ROWPAGES )` runs across panels.
- `LOOKUP` takes a last argument, `EXPLICIT` (the default) or `INFERRED` (July 2026). INFERRED fills
  in the axis columns that follow from the ones you give, so `LOOKUP ( [Sales], [Year], 2025,
  INFERRED )` shows on every row under 2025 instead of only the exact match.

Judgement: use a measure by default, and a visual calculation only when one visual owns the logic and
exporting that number does not matter. In `visual.json` it is stored as a `NativeVisualCalculation`
projection with `Language`, `Expression`, `Name`, and an optional `DataType`. Create it in Desktop and
read the file back rather than writing the shape by hand.

Custom totals are built on this feature, see `ratios-and-totals.md`.

Source: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-visual-calculations-overview
