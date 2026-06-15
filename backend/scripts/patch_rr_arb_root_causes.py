"""Patch expected_root_cause for all 50 RR_ARB cases to precise, RTL-accurate descriptions."""
import json
from pathlib import Path

CASES_DIR = Path(__file__).parents[1] / "mock_cases" / "round_robin"

# Precise expected_root_cause: matches what an agent reading the buggy RTL would say.
# Judge scores 1.0 when the prediction semantically matches; 0.5 for partial; 0.0 for wrong.
ROOT_CAUSES = {
    "RR_ARB_001": "The priority pointer (last_gnt) resets to zero whenever all requests go idle instead of preserving the last winner, causing the arbiter to always restart from master 0 after any idle period.",
    "RR_ARB_002": "The pointer increments unconditionally past the maximum master index (2), wrapping to index 3 which has no master, causing the arbiter to deadlock waiting for a non-existent request.",
    "RR_ARB_003": "The grant output is driven by a purely combinational assign statement with no clock edge, allowing it to glitch for fractions of a cycle whenever the request vector or last_gnt changes.",
    "RR_ARB_004": "The grant is a combinational function of req and mask with no registered hold; it de-asserts immediately when req drops even during an active bus transaction, violating the sticky-grant rule.",
    "RR_ARB_005": "The grant register (gnt) has no reset branch in its always_ff block, so its value is 4'bxxxx (unknown) from power-on until the first valid arbitration cycle.",
    "RR_ARB_006": "The priority mask is hardcoded to 4'hF, so its complement (~mask) is always zero; the masked request vector is permanently zero and no master is ever granted.",
    "RR_ARB_007": "A blocking assignment (=) is used inside an always_ff block to update last_gnt, creating a race condition between the pointer update and any combinational logic that reads last_gnt in the same time step.",
    "RR_ARB_008": "The combinational grant logic drives gnt to 4'h4 (master 2) unconditionally whenever the FSM is in IDLE state, regardless of whether master 2 has asserted a request.",
    "RR_ARB_009": "The FSM case statement handles only states 0–4 with no default branch; an illegal state (5, 6, or 7) reached via scan-shift or glitch causes the arbiter to freeze permanently.",
    "RR_ARB_010": "The grant register uses an asynchronous clear driven directly by an external signal without a synchronizer; if clr transitions near the clock edge the register enters metastability and gnt becomes unknown.",
    "RR_ARB_011": "The priority mask expression ({last_gnt[0] ? 4'hF : 4'h0}) does not correctly implement round-robin rotation; at the rollover boundary two masters simultaneously satisfy the mask condition producing a non-one-hot grant.",
    "RR_ARB_012": "The grant is a combinational function of req and mask; when the AXI slave asserts wait_sig to stall the bus and the master de-asserts req to wait, the grant drops mid-transfer corrupting the transaction.",
    "RR_ARB_013": "The priority pointer last_gnt is declared as logic [1:0] (4 states) in an 8-master design that requires 3 bits (8 states); masters 4–7 are permanently unreachable by the pointer.",
    "RR_ARB_014": "The round-robin pointer increments by 2 after each grant (last_gnt + 2) instead of 1, causing every other master (indices 1 and 3 in a 4-master design) to be permanently skipped.",
    "RR_ARB_015": "The unique case construct on the multi-hot req vector requires mutually exclusive branches; when two request bits are simultaneously set both branches match, causing a simulation error and undefined synthesis behavior.",
    "RR_ARB_016": "The combinational ternary expression drives gnt to 4'h1 when rst_n is low (reset active) rather than 4'h0; this asserts a spurious grant to master 0 throughout the entire reset period.",
    "RR_ARB_017": "The next-state combinational logic handles req[0] going to GNT0 but has no else-if branch for req[1]; when only master 1 requests, the FSM stays in IDLE indefinitely and master 1 is never served.",
    "RR_ARB_018": "Two concurrent assign statements both drive the gnt bus; the second assign (gnt[1] = req[1]) always overrides the first due to last-assignment-wins semantics, giving master 1 unconditional priority over master 0.",
    "RR_ARB_019": "The grant signal from clock domain A is captured in clock domain B with only a single flip-flop; there is no second synchronizer stage, leaving the design susceptible to metastability when a_gnt transitions near posedge clk_b.",
    "RR_ARB_020": "The SVA fairness property uses req as its antecedent but req is never driven high in the test; the implication is vacuously true every cycle and the assertion provides zero coverage of the actual arbitration logic.",
    "RR_ARB_021": "The arbiter releases the write grant when the AW-channel handshake (AWVALID/AWREADY) completes rather than waiting for the write-response channel (BVALID/BREADY); the bus master loses its grant before the write response arrives.",
    "RR_ARB_022": "The rotating mask is computed as (4'hF << last_gnt), which includes last_gnt itself in the masked-out set; master 0 (last_gnt=0) is excluded from every arbitration round because bit 0 is always in the mask.",
    "RR_ARB_023": "The grant register gnt is declared without an always_ff reset branch; its initial value is 4'bxxxx (unknown), and unknown bits propagate to all downstream bus interface signals on the first active cycle.",
    "RR_ARB_024": "Two case-inside branches use overlapping wildcard patterns; when req=4'b1100 both branches match simultaneously, producing non-deterministic grant selection that varies between simulation runs and synthesis implementations.",
    "RR_ARB_025": "The priority pointer advances only when all requests are idle (any_req=0) rather than after each grant; the first requesting master holds the grant indefinitely because the pointer never advances while any request is active.",
    "RR_ARB_026": "The active-low reset rst_n is used asynchronously without a synchronizer; a reset pulse shorter than one clock period releases before the grant register can complete its reset, leaving gnt in a partially-reset garbage state.",
    "RR_ARB_027": "The grant output register is clocked from the current FSM state; since the output lags the state by one pipeline stage, the downstream handshake partner sees the grant one cycle after the FSM enters the grant state and misses the intended transfer window.",
    "RR_ARB_028": "The pointer uses bitwise NOT (~last_gnt) as an increment, which oscillates correctly between 0 and 1 for two masters but never reaches index 2 in a 3-master design because ~2'b10 = 2'b01, not 2'b11.",
    "RR_ARB_029": "The single-master check (if req[1]) in the always_ff block does not evaluate concurrent req[0]; when both masters request simultaneously only master 1 is considered and master 0 is never granted in that cycle.",
    "RR_ARB_030": "The shift amount (last_gnt + 4) always places the one-hot grant bit in positions [7:4], which are outside the 4-bit gnt[3:0] vector; all shifted bits are truncated and gnt evaluates to 4'h0 every cycle.",
    "RR_ARB_031": "When the done signal fires, next_gnt is already asserted in the same cycle that the current grant is transferred; the downstream master sees no de-assertion gap between consecutive grants and interprets the continuous assertion as a single unbroken transaction.",
    "RR_ARB_032": "The 20-bit weight register packs master 0 weight in the MSB field and master 1 weight in the LSB field, but the arbitration logic reads the fields in the opposite order, inverting the intended priority relationship between the two masters.",
    "RR_ARB_033": "The equality comparison (req == value) propagates unknown (X) bits from req directly to gnt; when any bit of req is X, the comparison result is also X and the grant bus becomes unknown, corrupting all downstream logic.",
    "RR_ARB_034": "The always_ff block gates the grant update on the ready signal, but ready is itself combinationally derived from gnt; this creates a combinational feedback loop that causes simulation delta-cycle divergence and synthesis to generate unwanted latches.",
    "RR_ARB_035": "Both the arbiter and bus_monitor modules are instantiated with the master modport direction; both modules attempt to drive the gnt net simultaneously, producing a multi-driver conflict that forces the net to X.",
    "RR_ARB_036": "The arbiter releases the read grant when the AR-channel handshake (ARVALID/ARREADY) completes, but AXI requires holding the grant through the read-data channel (RVALID/RREADY); the bus master loses its grant before receiving the response data.",
    "RR_ARB_037": "After each grant the priority pointer is reset to 2'h0 rather than being updated to the ID of the master just served; subsequent arbitration always restarts from master 0, permanently preventing masters 1–3 from making forward progress.",
    "RR_ARB_038": "The SVA property checks $rose(gnt) as its antecedent, but gnt is driven to 0 throughout the entire test; $rose(gnt) is never true, so the property passes vacuously without exercising any part of the actual grant logic.",
    "RR_ARB_039": "The FSM always_ff block transitions state on every posedge clk with no conditional check on clk_en; during stall cycles when clk_en=0 the FSM advances anyway, placing it in the wrong state when normal operation resumes.",
    "RR_ARB_040": "The priority mask is applied directly to req (req & mask) rather than to its complement (~mask); masters in the masked-out set — the lower-priority ones — receive the grant while the higher-priority unmasked masters are blocked.",
    "RR_ARB_041": "The grant is assigned as ~rst_n, making gnt equal to 1 whenever rst_n is 0 (active reset); this asserts a spurious grant to a bus master for the entire duration of the reset interval.",
    "RR_ARB_042": "The priority mask expression ((1 << last_gnt) - 1) excludes masters 0 through last_gnt-1 but incorrectly includes last_gnt itself in the grant-eligible set, allowing the same master to be granted twice in consecutive arbitration cycles.",
    "RR_ARB_043": "The grant outputs are derived from both the current state and the next-state signal simultaneously; during the single cycle when state=GNT_S0 transitions to GNT_S1, both gnt[0] and gnt[1] are asserted concurrently, violating the one-hot grant requirement.",
    "RR_ARB_044": "The fairness window counter is declared as logic [7:0], limiting it to 255 cycles; the required window is 300 cycles, so the counter overflows at cycle 255, wraps to zero, and triggers a premature re-arbitration event.",
    "RR_ARB_045": "The always_comb block assigns sticky_gnt only in the if (active) branch with no else assignment; synthesis infers a latch to hold the previous value of gnt when active=0, causing simulation-synthesis mismatch.",
    "RR_ARB_046": "The request signal req arrives from an asynchronous clock domain and is used directly in combinational grant logic without a synchronizer; when req transitions near posedge clk the sampled value is metastable and gnt becomes unknown.",
    "RR_ARB_047": "The priority pointer decrements after each grant (last_gnt - 1) instead of incrementing, causing the arbiter to rotate backwards (3→2→1→0) rather than the required forward order (0→1→2→3).",
    "RR_ARB_048": "The grant output is driven by a combinational expression that reads done, which is itself combinationally derived from gnt; the circular dependency causes a delta-cycle simulation race where gnt glitches for one delta cycle on every done event.",
    "RR_ARB_049": "The active transaction ID register is assigned from last_gnt (the previous winner) rather than the currently active master ID; downstream response routing uses the stale pointer and directs responses to the wrong master.",
    "RR_ARB_050": "The priority pointer last_gnt is declared without an always_ff reset branch; its power-on value is 2'bxx (indeterminate), biasing the round-robin arbitration toward whichever master index the garbage value happens to match.",
}

def patch():
    updated = 0
    for case_id, rc in ROOT_CAUSES.items():
        path = CASES_DIR / f"{case_id}.json"
        if not path.exists():
            print(f"MISSING: {path}")
            continue
        case = json.loads(path.read_text(encoding="utf-8"))
        case["expected_root_cause"] = rc
        path.write_text(json.dumps(case, indent=2), encoding="utf-8")
        updated += 1
    print(f"Patched expected_root_cause for {updated}/50 RR_ARB cases.")

if __name__ == "__main__":
    patch()
