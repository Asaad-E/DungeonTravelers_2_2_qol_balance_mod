#!/usr/bin/env python
"""Phase 4 stratified random audit sampler (docs/ENGINE_CONFORMITY_ROADMAP.md, Section 3 Phase 4).

Draws, for one audit round:
  * 12 catalog items WITHOUT replacement (3 each from core_combat, status_procs,
    effects_passives, units_ai_loaders), excluding ids already in
    STATE.json -> phase4.sampled_item_ids;
  * 3 out-of-catalog "trace_event" packets (Stratum 5) parsed from a TextTrace
    (engine_cs/src/DtEngine/Trace.cs) text trace.

Usage:
  python tools/sample_audit_batch.py --round N [--seed S] [--out PATH] [--no-trace]
         [--trace-file TRACE.txt | --snapshot SNAP --job JOB [--dtcli PATH] [--level 2]]

The manifest goes to --out, or stdout when --out is omitted. This tool NEVER writes
STATE.json or anything under docs/binary_spec/ on its own; the coordinator records
the sampled ids after the round is launched.

Trace source (Stratum 5), in priority order:
  1. --trace-file: parse an existing TextTrace file (dtcli `trace --out`).
  2. --snapshot + --job: run `dtcli trace --snapshot S --job J --out T --level L` (the job
     file carries its own battle seed, so it must already be seeded) and parse the result.
     The `seed` in each packet is the sampler seed that selected the events from the trace.
  3. Otherwise (or with --no-trace): trace_events = [] and `trace_status` explains
     that the coordinator must feed a live C# trace via --trace-file. No synthetic
     data is fabricated, because auditors would verify it against the vanilla exe.

TextTrace line format (see Trace.cs):
  B <run> <battleIndex>           battle header
  U <pos> <name>|kind|side|...    initial unit state line
  S <nextTime...> w<words>        battle start
  r <rng draw>                    (level 2) RNG draw, flushed before the turn line
  T <n> <time> a<pos> <events> | <hp/tp/alive/next per unit> | w<words>   turn end
  E ...                           battle end
Events inside a T line (';' separated): A<actor>:<kind>:<source>:L<lvl>,
  H<actor>><target>=<0|1> (hit), D<actor>><target>=<amount> (damage),
  R<unit>+<n> (restore), L<unit>-<n> (hp loss).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import secrets
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INVENTORY = os.path.join(REPO_ROOT, "docs", "binary_spec", "00_INVENTORY.json")
DEFAULT_STATE = os.path.join(REPO_ROOT, "docs", "binary_spec", "STATE.json")
DEFAULT_DTCLI = os.path.join(REPO_ROOT, "engine_cs", "src", "DtEngine.Cli", "bin", "Debug", "net10.0", "dtcli.exe")

STRATA_ORDER = ["core_combat", "status_procs", "effects_passives", "units_ai_loaders"]
PER_STRATUM = 3
TRACE_PACKETS = 3
TRACE_KINDS = ["damage", "hit", "turn_end"]

_EVENT_RE = re.compile(r"^([AHDRL])(.*)$")
_HIT_RE = re.compile(r"^(\d+)>(\d+)=([01])$")
_DMG_RE = re.compile(r"^(\d+)>(\d+)=(-?\d+)$")


# --------------------------------------------------------------------------- catalog sampling

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def sampled_ids_from_state(state):
    p4 = (state or {}).get("phase4") or {}
    return list(p4.get("sampled_item_ids") or [])


def sample_catalog(catalog, already_sampled, rng):
    """Return 12 items (3 per stratum), without replacement, excluding already_sampled."""
    excluded = set(already_sampled)
    by_stratum = {s: [] for s in STRATA_ORDER}
    for item in catalog:
        s = item.get("stratum")
        if s in by_stratum and item.get("id") not in excluded:
            by_stratum[s].append(item)
    picked = []
    for s in STRATA_ORDER:
        pool = sorted(by_stratum[s], key=lambda i: i["id"])
        if len(pool) < PER_STRATUM:
            raise SystemExit("error: stratum %r has only %d unsampled items (need %d)" % (s, len(pool), PER_STRATUM))
        picked.extend(rng.sample(pool, PER_STRATUM))
    return picked


# --------------------------------------------------------------------------- trace parsing

def _split_events(raw):
    return [e for e in raw.split(";") if e]


def parse_turn_line(line):
    """Parse a 'T ...' line into a dict, or None if malformed."""
    parts = line.split(" | ")
    if len(parts) != 3:
        return None
    head, states, tail = parts
    toks = head.split(" ", 4)  # 'T', n, time, aPOS, events...
    if len(toks) < 4 or toks[0] != "T" or not toks[3].startswith("a"):
        return None
    events_raw = toks[4] if len(toks) > 4 else ""
    events = []
    for e in _split_events(events_raw.strip()):
        m = _EVENT_RE.match(e)
        if not m:
            continue
        code, body = m.group(1), m.group(2)
        ev = {"code": code, "raw": e}
        if code == "H":
            mm = _HIT_RE.match(body)
            if mm:
                ev.update(kind="hit", actor=int(mm.group(1)), target=int(mm.group(2)), landed=mm.group(3) == "1")
        elif code == "D":
            mm = _DMG_RE.match(body)
            if mm:
                ev.update(kind="damage", actor=int(mm.group(1)), target=int(mm.group(2)), amount=int(mm.group(3)))
        elif code == "A":
            f = body.split(":")
            ev.update(kind="action", actor=int(f[0]) if f and f[0].isdigit() else None,
                      action_kind=f[1] if len(f) > 1 else None,
                      source=f[2] if len(f) > 2 else None,
                      level=f[3] if len(f) > 3 else None)
        elif code == "R":
            ev.update(kind="restore")
        elif code == "L":
            ev.update(kind="lose_hp")
        events.append(ev)
    units = []
    for tok in states.split():
        f = tok.split("/")
        if len(f) == 4:
            units.append({"hp": f[0], "tp": f[1], "alive": f[2] == "1", "next_time": f[3]})
    words = tail.strip()
    words = int(words[1:]) if words.startswith("w") and words[1:].isdigit() else None
    return {
        "turn": int(toks[1]) if toks[1].isdigit() else None,
        "time": toks[2],
        "actor": int(toks[3][1:]) if toks[3][1:].isdigit() else None,
        "events": events,
        "unit_states_after": units,
        "rng_words_after": words,
    }


def parse_trace_lines(lines):
    """Parse TextTrace lines into candidate event records.

    Returns a list of dicts {event_kind, event, turn_info, battle_context, raw_trace_lines}.
    """
    records = []
    battle = None  # current battle context
    prev_words = None
    pending = []   # raw lines (r ...) accumulated since previous turn line
    for ln in lines:
        ln = ln.rstrip("\r\n")
        if not ln:
            continue
        tag = ln[0]
        if tag == "B" and ln[1:2] == " ":
            f = ln.split()
            battle = {"run": f[1] if len(f) > 1 else None, "battle_index": f[2] if len(f) > 2 else None,
                      "header": ln, "units": [], "start_line": None}
            prev_words, pending = None, []
        elif tag == "U" and ln[1:2] == " " and battle is not None:
            battle["units"].append(ln)
        elif tag == "S" and (ln[1:2] in (" ", "")) and battle is not None:
            battle["start_line"] = ln
            m = re.search(r" w(\d+)\s*$", ln)
            prev_words = int(m.group(1)) if m else None
            pending = []
        elif tag == "r" and ln[1:2] == " ":
            pending.append(ln)
        elif tag == "T" and ln[1:2] == " " and battle is not None:
            info = parse_turn_line(ln)
            if info is None:
                pending = []
                continue
            draws = list(pending)
            pending = []
            ctx = {
                "run": battle["run"], "battle_index": battle["battle_index"],
                "header": battle["header"], "initial_units": list(battle["units"]),
                "start_line": battle["start_line"],
                "turn": info["turn"], "time": info["time"], "acting_unit": info["actor"],
                "unit_states_after_turn": info["unit_states_after"],
                "rng_words_before_turn": prev_words, "rng_words_after_turn": info["rng_words_after"],
                "rng_draws_for_turn": draws,
                "turn_events": [e["raw"] for e in info["events"]],
            }
            raw = [battle["header"]] + battle["units"] + ([battle["start_line"]] if battle["start_line"] else []) + draws + [ln]
            for ev in info["events"]:
                if ev.get("kind") in ("damage", "hit"):
                    records.append({"event_kind": ev["kind"], "event": ev, "battle_context": ctx, "raw_trace_lines": raw})
            records.append({"event_kind": "turn_end", "event": {"kind": "turn_end", "raw": ln},
                            "battle_context": ctx, "raw_trace_lines": raw})
            prev_words = info["rng_words_after"]
    return records


def select_trace_events(records, rng, seed, n=TRACE_PACKETS):
    """Pick n distinct events: one per kind in TRACE_KINDS where possible, then fill randomly."""
    by_kind = {k: [r for r in records if r["event_kind"] == k] for k in TRACE_KINDS}
    chosen = []
    for k in TRACE_KINDS:
        if by_kind[k] and len(chosen) < n:
            chosen.append(rng.choice(by_kind[k]))
    rest = [r for r in records if all(r is not c for c in chosen)]
    while len(chosen) < n and rest:
        pick = rng.choice(rest)
        chosen.append(pick)
        rest = [r for r in rest if r is not pick]
    packets = []
    for r in chosen:
        ctx = r["battle_context"]
        ev = dict(r["event"])
        pid = "TR-%s-b%s-t%s-%s%s" % (seed, ctx["battle_index"], ctx["turn"], r["event_kind"],
                                      "-" + ev["raw"] if r["event_kind"] != "turn_end" else "")
        packets.append({
            "id": pid,
            "stratum": "trace_event",
            "event_kind": r["event_kind"],
            "seed": seed,
            "event": ev,
            "battle_context": ctx,
            "raw_trace_lines": r["raw_trace_lines"],
        })
    return packets


def run_dtcli_trace(dtcli, snapshot, job, level):
    """Run `dtcli trace` to a temp file and return its lines. Raises RuntimeError on failure."""
    if not os.path.isfile(dtcli):
        raise RuntimeError("dtcli not found at %s" % dtcli)
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "trace.txt")
        cmd = [dtcli, "trace", "--snapshot", snapshot, "--job", job, "--out", out, "--level", str(level)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0 or not os.path.isfile(out):
            raise RuntimeError("dtcli trace failed (rc=%s): %s" % (proc.returncode, (proc.stdout + proc.stderr)[-500:]))
        with open(out, "r", encoding="utf-8-sig") as fh:
            return fh.read().splitlines()


def build_trace_events(args, rng, seed):
    """Returns (trace_events, trace_status)."""
    if args.no_trace:
        return [], "skipped (--no-trace)"
    lines = None
    source = None
    try:
        if args.trace_file:
            with open(args.trace_file, "r", encoding="utf-8-sig") as fh:
                lines = fh.read().splitlines()
            source = "trace-file:" + args.trace_file
        elif args.snapshot and args.job:
            lines = run_dtcli_trace(args.dtcli, args.snapshot, args.job, args.level)
            source = "dtcli trace (level %d)" % args.level
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        return [], "error: %s" % exc
    if lines is None:
        return [], ("pending: no live trace supplied. `dtcli trace` needs --snapshot and a seeded --job; "
                    "rerun with --trace-file <TextTrace output> or --snapshot/--job.")
    records = parse_trace_lines(lines)
    if not records:
        return [], "error: no damage/hit/turn_end events parsed from %s" % source
    packets = select_trace_events(records, rng, seed)
    status = "ok: %d packets from %s" % (len(packets), source)
    if len(packets) < TRACE_PACKETS:
        status = "partial: only %d of %d packets available from %s" % (len(packets), TRACE_PACKETS, source)
    return packets, status


# --------------------------------------------------------------------------- manifest / CLI

def build_manifest(round_no, seed, catalog, already_sampled, args):
    # Separate generators so the catalog draw is independent of whether tracing is enabled.
    cat_rng = random.Random(seed)
    trace_rng = random.Random("trace:%s" % seed)
    items = sample_catalog(catalog, already_sampled, cat_rng)
    events, status = build_trace_events(args, trace_rng, seed)
    counts = {s: sum(1 for i in items if i["stratum"] == s) for s in STRATA_ORDER}
    counts["trace_event"] = len(events)
    return {
        "round": round_no,
        "seed": seed,
        "total_items": len(items) + len(events),
        "strata_counts": counts,
        "catalog_items": items,
        "trace_events": events,
        "trace_status": status,
        "sampled_item_ids": [i["id"] for i in items],
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Phase 4 stratified random audit sampler")
    p.add_argument("--round", type=int, required=True, dest="round_no")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--out", default=None, help="manifest path (default: stdout)")
    p.add_argument("--no-trace", action="store_true", help="skip Stratum 5 trace events")
    p.add_argument("--trace-file", default=None, help="existing TextTrace output to parse")
    p.add_argument("--snapshot", default=None)
    p.add_argument("--job", default=None)
    p.add_argument("--dtcli", default=DEFAULT_DTCLI)
    p.add_argument("--level", type=int, default=2)
    p.add_argument("--inventory", default=DEFAULT_INVENTORY)
    p.add_argument("--state", default=DEFAULT_STATE)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    inv = load_json(args.inventory)
    state = load_json(args.state)
    seed = args.seed if args.seed is not None else secrets.randbelow(2 ** 31)
    print("sample_audit_batch: round=%d seed=%d" % (args.round_no, seed), file=sys.stderr)
    manifest = build_manifest(args.round_no, seed, inv["audit_catalog"], sampled_ids_from_state(state), args)
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        parent = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(parent, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
