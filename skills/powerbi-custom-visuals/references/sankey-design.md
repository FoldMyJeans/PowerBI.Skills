# Making a Sankey readable

A Sankey has no crossings only when it is a strict tree (each block has one parent). Three business
fields such as team, service type and activity cut across each other, so some crossing is real
information. Remove what is avoidable.

The numbers below come from one model with 27,642 hours across 5 teams, 6 service types and 5
activities. Measure your own data.

## Measure before arguing

Score a layout by crossing hours: for every pair of links that cross between two columns, add the
smaller of the two flows. A crossing of two thin flows barely shows. Also count visible crossings,
meaning both flows are at least 0.5 percent of the hours.

## Column order

Test all six orders of three fields. The answer is not obvious.

| Column order | Crossing hours | Visible crossings |
| --- | --- | --- |
| Team, Activity, Service | 8,045 | 16 |
| Team, Service, Activity | 10,224 | 11 |
| Service, Team, Activity | 13,447 | 27 |

The lowest crossing hours did not give the cleanest chart. Team, Service, Activity won on visible
crossings and also reads in the order people think, so it stayed. Reversed orders score the same.

## Block order

The biggest single win. Sorting by hours, with activities near their main service, scored 18,792
crossing hours and 20 visible crossings. The best order for the same columns scored 10,224 and 11,
46 percent fewer crossing hours.

Blocks are few, so search exhaustively, not by heuristic. Fix each order of the middle column, then
solve each outer column on its own. Precompute a penalty per pair of outer blocks once per middle
order, and pre-build the permutations once, or the search costs hundreds of milliseconds per update.

On top of that:

- **Flip to read well.** An order and its mirror score the same. Flip so the biggest middle block is
  near the top.
- **Reorder on new data only.** Never when somebody picks a team, or the chart reshuffles under
  their cursor. Block order can still shift between sprints, which is the accepted cost.

## Keep identity across the whole chart

Color each ribbon by its first column, and split the later ribbons by it too, so one team can be
followed from left to right. Use neutral grey for the bars of later columns. Stack ribbons in a
consistent order inside each block so that ribbons between the same two blocks never cross.

## Reduce what remains

- **Fade tiny flows.** In this model most crossings came from flows under 0.5 percent. Draw those at
  low opacity, but keep their hours in every total. Base the threshold on the hours in view, so a
  flow becomes solid once the viewer narrows down to it.
- **Hide zeros completely,** both the block and its label.

## Narrow on click, do not grey out

Selecting a block keeps only the hours passing through it and rescales them to fill the height. Zeros
disappear and the chart often becomes a near tree. Dimming the rest and overlaying the chosen part
still looked busy, and showed labels like "Incident 0".

## Filtering on the chart, without a slicer

The first column can be the filter. First click focuses one block, later clicks add or remove blocks,
and unpicked blocks stay as small grey stubs so they can be picked again. Choosing every block
returns to all. Keep a Show all button on the visual, because a report's Clear filters button cannot
reach state held inside it.

## Wording the share

"23% of all" made a reviewer ask what it meant. "23% of 27,642" was rejected too, because nobody cares
about that number. What worked: hours as the big number, then smaller text reading "23% of all logged
time in the selected sprints". Avoid naming a group in that sentence if a block has the same name.
