# Layout, z order, and schema versions

The grid numbers here are a default for a report with no layout of its own. When the report
already has one, match it. Where a range is given, pick one value and hold it on every page.

## Canvas

16 by 9. Match the pages the report already has. Desktop makes new pages 1920 by 1080 on the
Fluent 2 base theme (2026) and 1280 by 720 on older ones. The grid numbers below assume 1280.
A tooltip page is `320 by 240`.

`page.json` requires four keys, `$schema`, `name`, `displayName` and `displayOption`, so a page
without `$schema` is invalid. Keep the same `displayOption` (usually `FitToPage`) on every page.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "pgOverview",
  "displayName": "Overview",
  "displayOption": "FitToPage",
  "width": 1280,
  "height": 720
}
```

Allowed `displayOption` values are `FitToPage`, `FitToWidth`, `ActualSize`, `ActualSizeTopLeft`
and `DeprecatedDynamic`. `width` and `height` are optional, and Desktop omits them on a page
left at the report default.

A page file may also carry `objects` (page level formatting, such as the canvas background),
`filterConfig` (see `filters-and-sync.md`), `visualInteractions`, `pageBinding` (marks the page
as a tooltip or drillthrough target), `type`, `visibility` and `annotations`.

## Margins and gutters: pick one density per report

Both keep every value a multiple of 8. Do not mix them in one report.

- **Dense operational, 8 and 8.** Margin 8 on all sides, gutter 8. Container padding and border
  radius do the separation instead of white space. Full width is `x: 8, width: 1264`, full height
  `y: 8, height: 704`.
- **Airy executive, 24 and 16.** Margin 24, gutter 16. For four or five visuals read from across
  a room.

### The vertical bands that follow from a header strip

Content starts one gutter below a slicer strip across the top.

| Header strip height | Content `y` | Content `height` | Bottom edge |
| --- | --- | --- | --- |
| 56 | 72 | 640 | 712 |
| 64 | 80 | 632 | 712 |
| 72 | 88 | 624 | 712 |

A vertical stack of slicers down the left uses a 64 pixel pitch (56 tall plus an 8 gap), so they
sit at `y` 80, 144, 208, 272, 336.

### Content splits that recur

On a 1280 canvas with an 8 margin:

| Split | Values |
| --- | --- |
| Full width | `x: 8, width: 1264` |
| Full width after a 128 left rail | `x: 144, width: 1128` |
| Two columns, equal | `x: 8, w: 624` and `x: 648, w: 624` |
| Two columns, asymmetric | `x: 8, w: 768` and `x: 792, w: 480` |
| Three columns | `x: 8, w: 560`, `x: 576, w: 320`, `x: 904, w: 368` |
| Two rows, equal | `y: 88, h: 312` and `y: 400, h: 312` |
| Chart, thin card, chart | `y: 88, h: 296`, then `y: 392, h: 32`, then `y: 432, h: 280` |

A left rail width `w` puts content at `x = 8 + w + 8`. Rails of 88, 128, 272, 280, and 328 all
work.

### A KPI row is optional

Four cards at `y: 24, height: 120, width: 296`, spaced 312 apart. Add the row when the page has a
headline number. An operational page that answers a question needs none. Never add it as
decoration.

## Z order: match what Desktop writes

Desktop bands z in thousands, with the main content visual at `0` and chrome above it.

| Band | Holds |
| --- | --- |
| 0 | the main content visual, the point of the page |
| 1000 to 3000 | secondary content, background shapes |
| 6000 to 9000 | images and logos |
| 10000 and up | slicers and the header strip |

A hand authored page numbered 0 to 399 becomes a meaningless stack once Desktop renumbers its own
visuals in thousands.

## Tab order: band it in hundreds

`position.tabOrder` left at the default follows the order visuals were added, rarely reading
order.

| Band | Holds |
| --- | --- |
| 100 | logo or the first thing a screen reader should hit |
| 200 to 400 | header slicers, left to right |
| 500 | the main content visual |
| 600 and up | secondary content |
| 2000 and up | hidden helper visuals, so they land last |

## Parking a visual without spending canvas

`isHidden` is a top level key in `visual.json`, a sibling of `position` and `visual`, not a
property inside either.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json",
  "name": "vSprintFilterCarrier",
  "position": { "x": 8, "y": 8, "z": 2000, "height": 56, "width": 112, "tabOrder": 2000 },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "dim_sprint" } }, "Property": "Sprint" } },
              "queryRef": "dim_sprint.Sprint",
              "nativeQueryRef": "Sprint"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  },
  "isHidden": true
}
```

This holds a filter on a page without showing the control. Keep the `query`: a slicer without
one filters nothing. Use the hidden tab order band so keyboard users are not stopped on it.

## Three file kinds, three different schemas

`$schema` is required in all three and they are not interchangeable. Never copy a `visual.json`
URL into a `page.json`. Base: `https://developer.microsoft.com/json-schemas/fabric/item/report`.

| File | Path after the base | Required keys |
| --- | --- | --- |
| `pages.json` | `/definition/pagesMetadata/1.1.0/schema.json` | `$schema` |
| `page.json` | `/definition/page/2.1.0/schema.json` | `$schema`, `name`, `displayName`, `displayOption` |
| `visual.json` | `/definition/visualContainer/2.x.0/schema.json` | `$schema`, `name`, `position`, and one of `visual` or `visualGroup` |

## Detecting the version instead of hardcoding it

Use the HIGHEST `visualContainer` version in the project, not the first file you open. Desktop
bumps a file's version only when it re-saves that file, so two visuals on one page can carry
different versions.

```powershell
Get-ChildItem .\*.Report\definition -Recurse -Filter visual.json |
  Select-String -Pattern '"\$schema"\s*:\s*"([^"]+)"' |
  ForEach-Object { $_.Matches[0].Groups[1].Value } |
  Sort-Object -Unique
```

No visuals yet: add one in Desktop, save, and read the version back.

Validating against the URL: `visualContainer` 2.11.0 and 2.12.0 both returned 404 at their own
addresses, so a validator pointed at the file's URL can fail a good file. Validate against the
newest version that resolves, and treat a 404 as a publishing gap, not a bad file.
