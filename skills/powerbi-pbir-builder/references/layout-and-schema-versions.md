# Layout, z order, and schema versions

Canvas sizes, the grid numbers a dense report uses, the z and tab order conventions
Power BI Desktop itself writes, and how to avoid hardcoding a schema version.

Where a range is given, pick one and hold it across every page. Consistency is what makes a
report feel like one document rather than a folder of them.

## Canvas

16 by 9, `1280 by 720` as the default. Use `1920 by 1080` only for a report meant to fill a
large screen, and `320 by 240` for a tooltip page.

Every `page.json` also carries a display option. `FitToPage` is the usual choice and it should
be the same on every page. The schema requires four keys, `$schema`, `name`, `displayName` and
`displayOption`, so a page file without `$schema` is invalid, not merely incomplete:

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

## Margins and gutters: pick a density and commit

There are two workable systems. Both keep every value a multiple of 8.

**Dense operational, 8 and 8.** Margin 8 on all four sides, gutter 8 between visuals. It fits
far more on a page than it sounds like it should, because the container padding and border
radius do the visual separation instead of white space. Full width content is `x: 8, width: 1264`. Full height content is
`y: 8, height: 704`.

**Airy executive, 24 and 16.** Margin 24, gutter 16. Better for a page with four or five
visuals that someone reads from across a room.

Do not mix them in one report.

### The vertical bands that follow from a header strip

A row of slicers across the top, then content below it, produces three repeating layouts. The
content starts exactly one gutter below the strip.

| Header strip height | Content `y` | Content `height` | Bottom edge |
| --- | --- | --- | --- |
| 56 | 72 | 640 | 712 |
| 64 | 80 | 632 | 712 |
| 72 | 88 | 624 | 712 |

A vertical stack of slicers down the left uses a 64 pixel pitch, that is 56 tall plus an 8 gap,
so they sit at `y` 80, 144, 208, 272, 336.

### Content splits that recur

On a 1280 canvas with an 8 margin, these are the divisions that land on the grid.

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

A row of four cards at `y: 24, height: 120, width: 296`, spaced 312 apart, is a good summary
page. It is not mandatory, and a report can be excellent without one. A report whose every page
answers an operational question rather than reporting a headline number may carry no KPI row at
all, and be better for it. Add the row when the page has a headline. Do not add it as
decoration.

## Z order: match what Desktop writes

Desktop bands z in thousands, and it puts the main content visual at `0` with chrome above it.
Follow the same bands and a visual you add by hand lands where Desktop would have put it.

| Band | Holds |
| --- | --- |
| 0 | the main content visual, the point of the page |
| 1000 to 3000 | secondary content, background shapes |
| 6000 to 9000 | images and logos |
| 10000 and up | slicers and the header strip |

Use this rather than inventing a scheme. A hand authored page that numbers 0 to 399 will produce
a mixed and meaningless stack the moment Desktop touches the report and renumbers its own
visuals in thousands.

## Tab order: band it in hundreds

Every visual carries `position.tabOrder`, and leaving it at the default gives the order visuals
were added, which is almost never reading order.

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

Useful for holding a filter on a page without showing the control. The field binding is the
point: a slicer with no `query` filters nothing, so a hidden one without it is an invisible box
that does nothing. Give it a tab order in the hidden band so keyboard users are not stopped on
an invisible object.

## Three file kinds, three different schemas

`$schema` is required in all three, and each kind has its own family. They are not
interchangeable, so never copy the URL out of a `visual.json` into a `page.json`.

All three share the base `https://developer.microsoft.com/json-schemas/fabric/item/report`:

| File | Path after the base | Required keys |
| --- | --- | --- |
| `pages.json` | `/definition/pagesMetadata/1.1.0/schema.json` | `$schema` |
| `page.json` | `/definition/page/2.1.0/schema.json` | `$schema`, `name`, `displayName`, `displayOption` |
| `visual.json` | `/definition/visualContainer/2.x.0/schema.json` | `$schema`, `name`, `position`, and one of `visual` or `visualGroup` |

## Detecting the version instead of hardcoding it

The `visualContainer` version changes as Desktop updates, so do not hardcode one you saw once.
Read the versions already in the project and use the HIGHEST one present, not the first one you
open. Desktop only bumps a file's version when it re-saves that file, so a real project carries
a mix, and two visuals sitting side by side on the same page can carry different versions.
Opening "one existing visual.json" gives a different answer depending on which you pick.

```powershell
Get-ChildItem .\*.Report\definition -Recurse -Filter visual.json |
  Select-String -Pattern '"\$schema"\s*:\s*"([^"]+)"' |
  ForEach-Object { $_.Matches[0].Groups[1].Value } |
  Sort-Object -Unique
```

If the project has no visuals yet, add one visual of any kind in Desktop, save, and read the
version back. That is one click and it beats guessing.

One trap if you plan to validate against the URL: not every version in production is published.
`visualContainer` 2.11.0 and 2.12.0 both return 404 at their own addresses, so a validator
pointed at the URL in the file can fail on a perfectly good file. Validate against the newest
version that does resolve, and treat a 404 as a publishing gap rather than a bad file.
