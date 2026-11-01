# Many to many

Many to many is not one problem. Microsoft separates three cases, and the answer differs for each.
Work out which one you have before you choose.
https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many

## Two dimensions: use a bridge

Sometimes two entities relate many to many by nature. A salesperson covers many regions, and a
region has many salespeople. A product belongs to many campaigns, and a campaign holds many
products.

Do not wire this as a direct many to many relationship. Add a bridge table (Kimball calls it a
factless fact table). It holds one row per valid pair of keys:

- `Bridge` table columns: `SalespersonKey`, `RegionKey`. One row per real assignment.
- One to many from `Salesperson` into `Bridge`, and one to many from `Region` into `Bridge`.

The bridge turns one awkward many to many into two clean one to many relationships. To make a
filter cross the bridge from one dimension to the other you may need bidirectional filtering on
one leg, or a measure using `CROSSFILTER`. Turn that on deliberately and test the totals.

Why the bridge beats a direct many to many relationship:
- You control exactly where filters cross, one leg at a time.
- Totals are easier to keep correct. Direct many to many relationships are prone to overcounting
  and surprising blank handling.
- The model stays a set of one to many relationships, which is easier to read and maintain.

Hide the bridge and the "many" side keys. If a key stays visible, keep it on the "one" side, which
filters faster. Totals across a bridge are not additive by nature: two people who share one account
each show its balance, and the total shows it once. Someone will report that as a bug, so say it on
the page.

## Two facts: add shared dimensions

Do not relate two facts directly with many to many cardinality. Visuals could then only group by the
key on the filtering fact, and integrity faults get hidden. Build shared dimensions with a one to
many relationship into each fact. When no shared dimension can be built, a virtual relationship in
a measure is the other route, see the `powerbi-dax` skill.

## A fact at a higher grain: guard the measure

Targets are the usual case, set by category and year while the dimensions go down to product and
day. Neither side is unique, so there is no one to many on category.

- For the date side, store the first day of the period in the fact and use a one to many relationship
  from the Date table.
- For anything else, use a many to many cardinality relationship, single direction, from the
  dimension to the fact.
- Either way, hide the fact's summable columns and write a measure that returns blank below the
  fact's grain. Otherwise a day level visual repeats a whole month, or a filter on a low level column
  shows the target of every category that low level touches. Test every column below the grain.

```dax
Target Hours =
IF (
    NOT ISFILTERED ( dim_product[Product Name] )
        && NOT ISFILTERED ( dim_product[Color] ),
    SUM ( fact_target[Hours] )
)
```

## Limited relationships

A many to many cardinality relationship is always limited, even when both columns happen to hold
unique values. The model view marks it with parentheses after the cardinality. That changes how it
behaves:

- It joins as INNER and adds no blank row. A fact row with no match drops out silently, where a
  regular one to many would show it under a blank member.
- `RELATED` cannot read across it, and row level security has topology limits.
- It is the slowest choice. Microsoft's order, fastest first, is one to many, then a bridge with a
  bidirectional leg, then many to many cardinality.

Source: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand
