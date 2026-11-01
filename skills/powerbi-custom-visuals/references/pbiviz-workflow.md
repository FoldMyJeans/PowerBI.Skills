# The pbiviz workflow, from project to published report

## Three things must line up

An embedded visual needs all three, or it renders as an empty box with no error:

```
payload       <Project>.Report/CustomVisuals/<guid>/package.json
              <Project>.Report/CustomVisuals/<guid>/resources/<guid>.pbiviz.json
registration  definition/report.json, resourcePackages entry with type "CustomVisual"
reference     <page>/visuals/<id>/visual.json, visual.visualType equal to <guid>
```

`pbiviz package --resources` writes the two payload files to `dist/`. Copy them as bytes. The bundle
is one long line of JavaScript and re-serialising it corrupts it. A registered resource item resolves
under `CustomVisuals/<guid>/resources/`, not `StaticResources/`, so a validator that assumes
`StaticResources` reports a missing file that exists. Marketplace visuals are not embedded, they are
listed in `publicCustomVisuals`.

In `visual.json`, each `queryState` key must be a `dataRoles[].name` from `capabilities.json`. A
wrong key delivers no field and shows the empty state, with nothing in any log.

Embedding mechanics follow the approach in Agentic-PBIP-Template (MIT):
https://github.com/Mofaji/Agentic-PBIP-Template

## The GUID length trap

`pbiviz new` makes a GUID of the name plus 32 hex characters. The payload path holds the GUID twice.
In a project under a deep OneDrive folder this reached 284 characters, past the Windows 260 limit.

What it looks like: `FileNotFoundError` on the `.pbiviz.json` copy, for a folder that plainly exists,
right after creating it. `package.json` copied fine, because its path is shorter. Nothing mentions
path length.

The fix is a shorter GUID, name plus 8 hex characters, set before any report binds to it. That gave
236 characters. A short GUID rendered in Desktop and published to the service without trouble. Work
out the length from the real project folder before you package:

```
len(project_folder + "\<Name>.Report\CustomVisuals\" + guid + "\resources\" + guid + ".pbiviz.json")
```

Never change a GUID once a report references it. Rename with `displayName`.

## The bundle cache

Desktop caches a bundle by GUID and version. Re-embedding changed code under the same version serves
the old code, and your fix appears to do nothing. Bump the version in `pbiviz.json` on every build,
in both places, then close and reopen Desktop.

## OneDrive can lock a folder mid swap

Deleting a visual folder in a OneDrive synced project failed with `PermissionError: Access is denied`
after its file was already gone, leaving an empty folder and no visual on the page. A retry a moment
later worked. So write the new visual first and delete the old one last, with a few retries, and
compare the result against a tested copy afterwards. Take a backup of the `.Report` folder first.

## Test clicks on a plain web page

Desktop gives you a screenshot, not a way to script clicks. So load the packaged `dist/resources/visual.js`
in an ordinary page with a fake host, and drive it with JavaScript. The bundle registers a global
named after the GUID, and its `default.create({ element, host })` returns the visual.

The host needs surprisingly little: `eventService`, `colorPalette`, `tooltipService` and `locale`.
Then call `update` with a table dataView. See `test/index.html` in the Sankey asset.

Test more than the happy path. These all found or ruled out real problems:

- pick one team, add a second, remove one, pick all of them
- change the data so a picked team has no rows, as a Sprint slicer would
- send an empty table, and send no dataView at all
- a resize, with the update type carrying no data flag
- keyboard, Enter on a focused block
- time the update itself. A brute force ordering took 373 ms per update until it stopped rebuilding
  permutations for every candidate, and then took 14 ms.

Serve the page over a local web server, because a page opened from `file://` may not run in every
preview tool. A hidden preview pane can stall CSS transitions, which is what exposed the fade problem
in the `powerbi-custom-visuals` rules of thumb.

## Verify in the real report

1. Close Desktop, run the embed, and run the project's JSON and field checks.
2. Render the page in Desktop. Compare the total with a query against the model.
3. Check by hand what a script cannot reach inside Desktop: clicks, the real slicer, Clear filters.
4. Publish to My workspace and repeat. This is the only real test of the tenant setting.
5. Then publish over production. Keep the backup until people have used it.

## The Microsoft tooling

`powerbi-visuals-tools` is the CLI and has its own MCP server, started with
`npx -y powerbi-visuals-tools mcp`. It offers API lookup and feature instructions while you build.
The `npx -y` form runs whatever version is latest, so pin the version when it matters. Source:
https://github.com/microsoft/PowerBI-visuals-tools
