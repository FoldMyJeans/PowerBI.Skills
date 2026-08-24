# Sources

Curated, deduped, and checked against a Power BI Pro lens. Everything here is free to read.
Where a source is mostly about Fabric or Premium features, it is flagged. Verified active as
of mid 2026. Re-check yearly.

## Must-read anchors

- Understand star schema and the importance for Power BI (Microsoft): https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- The importance of star schemas in Power BI (SQLBI): https://www.sqlbi.com/articles/the-importance-of-star-schemas-in-power-bi/
- DAX Guide, function reference with a version compatibility matrix (SQLBI): https://dax.guide/
- Query folding guidance in Power BI Desktop (Microsoft): https://learn.microsoft.com/en-us/power-bi/guidance/power-query-folding
- Why does Power BI query my data source more than once (Chris Webb): https://blog.crossjoin.co.uk/2019/10/13/why-does-power-bi-query-my-data-source-more-than-once/
- Design effective reports and accessibility (Microsoft): https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tips-and-tricks-for-creating-reports and https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-overview

## Modeling and star schema

- MS Learn, model relationships: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand
- MS Learn, many to many relationship guidance: https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many
- SQLBI, star schema or single table: https://www.sqlbi.com/articles/power-bi-star-schema-or-single-table/
- Kimball Group, dimensional modeling techniques (vendor neutral theory): https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/

## DAX

- DAX Patterns, second edition, free online (SQLBI): https://www.daxpatterns.com/
- SQLBI DAX topic hub, includes calculated columns vs measures and context transition: https://www.sqlbi.com/topics/dax/
- MS Learn DAX function reference: https://learn.microsoft.com/en-us/dax/dax-function-reference

## M, Power Query, and refresh performance

- Chris Webb's blog (Crossjoin), the deepest M and refresh performance blog: https://blog.crossjoin.co.uk/
- Chris Webb, basic query folding on a web service (pattern for non folding REST): https://blog.crossjoin.co.uk/2018/11/21/query-folding-web-service-power-bi/
- MS Learn, referencing Power Query queries (referenced steps re-execute, no free cache): https://learn.microsoft.com/en-us/power-bi/guidance/power-query-referenced-queries
- MS Learn, best practices when working with Power Query: https://learn.microsoft.com/en-us/power-query/best-practices
- MS Learn, understanding query evaluation and query folding: https://learn.microsoft.com/en-us/power-query/query-folding-basics

## Licensing and limits

- MS Learn, data refresh in Power BI (the 8 per day, 1 GB, 2 hour Pro limits): https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data
- MS Learn, configure incremental refresh and real time data: https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview
- MS Learn, dataflows considerations and limitations, Gen1 legacy: https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-features-limitations
- MS Learn, differences between Dataflow Gen1 and Gen2 (Gen2 needs Fabric or Premium): https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview

## Report design and visualization

- MS Learn, create custom report themes and the theme JSON structure: https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom
- MS Learn, visualizations overview and slicers and navigators: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualizations-overview
- SQLBI, Kurt Buhler articles, atomic design and re-using visual formatting: https://www.sqlbi.com/author/kurtbuhler/
- Data Goblins (Kurt Buhler), Dashboard Checklist and how-tos: https://data-goblins.com/power-bi
- Zebra BI, dashboard design best practices, and IBCS (guidance free, Zebra visual is a paid add-in): https://zebrabi.com/power-bi-dashboard-design-mistakes/ and https://www.ibcs.com/
- Storytelling with Data (Cole Nussbaumer Knaflic): https://www.storytellingwithdata.com/
- Financial Times Visual Vocabulary, chart selection by intent: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
- Havens Consulting (Reid Havens), report and dashboard design, table and matrix craft, and
  conditional formatting. Mostly video, courses, and downloadable PBIX walk-throughs rather than
  long written posts, and some are paid, but it is a top design source: https://www.havensconsulting.net/ and the blog at https://www.havensconsulting.net/blog-and-media

## Tables, matrix, and conditional formatting

- MS Learn, create a matrix visual: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-matrix-visual
- MS Learn, matrix visual format settings (layouts, subtotals, stepped layout): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-matrix-visual-format-settings
- MS Learn, create and format table visualizations: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-tables
- MS Learn, apply conditional table formatting (background, font color, data bars, icons, web URL, field value): https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting
- MS Learn, conditional formatting in Power BI visuals: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-conditional-formatting
- MS Learn, tips and tricks for color formatting (the good, neutral, bad SWITCH example): https://learn.microsoft.com/en-us/power-bi/visuals/service-tips-and-tricks-for-color-formatting
- MS Learn, sparklines in a table or matrix (5 per visual, 52 points, 25 column limits): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-sparklines-tables
- Tabular Editor blog, make better tables and matrixes, a written guide to cutting non data ink: https://tabulareditor.com/blog/make-better-tables-and-matrixes-in-power-bi-reports-a-comprehensive-guide
- Data Bear, the newer matrix visual layouts explained: https://databear.com/new-matrix-visual-layouts-in-power-bi/
- Excelerator BI (Matt Allington), conditional formatting with icons, including referencing icons by name: https://exceleratorbi.com.au/conditional-formatting-using-icons-in-power-bi/
- Chris Webb, performance tuning table visuals, why an unfiltered table spools the whole result before it windows to the visible rows: https://blog.crossjoin.co.uk/2022/11/10/performance-tuning-table-visuals-with-filters-applied-in-power-bi/

