---
name: powerbi-custom-visuals
description: >-
  Build a private Power BI custom visual with the pbiviz toolchain and embed it in a PBIP report,
  and decide whether a custom visual is the right answer at all. Use whenever the user wants a
  custom visual, a pbiviz, a Sankey or flow chart, a chart Power BI does not have, animation between
  states, click to open or expand behaviour, a visual written in TypeScript or D3, or asks why an
  embedded visual is blank, why a code change has no effect in Desktop, or whether SDK visuals work
  on Pro. Trigger on "custom visual", "pbiviz", "powerbi-visuals-tools", "IVisual", "capabilities.json",
  "Sankey", "animated chart", "embed the visual in the pbip", "developer visual", "Deneb or custom
  visual". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI custom visuals

Build a visual as a TypeScript project, package it, and embed it in a PBIP so the report opens
complete with nothing to import. A custom visual is code somebody has to maintain, so choose it
deliberately.

## When to use

Use this when the design needs something native visuals cannot do: a chart type Power BI lacks,
or animation between two states. For choosing a chart at all use `powerbi-report-design`. For an
SVG drawn by a measure use `powerbi-dax`. For hand editing PBIR around the visual use
`powerbi-pbir-builder`.

## Pick the lightest thing that works

| Need | Use | The limit you accept |
| --- | --- | --- |
| Inline bars, bullets or icons in a table or card | SVG from a DAX measure | Animation replays from a fixed start on every redraw. It cannot glide from the last state. |
| A chart type native lacks, static is fine | Deneb (Vega). See `powerbi-chart-recipes` for ready specs. | No built in animation between states. The data often needs reshaping first. |
| Common chart type from the marketplace | AppSource visual | Less control of the look, and a licence that can change. |
| Click to open, glide between states, full control | Private `pbiviz` | Code to maintain, an admin setting, and the export gap below. |

## What you sign up for

- **Admin setting.** Tenant setting "Allow visuals created using the Power BI SDK" can block it. A
  test publish to My workspace shows this without touching production.
- **Export gap.** A privately built visual is not certified, so it does not appear in PowerPoint
  exports or subscription emails. Suit it to pages people click through.
- **It lives in an iframe.** A visual draws only inside its own box. Other visuals react through
  Power BI selection, after a query, so there is no shared animation across visuals.
- **State the host does not own.** Choices held inside the visual are not cleared by a report's
  Clear filters button. Put a reset control on the visual itself.

## Workflow

1. Check the tenant setting first if production depends on the answer.
2. Scaffold with `npx -y powerbi-visuals-tools@7.2.1 new <name>`, or copy `assets/sankey-three-level`.
3. Shorten the GUID now, before any report binds to it. See `references/pbiviz-workflow.md`, because
   the default length can break a deep OneDrive path and it can never change later.
4. Write `capabilities.json` and `src/visual.ts`. Add `npx eslint .` to every build, because the
   visuals lint plugin rejects `innerHTML`.
5. Click test it on a plain web page with a fake host before opening Desktop. It takes seconds and
   finds real bugs. See `references/pbiviz-workflow.md`.
6. Package with `npx pbiviz package --resources --no-stats`, then embed. Desktop must be closed.
7. Render the page in Desktop and read the reconciliation number against the model. A successful
   build proves nothing about the report.
8. Test publish to My workspace, then replace production.

## Rules of thumb

- **Keep elements alive between updates.** Animation comes from moving the same SVG elements to new
  positions. Clearing the SVG on `update()` leaves nothing to animate from.
- **Tween with `requestAnimationFrame`, not CSS,** for path geometry. CSS transitions on `d` are not
  dependable across hosts. Keep CSS transitions for opacity only.
- **Do not hide things with a fade.** A label faded with a CSS transition stayed painted when the
  page was in a hidden pane, so zero labels stacked on top of each other in a screenshot. Set
  `display: none`.
- **Read columns by role, never by position.**
- **Skip expensive work on resize.** Read `options.type` and only re-parse when data changed.
- **Ask the palette for colors biggest entity first.** `colorPalette.getColor` hands out colors on
  first request, so asking in row order gave the biggest team a pale tint and made colors depend on
  sort order.
- **Call `renderingStarted` and `renderingFinished`,** including when a new update cancels a running
  animation, or exports capture a half drawn visual.
- **`privileges: []`** unless the visual truly needs the network. Then it cannot phone home at all.

## Pro vs Premium

Building, importing and publishing a private visual all work on Pro. Certification is a separate
process through AppSource and is not needed for internal use. See `powerbi-project-and-tools` for
the licensing facts.

## References in this skill

- `references/pbiviz-workflow.md`: embedding, the GUID length trap, the bundle cache, OneDrive locks,
  the click test page, and verification.
- `references/sankey-design.md`: how to make a Sankey readable, from crossing reduction to narrowing
  on click, with the numbers behind each choice.

## Assets

- `assets/sankey-three-level`: a working three column Sankey with team picking and narrowing, ready
  to bind to any three grouping fields and one measure. Read its `README.md` to build and embed it.
