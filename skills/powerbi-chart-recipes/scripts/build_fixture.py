#!/usr/bin/env python3
"""Build a test PBIP that holds only fake data, so a recipe can be opened in Desktop safely.

Every table is a calculated table from assets/fixtures, so it opens with no refresh, no credentials
and no real data. Screenshots of it are safe to share. --from is any PBIP Desktop saved, read only
for its schema versions and report settings. Its pages and tables are not copied.

    python build_fixture.py --from "C:/work/ABC Sales" --out "C:/work/chart-fixture"
"""
import argparse, glob, io, json, os, re, shutil, subprocess, sys, uuid

args = argparse.ArgumentParser(description=__doc__)
args.add_argument("--from", dest="source", required=True, help="folder holding a .pbip Desktop saved")
args.add_argument("--out", required=True, help="new folder, replaced if it exists")
args = args.parse_args()
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = args.source
OUT = args.out
SRCN = os.path.splitext(os.path.basename(glob.glob(os.path.join(SRC, "*.pbip"))[0]))[0]
N = "ABC_Charts"
if os.path.exists(OUT): shutil.rmtree(OUT)
SM = os.path.join(OUT, N + '.SemanticModel'); RP = os.path.join(OUT, N + '.Report')
D = os.path.join(SM, 'definition'); T = os.path.join(D, 'tables')
os.makedirs(T); os.makedirs(os.path.join(RP, 'definition', 'pages'))
tag = lambda: str(uuid.uuid4())
def wtext(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def wjson(p, o): wtext(p, json.dumps(o, indent=2, ensure_ascii=False) + '\n')

wjson(os.path.join(OUT, N + '.pbip'), {"version": "1.0", "artifacts": [{"report": {"path": N + ".Report"}}], "settings": {"enableAutoRecovery": True}})
shutil.copy(os.path.join(SRC, SRCN + '.SemanticModel', 'definition.pbism'), SM)
wtext(os.path.join(D, 'database.tmdl'), 'database\n\tcompatibilityLevel: 1606\n')

TYPES = {str: ('string', 'STRING'), int: ('int64', 'INTEGER'), float: ('double', 'DOUBLE')}
tables = []
def calc_table(name, rows, date_cols=()):
    cols = list(rows[0].keys())
    def col_type(c):
        if c in date_cols: return ('dateTime', 'DATETIME')
        vals = [r[c] for r in rows if r[c] is not None]
        if any(isinstance(v, float) for v in vals): return TYPES[float]
        return TYPES[type(vals[0])]
    defs = ', '.join(f'"{c}", {col_type(c)[1]}' for c in cols)
    def fmt(c, v):
        if v is None: return 'BLANK()'
        if isinstance(v, str): return '"' + v.replace('"', '""') + '"'
        return str(v)
    body = ',\n'.join('\t\t\t\t{' + ', '.join(fmt(c, r[c]) for c in cols) + '}' for r in rows)
    out = f"table {name}\n\tlineageTag: {tag()}\n\n"
    for c in cols:
        out += f"\tcolumn {c}\n\t\tdataType: {col_type(c)[0]}\n\t\tisDataTypeInferred\n\t\tlineageTag: {tag()}\n\t\tsummarizeBy: none\n\t\tisNameInferred\n\t\tsourceColumn: [{c}]\n\n"
    out += f"\tpartition {name} = calculated\n\t\tmode: import\n\t\tsource = ```\n\t\t\t\tDATATABLE({defs}, {{\n{body}\n\t\t\t\t}})\n\t\t\t\t```\n\n"
    wtext(os.path.join(T, name + '.tmdl'), out)
    tables.append(name)

fx = lambda n: json.load(io.open(os.path.join(SKILL, 'assets', 'fixtures', n + '.json'), encoding='utf-8'))
calc_table('Beeswarm', fx('beeswarm'))
cal = fx('calendar-heatmap')
calc_table('CalendarDays', [{'Date': r['Date'].replace('T', ' '), 'Value': r['Value']} for r in cal], date_cols=('Date',))
calc_table('Waffle', fx('waffle'))
# Stage on purpose: the spec reads Name, so this shows an alias renames a field for Deneb.
calc_table('Funnel', [{'Stage': r['Name'], 'StageOrder': r['StageOrder'], 'Value': r['Value']} for r in fx('funnel-sankey')])
calc_table('Bump', fx('bump'))
calc_table('Butterfly', fx('butterfly'))
calc_table('Variance', fx('variance-trio'))
calc_table('FloorPlan', [{**r, 'Value': r['Value']} for r in fx('floor-plan')])
calc_table('Ridge', fx('ridgeline'))
calc_table('Clock', fx('alert-clock'))
calc_table('KpiDim', [{'Name': n, 'Target': t} for n, t in [('Patching', 90), ('MFA', 95), ('Reviews', 85), ('Training', 80)]])
series = {'Patching': [60,62,66,63,70,74,72,69,71,75,73,72], 'MFA': [80,83,85,87,88,90,91,92,92,93,94,94], 'Reviews': [78,76,72,74,70,66,64,68,62,60,63,61], 'Training': [40,44,48,47,52,50,55,53,54,57,56,58]}
calc_table('KpiFact', [{'Name': n, 'Month': i + 1, 'Value': v} for n, vs in series.items() for i, v in enumerate(vs)])
calc_table('Date', [{'Month': i} for i in range(1, 13)])
calc_table('Theme', [{'Mode': 'Light'}, {'Mode': 'Dark'}])

def dax_measures(path):
    src = io.open(os.path.join(SKILL, 'assets', 'dax', path), encoding='utf-8').read()
    src = '\n'.join(l for l in src.splitlines() if not l.startswith('//'))
    parts = re.split(r'\n(?=(?!VAR )[A-Z][A-Za-z ]+ =)', src.strip())
    for p in parts:
        name, expr = p.split(' =', 1)
        yield name.strip(), expr.strip()

ms = f"table _Measures\n\tlineageTag: {tag()}\n\n"
def measure(name, expr, extra=''):
    global ms
    body = '\n'.join('\t\t\t\t' + l for l in expr.splitlines())
    ms += f"\tmeasure '{name}' = ```\n{body}\n\t\t\t\t```\n\t\tlineageTag: {tag()}\n{extra}\n"
measure('KPI Actual', 'AVERAGE ( KpiFact[Value] )')
measure('KPI Target', 'MAX ( KpiDim[Target] )')
measure('KPI Change', '-2.1')
measure('Opened Left', '-SUM ( Butterfly[Left] )', '\t\tformatString: #,0;#,0\n')
measure('Closed Right', 'SUM ( Butterfly[Right] )', '\t\tformatString: #,0\n')
for f in ('bullet.dax', 'split-sparkline.dax', 'animated-kpi-card.dax', 'filter-drawer.dax'):
    for name, expr in dax_measures(f):
        measure(name, expr, '\t\tdataCategory: ImageUrl\n')
for name, expr in dax_measures('theme-colours.dax'):
    measure(name, expr, '\t\tdataCategory: ImageUrl\n' if name.endswith('SVG') else '')
ms += f"\tpartition _Measures = calculated\n\t\tmode: import\n\t\tsource = ```\n\t\t\t\tROW(\"x\", BLANK())\n\t\t\t\t```\n\n\tcolumn x\n\t\tdataType: string\n\t\tisDataTypeInferred\n\t\tisHidden\n\t\tlineageTag: {tag()}\n\t\tsummarizeBy: none\n\t\tisNameInferred\n\t\tsourceColumn: [x]\n\n"
wtext(os.path.join(T, '_Measures.tmdl'), ms)
tables.append('_Measures')

model = 'model Model\n\tculture: en-CA\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-CA\n\tdataAccessOptions\n\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\nannotation __PBI_TimeIntelligenceEnabled = 0\n\n'
model += ''.join(f"ref table {t if t.isidentifier() and t != 'Date' else repr(t)}\n" for t in tables)
wtext(os.path.join(D, 'model.tmdl'), model)
wtext(os.path.join(D, 'relationships.tmdl'),
      f"relationship {tag()}\n\tfromColumn: KpiFact.Name\n\ttoColumn: KpiDim.Name\n\nrelationship {tag()}\n\tfromColumn: KpiFact.Month\n\ttoColumn: 'Date'.Month\n\n")

# Report shell: real files Desktop wrote, minus every page and the custom visual.
srep = os.path.join(SRC, SRCN + '.Report')
wjson(os.path.join(RP, 'definition.pbir'), {**json.load(io.open(os.path.join(srep, 'definition.pbir'))), 'datasetReference': {'byPath': {'path': f'../{N}.SemanticModel'}}})
shutil.copytree(os.path.join(srep, 'StaticResources'), os.path.join(RP, 'StaticResources'))
shutil.copy(os.path.join(srep, 'definition', 'version.json'), os.path.join(RP, 'definition'))
rj = json.load(io.open(os.path.join(srep, 'definition', 'report.json'), encoding='utf-8'))
rj['resourcePackages'] = [p for p in rj['resourcePackages'] if p['type'] != 'CustomVisual']
rj.pop('publicCustomVisuals', None)
wjson(os.path.join(RP, 'definition', 'report.json'), rj)

def newest(pattern):
    found = {}
    for path in glob.glob(os.path.join(srep, "definition", "pages", *pattern)):
        schema = json.load(io.open(path, encoding="utf-8")).get("$schema", "")
        match = re.search(r"/(\d+)\.(\d+)\.(\d+)/schema\.json$", schema)
        if match:
            found[tuple(int(n) for n in match.groups())] = schema
    return found[max(found)]
VS = newest(("*", "visuals", "*", "visual.json"))
PS = newest(("*", "page.json"))
lit = lambda v: {'expr': {'Literal': {'Value': v}}}
msr = lambda n: {'expr': {'Measure': {'Expression': {'SourceRef': {'Entity': '_Measures'}}, 'Property': n}}}
colour = lambda n: {'solid': {'color': msr(n)}}
def col(t, c): return {'field': {'Column': {'Expression': {'SourceRef': {'Entity': t}}, 'Property': c}}, 'queryRef': f'{t}.{c}', 'nativeQueryRef': c}
def m(n): return {'field': {'Measure': {'Expression': {'SourceRef': {'Entity': '_Measures'}}, 'Property': n}}, 'queryRef': f'_Measures.{n}', 'nativeQueryRef': n}
def page(name, title, extra=None, **kw):
    wjson(os.path.join(RP, 'definition', 'pages', name, 'page.json'), {'$schema': PS, 'name': name, 'displayName': title, 'displayOption': 'FitToPage', 'height': 720, 'width': 1280, **(extra or {})})
def vis(pg, name, x, y, w, h, visual, z=1000, extra_top=None):
    wjson(os.path.join(RP, 'definition', 'pages', pg, 'visuals', name, 'visual.json'), {'$schema': VS, 'name': name, 'position': {'x': x, 'y': y, 'z': z, 'height': h, 'width': w, 'tabOrder': z}, 'visual': visual, **(extra_top or {})})

page('pgDenA', 'Deneb 1'); page('pgDenB', 'Deneb 2'); page('pgDenC', 'Deneb 3'); page('pgNative', 'Native and SVG')
# Native first, so the Deneb helper can read a schema from a real file.
vis('pgNative', 'vButterflyNative', 20, 20, 600, 320, {'visualType': 'barChart', 'query': {'queryState': {
    'Category': {'projections': [col('Butterfly', 'Name')]},
    'Y': {'projections': [m('Opened Left'), m('Closed Right')]}},
    'sortDefinition': {'sort': [{'field': col('Butterfly', 'RowOrder')['field'], 'direction': 'Ascending'}], 'isDefaultSort': False}},
    'objects': {'labels': [{'properties': {'show': lit('true')}}], 'valueAxis': [{'properties': {'show': lit('false')}}]}, 'drillFilterOtherVisuals': True})
vis('pgNative', 'vKpiTable', 640, 20, 620, 320, {'visualType': 'tableEx', 'query': {'queryState': {'Values': {'projections': [col('KpiDim', 'Name'), m('KPI Actual'), m('Bullet SVG'), m('Split Sparkline SVG')]}}},
    'objects': {'grid': [{'properties': {'imageHeight': lit('40D'), 'imageWidth': lit('160D')}}]}, 'drillFilterOtherVisuals': True})
vis('pgNative', 'vCardImage', 20, 360, 420, 150, {'visualType': 'image', 'objects': {'image': [{'properties': {'sourceType': lit("'imageUrl'"), 'sourceUrl': msr('Animated KPI Card SVG')}}]}, 'drillFilterOtherVisuals': True})
vis('pgNative', 'vCardTable', 460, 360, 420, 180, {'visualType': 'tableEx', 'query': {'queryState': {'Values': {'projections': [m('Animated KPI Card SVG')]}}},
    'objects': {'grid': [{'properties': {'imageHeight': lit('140D'), 'imageWidth': lit('400D')}}]}, 'drillFilterOtherVisuals': True})

py = sys.executable
HELP = os.path.join(SKILL, 'scripts', 'new_deneb_visual.py')
def deneb(pg, name, spec, x, y, w, h, cols=(), meas=()):
    a = [py, HELP, '--report', RP, '--page', pg, '--name', name, '--spec', os.path.join(SKILL, 'assets', 'deneb', spec), '--x', str(x), '--y', str(y), '--w', str(w), '--h', str(h)]
    for c in cols: a += ['--column', c]
    for c in meas: a += ['--measure', c]
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL)
deneb('pgDenA', 'vBeeswarm', 'beeswarm.vega.json', 20, 20, 620, 330, ['Name=Beeswarm[Name]', 'Group=Beeswarm[Group]', 'GroupOrder=Beeswarm[GroupOrder]', 'Value=Beeswarm[Value]'])
deneb('pgDenA', 'vFunnel', 'funnel-sankey.vega.json', 650, 20, 610, 330, ['Name=Funnel[Stage]', 'StageOrder=Funnel[StageOrder]', 'Value=Funnel[Value]'])
deneb('pgDenA', 'vCalendar', 'calendar-heatmap.vl.json', 20, 360, 1000, 340, ['Date=CalendarDays[Date]', 'Value=CalendarDays[Value]'])
deneb('pgDenB', 'vBump', 'bump.vl.json', 20, 20, 620, 340, ['Name=Bump[Name]', 'Period=Bump[Period]', 'PeriodOrder=Bump[PeriodOrder]', 'Value=Bump[Value]'])
deneb('pgDenB', 'vButterfly', 'butterfly.vl.json', 650, 20, 610, 340, ['Name=Butterfly[Name]', 'RowOrder=Butterfly[RowOrder]', 'Left=Butterfly[Left]', 'Right=Butterfly[Right]'])
deneb('pgDenB', 'vVariance', 'variance-trio.vl.json', 20, 370, 760, 340, ['Name=Variance[Name]', 'Actual=Variance[Actual]', 'Plan=Variance[Plan]'])
deneb('pgDenB', 'vWaffle', 'waffle.vl.json', 790, 370, 470, 340, ['Name=Waffle[Name]', 'Value=Waffle[Value]'])
deneb('pgDenC', 'vFloor', 'floor-plan.vega.json', 20, 20, 620, 340, ['Name=FloorPlan[Name]', 'Path=FloorPlan[Path]', 'LabelX=FloorPlan[LabelX]', 'LabelY=FloorPlan[LabelY]', 'Value=FloorPlan[Value]'])
deneb('pgDenC', 'vRidge', 'ridgeline.vl.json', 650, 20, 610, 340, ['Name=Ridge[Name]', 'RowOrder=Ridge[RowOrder]', 'Hour=Ridge[Hour]', 'Value=Ridge[Value]'])
deneb('pgDenC', 'vClock', 'alert-clock.vega.json', 20, 370, 400, 340, ['Day=Clock[Day]', 'DayOrder=Clock[DayOrder]', 'Hour=Clock[Hour]', 'Value=Clock[Value]'])

