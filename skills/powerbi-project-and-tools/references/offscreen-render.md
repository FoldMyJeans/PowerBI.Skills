# Rendering and refreshing without the person's screen

The Desktop Bridge in `agent-verification.md` is the supported way to reload and screenshot. When it is
not available, or when the person is working in Desktop on the same machine, an agent can still render
pages, refresh the local model and save, without a window ever appearing on their monitors. This file
is that route. The fake data rule in `agent-verification.md` applies to every screenshot taken here.

## Never take over the person's monitors

Never maximize Desktop and never bring it to the front. A render that grabs the screen for two minutes
while someone types is the fastest way to lose permission to render at all.

## Render a page off screen

1. Copy the project to a temp folder. Never render the person's own copy.
2. In the copy's `pages.json`, set `activePageName` to the page you want.
3. Start Desktop on the copy's `.pbip`. The Store build is
   `%LOCALAPPDATA%\Microsoft\WindowsApps\PBIDesktopStore.exe`.
4. Every 250 ms, move every visible top level window of that process to x = -12000 at 1920 x 1080.
   Repeat it the whole time Desktop loads, because Desktop moves and resizes its windows as it starts.
   If a window is maximized, restore it first with `ShowWindow(h, 4)`, which does not activate it.
5. After 80 to 130 seconds, invoke the "Fit to page" button through UI Automation (find it by Name,
   then `InvokePattern`), wait a moment, then capture with `PrintWindow(hwnd, hdc, 2)`. Flag 2 is
   `PW_RENDERFULLCONTENT`, which captures a window that is off screen.

The park call, from a working script:

```csharp
// flags 0x0010 | 0x0004 | 0x0200 = SWP_NOACTIVATE | SWP_NOZORDER | SWP_NOOWNERZORDER
if (IsZoomed(h)) ShowWindow(h, 4);
RECT r; GetWindowRect(h, out r);
if (r.L > -11000) SetWindowPos(h, IntPtr.Zero, -12000, 0, 1920, 1080, 0x0010 | 0x0004 | 0x0200);
```

Loaded from PowerShell with `Add-Type`, inside an `EnumWindows` loop that matches the process id and
`IsWindowVisible`.

Signs a shot is not trustworthy:

- The window title is still "Untitled - Power BI Desktop". The model has not loaded. This happened when
  other Desktop instances were starting at the same time. Raise the wait, do not use the shot.
- A blank window. Enumerate every visible top level window of the process and capture each one. That is
  how a hidden "Potential security risk" dialog and a "Something went wrong" dialog were found behind a
  blank render. The engine still answers DAX while a dialog is up, so measures can be dumped by query.
- The script exits with code 1. Often that is only the cleanup of locked temp files, with every shot
  saved. Check the output folder before treating it as a failure.

## Open a slicer or tick an item for a picture

- Mouse messages sent with `PostMessage` to `Chrome_RenderWidgetHostHWND` only select the visual in
  edit mode. They do not open it.
- UI Automation works. Find the slicer's Group by its alt text, Invoke it, then within its bounding
  rectangle call `ExpandCollapsePattern.Expand()`. On a list slicer the target is the Button named
  `All`. On a classic slicer it is the ComboBox named after the field.
- To tick an item, find it by exact name and call `TogglePattern.Toggle()`.
  `SelectionItemPattern.Select()` selects the visual, not the item, so slicer sync cannot be click
  tested that way.

Small misalignments do not show to the eye. A 5 px offset between two slicers on one row was found by
scanning one pixel column per slicer in the render, converting to page units with the canvas scale, and
comparing box top and bottom against each visual's `y`.

## Refresh and save with no clicks

Desktop runs its own Analysis Services engine, `msmdsrv.exe`, as a child process.

1. Find the `msmdsrv` whose parent is the Desktop process you started. Picking the newest `msmdsrv`
   is wrong when another session starts Desktop at the same time. One check failed with "Cannot find
   table" because it reached another model.
2. Read its loopback port with `Get-NetTCPConnection -State Listen -OwningProcess <pid>`, connect over
   ADOMD.NET to `localhost:<port>`, and read the catalog name.
3. Send TMSL:

```json
{"refresh": {"type": "full", "objects": [{"database": "<catalog>"}]}}
```

Add `"table": "<name>"` to an object to refresh one table. `"type": "calculate"` recomputes calculated
tables and columns without calling any source, which is the cheap way to test a new calculated column.

4. Save by invoking the Desktop button whose Name starts with "Save" and is not "Save as", through UI
   Automation. Wait for `.pbi\cache.abf` to get a newer timestamp. The project now holds fresh data, so
   later renders show real numbers.

The same connection runs DAX, so the numbers check in `agent-verification.md` can run here too.

## Closing the person's Desktop before an edit

Close it with `CloseMainWindow`, not by killing the process, then wait up to 30 seconds. A process
still open after that is almost always an unsaved changes prompt. Ask the person about it. Then compare
the project with your backup by content before copying anything in, so nothing they changed since is
overwritten.

## Small scripting traps

- `pwsh -File script.ps1 -Only a,b,c` passes one string, not an array. Take one comma separated
  string and split it in the script.
- In PowerShell, a pipeline that returns one item returns that item, not a list. Wrap it in `@()`.
- Python `glob` on Windows returns backslash paths. Split with `os.path.normpath(p).split(os.sep)`.
