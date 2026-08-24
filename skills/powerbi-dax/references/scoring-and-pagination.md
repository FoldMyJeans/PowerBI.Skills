# Scoring, tiering, and ranked pagination

Two related but separate techniques. Part A turns raw metrics into a comparable 0 to 100 score
and combines several into one composite. Part B takes a rank and slices it into pages for a
leaderboard style visual. Both lean on patterns already covered in `patterns.md`,
DIVIDE and RANKX, so this file builds on those rather than repeating them.

## Part A: normalization and composite scoring

### Min-max normalize a metric to 0-100

Scale a metric between the lowest and highest value currently in view, so every metric lands on
the same 0 to 100 scale regardless of its native unit.

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

The bounds come from CALCULATE and ALLSELECTED over the current page selection, computed fresh
every time the measure runs, not typed in as literals. A hard coded `MinSales = 0` and
`MaxSales = 100000` looks fine on the day you write it and goes quietly wrong the first month a
product sells outside that range, every score above the old max clips at 100 and the report
never tells you why. Dynamic bounds cannot go stale, because there is nothing stored to go
stale.

The `SalesRange = 0` guard covers the case where every item in view has the same value, a single
selected product, or a metric that has not moved yet. Without it DIVIDE still returns blank on a
zero denominator, but blank in the middle of a composite score below is worse than a neutral 50.

### Invert the scale for lower is better

A metric like cost or a defect rate is better when it is lower, so flip the numerator before
scaling. Mark the flip with a comment, the DAX itself does not visually signal that the scale
was reversed.

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

`MaxRate - CurrentRate` in the numerator, instead of `CurrentRate - MinRate`, is the entire
inversion. Everything else is the same shape as the non inverted measure above.

### Combine normalized scores into a composite

Average the 0-100 scores with DIVIDE and a denominator counted from what is present,
not a hard coded count of how many scores you expect to have.

```dax
Product Composite Score =
VAR ScoreTable = { [Sales Score], [Defect Score], [OnTime Score] }
VAR ValidScores = FILTER ( ScoreTable, NOT ISBLANK ( [Value] ) )
VAR ScoreSum = SUMX ( ValidScores, [Value] )
VAR ScoreCount = COUNTROWS ( ValidScores )
RETURN
    DIVIDE ( ScoreSum, ScoreCount )
```

Counting the valid scores instead of writing `/ 3` means one missing input score lowers the
denominator along with the numerator, instead of dragging the composite down by silently
averaging in a zero.

### Tier classification from the composite

Rank the composite, then bucket the rank into thirds. This reuses the base RANKX pattern from
`patterns.md`, adapted to drive a label instead of a number.

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

### A lighter alternative: four quadrant sign classification

When two scores matter independently rather than blended into one composite, classify on
whether each clears its own threshold instead of ranking the blend.

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

Ship a paired color measure with a quadrant label, the same rule the measure naming taxonomy in
`powerbi-modeling` already sets for any label measure, one color per label, not repeated here.

## Part B: ranking with pagination

Start from the base RANKX form, `ALL`, `DESC`, `DENSE`, in `patterns.md`. This
section only covers windowing that rank into pages, not the rank itself.

### A disconnected page table

A small table with no relationship to the model, just page numbers and labels for a slicer.

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

Generate a real lineage tag per object in Desktop, do not copy the ones above. Every lineage tag
must be unique across the whole model, a duplicate breaks the pbip on open.

### Read the selection and gate the rank

SELECTEDVALUE with a default keeps the leaderboard on page 1 before anyone touches the slicer.
Compute the page window once as VARs, MinRank and MaxRank derived from a single PageSize
constant, and gate the rank measure through them.

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

Bind the visual's row filter or a rank column to this measure. Rows outside the current page
return blank and drop out of a matrix that has "show items with no data" turned off, which is
what makes it read as a real page instead of the whole list with some ranks blanked out.

## Anti-patterns

- **Hard coded normalization bounds.** A literal min and max looks correct until new data lands
  outside the old range, then every score silently clips.
- **A page size literal repeated across measures.** Typing `10` in three different measures
  means a page size change is three edits and three chances to leave one stale. Derive MinRank
  and MaxRank from one PageSize VAR per measure, or a single source measure every page measure
  reads.
- **Mixing a 0-100 scale and a 0-1 ratio with no naming signal.** Suffix a 0-100 score `Score`
  and a 0-1 ratio `Ratio`, every time. A measure named `Sales Score` that actually returns 0.82
  reads as broken the first time someone puts a percent format string on it.
