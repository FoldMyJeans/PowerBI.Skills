"use strict";

import powerbi from "powerbi-visuals-api";
import "./../style/visual.less";

import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;
import IVisual = powerbi.extensibility.visual.IVisual;
import IVisualHost = powerbi.extensibility.visual.IVisualHost;
import IVisualEventService = powerbi.extensibility.IVisualEventService;
import DataViewTable = powerbi.DataViewTable;

const SVG_NS = "http://www.w3.org/2000/svg";
const NODE_WIDTH = 12;
const NODE_GAP = 16;
const OFF_TEAM_HEIGHT = 7;
const COLUMN_HEAD = 24;
const TWEEN_MS = 480;
const CHAR_WIDTH = 6.6;
const HEAD_AND_HINT = 68;
const BLANK = "(Blank)";
const UNUSED = Number.MAX_SAFE_INTEGER;
const TINY_SHARE = 0.005;
const MAX_EXACT_ORDER = 7;
const HINT = "Select a team to focus it, then others to add them. Select a service or activity to narrow to it.";

const INK = "#242424";
const MUTED_INK = "#707070";
const NEUTRAL_BAR = "#616161";
const OFF_BAR = "#B0B0B0";

type Stage = 0 | 1 | 2;

interface Row {
    team: string;
    service: string;
    activity: string;
    hours: number;
}

interface NodeView {
    stage: Stage;
    name: string;
    group: SVGGElement;
    hit: SVGRectElement;
    bar: SVGRectElement;
    label: SVGTextElement;
    value: SVGTSpanElement;
    cur: { y: number; h: number };
    tgt: { y: number; h: number };
    from: { y: number; h: number };
    hours: number;
    off: boolean;
    stackOut: number;
    stackIn: number;
    order: number;
}

interface LinkView {
    key: string;
    stage: 0 | 1;
    source: string;
    target: string;
    team: string;
    base: SVGPathElement;
    rows: Row[];
    hours: number;
    cur: { y0: number; y1: number; w: number };
    tgt: { y0: number; y1: number; w: number };
    from: { y0: number; y1: number; w: number };
}

function stageName(row: Row, stage: Stage): string {
    return stage === 0 ? row.team : stage === 1 ? row.service : row.activity;
}

function sumHours(rows: Row[]): number {
    return rows.reduce((total, row) => total + row.hours, 0);
}

function svgEl<K extends keyof SVGElementTagNameMap>(tag: K, parent: Element, className?: string): SVGElementTagNameMap[K] {
    const element = document.createElementNS(SVG_NS, tag);
    if (className) {
        element.setAttribute("class", className);
    }
    parent.appendChild(element);
    return element;
}

function htmlEl(tag: string, parent: Element, className: string): HTMLElement {
    const element = document.createElement(tag);
    element.className = className;
    parent.appendChild(element);
    return element;
}

function permutations<T>(items: T[]): T[][] {
    if (items.length < 2) {
        return [items];
    }
    return items.flatMap((item, index) =>
        permutations([...items.slice(0, index), ...items.slice(index + 1)]).map((rest) => [item, ...rest]));
}

/** Link hours between two columns, keyed by the two block names. */
function flows(rows: Row[], left: Stage, right: Stage): [string, string, number][] {
    const totals = new Map<string, [string, string, number]>();
    rows.forEach((row) => {
        const a = stageName(row, left);
        const b = stageName(row, right);
        const key = `${a}|${b}`;
        const entry: [string, string, number] = totals.get(key) ?? [a, b, 0];
        entry[2] += row.hours;
        totals.set(key, entry);
    });
    return [...totals.values()];
}

/** Best order for an outer column once the middle column is fixed. A crossing costs the smaller of the two flows. */
function bestOuter(names: string[], orders: number[][], links: [string, string, number][], middleRank: Map<string, number>, outerIsLeft: boolean): { order: string[]; cost: number } {
    const count = names.length;
    const outerIndex = new Map(names.map((name, index) => [name, index]));
    const parsed = links.map((link) => ({
        outer: outerIndex.get(outerIsLeft ? link[0] : link[1]) ?? 0,
        middle: middleRank.get(outerIsLeft ? link[1] : link[0]) ?? 0,
        hours: link[2],
    }));
    const penalty = new Float64Array(count * count);
    for (const a of parsed) {
        for (const b of parsed) {
            if (a.outer !== b.outer && a.middle > b.middle) {
                penalty[a.outer * count + b.outer] += Math.min(a.hours, b.hours);
            }
        }
    }
    let bestOrder = orders[0];
    let lowest = Infinity;
    for (const order of orders) {
        let cost = 0;
        for (let i = 0; i < count; i++) {
            for (let j = i + 1; j < count; j++) {
                cost += penalty[order[i] * count + order[j]];
            }
        }
        if (cost < lowest) {
            lowest = cost;
            bestOrder = order;
        }
    }
    return { order: bestOrder.map((index) => names[index]), cost: lowest };
}

