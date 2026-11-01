# Three level Sankey

A Power BI custom visual: hours flowing through three columns, such as team to service type to
activity. No data lives here. The design choices and their numbers are in
`references/sankey-design.md` in this skill.

What the viewer does:

- Clicks a block in the first column to focus it, and more blocks to add or remove them.
- Clicks a block in a later column to narrow the chart to the hours passing through it.
- Uses Show all to clear both.

The role names `team`, `service` and `activity` are only names. Any three grouping fields will work.

## Build and embed

The project path to the bundle must stay under 260 characters. The GUID in `pbiviz.json` is short for
that reason. For a new visual, give it a new GUID of its own. Never change a GUID once a report is
bound to it. Fill in `author` and `supportUrl` in `pbiviz.json`, because packaging requires them.

1. Close Power BI Desktop.
2. `npm install`
3. Bump the version in `pbiviz.json`, in both places. Desktop caches a bundle by GUID and version.
4. `npx eslint .`
5. `npx pbiviz package --resources --no-stats`
6. Run `tools/embed.py` as its header describes.
7. Reopen Desktop. A reload does not pick up a new bundle.

## Click test without Desktop

Copy `dist/resources/visual.js` and `dist/resources/visual.prod.css` next to `test/index.html`, serve
that folder over a local web server, and open it. The data is made up. The page exposes `t.click("Team A")`,
`t.state()`, `t.sprint()`, `t.none()` and `t.all()` for scripted checks.