# Filter drawer: a hidden page with a dim layer, a panel, a slicer and a close button.
nav = lambda text, target, outline=True: {'visualType': 'actionButton', 'objects': {'icon': [{'properties': {'shapeType': lit("'blank'")}, 'selector': {'id': 'default'}}], 'text': [{'properties': {'show': lit('true')}}, {'properties': {'text': lit(f"'{text}'"), 'horizontalAlignment': lit("'center'")}, 'selector': {'id': 'default'}}], 'outline': [{'properties': {'show': lit('true' if outline else 'false')}}], 'fill': [{'properties': {'show': lit('true' if outline else 'false')}}]}, 'visualContainerObjects': {'visualLink': [{'properties': {'show': lit('true'), 'type': lit("'PageNavigation'"), 'navigationSection': lit(f"'{target}'")}}]}, 'drillFilterOtherVisuals': True}
img = lambda n: {'visualType': 'image', 'objects': {'image': [{'properties': {'sourceType': lit("'imageUrl'"), 'sourceUrl': msr(n), 'imageScalingType': lit("'Fill'")}}]}, 'drillFilterOtherVisuals': True}
page('pgFilters', 'Filters', {'visibility': 'HiddenInViewMode'})
vis('pgFilters', 'vDim', 0, 0, 900, 720, nav('', 'pgNative', False), z=100)
vis('pgFilters', 'vDimFill', 0, 0, 1280, 720, img('Drawer Dim SVG'), z=50)
vis('pgFilters', 'vPanel', 904, 16, 360, 688, img('Drawer Panel SVG'), z=200)
vis('pgFilters', 'vClose', 1212, 28, 36, 36, nav('X', 'pgNative'), z=300)
vis('pgFilters', 'vSlicerKpi', 924, 90, 320, 260, {'visualType': 'slicer', 'query': {'queryState': {'Values': {'projections': [{**col('KpiDim', 'Name'), 'active': True}]}}}, 'objects': {'data': [{'properties': {'mode': lit("'Basic'")}}]}, 'drillFilterOtherVisuals': True}, z=300)
# The way in, on the normal page.
vis('pgNative', 'vOpenFilters', 900, 360, 120, 36, nav('Filters', 'pgFilters'))