export class Visual implements IVisual {
    private host: IVisualHost;
    private events: IVisualEventService;
    private root: HTMLElement;
    private scope: HTMLElement;
    private total: HTMLElement;
    private share: HTMLElement;
    private empty: HTMLElement;
    private svg: SVGSVGElement;
    private linkLayer: SVGGElement;
    private nodeLayer: SVGGElement;
    private columnHeads: SVGTextElement[];
    private numberFormat: Intl.NumberFormat;

    private rows: Row[] = [];
    private nodes = new Map<string, NodeView>();
    private links = new Map<string, LinkView>();
    private activeTeams = new Set<string>();
    private traced: NodeView | null = null;
    private width = 0;
    private height = 0;
    private xs: [number, number, number] = [0, 0, 0];
    private frame = 0;
    private pendingRender: VisualUpdateOptions | null = null;

    constructor(options: VisualConstructorOptions) {
        this.host = options.host;
        this.events = options.host.eventService;
        this.numberFormat = new Intl.NumberFormat(options.host.locale || "en-US", { maximumFractionDigits: 0 });

        this.root = htmlEl("div", options.element, "sankey-root");
        const head = htmlEl("div", this.root, "sankey-head");
        const readout = htmlEl("div", head, "sankey-readout");
        this.scope = htmlEl("div", readout, "sankey-scope");
        const totalLine = htmlEl("div", readout, "sankey-total-line");
        this.total = htmlEl("span", totalLine, "sankey-total");
        this.share = htmlEl("span", totalLine, "sankey-share");
        const allTeams = htmlEl("button", head, "sankey-all");
        allTeams.textContent = "Show all";
        allTeams.addEventListener("click", () => {
            this.activeTeams.clear();
            this.traced = null;
            this.plan(false);
        });

        this.svg = svgEl("svg", this.root, "sankey-chart");
        this.svg.setAttribute("role", "group");
        this.linkLayer = svgEl("g", this.svg);
        this.nodeLayer = svgEl("g", this.svg);
        this.columnHeads = [0, 1, 2].map(() => svgEl("text", this.svg, "sankey-column"));

        htmlEl("div", this.root, "sankey-hint").textContent = HINT;
        this.empty = htmlEl("div", this.root, "sankey-empty");
    }

    public update(options: VisualUpdateOptions): void {
        this.events.renderingStarted(options);
        this.finishRender();
        this.pendingRender = options;
        try {
            this.width = options.viewport.width;
            this.height = options.viewport.height;
            const isResizeOnly = (options.type & powerbi.VisualUpdateType.Data) === 0;
            if (!isResizeOnly) {
                this.readTable(options.dataViews?.[0]?.table);
            }
            this.plan(isResizeOnly);
        } catch (error) {
            this.pendingRender = null;
            this.events.renderingFailed(options, String(error));
        }
    }

    public destroy(): void {
        cancelAnimationFrame(this.frame);
    }

    /** The visual has no format settings. An empty model keeps the Format pane valid. */
    public getFormattingModel(): powerbi.visuals.FormattingModel {
        return { cards: [] };
    }

    private finishRender(): void {
        if (this.pendingRender) {
            this.events.renderingFinished(this.pendingRender);
            this.pendingRender = null;
        }
    }

