"""Restore sl5-hotspots.json zone->title->body pairing and PNG-derived coords."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "content/esr-class/esr/main/sl5-hotspots.json"
COORDS_PATH = ROOT / "private/sl5-hotspot-png-coords.json"

# Zones chart (img-slide-5-zones-chart.png) — confirmed when modals were correct.
ZONE_TITLES: dict[str, str] = {
    "01": "REPORT FILTERS",
    "02": "DATE/TIME OF REPORT",
    "03": "MODEL",
    "04": "ADMIN NO.",
    "05": "SERIAL NO.",
    "06": "OPST",
    "07": "EQ DESCRIPTION",
    "08": "DL ST DATE/TIME",
    "09": "DAYS DL",
    "10": "UIC",
    "11": "UIC DESCRIPTION",
    "12": "REPORTABLE DL EQ",
    "13": "ORDER NO.",
    "14": "DESCRIPTION",
    "15": "SC-DATE",
    "16": "STAT",
    "17": "PRT-ORD-DT",
    "18": "NIIN",
    "19": "DESCRIPTION",
    "20": "ERC",
    "21": "SC",
    "22": "WO WORK CENTER",
    "23": "Q-ORD",
    "24": "Q-ISS",
    "25": "SOS",
    "26": "REF DOC",
    "27": "ST",
    "28": "DATE/TIME",
    "29": "Q-OH",
    "30": "Q-NL",
}

DESCRIPTION_WORK_ORDER = (
    "On the work order line, description states the fault or repair requirement "
    "driving the maintenance action. Leaders use it to understand the operational "
    "problem behind the status and to judge urgency and resource needs."
)

DESCRIPTION_PARTS = (
    "On the parts line, description identifies the material or part associated "
    "with the requirement. It helps confirm the correct item is on order or "
    "issued and supports conversations with supply about pacing parts."
)

ZONE_BODIES: dict[str, str] = {
    "01": (
        "The report filters at the top of the ESR define which equipment and status "
        "categories are included when the report is run, such as operational status "
        "and technical status selections. Leaders should confirm these filters match "
        "the readiness picture they intend to review so deadlined or critical items "
        "are not accidentally excluded from the output."
    ),
    "02": (
        "This field shows when the ESR was generated in GCSS-Army. Leaders should use "
        "it to confirm they are looking at current data before prioritizing maintenance "
        "actions, comparing entries across units, or briefing command on equipment status."
    ),
    "03": (
        "The model field identifies the equipment model for the deadlined item. It helps "
        "distinguish similar administrative numbers and supports correct technical "
        "references, parts identification, and maintenance planning."
    ),
    "04": (
        "The administrative number is the unit's identifier for a specific piece of "
        "equipment in the motor pool or property book. Match this number to the physical "
        "item and to work orders when driving maintenance follow-up."
    ),
    "05": (
        "The serial number uniquely identifies the individual item of equipment. Use it "
        "when multiple similar models exist in the unit and when coordinating with "
        "maintenance, supply, or higher headquarters on a specific asset."
    ),
    "06": (
        "Operational status shows the equipment's mission capability condition, such as "
        "NMCS or NMCM. It tells leaders whether the primary delay is maintenance "
        "execution, parts, or another factor driving non-mission-ready status."
    ),
    "07": (
        "Equipment description provides the plain-language name of the item on the ESR "
        "line. It helps non-technical leaders and staff quickly understand what type of "
        "asset is deadlined without interpreting model numbers alone."
    ),
    "08": (
        "Deadline start date and time indicate when the equipment entered its current "
        "deadlined status for this entry. Compare it with other dates on the line to see "
        "how long the item has been in its present condition and whether status has "
        "recently changed."
    ),
    "09": (
        "Days deadlined quantifies how long the equipment has been in a deadlined status "
        "on this entry. It is a primary field for leader prioritization because long "
        "durations often signal stalled maintenance, parts, or follow-up problems."
    ),
    "10": (
        "The Unit Identification Code identifies which organization owns or is responsible "
        "for the equipment line on the report. Use it to route follow-up to the correct "
        "unit and to align ESR entries with property accountability and maintenance "
        "responsibility."
    ),
    "11": (
        "This is the text description of the owning UIC shown on the ESR line. It helps "
        "leaders quickly recognize the unit name associated with the code, which is "
        "useful when briefing across formations or validating that the correct unit's "
        "equipment is under review."
    ),
    "12": (
        "This value reports how many reportable deadlined equipment items are associated "
        "with the UIC on that section of the ESR. It gives leaders a quick count of how "
        "much deadlined equipment the unit is carrying for the filtered report."
    ),
    "13": (
        "Order number identifies the maintenance work order or notification tied to the "
        "repair. Use it with maintenance control, the shop, and supply to track actions, "
        "updates, and accountability for returning the equipment to mission-ready status."
    ),
    "14": DESCRIPTION_WORK_ORDER,
    "15": (
        "Status change date shows when the work order or line last changed system "
        "condition. Leaders compare SC-DATE with other dates to see whether the repair "
        "is progressing or stagnating in a given stage."
    ),
    "16": (
        "The status field captures the current condition narrative or status text for the "
        "work order or requirement line. It supplements coded fields and helps explain "
        "what the system shows is happening with the repair or part."
    ),
    "17": (
        "Part order date indicates when the part requirement was ordered or entered into "
        "the supply process. Use it with quantity and status fields to judge whether "
        "parts delay is driving readiness risk."
    ),
    "18": (
        "National Item Identification Number uniquely identifies the part or material in "
        "the supply system. It is the key reference for ordering, tracking, and "
        "discussing requisitions and issues with supply personnel."
    ),
    "19": DESCRIPTION_PARTS,
    "20": (
        "Equipment Readiness Code classifies the readiness or priority category associated "
        "with the equipment or requirement on the line. Leaders use it with operational "
        "status to understand how the system is classifying repair priority."
    ),
    "21": (
        "System condition code shows the work order's stage in the maintenance workflow, "
        "such as awaiting parts or in shop. Read SC together with SC-DATE and WO WORK "
        "CENTER to know where to apply leader pressure."
    ),
    "22": (
        "Work order work center identifies the maintenance activity or shop responsible "
        "for the repair action. It tells leaders which maintenance organization owns "
        "execution on the work order."
    ),
    "23": (
        "Quantity ordered shows how much of the material was requested for the work order. "
        "Compare it to issued and on-hand quantities to see whether supply action matches "
        "the maintenance need."
    ),
    "24": (
        "Quantity issued shows how much material has been issued against the requirement. "
        "A mismatch between ordered and issued quantities often explains why a repair "
        "cannot move forward."
    ),
    "25": (
        "Source of supply identifies which supply source or system is fulfilling the "
        "material requirement. It supports follow-up with the correct supply activity when "
        "parts are the limiting factor."
    ),
    "26": (
        "Reference document ties the requirement to a purchase order, delivery document, "
        "or other supply reference. Values such as a document number—or text like PR "
        "REJECTED—show whether supply action is moving or blocked."
    ),
    "27": (
        "Status on the parts line shows where the requisition or issue stands in the supply "
        "process. Leaders use ST with DATE/TIME to see how long a requirement has remained "
        "in its current supply state."
    ),
    "28": (
        "On the parts or status line, date and time show when the current supply or status "
        "condition was recorded. Use it to detect aging requisitions and to time follow-up "
        "with supply agencies."
    ),
    "29": (
        "Quantity on hand shows stock available in the supporting supply context for that "
        "requirement. It helps leaders see whether the part is already available locally "
        "even if the work order is still waiting."
    ),
    "30": (
        "Quantity at next level indicates material positioned or expected at the next supply "
        "echelon. Use it when local on-hand is zero but higher-level supply may still "
        "support the repair."
    ),
}


def main() -> None:
    coords = {c["zone"]: c for c in json.loads(COORDS_PATH.read_text(encoding="utf-8"))}
    zones = []
    for zid in sorted(ZONE_TITLES.keys(), key=lambda k: int(k)):
        if zid not in coords:
            raise SystemExit(f"Missing PNG coords for zone {zid}")
        c = coords[zid]
        zones.append(
            {
                "title": ZONE_TITLES[zid],
                "zone": zid,
                "x": c["x"],
                "y": c["y"],
                "w": c["w"],
                "h": c["h"],
                "body": ZONE_BODIES[zid],
            }
        )

    JSON_PATH.write_text(json.dumps(zones, indent=2) + "\n", encoding="utf-8")
    print(f"Restored {len(zones)} zone modal pairs in {JSON_PATH.name}")


if __name__ == "__main__":
    main()
