---
name: powerbi-modeling
description: >-
  Design the model layer of a Power BI dataset: star schema (fact and dimension tables), the
  grain of a fact table, relationships and cardinality, single vs both cross filter direction,
  active and inactive relationships and USERELATIONSHIP, many to many and bridge tables, a
  dedicated _Measures table, and naming and hiding conventions. Use whenever the user is
  shaping or fixing a data model, deciding fact vs dimension, setting the grain, wiring or
  debugging relationships, seeing a blank or wrong number that traces to a relationship,
  flattening a snowflake, adding a Date table, organizing measures, or asking "star schema or
  one big table". Trigger on phrases like "star schema", "fact and dimension", "set up
  relationships", "one to many", "both cross filter", "bidirectional filter", "many to many",
  "bridge table", "inactive relationship", "USERELATIONSHIP", "where do my measures go",
  "measures table", or a model that returns the wrong totals. Assumes Power BI Pro only, no
  Fabric or Premium.
---

# Power BI modeling

This skill covers the model layer: how tables relate, what shape the model should take, and
where measures and names live. The target is a star schema that VertiPaq can compress and
filter fast. It assumes Power BI Pro (no Fabric or Premium). For the hard license facts, read
`pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.

## When to use

Use this for star schema design, fact vs dimension decisions, the grain of a fact table,
relationships and cross filter direction, many to many and bridge tables, and where measures
and names should live. For M and Power Query and refresh use `powerbi-data-and-refresh`. For
DAX measure logic use `powerbi-dax`. For page layout and visuals use `powerbi-report-design`.
For the pbip and TMDL files and external tools use `powerbi-project-and-tools`.

## The mental model

1. Dimensions filter and group. Facts summarize. A report visual filters and groups by
   dimension columns, then aggregates fact columns. Build the model to serve that.
2. Define the grain of each fact table first, in one sentence, before adding a single column.
   Every row in the fact must mean the same thing at the same level of detail.
3. Relationships are the model. The "one" side is a dimension, the "many" side is a fact. Keep
   filters flowing one way, from dimension to fact, and the numbers stay predictable.

## The shape you are aiming at

This is the worked Sales example from `references/star-schema.md`, drawn. Arrows point the way
filters flow, from dimension into fact, which is also the "one" side into the "many" side.

```mermaid
flowchart TD
    D["Date (dimension)<br/>one row per day<br/>DateKey, Year, Quarter, Month<br/>marked as the date table"]
    P["Product (dimension)<br/>one row per product<br/>ProductKey, ProductName<br/>Category, Subcategory, Color"]
    C["Customer (dimension)<br/>one row per customer<br/>CustomerKey, CustomerName<br/>Segment, City, Country"]
    F["Sales (fact)<br/>grain: one row per sales order line<br/>keys: DateKey, ProductKey, CustomerKey<br/>numbers: Quantity, UnitPrice, SalesAmount, Cost"]
    M["_Measures<br/>no rows, no relationships<br/>Total Sales = SUM of SalesAmount"]

    D -->|"one to many, single direction"| F
    P -->|"one to many, single direction"| F
    C -->|"one to many, single direction"| F
    M -.->|"measures live here,<br/>not on the fact"| F
```

Three things in that picture are the whole skill. Every arrow runs one way, so no visual can
produce an ambiguous filter path. Category and Subcategory sit inside `Product` rather than
hanging off it, which is a star rather than a snowflake. And `_Measures` connects to nothing,
because it is a holder table with no rows.

## Workflow

1. List the questions the report must answer. That tells you which facts to measure and which
   dimensions to slice by.
2. Pick each fact table and write its grain in one sentence. If two facts have different
   grains, keep them in separate tables. Do not mix grains in one table.
3. Split the wide source into dimensions and facts. Facts keep the keys and the numbers.
   Dimensions carry the descriptive columns you filter and group by. See
   `references/star-schema.md`.
4. Build one to many relationships from each dimension into the fact, on clean single column
   keys. Keep cross filter direction single. See `references/relationships.md`.
5. Add one Date table, mark it as a date table, and relate it to each date key on the facts.
6. Put every measure in a dedicated `_Measures` table. Hide keys and technical columns. Give
   the rest friendly business names. See `references/naming-and-measures.md`.

## Rules of thumb

- Prefer a star over a snowflake. Flatten a snowflaked dimension into one table unless the
  volume makes that expensive. Fewer hops filter faster and read cleaner.
- Prefer a star over one big flat table too. A single wide table repeats dimension text on
  every row, compresses worse, and cannot filter two facts from a shared dimension.
- One to many is the default and the goal. If you reach for many to many, stop and add a
  bridge table instead. See `references/relationships.md`.
- Single cross filter direction is the safe default. Both directions can cause ambiguous
  filter paths, wrong totals, and slower queries. Turn it on only for a deliberate bridge, and
  know why.
- Only one active relationship is allowed between two tables. Extra date roles (order date,
  ship date) go through inactive relationships plus `USERELATIONSHIP` in a measure, or a second
  Date table. See `references/relationships.md` and `powerbi-dax`.
- Relationship columns must be clean keys. No blanks, no duplicates on the "one" side, one data
  type on both ends. A dirty key is the usual cause of a blank or doubled number.
- Never name a table exactly `Measures`. That literal name is reserved and a model with it can
  fail to open. Use `_Measures`. See `references/naming-and-measures.md`.
- Compute columns upstream in M or at the source when you can. DAX calculated columns compress
  worse and grow the model. See `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill.

## References in this skill

- `references/star-schema.md`: dimensions vs facts, defining the grain, why a star suits
  VertiPaq, star vs snowflake, why a star beats one flat table, the three fact types, and a
  worked Sales example.
- `references/relationships.md`: cardinality, single vs both cross filter direction, active vs
  inactive and USERELATIONSHIP, the many to many pitfall and bridge tables, and clean keys.
- `references/naming-and-measures.md`: the `_Measures` holder table and the reserved name trap,
  friendly names, hiding keys and foreign keys, one marked Date table, and casing.

## Shared facts

- `pro-vs-premium-facts.md` in the `powerbi-project-and-tools` skill: Pro limits, and the cost
  of calculated columns and tables.
