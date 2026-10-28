"""Collect existing evidence without granting incomplete scopes pass credit."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path

W = Path(__file__).resolve().parents[1]
R = W.parents[1]


def read(name):
    return json.loads((W / name).read_text())


def optional(name):
    return read(name) if (W / name).exists() else None


def sha(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


base = read("base/geometry.json")
verify = read("base/verification.json")
tile = read("integrated/geometry.json")
full = read("timing/full-readout/results.json")
timing = read("timing/joined-bank0-v2/results.json")
periphery = read("periphery/results.json")
w2path = R / "overnight-20261014/fabric-k64/results.json"
w2bytes = w2path.read_bytes()
w2 = json.loads(w2bytes)["variants"]["array_port"]
snapshot = {
    "source": str(w2path.relative_to(R)),
    "source_sha256": hashlib.sha256(w2bytes).hexdigest(),
    "last_completed_step": w2.get("last_completed_step"),
    "routed_area_mm2": w2.get("routed_area_mm2"),
    "synthesis": w2.get("synthesis"),
    "floorplan": w2.get("floorplan"),
    "qualification": "Snapshot only; W2b continues independently. Placed footprint is not routed closure.",
}
blocks = {}
for name, block in periphery["blocks"].items():
    sta = block["extracted_sta"]
    blocks[name] = {
        k: block[k] for k in (
            "dimensions_um", "outline_area_um2", "cell_area_excluding_fill_um2",
            "magic_drc_markers", "netgen_lvs_errors", "sta_load_ff",
        )
    }
    blocks[name].update({
        "klayout_drc_markers": block["klayout"]["markers"],
        "worst_setup_slack_ns": min(c["setup_slack_ns"] for c in sta.values()),
        "worst_slew_violations": max(c["max_slew_violations"] for c in sta.values()),
        "worst_capacitance_violations": max(c["max_cap_violations"] for c in sta.values()),
        "integrated_with_full_macro": False,
    })
cases = [
    {k: c[k] for k in (
        "corner", "voltage_v", "temperature_c", "period_ns", "checked_bits",
        "maximum_sampled_settled_time_ns_after_evaluate",
        "mean_net_source_energy_pj_per_32_lane_row_read",
        "maximum_net_source_energy_pj_per_32_lane_row_read",
        "raw_70_30_failures", "restored_90_10_failures",
    )}
    for c in timing["cases"]
]
decoded = optional("timing/decoded-tile/results.json")
latch = optional("periphery/latch-results.json")
if decoded:
    decoded = {"source_directory": "timing/decoded-tile", "gds": "v1/decoded-tile.gds", **decoded}
if latch:
    latch = {"source_directory": "periphery", **latch}
result = {
    "schema_version": 1,
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "partial_physical_evidence_complete_macro_not_qualified",
    "complete_macro": False,
    "approved_projection": "encoder block0 FF project_out; K64;1280x320",
    "selections": 409600,
    "index_bits": 1638400,
    "architecture": "mask-programmed stored-index readable cells;4 access NMOS per four-bit selection",
    "identity": read("identity.json"),
    "area_um2_per_selection": {
        "cell_only_measured": base["cell_only_um2_per_selection"],
        "array_plus_analog_readout_tile_partial": tile["partial_um2_per_selection"],
        "full20_partial_readout_assembly_with_gaps": full["geometry"]["bounding_area_um2_per_selection"],
        "decoded_array_readout_local_decoders_tile_partial": decoded["area_um2_per_selection_including_present_periphery"] if decoded else None,
        "complete_macro_including_all_periphery": None,
        "qualification": "Different measured scopes; do not add or substitute partial values for complete-macro cost.",
    },
    "cell_array": {
        "tile_dimensions_um": base["tile_dimensions_um"],
        "tile_area_um2": base["tile_area_um2"],
        "sum20_tile_area_um2": base["sum_tile_area_um2"],
        "assembly_dimensions_um": base["composition_dimensions_um"],
        "assembly_area_um2": base["composition_area_um2"],
        "gds": "base/array-core.gds",
        "tile_gds": "base/tile0.gds",
        "layout_bit_readback": base["layout_to_bits"],
        "verification": verify,
        "composition_top_level_lvs": None,
        "composition_audit": "base/composition-audit.json",
        "exclusions": base["exclusions"],
    },
    "array_plus_readout_tile": {
        "geometry": tile,
        "gds": "integrated/readout-tile0.gds",
        "drc": read("integrated/drc-result.json"),
        "lvs": read("integrated/lvs-result.json"),
        "lef": "integrated/readout-tile0.lef",
        "lef_audit": read("integrated/lef-audit.json"),
    },
    "full20_partial_readout_assembly": {
        "gds": "timing/full-readout/partial-full-readout.gds",
        "gds_sha256": full["geometry"]["gds_sha256"],
        "dimensions_um": full["geometry"]["dimensions_um"],
        "area_um2": full["geometry"]["bounding_area_um2"],
        "drc": full["drc"],
        "layout_bit_readback": full["gds_mask_readback"],
        "top_level_lvs": None,
        "lef": None,
        "exclusions": full["geometry"]["exclusions"] + ["No physical raw-index output latches"],
    },
    "decoded_tile_experiment": decoded,
    "decoded_tile_pending_evidence": None if decoded else {
        "geometry": optional("timing/decoded-tile/v1/geometry.json"),
        "drc": optional("timing/decoded-tile/v1/decoded-tile-checks.json"),
        "bit_readback": optional("timing/decoded-tile/v1/readback.json"),
        "qualification": "Await final results; no LVS pass inferred from DRC/readback.",
    },
    "digital_periphery_components": blocks,
    "periphery_component_ledger": periphery["planned200subbank_ledger"],
    "output_latch_component": latch,
    "joined32_lane_bank_timing_energy": {
        "results": "timing/joined-bank0-v2/results.json",
        "cases": cases,
        "limitations": timing["limitations"],
        "worst_case_full_tile_proven": False,
    },
    "schedule": {
        "actual_index_reads_per_projection": 1280,
        "integer_cycles": 4160,
        "fp32_cycles": 4163,
        "target_clock_period_ns": 20,
        "target_only_integer_duration_us": 83.2,
        "target_only_fp32_duration_us": 83.26,
        "qualified_complete_macro_row_read_time_ns": None,
        "qualified_complete_macro_energy_pj_per_row": None,
        "achieved_projection_duration_us": None,
        "real_time_schedule_proven": False,
    },
    "integration": {
        "document": "INTEGRATION.md",
        "w2b_snapshot": snapshot,
        "area_formula": "W2b ARRAY-PORT routed footprint + complete macro footprint + external routing allowance",
        "complete_macro_area_mm2": None,
        "routing_allowance_mm2": None,
        "complete_projection_area_mm2": None,
        "stretch_macro_placement": "not run; complete qualified macro/Liberty absent",
        "optional_lead_cloud_monolithic_lvs_commands": "CLOUD-REQUEST.md",
    },
    "verification_scope": "Selected GF180 FEOL+BEOL+connectivity+offgrid DRC; density/antenna excluded; open-flow evidence, not foundry signoff",
    "unresolved": [
        "Physical precharge/evaluate/latch phases, reset/abort behavior and minimum enable setup",
        "Global20-bank output mux/latch wiring and power distribution",
        "Complete composition independent LVS and full-macro LEF/Liberty",
        "Distributed RC/address-to-W2b-representative timing; decoder/mux isolated STA failures",
        "Worst-case full-tile PVT read energy and whole-projection timing/power",
    ],
    "failure_records": [
        "base/failed-v1/", "base/tile0-netgen.log", "base/tile0-netgen-ports.log",
        "integrated/failed-v1/", "integrated/failed-v2/",
        "integrated/geometry-before-latch-audit.json", "periphery/LATCH-ERRATUM.md",
        "periphery/pre-review-latch-erratum/", "timing/COMMANDS.md",
        "periphery/RESULTS.md",
        "timing/decoded-tile/v1/netgen.log (bounded incomplete monolithic comparison)",
    ],
    "resource_scope": {
        "writes": "overnight-20261014/taalas-array/ only",
        "cloud_used": False, "git_used": False,
        "minimum_required_free_gib": 22,
        "observed_free_gib_at_report": shutil.disk_usage(W).free / 2**30,
    },
    "commands": "COMMANDS.md",
}
(W / "results.json").write_text(json.dumps(result, indent=2) + "\n")
assert result["identity"]["pass"]
assert result["cell_array"]["layout_bit_readback"]["mismatches"] == 0
assert result["full20_partial_readout_assembly"]["layout_bit_readback"]["mismatches"] == 0
assert result["integration"]["complete_projection_area_mm2"] is None
assert result["schedule"]["qualified_complete_macro_row_read_time_ns"] is None
print("W5-STATUS: handoff evidence collected; complete macro remains unqualified")
