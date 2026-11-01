"""Embeds the packaged visual in a PBIP report and adds it to a page.

Close Power BI Desktop, run `npx pbiviz package --resources --no-stats`, then for example:

  python tools/embed.py "C:\\path\\to\\pbip-folder" --page pgMyPage --table fact_hours \
      --columns Team "Service Type" Activity --hours Hours --replace vOldVisual \
      --title "Where the hours go"

Safe to run again. With --replace, the new visual takes the old visual's position and container
formatting, and the old one is removed last. Without it, pass --x --y --width --height.
"""
import argparse
import glob
import json
import os
import shutil
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUID = json.load(open(os.path.join(HERE, "pbiviz.json"), encoding="utf-8"))["visual"]["guid"]
DIST = os.path.join(HERE, "dist")
VISUAL_NAME = "vSankey"
ROLES = ("team", "service", "activity")

parser = argparse.ArgumentParser()
parser.add_argument("project")
parser.add_argument("--page", required=True)
parser.add_argument("--table", required=True)
parser.add_argument("--columns", nargs=3, required=True, help="first, middle and last column")
parser.add_argument("--hours", required=True, help="numeric column to sum")
parser.add_argument("--replace")
parser.add_argument("--title")
parser.add_argument("--subtitle")
parser.add_argument("--x", type=int, default=16)
parser.add_argument("--y", type=int, default=136)
parser.add_argument("--width", type=int, default=1256)
parser.add_argument("--height", type=int, default=576)
args = parser.parse_args()

report = glob.glob(os.path.join(args.project, "*.Report"))[0]
visuals = os.path.join(report, "definition", "pages", args.page, "visuals")
os.makedirs(os.path.join(report, "CustomVisuals"), exist_ok=True)
payload = os.path.join(report, "CustomVisuals", GUID, "resources", GUID + ".pbiviz.json")
if len(os.path.abspath(payload)) >= 260:
    raise SystemExit(f"Path is {len(os.path.abspath(payload))} characters, over the Windows limit. Use a shorter GUID.")


def write_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(doc, indent=2, ensure_ascii=False).replace("\n", "\r\n"))


def literal(text):
    return {"expr": {"Literal": {"Value": "'" + text + "'"}}}


def column(name):
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": args.table}}, "Property": name}},
        "queryRef": f"{args.table}.{name}",
        "nativeQueryRef": name,
    }


def hours():
    ref = {"Column": {"Expression": {"SourceRef": {"Entity": args.table}}, "Property": args.hours}}
    return {
        "field": {"Aggregation": {"Expression": ref, "Function": 0}},
        "queryRef": f"Sum({args.table}.{args.hours})",
        "nativeQueryRef": args.hours,
        "displayName": "Hours",
        "format": "#,0",
    }


# Payload. Byte copy only, because re-serialising the bundle corrupts it.
target = os.path.join(report, "CustomVisuals", GUID)
shutil.rmtree(target, ignore_errors=True)
os.makedirs(os.path.join(target, "resources"))
shutil.copyfile(os.path.join(DIST, "package.json"), os.path.join(target, "package.json"))
shutil.copyfile(os.path.join(DIST, "resources", GUID + ".pbiviz.json"), payload)

# Registration.
report_path = os.path.join(report, "definition", "report.json")
doc = json.load(open(report_path, encoding="utf-8"))
doc["resourcePackages"] = [p for p in doc["resourcePackages"] if p["name"] != GUID] + [{
    "name": GUID,
    "type": "CustomVisual",
    "items": [{"name": GUID + ".pbiviz.json", "path": GUID + ".pbiviz.json", "type": "CustomVisualMetadata"}],
}]
write_json(report_path, doc)

# The visual. A replaced visual donates its position, schema version and container formatting.
old_dir = os.path.join(visuals, args.replace) if args.replace else None
new_path = os.path.join(visuals, VISUAL_NAME, "visual.json")
source = None
if old_dir and os.path.isdir(old_dir):
    source = json.load(open(os.path.join(old_dir, "visual.json"), encoding="utf-8"))
elif os.path.exists(new_path):
    source = json.load(open(new_path, encoding="utf-8"))
position = source["position"] if source else {
    "x": args.x, "y": args.y, "z": 1300, "height": args.height, "width": args.width, "tabOrder": 300,
}
schema = source["$schema"] if source else json.load(open(glob.glob(os.path.join(visuals, "*", "visual.json"))[0], encoding="utf-8"))["$schema"]
objects = source["visual"].get("visualContainerObjects", {}) if source else {}

for name, value in (("title", args.title), ("subTitle", args.subtitle)):
    if value:
        objects.setdefault(name, [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}])
        objects[name][0]["properties"]["text"] = literal(value)
if args.subtitle:
    objects.setdefault("general", [{"properties": {}}])[0]["properties"]["altText"] = literal(args.subtitle)

query = {role: {"projections": [column(name)]} for role, name in zip(ROLES, args.columns)}
query["hours"] = {"projections": [hours()]}
visual = {
    "$schema": schema,
    "name": VISUAL_NAME,
    "position": position,
    "visual": {
        "visualType": GUID,
        "query": {"queryState": query},
        "visualContainerObjects": objects,
        "drillFilterOtherVisuals": True,
    },
}
os.makedirs(os.path.dirname(new_path), exist_ok=True)
write_json(new_path, visual)

# Old visual last, with retries, because OneDrive can briefly lock a folder.
if old_dir and os.path.isdir(old_dir):
    for attempt in range(6):
        try:
            shutil.rmtree(old_dir)
            break
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(5)

print("Embedded", GUID, "into", report)
