# On time and snapshot rates

Two rates that quietly mislead. The total level traps for any ratio are in `ratios-and-totals.md`.

## A rate where some items are still in their window

An item with a due date (training, a ticket, a task) is done on time, late, or still inside its
window. Late means done after the due date, or not done and the due date has passed. An item inside
its window belongs on neither side. Counting it as not on time drags the rate down early in every
period, and counting only finished items hides everyone who is overdue and has not started.

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

`Items[Done]` is a true or false column. Progress ("how far along are we", done out of all assigned)
and lateness ("is anyone behind", done out of done plus overdue) are two questions. Show them as two
cards, and use one rule for "on time" across every page of a report.

## A rate against the previous snapshot, and its usual level

For snapshot data (a scan, a cycle), a fix rate is items fixed since the previous snapshot divided by
the count in the previous snapshot. Its usual level is the median of the last 12 cycles, from a
tracker table with one row per cycle:

```dax
Usual Fix Rate =
MEDIANX ( TOPN ( 12, ALL ( Tracker[Cycle Date] ), Tracker[Cycle Date], DESC ), [Fix Rate] )
```

- The median ignores the one cycle where a scan failed. An average would not.
- Check coverage first: count items in both snapshots, only in the previous one, and only in the
  current one. A rise in "fixed" that matches a rise in "only in the previous snapshot" is items
  that were not scanned, not items that were fixed.
- Page slicers reach a tracker with no relationship through `TREATAS` (`virtual-relationships.md`).
