#!/usr/bin/env python3
"""Validate PEX packages: each file against the schema, then each overlay stacked on its base.

Usage:  python tools/validate.py            # validate everything
        python tools/validate.py de de-hh   # validate one stack

SPDX-License-Identifier: Apache-2.0
"""
import copy, json, sys
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    sys.exit("pip install jsonschema")

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schema" / "pex.schema.json").read_text(encoding="utf-8"))
PKG = ROOT / "packages"

ID_LISTS = ["stages", "grades", "programs", "tracks", "qualifications",
            "subject_domains", "subjects", "rules", "exams", "legal"]


def load(pid):
    for sub in ("base", "overlays"):
        p = PKG / sub / f"{pid}.pex.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(pid)


def merge(base, over):
    """Deep merge: dicts merge; lists of {id} merge by id; other lists replace."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = copy.deepcopy(base)
        for k, v in over.items():
            out[k] = merge(base[k], v) if k in base else copy.deepcopy(v)
        return out
    if isinstance(base, list) and isinstance(over, list) and all(isinstance(x, dict) and "id" in x for x in base + over):
        out = {x["id"]: copy.deepcopy(x) for x in base}
        for x in over:
            out[x["id"]] = merge(out[x["id"]], x) if x["id"] in out else copy.deepcopy(x)
        return list(out.values())
    return copy.deepcopy(over)


def stack(ids):
    eff = load(ids[0])
    for pid in ids[1:]:
        ov = load(pid)
        ext = ov["meta"].get("extends")
        exts = ext if isinstance(ext, list) else [ext]
        if "*" not in exts and ids[0] not in exts:
            raise ValueError(f"{pid} extends {exts}, not {ids[0]}")
        ov = copy.deepcopy(ov)
        ov["meta"] = {k: v for k, v in ov["meta"].items() if k in ("version",)}  # keep base meta
        eff = merge(eff, ov)
    return eff


def check_refs(eff):
    ids = {k: {x["id"] for x in eff.get(k, []) if not x.get("disabled")} for k in ID_LISTS}
    scales = {x["id"] for x in eff.get("grading", {}).get("scales", [])}
    periods = {x["id"] for x in eff.get("calendar", {}).get("periods", [])}
    errs = []

    def need(kind, ref, ctx):
        if ref not in ids.get(kind, set()):
            errs.append(f"{ctx}: unknown or disabled {kind} '{ref}'")

    for st in eff.get("stages", []):
        for g in st.get("grades", []): need("grades", g, f"stage {st['id']}")
    for g in eff.get("grades", []):
        if "stage" in g: need("stages", g["stage"], f"grade {g['id']}")
    for p in eff.get("programs", []):
        if p.get("disabled"): continue
        for g in p.get("grades", []): need("grades", g, f"program {p['id']}")
        for s in p.get("stages", []): need("stages", s, f"program {p['id']}")
        for t in p.get("tracks", []): need("tracks", t, f"program {p['id']}")
        for q in p.get("qualifications", []): need("qualifications", q, f"program {p['id']}")
    for q in eff.get("qualifications", []):
        if q.get("disabled"): continue
        if "after_grade" in q: need("grades", q["after_grade"], f"qualification {q['id']}")
        for p in q.get("programs", []): need("programs", p, f"qualification {q['id']}")
    for s in eff.get("subjects", []):
        if s.get("disabled"): continue
        if "domain" in s: need("subject_domains", s["domain"], f"subject {s['id']}")
        for g in s.get("grades", []): need("grades", g, f"subject {s['id']}")
        for p in s.get("programs", []): need("programs", p, f"subject {s['id']}")
    for e in eff.get("exams", []):
        if e.get("disabled"): continue
        need("qualifications", e["qualification"], f"exam {e['id']}")
        if "at_grade" in e: need("grades", e["at_grade"], f"exam {e['id']}")
    for r in eff.get("rules", []):
        a = r.get("applies_to", {})
        for k in ("from_grade", "to_grade"):
            if k in a: need("grades", a[k], f"rule {r['id']}")
        for k in ("from_program", "to_program"):
            if k in a: need("programs", a[k], f"rule {r['id']}")
    gr = eff.get("grading", {})
    if "default_scale" in gr and gr["default_scale"] not in scales:
        errs.append(f"grading.default_scale '{gr['default_scale']}' unknown")
    for bp in gr.get("by_program", []):
        need("programs", bp["program"], "grading.by_program")
        if bp["scale"] not in scales: errs.append(f"grading.by_program: unknown scale '{bp['scale']}'")
    for hm in gr.get("head_marks", []):
        if "scale" in hm and hm["scale"] not in scales: errs.append(f"head_mark {hm['id']}: unknown scale")
    cal = eff.get("calendar", {})
    for rp in cal.get("report_points", []):
        if rp not in periods: errs.append(f"calendar.report_points: unknown period '{rp}'")
    for x in cal.get("report_points_by_program", []):
        need("programs", x["program"], "calendar.report_points_by_program")
    # labels in declared languages
    langs = set(eff["meta"].get("languages", []))
    for k in ID_LISTS:
        for x in eff.get(k, []):
            if "label" in x and not (set(x["label"]) & langs):
                errs.append(f"{k} {x['id']}: label has none of {sorted(langs)}")
    return errs


def main(argv):
    v = jsonschema.Draft202012Validator(SCHEMA)
    ok = True
    files = sorted(PKG.glob("*/*.pex.json"))
    for f in files:
        errs = [e.message for e in v.iter_errors(json.loads(f.read_text(encoding="utf-8")))]
        print(f"[schema] {f.relative_to(ROOT)}: {'OK' if not errs else errs[0][:160]}")
        ok &= not errs
    if argv:
        stacks = [argv]
    else:
        bases = [json.loads(f.read_text(encoding="utf-8"))["meta"]["id"] for f in (PKG / "base").glob("*.pex.json")]
        stacks = [[b] for b in bases]
        for f in (PKG / "overlays").glob("*.pex.json"):
            m = json.loads(f.read_text(encoding="utf-8"))["meta"]
            ext = m.get("extends")
            exts = ext if isinstance(ext, list) else [ext]
            targets = bases if "*" in exts else exts
            stacks += [[t, m["id"]] for t in targets if t in bases]
    for st in stacks:
        try:
            errs = check_refs(stack(st))
        except Exception as ex:  # noqa
            errs = [str(ex)]
        print(f"[stack]  {' + '.join(st)}: {'OK' if not errs else f'{len(errs)} issue(s)'}")
        for e in errs[:8]:
            print(f"           - {e}")
        ok &= not errs
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
