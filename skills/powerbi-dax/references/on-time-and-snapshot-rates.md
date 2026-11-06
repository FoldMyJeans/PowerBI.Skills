# On time and snapshot rates

Two rates that look simple and quietly mislead: an on time rate while some items are still inside
their window, and a fix rate between snapshots. The total level traps for any ratio are in
`ratios-and-totals.md`.

## A rate where some items are still in their window

An on time rate over items with a due date (training, tickets, tasks) has three kinds of item, not two:
done on time, late, and still inside the window. Late means done after the due date, or not done and the
due date has passed. An item still inside its window belongs on neither side. Counting it as not on time
drags the rate down early in every period, and counting only finished items hides everyone who is
overdue and has not started.

```dax
On Time % =
VAR __today = TODAY ()
VAR __onTime =
    COUNTROWS ( FILTER ( Items, Items[Done] && Items[Done Date] <= Items[Due Date] ) )
VAR __late =
    COUNTROWS (
        FILTER (
            Items,
            ( Items[Done] && Items[Done Date] > Items[Due Date] )
                || ( NOT Items[Done] && Items[Due Date] < __today )
        )
    )
RETURN DIVIDE ( __onTime, __onTime + __late )
```

Progress and lateness are two questions. "How far along are we?" is done out of all assigned. "Is
anyone behind?" is done out of done plus overdue, with items in their window left out. `Items[Done]` is a true or false column. Show them as two
cards rather than one number, and use one rule for "on time" across every page of a report.

## A rate against the previous snapshot, and its usual level

For data that arrives as snapshots (a scan, a cycle), a fix rate is items fixed since the previous
snapshot divided by the count in the previous snapshot. Its usual level is the median of the last 12
cycles, read from a tracker table with one row per cycle:

```dax
Usual Fix Rate =
MEDIANX ( TOPN ( 12, ALL ( Tracker[Cycle Date] ), Tracker[Cycle Date], DESC ), [Fix Rate] )
```

The median ignores the one cycle where a scan failed, which an average would not. Check coverage before
trusting a fix rate: count items in both snapshots, only in the previous one, and only in the current
one. A rise in "fixed" that matches a rise in "only in the previous snapshot" is items that were not
scanned, not items that were fixed. Page slicers reach a tracker with no relationship through
`TREATAS`, see `virtual-relationships.md`.
