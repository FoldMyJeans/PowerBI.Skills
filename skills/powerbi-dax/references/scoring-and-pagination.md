# Scoring, tiering, and ranked pagination

Part A turns raw metrics into a comparable 0 to 100 score and combines several into one composite.
Part B slices a rank into pages for a leaderboard. Both build on DIVIDE and RANKX in `patterns.md`.

## Part A: normalization and composite scoring

### Min-max normalize a metric to 0-100

```dax
Sales Score =
VAR Bounds =
    ADDCOLUMNS (
        ALLSELECTED ( Product[Product Name] ),
        "@Sales", CALCULATE ( [Total Sales] )
    )
VAR MinSales = MINX ( Bounds, [@Sales] )
VAR MaxSales = MAXX ( Bounds, [@Sales] )
VAR SalesRange = MaxSales - MinSales
VAR CurrentSales = [Total Sales]
RETURN
    IF (
        SalesRange = 0,
        50,
        DIVIDE ( CurrentSales - MinSales, SalesRange ) * 100
    )
```

- The bounds are computed from the current page selection every time, never typed as literals. A
  hard coded `MinSales = 0` and `MaxSales = 100000` goes wrong the first month a product sells
  outside that range: every score above the old max clips at 100 and the report never says why.
- The `SalesRange = 0` guard covers every item in view having the same value (a single selected
  product, a metric that has not moved). DIVIDE alone would return blank, and a blank inside the
  composite below is worse than a neutral 50.

### Invert the scale for lower is better

For cost or a defect rate, `MaxRate - CurrentRate` in the numerator, instead of
`CurrentRate - MinRate`, is the entire inversion. Mark it with a comment, since nothing in the DAX
signals the flip.

```dax
Defect Score = -- inverted: lower defect rate scores higher
VAR Bounds =
    ADDCOLUMNS (
        ALLSELECTED ( Product[Product Name] ),
        "@Rate", CALCULATE ( [Defect Rate] )
    )
VAR MinRate = MINX ( Bounds, [@Rate] )
VAR MaxRate = MAXX ( Bounds, [@Rate] )
VAR RateRange = MaxRate - MinRate
VAR CurrentRate = [Defect Rate]
RETURN
    IF (
        RateRange = 0,
        50,
        DIVIDE ( MaxRate - CurrentRate, RateRange ) * 100
    )
```

### Combine normalized scores into a composite

```dax
Product Composite Score =
VAR ScoreTable = { [Sales Score], [Defect Score], [OnTime Score] }
VAR ValidScores = FILTER ( ScoreTable, NOT ISBLANK ( [Value] ) )
VAR ScoreSum = SUMX ( ValidScores, [Value] )
VAR ScoreCount = COUNTROWS ( ValidScores )
RETURN
    DIVIDE ( ScoreSum, ScoreCount )
```

Counting the valid scores instead of writing `/ 3` means a missing score lowers the denominator too,
instead of silently averaging in a zero.

### Tier classification from the composite

Rank the composite, then bucket the rank into thirds.

```dax
Product Tier =
VAR CurrentRank =
    RANKX ( ALLSELECTED ( Product[Product Name] ), [Product Composite Score], , DESC, DENSE )
VAR TotalProducts =
    CALCULATE ( DISTINCTCOUNT ( Product[Product Name] ), ALLSELECTED ( Product[Product Name] ) )
VAR TopThird = TotalProducts / 3
VAR MiddleThird = TotalProducts * 2 / 3
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( CurrentRank ), BLANK (),
        CurrentRank <= TopThird, "Top Third",
        CurrentRank <= MiddleThird, "Middle Third",
        "Bottom Third"
    )
```

### A lighter alternative: four quadrant classification

When two scores matter independently, classify on whether each clears its own threshold instead of
ranking a blend.

```dax
Product Quadrant =
VAR SalesPoints = [Sales Score]
VAR QualityPoints = [Defect Score]
VAR SalesThreshold = 50
VAR QualityThreshold = 50
RETURN
    SWITCH (
        TRUE (),
        SalesPoints >= SalesThreshold && QualityPoints >= QualityThreshold, "Star",
        SalesPoints >= SalesThreshold && QualityPoints < QualityThreshold,
            "High Volume, Low Quality",
        SalesPoints < SalesThreshold && QualityPoints >= QualityThreshold,
            "Low Volume, High Quality",
        "Needs Attention"
    )
```

Ship a paired color measure with a label measure, per the measure naming taxonomy in
`powerbi-modeling`.

## Part B: ranking with pagination

### A disconnected page table

Page numbers and labels for a slicer, related to nothing.

```tmdl
table cfg_LeaderboardPage
	lineageTag: 3b6f1000-0000-4000-8000-000000000010
	column 'Page Number'
		dataType: int64
		lineageTag: 3b6f1000-0000-4000-8000-000000000011
	column 'Page Label'
		dataType: string
		lineageTag: 3b6f1000-0000-4000-8000-000000000012
	partition cfg_LeaderboardPage = m
		mode: import
		source =
			let
			    Source = #table({"Page Number", "Page Label"}, {{1, "Page 1"}, {2, "Page 2"}, {3, "Page 3"}})
			in
			    Source
```

Generate real lineage tags in Desktop, do not copy these. Every lineage tag must be unique across the
whole model, and a duplicate breaks the pbip on open.

### Read the selection and gate the rank

SELECTEDVALUE with a default keeps the leaderboard on page 1 before anyone touches the slicer. MinRank
and MaxRank derive from one PageSize VAR.

```dax
Sales Rep Rank In Page =
VAR PageSize = 10
VAR CurrentPage = SELECTEDVALUE ( cfg_LeaderboardPage[Page Number], 1 )
VAR MinRank = ( CurrentPage - 1 ) * PageSize + 1
VAR MaxRank = CurrentPage * PageSize
VAR CurrentRank =
    RANKX ( ALL ( SalesRep[Sales Rep Name] ), [Total Sales], , DESC, DENSE )
RETURN
    IF ( CurrentRank >= MinRank && CurrentRank <= MaxRank, CurrentRank, BLANK () )
```

Bind the visual's row filter or a rank column to this measure. Rows outside the page return blank
and drop out of a matrix with "show items with no data" off, so it reads as a real page. DENSE ties
can overfill a page. RANK with a name tie break (`window-and-visual-calculations.md`) gives exact
page sizes.

## Anti-patterns

- **Hard coded normalization bounds.** Every score silently clips once new data lands outside the
  old range.
- **A page size literal repeated across measures.** A page size change becomes three edits and three
  chances to leave one stale. Derive MinRank and MaxRank from one PageSize VAR per measure, or one
  source measure every page measure reads.
- **A 0-100 scale and a 0-1 ratio with no naming signal.** Suffix a 0-100 score `Score` and a 0-1
  ratio `Ratio`. A `Sales Score` that returns 0.82 reads as broken the first time someone puts a
  percent format on it.