# Dark mode: page, card and text bound to measures, forced to Dark with a page filter for the test.
page('pgDark', 'Dark', {
    'filterConfig': {'filters': [{'name': 'fDark', 'field': col('Theme', 'Mode')['field'], 'type': 'Categorical', 'filter': {'Version': 2, 'From': [{'Name': 't', 'Entity': 'Theme', 'Type': 0}], 'Where': [{'Condition': {'In': {'Expressions': [{'Column': {'Expression': {'SourceRef': {'Source': 't'}}, 'Property': 'Mode'}}], 'Values': [[{'Literal': {'Value': "'Dark'"}}]]}}}]}, 'howCreated': 'User'}]}})
vis('pgDark', 'vBackdrop', 0, 0, 1280, 720, img('Page Backdrop SVG'), z=0)
vis('pgDark', 'vDarkCard', 40, 40, 300, 160, {'visualType': 'card', 'query': {'queryState': {'Values': {'projections': [m('KPI Actual')]}}}, 'objects': {'labels': [{'properties': {'color': colour('Colour Accent'), 'fontSize': lit('32D')}}], 'categoryLabels': [{'properties': {'color': colour('Colour Muted Text')}}]}, 'visualContainerObjects': {'border': [{'properties': {'show': lit('false')}}], 'background': [{'properties': {'show': lit('true'), 'color': colour('Colour Card'), 'transparency': lit('0D')}}]}, 'drillFilterOtherVisuals': True})
vis('pgDark', 'vDarkLine', 360, 40, 880, 320, {'visualType': 'lineChart', 'query': {'queryState': {'Category': {'projections': [col('Date', 'Month')]}, 'Y': {'projections': [m('KPI Actual')]}}}, 'objects': {'dataPoint': [{'properties': {'fill': colour('Colour Accent')}, 'selector': {'metadata': '_Measures.KPI Actual'}}], 'categoryAxis': [{'properties': {'labelColor': colour('Colour Muted Text')}}], 'valueAxis': [{'properties': {'labelColor': colour('Colour Muted Text'), 'gridlineColor': colour('Colour Muted Text'), 'gridlineThickness': lit('1D')}}]}, 'visualContainerObjects': {'border': [{'properties': {'show': lit('false')}}], 'title': [{'properties': {'show': lit('false')}}], 'background': [{'properties': {'show': lit('true'), 'color': colour('Colour Card'), 'transparency': lit('0D')}}]}, 'drillFilterOtherVisuals': True})

wjson(os.path.join(RP, 'definition', 'pages', 'pages.json'), {'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json', 'pageOrder': ['pgDenA', 'pgDenB', 'pgDenC', 'pgNative', 'pgFilters', 'pgDark'], 'activePageName': 'pgDenA'})
print('built', OUT)