    private readTable(table: DataViewTable | undefined): void {
        this.rows = [];
        this.nodes.forEach((node) => { node.order = UNUSED; });
        this.links.forEach((link) => { link.rows = []; link.hours = 0; });
        if (!table) {
            return;
        }
        const indexOf = (role: string): number => table.columns.findIndex((column) => column.roles?.[role]);
        const columns = { team: indexOf("team"), service: indexOf("service"), activity: indexOf("activity"), hours: indexOf("hours") };
        if (Object.values(columns).some((index) => index < 0)) {
            return;
        }
        const text = (value: powerbi.PrimitiveValue): string => {
            const trimmed = value === null || value === undefined ? "" : String(value).trim();
            return trimmed || BLANK;
        };
        for (const row of table.rows ?? []) {
            const hours = Number(row[columns.hours]);
            if (hours > 0) {
                this.rows.push({
                    team: text(row[columns.team]),
                    service: text(row[columns.service]),
                    activity: text(row[columns.activity]),
                    hours,
                });
            }
        }
        this.columnHeads[0].textContent = table.columns[columns.team].displayName;
        this.columnHeads[1].textContent = table.columns[columns.service].displayName;
        this.columnHeads[2].textContent = table.columns[columns.activity].displayName;

        this.assignOrder();
        for (const row of this.rows) {
            this.linkFor(0, row.team, row.service, row.team).rows.push(row);
            this.linkFor(1, row.service, row.activity, row.team).rows.push(row);
        }
        this.links.forEach((link) => { link.hours = sumHours(link.rows); });
    }

    /**
     * Picks the block order with the least crossing hours. It runs on new data only, so picking a team
     * never reshuffles the chart. The columns are flipped if needed to put the biggest service on top.
     */
    private assignOrder(): void {
        const byHours = (stage: Stage): string[] => {
            const totals = new Map<string, number>();
            this.rows.forEach((row) => totals.set(stageName(row, stage), (totals.get(stageName(row, stage)) ?? 0) + row.hours));
            return [...totals.entries()].sort((a, b) => b[1] - a[1]).map((entry) => entry[0]);
        };
        // The palette hands out colors on first request, so asking biggest team first keeps them independent of row order.
        const teamsByHours = byHours(0);
        teamsByHours.forEach((team) => this.teamColor(team));
        const activitiesByHours = byHours(2);
        let teams = teamsByHours;
        let services = byHours(1);
        let activities = activitiesByHours;
        const biggestService = services[0];

        if (Math.max(teams.length, services.length, activities.length) <= MAX_EXACT_ORDER) {
            const left = flows(this.rows, 0, 1);
            const right = flows(this.rows, 1, 2);
            const teamOrders = permutations(teamsByHours.map((_, index) => index));
            const activityOrders = permutations(activitiesByHours.map((_, index) => index));
            let lowest = Infinity;
            permutations(services).forEach((middle) => {
                const rank = new Map(middle.map((name, index) => [name, index]));
                const outerLeft = bestOuter(teamsByHours, teamOrders, left, rank, true);
                const outerRight = bestOuter(activitiesByHours, activityOrders, right, rank, false);
                if (outerLeft.cost + outerRight.cost < lowest) {
                    lowest = outerLeft.cost + outerRight.cost;
                    teams = outerLeft.order;
                    services = middle;
                    activities = outerRight.order;
                }
            });
            if (services.indexOf(biggestService) > services.length / 2) {
                teams = [...teams].reverse();
                services = [...services].reverse();
                activities = [...activities].reverse();
            }
        }
        [teams, services, activities].forEach((names, stage) => {
            names.forEach((name, order) => { this.nodeFor(stage as Stage, name).order = order; });
        });
    }

