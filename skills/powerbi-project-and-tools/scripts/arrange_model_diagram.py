"""Arrange a PBIP model diagram: facts down the left, dimensions across the top.

Usage:  python arrange_model_diagram.py "<path>\\<name>.SemanticModel" [--dry-run]

Only box positions in diagramLayout.json change. Sizes, tables and relationships are untouched.
Close Power BI Desktop first, it overwrites the file from memory on save.
"""
import json
import re
import sys
from pathlib import Path

GAP = 50        # between neighbouring boxes
CHANNEL = 120   # free lane between the fact column and the dimension row, where the lines run


def table_of(ref):
    """Table name out of a TMDL column reference: fact_x.Col or 'My Table'.'My Col'."""
    ref = ref.strip()
    if ref.startswith("'"):
        m = re.match(r"'((?:[^']|'')*)'", ref)
        return m.group(1).replace("''", "'")
    return ref.split(".", 1)[0]


def read_relationships(model_dir):
    """Per table: how many relationships touch it, and whether it sits on a one side."""
    path = model_dir / "definition" / "relationships.tmdl"
    count, one_side = {}, set()
    if not path.exists():
        return count, one_side
    for block in re.split(r"(?m)^relationship ", path.read_text(encoding="utf-8-sig"))[1:]:
        props = dict(re.findall(r"(?m)^\t(\w+): (.+?)\s*$", block))
        src, dst = table_of(props["fromColumn"]), table_of(props["toColumn"])
        for t in (src, dst):
            count[t] = count.get(t, 0) + 1
        if props.get("fromCardinality") == "one":
            one_side.add(src)
        if props.get("toCardinality", "one") == "one":
            one_side.add(dst)
    return count, one_side


def missing_nodes(model_dir, drawn):
    """Nodes for tables the diagram does not hold yet, which is the normal state of a model built by code.

    Left alone, Desktop drops them wherever it finds room on the next open. Auto date/time tables
    are skipped, Desktop never draws those.
    """
    nodes = []
    for path in sorted((model_dir / "definition" / "tables").glob("*.tmdl")):
        text = path.read_text(encoding="utf-8-sig")
        head = re.match(r"(?:///.*\n)*table (.+?)\s*\n", text)
        name = head.group(1)
        name = name[1:-1].replace("''", "'") if name.startswith("'") else name
        if name in drawn or re.search(r"(?m)^\t(showAsVariationsOnly|isPrivate)\s*$", text):
            continue
        fields = len(re.findall(r"(?m)^\t(?:column|measure) ", text))
        node = {"location": {}, "nodeIndex": name}
        tag = re.search(r"(?m)^\tlineageTag: (\S+)", text)
        if tag:
            node["nodeLineageTag"] = tag.group(1)
        node["size"] = {"height": min(300, 80 + 24 * fields), "width": 234}   # Desktop's own default box
        node["zIndex"] = 0
        nodes.append(node)
    return nodes


def classify(name, count, one_side):
    if re.match(r"(?i)fact[_ ]", name):
        return "fact"
    if re.match(r"(?i)(dim|dimension)[_ ]", name):
        return "dim"
    if name not in count:
        return "other"   # measures table, field parameters, config tables
    return "dim" if name in one_side else "fact"


def arrange(nodes, count, one_side):
    groups = {"fact": [], "dim": [], "other": []}
    for n in nodes:
        groups[classify(n["nodeIndex"], count, one_side)].append(n)
    for g in groups.values():   # busiest tables sit closest to the corner, so their lines are shortest
        g.sort(key=lambda n: (-count.get(n["nodeIndex"], 0), n["nodeIndex"].lower()))

    fact_w = max((n["size"]["width"] for n in groups["fact"]), default=0)
    left = fact_w + CHANNEL if groups["fact"] else 0

    y = 0
    for row in (groups["other"], groups["dim"]):
        x = left
        for n in row:
            n["location"] = {"x": x, "y": y}
            x += n["size"]["width"] + GAP
        if row:
            y += max(n["size"]["height"] for n in row) + (CHANNEL if row is groups["dim"] else GAP)
    for n in groups["fact"]:
        n["location"] = {"x": 0, "y": y}
        y += n["size"]["height"] + GAP
    return groups


def overlaps(nodes):
    box = lambda n: (n["location"]["x"], n["location"]["y"],
                     n["location"]["x"] + n["size"]["width"], n["location"]["y"] + n["size"]["height"])
    hits = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            ax0, ay0, ax1, ay1 = box(a)
            bx0, by0, bx1, by1 = box(b)
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                hits.append((a["nodeIndex"], b["nodeIndex"]))
    return hits


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    model_dir = Path(args[0])
    path = model_dir / "diagramLayout.json"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    layout = json.loads(text)
    count, one_side = read_relationships(model_dir)

    for diagram in layout["diagrams"]:
        nodes = diagram["nodes"]
        before = [(n["nodeIndex"], json.dumps(n["size"])) for n in nodes]
        added = []
        if diagram is layout["diagrams"][0]:   # the All tables diagram, other layouts are chosen subsets
            added = missing_nodes(model_dir, {n["nodeIndex"] for n in nodes})
            nodes.extend(added)
        groups = arrange(nodes, count, one_side)
        diagram["scrollPosition"] = {"x": 0, "y": 0}

        kept = [(n["nodeIndex"], json.dumps(n["size"])) for n in nodes[:len(before)]]
        assert kept == before, "an existing node or size changed"
        assert not overlaps(nodes), f"boxes overlap: {overlaps(nodes)}"
        print(f'{model_dir.name} / {diagram.get("name")}')
        for kind in ("fact", "dim", "other"):
            print(f"  {kind:5} {[n['nodeIndex'] for n in groups[kind]]}")
        if added:
            print(f"  added  {[n['nodeIndex'] for n in added]}")

    out = json.dumps(layout, indent=2, ensure_ascii=False)
    if "\r\n" in text:
        out = out.replace("\n", "\r\n")
    if text.endswith("\n"):
        out += "\r\n" if "\r\n" in text else "\n"
    data = (b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8")
    json.loads(data.decode("utf-8-sig"))
    if dry:
        print("  dry run, nothing written")
        return
    path.write_bytes(data)
    print(f"  written {path}")


if __name__ == "__main__":
    main()
