# Plan: 3-Tier Architecture draw.io Diagrams

## Goal
Produce **7 draw.io diagrams** illustrating a standard 3-tier web application
under increasing levels of high-availability (HA) and disaster-recovery (DR)
topology. One `.drawio` file per scenario, plus an optional exported PNG/SVG.

## The 7 scenarios
| # | File | Topology | Meaning |
|---|------|----------|---------|
| 1 | `01-active.drawio`                  | Active                                   | Single site, one full stack. Baseline, no redundancy. |
| 2 | `02-active-dr.drawio`               | Active + DR                              | Primary site + DR site in a **second region** (async replication, manual/scripted failover). |
| 3 | `03-active-passive.drawio`          | Active + Passive                         | Two stacks, one live one on standby; automatic failover (same region). |
| 4 | `04-active-passive-dr.drawio`       | Active + Passive + DR                    | Local active/passive HA pair **plus** a DR region. |
| 5 | `05-active-3az.drawio`              | Active(az)×3                             | Single region, 3 Availability Zones, all active (active/active/active). |
| 6 | `06-active-3az-dr.drawio`           | Active(az)×3 + DR region (3 AZ active)   | 3-AZ active/active in region 1 + a DR region 2 that is itself 3-AZ active/active/active. |
| 7 | `07-multi-region-active.drawio`     | Active(az)×3 (region1) + Active(az)×3 (region2) | Full multi-region active/active; 3 active AZs in each of two regions, global traffic distribution. |
| 6.5 | `06b-active-3az-dr-aws.drawio`     | Azure 3 AZ Active + DR in **AWS** (3 AZ active) | 3-AZ active/active in Azure; cross-cloud DR region in AWS, itself 3-AZ active/active/active (async replication). |
| 7.5 | `07b-active-active-azure-aws.drawio` | Azure 3 AZ Active + AWS 3 AZ Active    | Active/active **across clouds**: 3 AZ active in Azure and 3 AZ active in AWS, global DNS distribution, bidirectional replication. |
| 8 | `08-multicloud-active-active.drawio` | Azure ×2 regions + AWS ×2 regions, all active | Multi-cloud, multi-region — two active regions in each of Azure and AWS, everything active, global DNS + global async replication. |

## The 3 tiers (common building block)
Every diagram reuses the same stack, with **a load balancer in front of each
compute tier**:

1. **Web / Presentation tier** — public load balancer (App Gateway / ALB) + web servers
2. **Application / Logic tier** — internal load balancer (Azure LB / NLB) + app servers
3. **Data tier** — database (primary/replica as topology dictates)

Flow: `Front LB → Web → Internal LB → App → DB`. In the multi-AZ scenarios the
**internal load balancer is zone-redundant and distributes the app tier across
all AZs** (and the front LB spreads web traffic across AZs likewise).

Fronting element above the stack: **DNS / Global Load Balancer** (Traffic
Manager / Route 53) — used to direct traffic between sites/regions/clouds in
scenarios 2, 4, 6, 6.5, 7, 7.5, 8.

## Visual conventions
- **Color coding**
  - Active stack: blue/green fill
  - Passive / standby stack: grey fill, dashed border
  - DR stack: amber/orange fill, dashed border
- **Containers**: dashed rounded rectangle per Region; nested dashed rectangle
  per Availability Zone.
- **Replication arrows**: dashed arrow labeled `async replication` (DR) or
  `sync replication` (local HA); solid arrows for live traffic.
- **Legend** box (bottom-left of each diagram) explaining colors/line styles.
- Consistent canvas: tiers laid out top→bottom, regions/AZs laid out
  left→right.

## Approach / tooling
draw.io files are XML (`mxGraphModel`). Two build options:

- **Option A (recommended): hand-author the XML** for one reusable
  "tier stack" group, then compose/duplicate it per scenario via a small
  Python/Node generator script (`generate.py`) that stamps the stack into
  regions/AZs and wires the replication links. Guarantees visual consistency
  and makes scenarios 5–7 (lots of repeated stacks) cheap.
- **Option B: author each `.drawio` by hand** in XML. Simpler for #1–4,
  tedious and error-prone for #5–7.

Recommendation: **Option A** — write `lib/stack.xml` template + `generate.py`.

## Deliverables & layout
```
Diagrams/
  plan.md
  failover-methods-and-slo.md   # write-up: failover methods + SLO/RTO/RPO per diagram
  generate.py                   # composes all diagrams (architectures + flowchart)
  out/
    01-active.drawio ... 08-multicloud-active-active.drawio
    09-decision-flowchart.drawio  # topology-selection decision tree
  out/png/                      # exported PNGs (drawio CLI, 2x scale)
```

## Build steps
1. Define the reusable 3-tier stack fragment (DNS optional, LB → web → app → DB).
2. Write `generate.py`: helpers to place a stack at an (x,y) offset, wrap stacks
   in Region/AZ containers, draw traffic + replication arrows, add legend.
3. Generate scenarios in order of complexity (1 → 7), reusing the stack:
   - 1: single stack.
   - 2: two stacks in two Region containers + DNS + async-replication arrow.
   - 3: two stacks (active solid, passive dashed/grey) + sync replication + failover note.
   - 4: scenario 3 stack pair + a third DR stack in a second region.
   - 5: one Region container with 3 AZ containers, each a full stack; LB spans AZs; DB sync replication between AZs.
   - 6: scenario 5 + a DR Region container with its own stack + cross-region async replication.
   - 7: two Region containers, each = scenario 5 (3 active AZs); global LB on top; cross-region active/active data replication.
4. Validate each file opens in draw.io / VS Code Draw.io extension.
5. (Optional) Export PNG/SVG via the draw.io desktop CLI:
   `drawio --export --format png --output out/png out/*.drawio`.

## Decisions (confirmed)
- **Icons:** Azure stencils (draw.io `azure2` image library — Traffic Manager,
  Application Gateway, Virtual Machine, SQL Database).
- **Packaging:** 7 separate `.drawio` files.
- **Build:** generate now via `generate.py`.

## Cloud mapping
| Generic tier | Azure (image stencils) | AWS (mxgraph.aws4 stencils) |
|--------------|------------------------|-----------------------------|
| DNS / Global LB | Traffic Manager | Route 53 |
| Web-tier LB | Application Gateway | Application Load Balancer |
| App-tier (internal) LB | Azure Load Balancer | Network Load Balancer |
| Web / App servers | Virtual Machine | EC2 |
| Data tier | Azure SQL Database | RDS |
| Region / AZ | dashed container box (colored by role) | dashed container box |

Azure shapes use the bundled `img/lib/azure2/...` SVG images; AWS shapes use the
bundled `mxgraph.aws4.resourceIcon` stencils. Cross-cloud scenarios (6.5, 7.5,
8) mix both themes in one diagram.