    private nodeFor(stage: Stage, name: string): NodeView {
        const key = `${stage}|${name}`;
        const existing = this.nodes.get(key);
        if (existing) {
            return existing;
        }
        const group = svgEl("g", this.nodeLayer, "sankey-node");
        group.setAttribute("tabindex", "0");
        group.setAttribute("role", "button");
        const hit = svgEl("rect", group);
        hit.setAttribute("fill", "transparent");
        const bar = svgEl("rect", group, "sankey-bar");
        bar.setAttribute("rx", "2");
        const label = svgEl("text", group, "sankey-label");
        label.setAttribute("dominant-baseline", "middle");
        svgEl("tspan", label).textContent = `${name} `;
        const value = svgEl("tspan", label, "sankey-value");
        const node: NodeView = {
            stage, name, group, hit, bar, label, value,
            cur: { y: COLUMN_HEAD, h: 0 }, tgt: { y: COLUMN_HEAD, h: 0 }, from: { y: COLUMN_HEAD, h: 0 },
            hours: 0, off: false, stackOut: 0, stackIn: 0, order: UNUSED,
        };
        const pick = (): void => this.pick(node);
        group.addEventListener("click", pick);
        group.addEventListener("keydown", (event: KeyboardEvent) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                pick();
            }
        });
        this.bindTooltip(group, () => [{ displayName: node.name, value: `${this.format(node.hours)} hours` }]);
        this.nodes.set(key, node);
        return node;
    }

    private linkFor(stage: 0 | 1, source: string, target: string, team: string): LinkView {
        const key = `${stage}|${source}|${target}|${team}`;
        const existing = this.links.get(key);
        if (existing) {
            return existing;
        }
        const color = this.teamColor(team);
        const base = svgEl("path", this.linkLayer, "sankey-link");
        base.style.stroke = color;
        const link: LinkView = {
            key, stage, source, target, team, base, rows: [], hours: 0,
            cur: { y0: COLUMN_HEAD, y1: COLUMN_HEAD, w: 0 },
            tgt: { y0: COLUMN_HEAD, y1: COLUMN_HEAD, w: 0 },
            from: { y0: COLUMN_HEAD, y1: COLUMN_HEAD, w: 0 },
        };
        this.bindTooltip(base, () => [
            { displayName: link.team, value: link.stage === 0 ? `to ${link.target}` : `${link.source} to ${link.target}` },
            { displayName: "Hours", value: this.format(link.hours) },
        ]);
        this.links.set(key, link);
        return link;
    }

    private teamColor(team: string): string {
        const palette = this.host.colorPalette;
        return palette.isHighContrast ? palette.foreground.value : palette.getColor(team).value;
    }

    private bindTooltip(element: Element, items: () => powerbi.extensibility.VisualTooltipDataItem[]): void {
        const service = this.host.tooltipService;
        const coordinates = (event: Event): number[] => [(event as MouseEvent).clientX, (event as MouseEvent).clientY];
        element.addEventListener("mouseenter", (event) => {
            service.show({ coordinates: coordinates(event), isTouchEvent: false, dataItems: items(), identities: [] });
        });
        element.addEventListener("mousemove", (event) => {
            service.move({ coordinates: coordinates(event), isTouchEvent: false, dataItems: items(), identities: [] });
        });
        element.addEventListener("mouseleave", () => {
            service.hide({ immediately: true, isTouchEvent: false });
        });
    }

    private format(hours: number): string {
        return this.numberFormat.format(hours);
    }

    private isOn(team: string): boolean {
        return this.activeTeams.size === 0 || this.activeTeams.has(team);
    }

    private pick(node: NodeView): void {
        if (node.stage === 0) {
            if (this.activeTeams.has(node.name)) {
                this.activeTeams.delete(node.name);
            } else {
                this.activeTeams.add(node.name);
            }
            const teamCount = new Set(this.rows.map((row) => row.team)).size;
            if (this.activeTeams.size >= teamCount) {
                this.activeTeams.clear();
            }
        } else {
            this.traced = this.traced === node ? null : node;
        }
        this.plan(false);
    }

    /** Works out where everything should end up, then animates there. */
    private plan(jump: boolean): void {
        const teamRows = this.rows.filter((row) => this.isOn(row.team));
        const traced = this.traced;
        if (traced && !teamRows.some((row) => stageName(row, traced.stage) === traced.name)) {
            this.traced = null;
        }
        const focus = this.traced;
        const matches = (row: Row): boolean => !focus || stageName(row, focus.stage) === focus.name;
        const scoped = teamRows.filter(matches);
        const scopedHours = sumHours(scoped);

        this.empty.textContent = this.rows.length === 0
            ? "No hours to show. Check the fields and the Sprint slicer."
            : scoped.length === 0 ? "The picked teams have no hours for this selection." : "";

        const chartHeight = Math.max(80, this.height - HEAD_AND_HINT);
        this.svg.setAttribute("width", String(this.width));
        this.svg.setAttribute("height", String(chartHeight));
        this.placeColumns();

        const stages: Stage[] = [0, 1, 2];
        const columns = stages.map((stage) => [...this.nodes.values()]
            .filter((node) => node.stage === stage && node.order !== UNUSED)
            .sort((a, b) => a.order - b.order));

        columns.flat().forEach((node) => {
            node.hours = sumHours(scoped.filter((row) => stageName(row, node.stage) === node.name));
            node.off = node.stage === 0 && !this.isOn(node.name);
            node.stackOut = 0;
            node.stackIn = 0;
        });

        const body = chartHeight - COLUMN_HEAD - 6;
        const room = columns.map((column) => {
            const shown = column.filter((node) => node.off || node.hours > 0);
            const offCount = column.filter((node) => node.off).length;
            return body - NODE_GAP * Math.max(0, shown.length - 1) - offCount * OFF_TEAM_HEIGHT;
        });
        const scale = scopedHours > 0 ? Math.max(0, Math.min(...room)) / scopedHours : 0;

        columns.forEach((column) => {
            let y = COLUMN_HEAD;
            column.forEach((node) => {
                if (node.off) {
                    node.tgt = { y, h: OFF_TEAM_HEIGHT };
                    y += OFF_TEAM_HEIGHT + NODE_GAP;
                } else if (node.hours > 0) {
                    node.tgt = { y, h: node.hours * scale };
                    y += node.hours * scale + NODE_GAP;
                } else {
                    node.tgt = { y: Math.max(COLUMN_HEAD, y - NODE_GAP / 2), h: 0 };
                }
            });
        });

        const nodeOf = (stage: Stage, name: string): NodeView | undefined => this.nodes.get(`${stage}|${name}`);
        const rankOf = (stage: Stage, name: string): number => nodeOf(stage, name)?.order ?? 0;
        const links = [...this.links.values()];

        links
            .slice()
            .sort((a, b) => a.stage - b.stage
                || rankOf(a.stage, a.source) - rankOf(b.stage, b.source)
                || rankOf((a.stage + 1) as Stage, a.target) - rankOf((b.stage + 1) as Stage, b.target)
                || rankOf(0, a.team) - rankOf(0, b.team))
            .forEach((link) => {
                const source = nodeOf(link.stage, link.source);
                const shown = this.isOn(link.team) ? sumHours(link.rows.filter(matches)) : 0;
                link.hours = shown;
                const width = shown * scale;
                link.tgt.w = width;
                if (source) {
                    link.tgt.y0 = source.tgt.y + source.stackOut + width / 2;
                    source.stackOut += width;
                }
                link.base.style.strokeOpacity = shown < scopedHours * TINY_SHARE ? "0.16" : "0.45";
            });

        links
            .slice()
            .sort((a, b) => a.stage - b.stage
                || rankOf((a.stage + 1) as Stage, a.target) - rankOf((b.stage + 1) as Stage, b.target)
                || rankOf(a.stage, a.source) - rankOf(b.stage, b.source)
                || rankOf(0, a.team) - rankOf(0, b.team))
            .forEach((link) => {
                const target = nodeOf((link.stage + 1) as Stage, link.target);
                if (target) {
                    link.tgt.y1 = target.tgt.y + target.stackIn + link.tgt.w / 2;
                    target.stackIn += link.tgt.w;
                }
            });

        const allHours = sumHours(this.rows);
        columns.flat().forEach((node) => this.styleNode(node, allHours));
        this.nodes.forEach((node) => {
            if (node.order === UNUSED) {
                node.hours = 0;
                node.off = false;
                node.tgt = { y: node.cur.y, h: 0 };
                node.label.style.display = "none";
                node.group.style.pointerEvents = "none";
                node.group.setAttribute("tabindex", "-1");
            }
        });

        this.updateReadout(scopedHours, allHours);
        this.animate(jump);
    }

    private styleNode(node: NodeView, allHours: number): void {
        const palette = this.host.colorPalette;
        const highContrast = palette.isHighContrast;
        const shown = node.off ? sumHours(this.rows.filter((row) => row.team === node.name)) : node.hours;
        node.value.textContent = this.format(shown);

        const isFocus = this.traced === node;
        const bar = node.stage === 0 ? (node.off ? OFF_BAR : this.teamColor(node.name)) : (isFocus ? INK : NEUTRAL_BAR);
        node.bar.style.fill = highContrast ? palette.foreground.value : bar;
        node.label.style.fill = highContrast ? palette.foreground.value : (node.off ? MUTED_INK : INK);
        node.label.style.fontWeight = isFocus ? "600" : "400";

        const isHidden = !node.off && node.hours <= 0;
        node.label.style.display = isHidden ? "none" : "";
        node.group.style.pointerEvents = isHidden ? "none" : "auto";
        node.group.setAttribute("tabindex", isHidden ? "-1" : "0");
        const share = allHours > 0 ? Math.round((shown / allHours) * 100) : 0;
        node.group.setAttribute("aria-label", `${node.name}, ${this.format(shown)} hours, ${share}% of all logged time`);
        node.group.setAttribute("aria-pressed", String(node.stage === 0 ? this.activeTeams.has(node.name) : this.traced === node));

        const x = this.xs[node.stage];
        node.bar.setAttribute("x", String(x));
        node.bar.setAttribute("width", String(NODE_WIDTH));
        node.hit.setAttribute("x", String(x - 4));
        node.hit.setAttribute("width", String(NODE_WIDTH + 8));
        const isFirst = node.stage === 0;
        node.label.setAttribute("x", String(isFirst ? x - 6 : x + NODE_WIDTH + 6));
        node.label.setAttribute("text-anchor", isFirst ? "end" : "start");
        if (node.stage === 1) {
            node.label.style.paintOrder = "stroke";
            node.label.style.stroke = "#FFFFFF";
            node.label.style.strokeWidth = "3px";
        }
    }

    private updateReadout(shown: number, allHours: number): void {
        const teams = [...this.activeTeams];
        const who = teams.length === 0 ? "All teams"
            : teams.length < 3 ? teams.join(" and ")
            : `${teams.length} teams`;
        this.scope.textContent = this.traced ? `${who}, ${this.traced.name}` : who;
        this.total.textContent = `${this.format(shown)} hours`;
        this.share.textContent = allHours > 0 && shown < allHours - 0.5
            ? `${Math.round((shown / allHours) * 100)}% of all logged time in the selected sprints`
            : "";
    }

    /** Label room comes from the longest name in each outer column, so nothing clips. */
    private placeColumns(): void {
        const labelRoom = (stage: Stage): number => {
            let longest = 0;
            this.nodes.forEach((node) => {
                if (node.stage === stage && node.order !== UNUSED) {
                    longest = Math.max(longest, node.name.length + 7);
                }
            });
            return Math.min(this.width * 0.3, longest * CHAR_WIDTH + 12);
        };
        const first = labelRoom(0);
        const last = this.width - labelRoom(2) - NODE_WIDTH;
        this.xs = [first, (first + last) / 2, last];
        this.columnHeads[0].setAttribute("x", String(first + NODE_WIDTH));
        this.columnHeads[0].setAttribute("text-anchor", "end");
        this.columnHeads[1].setAttribute("x", String(this.xs[1]));
        this.columnHeads[2].setAttribute("x", String(last));
        this.columnHeads.forEach((head) => head.setAttribute("y", "14"));
    }

    private applyFrame(): void {
        this.nodes.forEach((node) => {
            const { y, h } = node.cur;
            node.bar.setAttribute("y", String(y));
            node.bar.setAttribute("height", String(h > 0.3 ? Math.max(2, h) : 0));
            node.hit.setAttribute("y", String(y - 6));
            node.hit.setAttribute("height", String(h + 12));
            node.label.setAttribute("y", String(y + h / 2));
        });
        this.links.forEach((link) => {
            const x0 = this.xs[link.stage] + NODE_WIDTH;
            const x1 = this.xs[link.stage + 1];
            const mid = (x0 + x1) / 2;
            const { y0, y1, w } = link.cur;
            const path = `M${x0},${y0}C${mid},${y0} ${mid},${y1} ${x1},${y1}`;
            link.base.setAttribute("d", path);
            link.base.style.strokeWidth = String(w > 0.05 ? Math.max(0.6, w) : 0);
            link.base.style.pointerEvents = w > 0.05 ? "auto" : "none";
        });
    }

    /** Elements stay in the DOM between updates and move to their new place, which is what makes the change glide. */
    private animate(jump: boolean): void {
        cancelAnimationFrame(this.frame);
        const nodes = [...this.nodes.values()];
        const links = [...this.links.values()];
        const stillMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
        if (jump || stillMotion || document.hidden) {
            nodes.forEach((node) => { node.cur = { ...node.tgt }; });
            links.forEach((link) => { link.cur = { ...link.tgt }; });
            this.applyFrame();
            this.finishRender();
            return;
        }
        nodes.forEach((node) => { node.from = { ...node.cur }; });
        links.forEach((link) => { link.from = { ...link.cur }; });
        const start = performance.now();
        const step = (now: number): void => {
            const progress = Math.min(1, Math.max(0, (now - start) / TWEEN_MS));
            const eased = 1 - Math.pow(1 - progress, 3);
            const mix = (a: number, b: number): number => a + (b - a) * eased;
            nodes.forEach((node) => {
                node.cur = { y: mix(node.from.y, node.tgt.y), h: mix(node.from.h, node.tgt.h) };
            });
            links.forEach((link) => {
                link.cur = {
                    y0: mix(link.from.y0, link.tgt.y0),
                    y1: mix(link.from.y1, link.tgt.y1),
                    w: mix(link.from.w, link.tgt.w),
                };
            });
            this.applyFrame();
            if (progress < 1) {
                this.frame = requestAnimationFrame(step);
            } else {
                this.finishRender();
            }
        };
        this.frame = requestAnimationFrame(step);
    }
}
