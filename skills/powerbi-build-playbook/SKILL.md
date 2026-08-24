---
name: powerbi-build-playbook
description: >-
  Plan and run a whole Power BI build end to end, and route to the right skill at each phase.
  Covers the phase order (questions, sources, day one defaults, star schema, measures, theme,
  pages, hardening), the manual Power BI Desktop steps only a person can do, and creating the
  pbip project that every other skill assumes already exists. Use whenever the user is starting
  a new report or dataset, asks what to build first or in what order, asks what they need to
  click in Desktop, wants a new pbip or PBIP project set up, or asks which of the Power BI
  skills applies to their question. Trigger on "build a new power bi report", "start a new
  dashboard", "where do I start", "what order should I do this in", "create a pbip", "set up
  the project", "which skill should I use", "plan this power bi build", "new semantic model".
  Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI build playbook

The order to build a Power BI model and report in, and which skill owns each phase. Use this
when starting something new, or when you are not sure which skill answers a question.

The order matters more than it looks. Several decisions are cheap before the first table loads
and expensive afterwards, and two of them are one way doors.

## Which skill answers this

| The question | Skill |
| --- | --- |
| How do I get the data in, why is refresh slow | `powerbi-data-and-refresh` |
| What shape should the tables be, how do they relate | `powerbi-modeling` |
| Write or fix a measure | `powerbi-dax` |
| What should the page look like, which chart, what colors | `powerbi-report-design` |
| Write pages and visuals as JSON instead of clicking | `powerbi-pbir-builder` |
| Edit the model files, external tools, what needs Premium | `powerbi-project-and-tools` |
| Document a finished model into a shareable repo | `powerbi-doc-repo` |

## The phase order

```mermaid
flowchart TD
    p1["1. Write the questions down"] --> p2["2. Inventory the sources"]
    p2 --> p3["3. Create the pbip,<br/>set the day one defaults"]
    p3 --> p4["4. Build the data layer"]
    p4 --> p5["5. Shape the model"]
    p5 --> p6["6. Write the measures"]
    p6 --> p7["7. Apply the theme,<br/>then lay out the pages"]
    p7 --> p8["8. Harden before you ship"]
    p8 --> p9["9. Document it"]

    door["One way doors<br/>reversing either of these later<br/>is a breaking change"]
    p3 -.->|"auto date/time"| door
    p5 -.->|"fact grain"| door
```

### 1. Write down the questions first

List the questions the report must answer, in the business's words. That list decides the facts,
the dimensions, and the pages. Everything after this is downstream of it, and skipping it is why
reports end up as a wall of numbers nobody reads.

One question per page is the target. See `powerbi-report-design`.

### 2. Inventory the sources

For each source, note what it is, how it connects, and roughly how much data. Decide what can be
filtered at the source, because on a non folding source that is the only filtering that saves
time. See `powerbi-data-and-refresh`.

### 3. Create the pbip, then set the day one defaults

This is the phase every other skill assumes has already happened, and it needs a person in
Desktop. See `references/new-model-setup.md` for the exact clicks.

Turn auto date/time off BEFORE the first table loads. Left on, Power BI builds a hidden date
table for every date column in every import table and rebuilds them all on every refresh.
Turning it off later is a breaking change that strips date hierarchies out of live visuals. This
is the highest value 5 seconds in the whole build.

### 4. Build the data layer

Staging queries load disabled, filters and column selection at the source, paging with a stable
order key. Count the fan out as you go rather than after. See `powerbi-data-and-refresh`.

### 5. Shape the model

Grain of each fact in one sentence, dimensions split out, one to many relationships on clean
keys, single cross filter direction, one date or period dimension, everything named and hidden
properly. See `powerbi-modeling`.

Do this before writing measures. A measure written against a bad model encodes the bad model.

### 6. Write the measures

Base measures first, then build on them. Every measure into `_Measures` with a display folder, a
description, and a format string. Check every ratio at the total, not just on a row. See
`powerbi-dax`.

### 7. Apply the theme, then lay out the pages

Theme first, so every visual you add inherits the look instead of being styled by hand. Then
layout, chart choice, slicers, and navigation. See `powerbi-report-design`.

If you are generating pages or many similar visuals, bring the design decision to
`powerbi-pbir-builder` and write the JSON. Desktop must be closed while you do.

### 8. Harden before you ship

Accessibility pass with the verification greps, refresh timing in the Service and not just
Desktop, Best Practice Analyzer, and remove what is unused. See `powerbi-report-design`,
`powerbi-data-and-refresh`, and `powerbi-project-and-tools`.

### 9. Document it

Once it is real and stable. See `powerbi-doc-repo`.

## The one way doors

Two decisions are painful to reverse. Make them deliberately in phase 3.

1. Auto date/time. Free to turn off on an empty file. Turning it off later breaks every visual
   using a built in date hierarchy and every measure using the `Table[Date].[Year]` syntax.
2. The grain of a fact table. Changing it later means rewriting the measures and usually the
   pages too. Write the grain in one sentence and get agreement on it before building.

## Rules of thumb

- Do not start in the report. A page built before the model is a page you rebuild.
- Get one page working end to end before building ten. The first page finds the modeling
  mistakes.
- Close Power BI Desktop before any file edit, and reopen to verify. This applies to TMDL and to
  PBIR JSON equally.
- Commit early and branch per change. The pbip format is text, so use it.
- Validate numbers against the source before styling anything. A beautiful wrong report is worse
  than an ugly right one.
- When the user asks for something the model cannot answer yet, say so and name the phase it
  belongs to, rather than forcing it at the report layer.

## References in this skill

- `references/new-model-setup.md`: the manual Power BI Desktop steps to create a pbip and set the
  day one defaults, written as exact clicks, plus the folder layout you should end up with.
