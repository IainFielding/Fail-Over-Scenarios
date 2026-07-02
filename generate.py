#!/usr/bin/env python3
"""Generate 7 draw.io diagrams for 3-tier architecture HA/DR topologies.

Uses Azure (azure2) image stencils. Emits one .drawio file per scenario into out/.
Run: python generate.py
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "out")

# ---- Azure azure2 image stencils (bundled with draw.io) ----
IMG = "img/lib/azure2"
TM = f"{IMG}/networking/Traffic_Manager_Profiles.svg"      # DNS / global LB
AGW = f"{IMG}/networking/Application_Gateways.svg"          # web-tier load balancer
LB = f"{IMG}/networking/Load_Balancers.svg"                # internal (app-tier) LB
VM = f"{IMG}/compute/Virtual_Machine.svg"                   # web / app servers
SQL = f"{IMG}/databases/SQL_Database.svg"                   # data tier


def azure_img(image):
    """Style for an Azure azure2 image stencil."""
    return (f"sketch=0;html=1;shape=image;image={image};"
            f"verticalLabelPosition=bottom;verticalAlign=top;"
            f"labelBackgroundColor=none;fontSize=11;")


def aws_icon(res, fill="#E7157B", grad="#F34482"):
    """Style for an AWS mxgraph.aws4 resource icon (bundled stencils)."""
    return (f"sketch=0;outlineConnect=0;fontColor=#232F3E;"
            f"gradientColor={grad};gradientDirection=north;fillColor={fill};"
            f"strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;"
            f"verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;"
            f"aspect=fixed;shape=mxgraph.aws4.resourceIcon;"
            f"resIcon=mxgraph.aws4.{res};")


# Per-cloud icon + label sets. Each tier maps to a ready-to-use cell style.
THEME_AZURE = {
    "cloud": "Azure",
    "dns": azure_img(TM), "agw": azure_img(AGW), "ilb": azure_img(LB),
    "vm": azure_img(VM), "db": azure_img(SQL),
    "L": {"dns": "Traffic Manager (DNS)", "agw": "App Gateway",
          "ilb": "Internal LB", "web": "Web VMs", "app": "App VMs",
          "db": "SQL DB"},
}
THEME_AWS = {
    "cloud": "AWS",
    "dns": aws_icon("route_53", "#8C4FFF", "#B392F0"),
    "agw": aws_icon("application_load_balancer", "#8C4FFF", "#B392F0"),
    "ilb": aws_icon("network_load_balancer", "#8C4FFF", "#B392F0"),
    "vm": aws_icon("ec2", "#D45B07", "#F58534"),
    "db": aws_icon("rds", "#2E27AD", "#527FFF"),
    "L": {"dns": "Route 53 (DNS)", "agw": "App Load Balancer",
          "ilb": "Internal NLB", "web": "Web EC2", "app": "App EC2",
          "db": "RDS"},
}

# ---- palette (role colors) ----
ACTIVE = "#DAE8FC"   # blue
PASSIVE = "#E8E8E8"  # grey
DR = "#FFE6CC"       # amber
REGION = "#F8F8F8"   # neutral region wrapper
AZ = "#FFFFFF"


def esc(s):
    return escape(str(s))


class Diagram:
    def __init__(self, name):
        self.name = name
        self.bg = []   # containers (drawn first / behind)
        self.fg = []   # nodes + edges (drawn on top)
        self._n = 0

    def nid(self):
        self._n += 1
        return f"c{self._n}"

    def box(self, x, y, w, h, label, fill, dashed=True):
        i = self.nid()
        dash = 1 if dashed else 0
        style = (f"rounded=1;dashed={dash};dashPattern=8 4;fillColor={fill};"
                 f"strokeColor=#888888;verticalAlign=top;align=left;"
                 f"spacingLeft=10;spacingTop=6;fontSize=12;fontStyle=1;"
                 f"arcSize=4;opacity=60;")
        self.bg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def shape(self, x, y, label, style, w=48, h=48):
        i = self.nid()
        self.fg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def icon(self, x, y, label, image, w=48, h=48):
        return self.shape(x, y, label, azure_img(image), w, h)

    def text(self, x, y, w, h, label, size=11, bold=False):
        i = self.nid()
        fs = 1 if bold else 0
        style = (f"text;html=1;align=center;verticalAlign=middle;"
                 f"fontSize={size};fontStyle={fs};")
        self.fg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def diamond(self, x, y, label, w=200, h=110, fill="#FFF2CC",
                stroke="#D6B656"):
        """Decision node (rhombus). label may contain <br> (not escaped)."""
        i = self.nid()
        style = (f"rhombus;whiteSpace=wrap;html=1;fillColor={fill};"
                 f"strokeColor={stroke};fontSize=11;")
        self.fg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def pnode(self, x, y, label, w=215, h=70, fill="#DAE8FC",
              stroke="#6C8EBF", arc=12):
        """Process / outcome box. label may contain <br> (not escaped)."""
        i = self.nid()
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
                 f"strokeColor={stroke};fontSize=11;arcSize={arc};"
                 f"verticalAlign=middle;align=center;")
        self.fg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def edge(self, src, dst, label="", dashed=False, color="#333333",
             waypoints=None, exit=None, entry=None):
        """Orthogonal edge. `waypoints` is a list of (x, y) the line must pass
        through (used to route around shapes); `exit`/`entry` are (x, y)
        fractions (0..1) pinning where the line leaves src / meets dst."""
        i = self.nid()
        dash = 1 if dashed else 0
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
                 f"dashed={dash};strokeColor={color};endArrow=block;"
                 f"fontSize=10;labelBackgroundColor=#FFFFFF;jettySize=auto;")
        if exit is not None:
            style += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry is not None:
            style += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        geo = '<mxGeometry relative="1" as="geometry">'
        if waypoints:
            pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in waypoints)
            geo += f'<Array as="points">{pts}</Array>'
        geo += '</mxGeometry>'
        self.fg.append(
            f'<mxCell id="{i}" value="{esc(label)}" style="{style}" '
            f'edge="1" parent="1" source="{src}" target="{dst}">'
            f'{geo}</mxCell>')
        return i

    # ---- a full 3-tier stack; returns dict of tier node ids ----
    # AppGateway -> Web -> Internal LB -> App -> SQL DB
    def stack(self, x, y, tag="", theme=None):
        t = theme or THEME_AZURE
        L = t["L"]
        sw = 150
        cx = x + (sw - 48) // 2
        lb = self.shape(cx, y, f"{L['agw']}{tag}", t["agw"])
        web = self.shape(cx, y + 70, f"{L['web']}{tag}", t["vm"])
        ilb = self.shape(cx, y + 140, f"{L['ilb']}{tag}", t["ilb"])
        app = self.shape(cx, y + 210, f"{L['app']}{tag}", t["vm"])
        db = self.shape(cx, y + 280, f"{L['db']}{tag}", t["db"])
        self.edge(lb, web)
        self.edge(web, ilb)
        self.edge(ilb, app)
        self.edge(app, db)
        return {"lb": lb, "web": web, "ilb": ilb, "app": app, "db": db,
                "x": x, "w": sw, "top": y, "bottom": y + 280 + 48}

    def legend(self, x, y):
        self.box(x, y, 250, 130, "Legend", "#FFFFFF", dashed=False)
        rows = [
            (ACTIVE, "Active stack"),
            (PASSIVE, "Passive / standby"),
            (DR, "Disaster recovery"),
        ]
        yy = y + 28
        for fill, lbl in rows:
            self.box(x + 12, yy, 24, 16, "", fill, dashed=False)
            self.text(x + 44, yy - 2, 180, 20, lbl, size=10)
            yy += 24
        self.text(x + 12, yy - 2, 230, 20,
                  "— solid: live traffic   - - dashed: replication / failover",
                  size=9)

    def render(self):
        cells = "\n        ".join(self.bg + self.fg)
        return (
            f'<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="{esc(self.name)}" id="{esc(self.name)}">\n'
            f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            f'page="1" pageScale="1" pageWidth="1600" pageHeight="1100" '
            f'math="0" shadow="0">\n'
            f'      <root>\n'
            f'        <mxCell id="0"/>\n'
            f'        <mxCell id="1" parent="0"/>\n'
            f'        {cells}\n'
            f'      </root>\n'
            f'    </mxGraphModel>\n'
            f'  </diagram>\n'
            f'</mxfile>\n')

    def save(self, filename):
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render())
        print(f"wrote {path}")


def dns(d, x, y, theme=None, label=None):
    t = theme or THEME_AZURE
    return d.shape(x, y, label or t["L"]["dns"], t["dns"])


# ---------- Scenario builders ----------

def s01_active():
    d = Diagram("01-active")
    d.text(0, 0, 700, 30, "Scenario 1 - Active (single site)", size=16, bold=True)
    tm = dns(d, 300, 50)
    d.box(220, 130, 250, 410, "Region 1  (Active)", ACTIVE)
    st = d.stack(270, 165)
    d.edge(tm, st["lb"], "traffic")
    d.legend(560, 130)
    d.save("01-active.drawio")


def s02_pilot():
    d = Diagram("02-active-dr-pilot-light")
    d.text(0, 0, 1000, 30,
           "Scenario 2 - Active + DR (Pilot Light)", size=16, bold=True)
    tm = dns(d, 430, 50)
    d.box(180, 130, 250, 410, "Region 1  (Active)", ACTIVE)
    a = d.stack(230, 165)
    d.box(560, 130, 250, 410, "Region 2  (DR - Pilot Light)", DR)
    # Only the data tier stays live in the DR region; the compute tiers are
    # dormant and provisioned / scaled up on failover.
    dormant = d.box(610, 165, 150, 235, "Compute dormant", PASSIVE)
    drdb = d.shape(610 + 51, 165 + 280, "SQL DB (DR)", THEME_AZURE["db"])
    d.text(560, 545, 250, 30,
           "Compute scaled to 0 - provisioned on failover", size=9)
    d.edge(tm, a["lb"], "traffic")
    d.edge(tm, dormant, "failover: provision + scale up",
           dashed=True, color="#888888")
    d.edge(a["db"], drdb, "async replication (data only)",
           dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.legend(900, 130)
    d.save("02-active-dr-pilot-light.drawio")


def s03_warm():
    d = Diagram("03-active-dr-warm-standby")
    d.text(0, 0, 1000, 30,
           "Scenario 3 - Active + DR (Warm Standby)", size=16, bold=True)
    tm = dns(d, 430, 50)
    d.box(180, 130, 250, 410, "Region 1  (Active)", ACTIVE)
    a = d.stack(230, 165)
    d.box(560, 130, 250, 410, "Region 2  (DR - Warm Standby)", DR)
    dr = d.stack(610, 165, tag=" (warm)")
    d.edge(tm, a["lb"], "traffic")
    d.edge(tm, dr["lb"], "failover (scale up + cut over)",
           dashed=True, color="#888888")
    d.edge(a["db"], dr["db"], "async replication",
           dashed=True, color="#D79B00")
    d.legend(900, 130)
    d.save("03-active-dr-warm-standby.drawio")


def s04_hot():
    d = Diagram("04-active-dr-hot-standby")
    d.text(0, 0, 1000, 30,
           "Scenario 4 - Active + DR (Automatic Hot Standby)",
           size=16, bold=True)
    tm = dns(d, 430, 50)
    d.box(180, 130, 250, 410, "Region 1  (Active)", ACTIVE)
    a = d.stack(230, 165)
    d.box(560, 130, 250, 410, "Region 2  (Hot standby)", PASSIVE)
    p = d.stack(610, 165, tag=" (standby)")
    d.edge(tm, a["lb"], "traffic")
    d.edge(tm, p["lb"], "automatic failover (health probe)",
           dashed=True, color="#888888")
    d.edge(a["db"], p["db"], "async replication",
           dashed=True, color="#D79B00")
    d.legend(900, 130)
    d.save("04-active-dr-hot-standby.drawio")


def s05_ap():
    d = Diagram("05-active-passive")
    d.text(0, 0, 900, 30, "Scenario 5 - Active + Passive (local HA)",
           size=16, bold=True)
    tm = dns(d, 430, 50)
    d.box(150, 130, 620, 440, "Region 1", REGION)
    d.box(180, 160, 250, 390, "Active", ACTIVE)
    a = d.stack(230, 195)
    d.box(490, 160, 250, 390, "Passive (standby)", PASSIVE)
    p = d.stack(540, 195, tag=" (standby)")
    d.edge(tm, a["lb"], "traffic")
    d.edge(tm, p["lb"], "failover", dashed=True, color="#888888")
    d.edge(a["db"], p["db"], "sync replication", dashed=True, color="#6C8EBF")
    d.legend(820, 130)
    d.save("05-active-passive.drawio")


def s06_apdr():
    d = Diagram("06-active-passive-dr")
    d.text(0, 0, 1100, 30, "Scenario 6 - Active + Passive + DR",
           size=16, bold=True)
    tm = dns(d, 520, 50)
    d.box(120, 130, 620, 440, "Region 1 (Active/Passive HA)", REGION)
    d.box(150, 160, 250, 390, "Active", ACTIVE)
    a = d.stack(200, 195)
    d.box(460, 160, 250, 390, "Passive (standby)", PASSIVE)
    p = d.stack(510, 195, tag=" (standby)")
    d.box(820, 130, 250, 440, "Region 2 (DR)", DR)
    dr = d.stack(870, 195, tag=" (DR)")
    d.edge(tm, a["lb"], "traffic")
    d.edge(tm, p["lb"], "failover", dashed=True, color="#888888")
    d.edge(tm, dr["lb"], "DR failover", dashed=True, color="#888888")
    d.edge(a["db"], p["db"], "sync", dashed=True, color="#6C8EBF",
           exit=(1, 0.5), entry=(0, 0.5))
    # async to the DR region routes below the row so it clears the passive DB
    db_lane = 195 + 280 + 60   # just below the stack DB icons
    d.edge(a["db"], dr["db"], "async replication", dashed=True, color="#D79B00",
           exit=(0.5, 1), entry=(0.5, 1),
           waypoints=[(275, db_lane), (945, db_lane)])
    d.legend(1100, 130)
    d.save("06-active-passive-dr.drawio")


def az_region(d, x, label, fill, n=3, theme=None, region_fill=None):
    """A region with zone-redundant regional LBs (Application Gateway + internal
    Load Balancer) fronting n Availability Zones. The internal LB balances the
    app tier across all AZs. Returns a dict with front LB id, db ids, w, h.

    Layout: regional LBs in a left column; AZ columns (Web / App / SQL) to the
    right. Edges fan out from the LBs to every AZ to show cross-AZ balancing.
    `region_fill` tints the region container (e.g. DR) while AZ boxes keep `fill`.
    """
    t = theme or THEME_AZURE
    L = t["L"]
    y = 130
    region_w = 220 + n * 175
    region_h = 480
    az_y = y + 40
    az_h = region_h - 70
    d.box(x, y, region_w, region_h, label, region_fill or REGION)
    agw = d.shape(x + 30, y + 80, L["agw"], t["agw"])         # zone-redundant
    ilb = d.shape(x + 30, y + 160, L["ilb"], t["ilb"])        # zone-redundant
    ilb_cx = x + 54
    rx = x + 130              # riser column just right of the LBs (clear of AZs)
    # Routing lanes (gaps between rows) so fan-out edges never cross icons:
    lane_agw = az_y + 26      # just above the web row (below AZ labels)
    lane_w2i = az_y + 114     # web -> internal LB, below the web labels / above LB top
    lane_i2a = az_y + 160     # internal LB -> app, below the LB so the fan-out drops
    webs, apps, dbs, web_cx = [], [], [], []
    for i in range(n):
        ax = x + 190 + i * 175
        d.box(ax, az_y, 150, az_h, f"AZ-{i+1}  (Active)", fill)
        cx = ax + 51
        web_cx.append(cx + 24)
        webs.append(d.shape(cx, az_y + 40, L["web"], t["vm"]))
        apps.append(d.shape(cx, az_y + 180, L["app"], t["vm"]))
        dbs.append(d.shape(cx, az_y + 320, L["db"], t["db"]))
        d.edge(apps[i], dbs[i])
    # presentation LB -> web: leave from the SIDE (in arrives on top), rise into
    # a lane above the web row, then drop into each web's top.
    for i, w in enumerate(webs):
        d.edge(agw, w, exit=(1, 0.5), entry=(0.5, 0),
               waypoints=[(rx, lane_agw), (web_cx[i], lane_agw)])
    # web -> internal LB: out the web bottom, converge on the LB top
    for i, w in enumerate(webs):
        d.edge(w, ilb, exit=(0.5, 1), entry=(0.5, 0),
               waypoints=[(web_cx[i], lane_w2i), (ilb_cx, lane_w2i)])
    # internal LB -> app tier: leave from the SIDE (in arrives on top), into a
    # lane above the app row, then drop into each app's top.
    for i, a in enumerate(apps):
        d.edge(ilb, a, "load balanced across AZs" if i == n // 2 else "",
               exit=(1, 0.5), entry=(0.5, 0),
               waypoints=[(rx, lane_i2a), (web_cx[i], lane_i2a)])
    # synchronous data replication between adjacent AZ databases
    for i in range(n - 1):
        d.edge(dbs[i], dbs[i + 1], "sync", dashed=True, color="#6C8EBF",
               exit=(1, 0.5), entry=(0, 0.5))
    return {"front": agw, "ilb": ilb, "webs": webs, "apps": apps,
            "dbs": dbs, "w": region_w, "h": region_h}


def s07_3az():
    d = Diagram("07-active-3az")
    d.text(0, 0, 900, 30,
           "Scenario 7 - Active across 3 Availability Zones (1 region)",
           size=16, bold=True)
    tm = dns(d, 330, 60)
    r = az_region(d, 120, "Region 1  (3 AZ Active/Active/Active)", ACTIVE)
    d.edge(tm, r["front"], "traffic")
    d.legend(120 + r["w"] + 40, 160)
    d.save("07-active-3az.drawio")


def s08_3azdr():
    d = Diagram("08-active-3az-dr")
    d.text(0, 0, 1200, 30,
           "Scenario 8 - 3 AZ Active + DR (second region)", size=16, bold=True)
    r = az_region(d, 100, "Region 1  (3 AZ Active)", ACTIVE)
    drx = 100 + r["w"] + 80
    dr = az_region(d, drx, "Region 2  (DR - 3 AZ Active/Active/Active)",
                   ACTIVE, region_fill=DR)
    tm = dns(d, (drx + dr["w"]) // 2 - 24, 60)
    d.edge(tm, r["front"], "traffic")
    d.edge(tm, dr["front"], "DR failover", dashed=True, color="#888888")
    # async replication region1 -> DR
    d.edge(r["dbs"][2], dr["dbs"][0], "async replication",
           dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.legend(100, 130 + r["h"] + 20)
    d.save("08-active-3az-dr.drawio")


def s09_reads():
    d = Diagram("09-global-read-replicas")
    d.text(0, 0, 1200, 30,
           "Scenario 9 - Single-writer, global read replicas "
           "(write-global / read-local)", size=16, bold=True)
    tm = dns(d, 490, 50, label="Global DNS (geo-routing)")
    d.box(150, 130, 250, 410, "Region 1  (Primary - reads + writes)", ACTIVE)
    a = d.stack(200, 165)
    d.box(620, 130, 250, 410, "Region 2  (Read replica - reads only)", ACTIVE)
    b = d.stack(670, 165, tag=" (replica)")
    d.edge(tm, a["lb"], "read + write traffic", color="#82B366")
    d.edge(tm, b["lb"], "read-only traffic", color="#82B366")
    # one-way (single-writer) async replication: primary -> replica
    d.edge(a["db"], b["db"], "one-way async replication (primary -> replica)",
           dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.text(150, 560, 720, 40,
           "Writes always go to the Region 1 primary; a region-1 loss means<br>"
           "promoting a replica (RPO = replication lag). Single writer - "
           "no write conflicts.", size=10)
    d.legend(950, 130)
    d.save("09-global-read-replicas.drawio")


def s10_multi():
    d = Diagram("10-multi-region-active")
    d.text(0, 0, 1400, 30,
           "Scenario 10 - Multi-region Active/Active (3 AZ per region)",
           size=16, bold=True)
    tm = dns(d, 620, 60)
    r1 = az_region(d, 80, "Region 1  (3 AZ Active)", ACTIVE)
    x2 = 80 + r1["w"] + 80
    r2 = az_region(d, x2, "Region 2  (3 AZ Active)", ACTIVE)
    d.edge(tm, r1["front"], "traffic", color="#82B366")
    d.edge(tm, r2["front"], "traffic", color="#82B366")
    # bidirectional cross-region async replication between the two data tiers
    d.edge(r1["dbs"][2], r2["dbs"][0],
           "bidirectional async replication", dashed=True, color="#D79B00",
           exit=(1, 0.5), entry=(0, 0.5))
    d.legend(80, 130 + r1["h"] + 20)
    d.save("10-multi-region-active.drawio")


def s11_3azdraws():
    d = Diagram("11-active-3az-dr-aws")
    d.text(0, 0, 1300, 30,
           "Scenario 11 - Azure 3 AZ Active + DR in AWS (cross-cloud)",
           size=16, bold=True)
    r = az_region(d, 100, "Azure Region  (3 AZ Active)", ACTIVE, theme=THEME_AZURE)
    drx = 100 + r["w"] + 80
    dr = az_region(d, drx, "AWS Region  (DR - 3 AZ Active/Active/Active)",
                   ACTIVE, theme=THEME_AWS, region_fill=DR)
    tm = dns(d, (drx + dr["w"]) // 2 - 24, 60, theme=THEME_AZURE)
    d.edge(tm, r["front"], "traffic")
    d.edge(tm, dr["front"], "DR failover", dashed=True, color="#888888")
    d.edge(r["dbs"][2], dr["dbs"][0], "cross-cloud async replication",
           dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.legend(100, 130 + r["h"] + 20)
    d.save("11-active-3az-dr-aws.drawio")


def s12_aaaws():
    d = Diagram("12-active-active-azure-aws")
    d.text(0, 0, 1400, 30,
           "Scenario 12 - Active/Active across Azure + AWS (3 AZ each)",
           size=16, bold=True)
    tm = dns(d, 620, 60, theme=THEME_AZURE,
             label="Global DNS (Traffic Manager / Route 53)")
    r1 = az_region(d, 80, "Azure Region  (3 AZ Active)", ACTIVE, theme=THEME_AZURE)
    x2 = 80 + r1["w"] + 80
    r2 = az_region(d, x2, "AWS Region  (3 AZ Active)", ACTIVE, theme=THEME_AWS)
    d.edge(tm, r1["front"], "traffic", color="#82B366")
    d.edge(tm, r2["front"], "traffic", color="#82B366")
    d.edge(r1["dbs"][2], r2["dbs"][0],
           "bidirectional async replication (cross-cloud)",
           dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.legend(80, 130 + r1["h"] + 20)
    d.save("12-active-active-azure-aws.drawio")


def s13_multicloud():
    d = Diagram("13-multicloud-active-active")
    d.text(0, 0, 1600, 30,
           "Scenario 13 - Multi-cloud, multi-region Active/Active "
           "(Azure + AWS, everything active)", size=16, bold=True)
    specs = [
        ("Azure Region 1  (3 AZ Active)", THEME_AZURE),
        ("Azure Region 2  (3 AZ Active)", THEME_AZURE),
        ("AWS Region 1  (3 AZ Active)", THEME_AWS),
        ("AWS Region 2  (3 AZ Active)", THEME_AWS),
    ]
    x = 80
    regions = []
    for label, theme in specs:
        r = az_region(d, x, label, ACTIVE, theme=theme)
        regions.append(r)
        x += r["w"] + 50
    total_w = x
    tm = dns(d, total_w // 2 - 24, 60, theme=THEME_AZURE,
             label="Global DNS / Traffic Director")
    for r in regions:
        d.edge(tm, r["front"], "traffic", color="#82B366")
    # global active/active data replication (chained across all regions/clouds)
    for i in range(len(regions) - 1):
        lbl = "global async replication (active/active)" if i == 0 else ""
        d.edge(regions[i]["dbs"][2], regions[i + 1]["dbs"][0], lbl,
               dashed=True, color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.legend(80, 130 + regions[0]["h"] + 20)
    d.save("13-multicloud-active-active.drawio")


def s14_cell():
    d = Diagram("14-cell-based")
    d.text(0, 0, 1300, 30,
           "Scenario 14 - Cell-based / shuffle-sharded (blast-radius isolation)",
           size=16, bold=True)
    tm = dns(d, 500, 40, label="Global DNS")
    router = d.pnode(360, 130,
                     "Cell router / partition layer<br>"
                     "(shuffle sharding: each tenant pinned to a fixed cell)",
                     w=320, h=60, fill="#E1D5E7", stroke="#9673A6")
    d.edge(tm, router)
    n = 4
    cell_w, pitch, y0 = 180, 210, 260
    lane = y0 - 20
    for i in range(n):
        cx0 = 90 + i * pitch
        failed = (i == 2)
        fill = PASSIVE if failed else ACTIVE
        lbl = f"Cell {i + 1}" + ("  (failed)" if failed else "")
        d.box(cx0, y0, cell_w, 380, lbl, fill)
        st = d.stack(cx0 + 15, y0 + 40, tag=f" C{i + 1}")
        lb_cx = cx0 + 15 + 51 + 24
        d.edge(router, st["lb"], exit=(0.5, 1), entry=(0.5, 0),
               waypoints=[(520, lane), (lb_cx, lane)])
    d.text(90, y0 + 400, 840, 40,
           "Each cell is an independent full stack serving a slice of tenants.<br>"
           "A cell failure (or poison-pill request) is contained to that cell's "
           "tenants - it cannot take down the whole service.", size=10)
    d.legend(90 + n * pitch + 20, y0)
    d.save("14-cell-based.drawio")


def flowchart():
    """Decision tree for choosing one of the topologies above."""
    d = Diagram("15-decision-flowchart")
    d.text(0, 0, 1900, 30,
           "Choosing a 3-tier resilience topology - decision flow",
           size=16, bold=True)

    def X(depth):
        return 50 + depth * 270

    # SLO heat colours for outcomes (least -> most resilient)
    RED, ORANGE, YEL, GRN = "#F8CECC", "#FFE6CC", "#FFF2CC", "#D5E8D4"
    RS, OS, YS, GS = "#B85450", "#D79B00", "#D6B656", "#82B366"

    # --- decision nodes ---
    start = d.pnode(X(0), 360, "Start", w=150, h=50, fill="#E1D5E7",
                    stroke="#9673A6", arc=40)
    q1 = d.diamond(X(1), 350, "Survive an entire<br>cloud-provider outage?")
    q5 = d.diamond(X(2), 150, "Survive a full<br>region outage?")
    q2 = d.diamond(X(2), 620, "Need continuous service,<br>"
                              "no failover (active/active)?")
    q9 = d.diamond(X(3), 60, "Need automatic recovery<br>"
                             "from instance / zone failure?")
    q6 = d.diamond(X(3), 300, "Need zero-downtime regional<br>"
                              "failover (active/active)?")
    q3 = d.diamond(X(3), 760, "More than one<br>region per cloud?")
    q10 = d.diamond(X(4), 110, "Spread compute across<br>multiple AZs?")
    qw = d.diamond(X(4), 290, "Need multi-region writes<br>(multi-master)?")
    q7 = d.diamond(X(4), 460, "Is the primary already<br>3-AZ active?")
    q8 = d.diamond(X(5), 460, "Need automatic local<br>HA (no data loss) too?")
    qdr = d.diamond(X(6), 460, "How fast must regional<br>recovery be?")
    qcell = d.diamond(X(4), 870, "Also need per-tenant<br>"
                                 "blast-radius isolation?")

    # --- outcome nodes (SLO heat-coloured) ---
    o1 = d.pnode(X(4), 20, "1 · Active<br>SLO ~99.9%", fill=RED, stroke=RS)
    o7 = d.pnode(X(5), 40, "7 · 3-AZ Active<br>SLO ~99.99%", fill=YEL, stroke=YS)
    o5 = d.pnode(X(5), 160, "5 · Active + Passive<br>SLO ~99.95%",
                 fill=ORANGE, stroke=OS)
    o10 = d.pnode(X(5), 250, "10 · Multi-region A/A<br>SLO ~99.99–99.999%",
                  fill=GRN, stroke=GS)
    o9 = d.pnode(X(5), 355, "9 · Global read replicas<br>SLO ~99.99% (reads)",
                 fill=YEL, stroke=YS)
    o8 = d.pnode(X(5), 560, "8 · 3-AZ + DR region<br>SLO ~99.99%",
                 fill=YEL, stroke=YS)
    o6 = d.pnode(X(6), 330, "6 · Active + Passive + DR<br>SLO ~99.95%",
                 fill=ORANGE, stroke=OS)
    o2 = d.pnode(X(7), 360, "2 · Pilot Light<br>SLO ~99.9%", fill=RED, stroke=RS)
    o3 = d.pnode(X(7), 450, "3 · Warm Standby<br>SLO ~99.9%",
                 fill=RED, stroke=RS)
    o4 = d.pnode(X(7), 540, "4 · Hot Standby (auto)<br>SLO ~99.95%",
                 fill=ORANGE, stroke=OS)
    o11 = d.pnode(X(4), 620, "11 · 3-AZ + DR in AWS<br>SLO ~99.99%",
                  fill=YEL, stroke=YS)
    o12 = d.pnode(X(4), 760, "12 · Azure + AWS A/A<br>SLO ~99.999%",
                  fill=GRN, stroke=GS)
    o13 = d.pnode(X(5), 810, "13 · Multi-cloud A/A<br>SLO ~99.999%+",
                  fill=GRN, stroke=GS)
    o14 = d.pnode(X(5), 915, "14 · Cell-based<br>SLO ~99.999%+ (isolated)",
                  fill=GRN, stroke=GS)

    YES, NO = "#82B366", "#999999"
    d.edge(start, q1)
    d.edge(q1, q5, "No", color=NO)
    d.edge(q1, q2, "Yes", color=YES)
    d.edge(q5, q9, "No", color=NO)
    d.edge(q5, q6, "Yes", color=YES)
    d.edge(q9, o1, "No", color=NO)
    d.edge(q9, q10, "Yes", color=YES)
    d.edge(q10, o7, "Yes", color=YES)
    d.edge(q10, o5, "No", color=NO)
    d.edge(q6, qw, "Yes", color=YES)
    d.edge(q6, q7, "No", color=NO)
    d.edge(qw, o10, "Yes", color=YES)
    d.edge(qw, o9, "No", color=NO)
    d.edge(q7, o8, "Yes", color=YES)
    d.edge(q7, q8, "No", color=NO)
    d.edge(q8, o6, "Yes", color=YES)
    d.edge(q8, qdr, "No", color=NO)
    d.edge(qdr, o2, "Slow / cheap", color=NO)
    d.edge(qdr, o3, "Warm", color=NO)
    d.edge(qdr, o4, "Auto / fast", color=YES)
    d.edge(q2, o11, "No", color=NO)
    d.edge(q2, q3, "Yes", color=YES)
    d.edge(q3, o12, "No", color=NO)
    d.edge(q3, qcell, "Yes", color=YES)
    d.edge(qcell, o13, "No", color=NO)
    d.edge(qcell, o14, "Yes", color=YES)
    d.save("15-decision-flowchart.drawio")


if __name__ == "__main__":
    for fn in (s01_active, s02_pilot, s03_warm, s04_hot, s05_ap, s06_apdr,
               s07_3az, s08_3azdr, s09_reads, s10_multi, s11_3azdraws,
               s12_aaaws, s13_multicloud, s14_cell, flowchart):
        fn()
    print("done")
