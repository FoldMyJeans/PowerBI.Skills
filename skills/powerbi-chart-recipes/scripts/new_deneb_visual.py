#!/usr/bin/env python3
"""Write a Deneb visual into a PBIR page and register Deneb in report.json.

Close Power BI Desktop first. The provider is read from the spec's file name, so name a Vega-Lite
spec *.vl.json and a Vega spec *.vega.json.

    python new_deneb_visual.py --report "ABC.Report" --page pgOps --name vWaffle \
        --spec assets/deneb/waffle.vl.json \
        --column Name=dim_control[Control] --measure Value=_Measures[Coverage %] \
        --x 40 --y 80 --w 600 --h 300
"""
import argparse
import glob
import io
import json
import os
import re
import sys

DENEB_GUID = "deneb7E15AEF80B9E4D4F8E12924291ECE89A"
# The versions bundled with Deneb 2.0.1. Read them again after a Deneb update.
ENGINE_VERSION = {"vegaLite": "6.4.3", "vega": "6.4.0"}
FIELD = re.compile(r"^(?P<alias>[^=]+)=(?P<table>.+)\[(?P<name>[^\]]+)\]$")


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def literal(value):
    return {"expr": {"Literal": {"Value": value}}}


def text(value):
    return literal("'" + value.replace("'", "''") + "'")


def projection(raw, kind):
    match = FIELD.match(raw)
    if not match:
        sys.exit(f"Bad field '{raw}'. Use Alias=Table[Name].")
    alias, table, name = match.group("alias"), match.group("table"), match.group("name")
    return {
        "field": {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
        "queryRef": f"{table}.{name}",
        "nativeQueryRef": alias,
        "displayName": alias,
    }


def newest_visual_schema(report):
    """Take the visual schema from a file Desktop wrote, never a hardcoded one."""
    found = {}
    for path in glob.glob(os.path.join(report, "definition", "pages", "*", "visuals", "*", "visual.json")):
        schema = read_json(path).get("$schema", "")
        match = re.search(r"/(\d+)\.(\d+)\.(\d+)/schema\.json$", schema)
        if match:
            found[tuple(int(n) for n in match.groups())] = schema
    if not found:
        sys.exit("No visual.json to read a schema from. Add any visual in Desktop first.")
    return found[max(found)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="the .Report folder")
    parser.add_argument("--page", required=True, help="page folder name")
    parser.add_argument("--name", required=True, help="visual folder name")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--column", action="append", default=[], help="Alias=Table[Column]")
    parser.add_argument("--measure", action="append", default=[], help="Alias=Table[Measure]")
    for axis in ("x", "y", "w", "h"):
        parser.add_argument(f"--{axis}", type=int, required=True)
    args = parser.parse_args()

    if args.spec.endswith(".vl.json"):
        provider = "vegaLite"
    elif args.spec.endswith(".vega.json"):
        provider = "vega"
    else:
        sys.exit("Name the spec *.vl.json or *.vega.json.")
    with io.open(args.spec, encoding="utf-8") as f:
        spec = f.read()

    page = os.path.join(args.report, "definition", "pages", args.page)
    if not os.path.isfile(os.path.join(page, "page.json")):
        sys.exit(f"No page at {page}")

    projections = [projection(c, "Column") for c in args.column] + [projection(m, "Measure") for m in args.measure]
    visual = {
        "$schema": newest_visual_schema(args.report),
        "name": args.name,
        "position": {"x": args.x, "y": args.y, "z": 1000, "height": args.h, "width": args.w, "tabOrder": 1000},
        "visual": {
            "visualType": DENEB_GUID,
            "query": {"queryState": {"dataset": {"projections": projections}}},
            "objects": {
                "vega": [{"properties": {
                    "provider": text(provider),
                    "version": text(ENGINE_VERSION[provider]),
                    "jsonSpec": text(spec),
                    "jsonConfig": text("{}"),
                    "enableTooltips": literal("true"),
                    "enableContextMenu": literal("true"),
                    "enableHighlight": literal("false"),
                    "enableSelection": literal("false"),
                }}],
            },
            "drillFilterOtherVisuals": True,
        },
    }
    write_json(os.path.join(page, "visuals", args.name, "visual.json"), visual)

    report_path = os.path.join(args.report, "definition", "report.json")
    report = read_json(report_path)
    public = report.setdefault("publicCustomVisuals", [])
    if DENEB_GUID not in public:
        public.append(DENEB_GUID)
        write_json(report_path, report)
    print(f"Wrote {args.name} with {len(projections)} fields. Reopen the PBIP in Desktop to check it.")


if __name__ == "__main__":
    main()