## Native analytical and AI visuals (all Pro safe unless noted)

- MS Learn, decomposition tree, with its High and Low value AI splits: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-decomposition-tree
- MS Learn, key influencers, in-engine machine learning, not Copilot: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-influencers
- MS Learn, small multiples: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-small-multiples
- MS Learn, the new card visual (general availability November 2025, replaces Card and Multi-row card): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-new-card
- MS Learn, KPI visual (note it has no sort option, sort the data first): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-kpi
- MS Learn, Q&A visual (Pro, but retiring around December 2026, replaced by Copilot): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-q-and-a
- MS Learn, smart narrative (Custom mode is Pro, Copilot authored narrative needs Fabric): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-smart-narrative

## Color and accessibility

- Okabe-Ito colorblind safe categorical palette: https://siegal.bio.nyu.edu/color-palette/
- ColorBrewer 2.0, sequential and diverging with a colorblind safe filter: https://colorbrewer2.org/
- Viz Palette, test a palette for color vision deficiency: https://projects.susielu.com/viz-palette
- WebAIM contrast checker: https://webaim.org/resources/contrastchecker/
- TPGi Colour Contrast Analyser, desktop eyedropper for a live canvas: https://www.tpgi.com/color-contrast-checker/
- Theme generators, all free: PowerBI.tips (https://themes.powerbi.tips/), BIBB (https://bibb.pro/apps/theme-generator/)

## Free, Pro friendly external tools

- Tabular Editor 2, free and open source, model and TMDL editing plus Best Practice Analyzer: https://tabulareditor.com/
- DAX Studio, free, DAX authoring, server timings, and VertiPaq Analyzer for model size: https://daxstudio.org/
- Bravo for Power BI (SQLBI), free, model size, format DAX, generate a Date table: https://bravo.bi/
- Measure Killer, free single file tier, find and remove unused measures and columns: https://measurekiller.com/
- Note: all of these edit your LOCAL pbip or pbix. Writing to a PUBLISHED dataset needs the
  XMLA write endpoint, which is Premium, not Pro.

## PBIP and TMDL

- MS Learn, Power BI Desktop projects (pbip) overview: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
- MS Learn, semantic model folder and TMDL: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset

## Maintained GitHub repos

- microsoft/powerbi-desktop-samples, monthly sample pbix files and the official report theme
  JSON schema for validation: https://github.com/microsoft/powerbi-desktop-samples
- microsoft/Analysis-Services, the Best Practice Rules JSON used by Tabular Editor's analyzer:
  https://github.com/microsoft/Analysis-Services/tree/master/BestPracticeRules
- deldersveld/PowerBI-ThemeTemplates, per visual theme JSON snippets (validate against the
  official schema, some are dated): https://github.com/deldersveld/PowerBI-ThemeTemplates
- NajiElKotob/Awesome-Power-BI, curated link directory (includes Fabric links, filter for Pro):
  https://github.com/NajiElKotob/Awesome-Power-BI

## Claude Code plugin marketplaces for Power BI (learn from, do not copy)

Two active, third party Claude Code skill collections for Power BI surfaced during research.
Both are worth reading for ideas, neither should be copied into this repo.

- data-goblin/power-bi-agentic-development, by Kurt Buhler (Data Goblins). A full Claude Code
  plugin marketplace: TMDL and PBIR authoring, a live Power BI Desktop bridge with validation
  hooks, Tabular Editor CLI and Best Practice Analyzer rule authoring, DAX and Power Query
  skills, and a Fabric CLI plugin documented as working fully on Pro and PPU (Fabric not
  required for that one). GPL 3.0 licensed. The README says explicitly: content must not be
  copied or incorporated into your own products or tools, even by having an agent rewrite it,
  without attribution. If a plugin from here is genuinely useful, install it directly with
  `claude plugin marketplace add data-goblin/power-bi-agentic-development` scoped to the
  project that needs it, per their own guidance not to install everything globally.
  https://github.com/data-goblin/power-bi-agentic-development
- lukasreese/powerbi-claude-skills, by Lukas Reese. Smaller, two skills: a structured
  requirements gathering conversation for scoping a Power BI project, and a PBIR report
  builder that writes pages and visuals directly into a PBIP, including IBCS variance chart
  templates. No explicit license file, so treat the same way, do not copy the text. The
  requirements gathering skill ends by promoting the author's own contact details to whoever
  is in the conversation, worth knowing before installing it as is for client work.
  https://github.com/lukasreese/powerbi-claude-skills

`powerbi-pbir-builder` in this repo was written from scratch after reviewing both, grounded in
the official Microsoft PBIR JSON schema and a real working report, not copied from either.
