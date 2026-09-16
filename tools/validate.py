#!/usr/bin/env python3
"""Validate PEX packages – the reference implementation of the PEX semantics.

Two stages:
  1. every file against schema/pex.schema.json
  2. every stack (base, base+overlay, base+regional+pedagogical) merged and
     checked referentially: every id that is referenced must exist in the
     effective PEX and must not be disabled.

Usage:  python tools/validate.py              # everything
        python tools/validate.py de de-hh     # one stack
        python tools/validate.py --json       # machine-readable report on stdout

The merge and the reference checks here are mirrored 1:1 in tools/pex.mjs
(JavaScript, for Prilog). tools/build.py writes the materialised stacks to
dist/ and CI fails when the two implementations disagree.

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


# ----------------------------------------------------------------- loading

def package_files():
    return sorted(PKG.glob("*/*.pex.json"))


def load(pid):
    for sub in ("base", "overlays"):
        p = PKG / sub / f"{pid}.pex.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"unknown package '{pid}'")


def extends_of(meta):
    ext = meta.get("extends")
    if ext is None:
        return []
    return ext if isinstance(ext, list) else [ext]


# ------------------------------------------------------------------- merge

def merge(base, over):
    """Deep merge: dicts merge key by key; lists whose items all carry an `id`
    merge by id (same id → element merged, new id → appended, missing id →
    kept); every other list is replaced by the upper layer."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = copy.deepcopy(base)
        for k, v in over.items():
            out[k] = merge(base[k], v) if k in base else copy.deepcopy(v)
        return out
    if (isinstance(base, list) and isinstance(over, list)
            and all(isinstance(x, dict) and "id" in x for x in base + over)):
        out = {x["id"]: copy.deepcopy(x) for x in base}
        for x in over:
            out[x["id"]] = merge(out[x["id"]], x) if x["id"] in out else copy.deepcopy(x)
        return list(out.values())
    return copy.deepcopy(over)


def stack(ids):
    """Merge a stack bottom-up. `meta` stays the base's; the layers are
    recorded in meta.layers so the effective PEX says where it came from."""
    eff = copy.deepcopy(load(ids[0]))
    if eff["meta"].get("kind", "base") != "base":
        raise ValueError(f"{ids[0]} is not a base package")
    layers = [{"id": eff["meta"]["id"], "version": eff["meta"]["version"]}]
    for pid in ids[1:]:
        ov = copy.deepcopy(load(pid))
        if ov["meta"].get("kind") != "overlay":
            raise ValueError(f"{pid} is not an overlay")
        exts = extends_of(ov["meta"])
        if "*" not in exts and ids[0] not in exts:
            raise ValueError(f"{pid} extends {exts}, not {ids[0]}")
        layers.append({"id": ov["meta"]["id"], "version": ov["meta"]["version"]})
        ov.pop("meta")
        eff = merge(eff, ov)
    eff["meta"]["layers"] = layers
    return eff


def stack_house(base_ids, overlay_ids):
    """One effective package for a house that runs several school systems:
    the first base is the main system (it wins on equal ids), every further
    base adds what it brings, then the overlays that fit any base, in order.
    meta is the main system's, languages the union, layers list everything."""
    bases = [copy.deepcopy(load(b)) for b in base_ids]
    for bid, b in zip(base_ids, bases):
        if b["meta"].get("kind", "base") != "base":
            raise ValueError(f"{bid} is not a base package")
    if not bases:
        raise ValueError("a house needs at least one base")
    eff = copy.deepcopy(bases[-1])
    for b in reversed(bases[:-1]):
        b = copy.deepcopy(b); b.pop("meta")
        eff = merge(eff, b)
    eff["meta"] = copy.deepcopy(bases[0]["meta"])
    langs = []
    for b in bases:
        for l in b["meta"]["languages"]:
            if l not in langs: langs.append(l)
    eff["meta"]["languages"] = langs
    layers = [{"id": b["meta"]["id"], "version": b["meta"]["version"]} for b in bases]
    for oid in overlay_ids:
        ov = copy.deepcopy(load(oid))
        if ov["meta"].get("kind") != "overlay":
            raise ValueError(f"{oid} is not an overlay")
        exts = extends_of(ov["meta"])
        if "*" not in exts and not any(b in exts for b in base_ids):
            raise ValueError(f"{oid} extends {exts}, none of {base_ids}")
        layers.append({"id": ov["meta"]["id"], "version": ov["meta"]["version"]})
        ov.pop("meta")
        eff = merge(eff, ov)
    eff["meta"]["layers"] = layers
    return eff


# ------------------------------------------------------------ derivations
# These mirror what Prilog needs at runtime; keeping them here means the
# validator checks the same derivation the application will use.

def grades_for_age(eff, age_from=None, age_to=None, years=None):
    """Grade ids whose typical_age lies in [age_from, age_to] (both inclusive)
    or in `years`. Grades without typical_age never match."""
    if age_from is None and age_to is None and not years:
        return []
    wanted = set(years) if years else None
    out = []
    for g in eff.get("grades", []):
        if g.get("disabled"):
            continue
        a = g.get("typical_age")
        if a is None:
            continue
        if wanted is not None:
            if a in wanted:
                out.append(g["id"])
        elif (age_from is None or a >= age_from) and (age_to is None or a <= age_to):
            out.append(g["id"])
    return out


def subject_grades(eff, s):
    """Effective grade ids of a subject: explicit `grades`, else resolved from
    its age anchor."""
    if s.get("grades"):
        return list(s["grades"])
    return grades_for_age(eff, s.get("age_from"), s.get("age_to"), s.get("age_years"))


def program_grades(eff, p):
    """Grade ids of a program: explicit `grades`, else resolved from age_range
    [from, to) – upper bound exclusive."""
    if p.get("grades"):
        return list(p["grades"])
    a = p.get("age_range")
    if isinstance(a, list) and len(a) == 2:
        return grades_for_age(eff, a[0], a[1] - 1)
    return []


def subjects_of_program(eff, p):
    """Subjects that belong to a program.
    - a subject that names `programs` belongs only to those;
    - a program scoped by grades or age_range takes the subjects whose grades
      intersect its own (a scope that resolves to nothing takes none);
    - a program without any scope takes every subject not restricted elsewhere."""
    scoped = bool(p.get("grades")) or isinstance(p.get("age_range"), list)
    pg = set(program_grades(eff, p))
    out = []
    for s in eff.get("subjects", []):
        if s.get("disabled"):
            continue
        named = s.get("programs") or []
        if named and p["id"] not in named:
            continue
        if not scoped:
            out.append(s)
            continue
        sg = subject_grades(eff, s)
        if (not sg and p["id"] in named) or set(sg) & pg:
            out.append(s)
    return out


# -------------------------------------------------------------- checking

def check_refs(eff):
    """Referential and semantic checks on an effective PEX.
    Returns (errors, hints). Errors block loading; hints do not."""
    ids = {k: {x["id"] for x in eff.get(k, []) if not x.get("disabled")} for k in ID_LISTS}
    alle = {k: {x["id"] for x in eff.get(k, [])} for k in ID_LISTS}
    scales = {x["id"] for x in eff.get("grading", {}).get("scales", []) if not x.get("disabled")}
    periods = {x["id"] for x in eff.get("calendar", {}).get("periods", []) if not x.get("disabled")}
    tracks = {t["id"]: t for t in eff.get("tracks", []) if not t.get("disabled")}
    errs, hints = [], []

    def need(kind, ref, ctx):
        """Anchor reference: the target must exist and must not be disabled."""
        if ref not in ids.get(kind, set()):
            errs.append(f"{ctx}: unknown or disabled {kind} '{ref}'")

    def member(kind, ref, ctx):
        """Membership reference (grades[], programs[], tracks[], qualifications[]):
        the target must exist; a disabled target is allowed and simply filtered
        when reading – so a school can hide a program without rewriting every
        subject and qualification that mentions it."""
        if ref not in alle.get(kind, set()):
            errs.append(f"{ctx}: unknown {kind} '{ref}'")

    def need_scale(ref, ctx):
        if ref not in scales:
            errs.append(f"{ctx}: unknown scale '{ref}'")

    for st in eff.get("stages", []):
        if st.get("disabled"):
            continue
        for g in st.get("grades", []):
            member("grades", g, f"stage {st['id']}")
    for g in eff.get("grades", []):
        if g.get("disabled"):
            continue
        if "stage" in g:
            need("stages", g["stage"], f"grade {g['id']}")

    progs = {p["id"]: p for p in eff.get("programs", []) if not p.get("disabled")}
    quals = {q["id"]: q for q in eff.get("qualifications", []) if not q.get("disabled")}

    for p in progs.values():
        ctx = f"program {p['id']}"
        for g in p.get("grades", []):
            member("grades", g, ctx)
        for s in p.get("stages", []):
            need("stages", s, ctx)
        for t in p.get("tracks", []):
            member("tracks", t, ctx)
        for q in p.get("qualifications", []):
            member("qualifications", q, ctx)
            if q in quals and p["id"] not in quals[q].get("programs", []):
                errs.append(f"{ctx} lists qualification '{q}', but qualification '{q}' does not list the program")
        if not p.get("grades") and not p.get("age_range"):
            hints.append(f"{ctx}: neither grades nor age_range – groups can be tied to neither a grade nor an age")
        if not subjects_of_program(eff, p) and not p.get("remark"):
            hints.append(f"{ctx}: no subject and no remark – intentionally thin or forgotten? Say so in `remark`")
    # `tracked` only has an effect in programs that carry an enrollment track.
    # A subject that is tracked but reaches no such program at all is dead data.
    enrollment_progs = [p for p in progs.values()
                        if any(tracks[t]["scope"] == "enrollment" for t in p.get("tracks", []) if t in tracks)]
    for s in eff.get("subjects", []):
        if s.get("tracked") and not s.get("disabled"):
            if not any(s in subjects_of_program(eff, p) for p in enrollment_progs):
                hints.append(f"subject {s['id']}: `tracked`, but no program with an enrollment track contains it")

    for q in quals.values():
        ctx = f"qualification {q['id']}"
        if "after_grade" in q:
            need("grades", q["after_grade"], ctx)
        for p in q.get("programs", []):
            member("programs", p, ctx)
            if p in progs and q["id"] not in progs[p].get("qualifications", []):
                errs.append(f"{ctx} lists program '{p}', but program '{p}' does not list the qualification")
        for x in q.get("after_grade_by_program", []):
            member("programs", x["program"], f"{ctx}.after_grade_by_program")
            need("grades", x["after_grade"], f"{ctx}.after_grade_by_program")

    for t in tracks.values():
        live = [l for l in t.get("levels", []) if not l.get("disabled")]
        if len(live) < 2:
            errs.append(f"track {t['id']}: fewer than two active levels")

    for s in eff.get("subjects", []):
        if s.get("disabled"):
            continue
        ctx = f"subject {s['id']}"
        if "domain" in s:
            need("subject_domains", s["domain"], ctx)
        for g in s.get("grades", []):
            member("grades", g, ctx)
        for p in s.get("programs", []):
            member("programs", p, ctx)
        has_age = any(k in s for k in ("age_from", "age_to", "age_years"))
        if has_age and s.get("grades"):
            errs.append(f"{ctx}: both grades and an age anchor – choose one")
        if has_age:
            if s.get("age_from") is not None and s.get("age_to") is not None and s["age_from"] > s["age_to"]:
                errs.append(f"{ctx}: age_from > age_to")
            elif not subject_grades(eff, s):
                hints.append(f"{ctx}: age anchor matches no grade of this base")

    # Rules and exams follow what they are about: a rule on admission to a
    # program a school has hidden is simply inactive – a hint, not an error.
    # (Ecole 17.09.2026: hiding the Gymnasium must not force hiding every
    # cantonal rule that names it.)
    def inactive_if(kind, ref, ctx):
        if ref in alle.get(kind, set()) and ref not in ids.get(kind, set()):
            hints.append(f"{ctx}: refers to disabled {kind} '{ref}' – inactive")
            return True
        member(kind, ref, ctx)
        return False
    for e in eff.get("exams", []):
        if e.get("disabled"):
            continue
        inactive_if("qualifications", e["qualification"], f"exam {e['id']}")
        if "at_grade" in e:
            inactive_if("grades", e["at_grade"], f"exam {e['id']}")
    for r in eff.get("rules", []):
        if r.get("disabled"):
            continue
        a = r.get("applies_to", {})
        for k in ("from_grade", "to_grade"):
            if k in a:
                inactive_if("grades", a[k], f"rule {r['id']}")
        for k in ("from_program", "to_program"):
            if k in a:
                inactive_if("programs", a[k], f"rule {r['id']}")
        for p in a.get("programs", []):
            member("programs", p, f"rule {r['id']}")

    gr = eff.get("grading", {})
    if "default_scale" in gr:
        need_scale(gr["default_scale"], "grading.default_scale")
    for bp in gr.get("by_program", []):
        member("programs", bp["program"], "grading.by_program")
        need_scale(bp["scale"], "grading.by_program")
        for g in bp.get("grades", []):
            member("grades", g, f"grading.by_program[{bp['program']}]")
    for hm in gr.get("head_marks", []):
        if "scale" in hm and not hm.get("disabled"):
            need_scale(hm["scale"], f"head_mark {hm['id']}")
    cal = eff.get("calendar", {})
    for rp in cal.get("report_points", []):
        if rp not in periods:
            errs.append(f"calendar.report_points: unknown period '{rp}'")
    for x in cal.get("report_points_by_program", []):
        member("programs", x["program"], "calendar.report_points_by_program")
        for rp in x.get("report_points", []):
            if rp not in periods:
                errs.append(f"calendar.report_points_by_program[{x['program']}]: unknown period '{rp}'")

    # labels in the declared languages – on every visible element
    langs = set(eff["meta"].get("languages", []))
    def check_label(x, ctx):
        if x.get("disabled"):
            return
        if "label" in x and not (set(x["label"]) & langs):
            errs.append(f"{ctx}: label has none of {sorted(langs)}")
        if "remark" in x and not (set(x["remark"]) & langs):
            errs.append(f"{ctx}: remark has none of {sorted(langs)}")
    for k in ID_LISTS:
        for x in eff.get(k, []):
            check_label(x, f"{k} {x['id']}")
            for l in x.get("levels", []) if k == "tracks" else []:
                check_label(l, f"track {x['id']} level {l['id']}")
    for x in gr.get("scales", []):
        check_label(x, f"scale {x['id']}")
    for x in cal.get("periods", []):
        check_label(x, f"period {x['id']}")
    return errs, hints


def check_overlay_alone(ov):
    """What can be said about an overlay without its base."""
    errs = []
    m = ov["meta"]
    if m.get("kind") == "overlay":
        if not extends_of(m):
            errs.append("overlay without `extends`")
        if "*" in extends_of(m):
            # an overlay for every base may not bind to grade ids of one base
            for s in ov.get("subjects", []):
                if s.get("grades"):
                    errs.append(f"subject {s['id']}: extends '*' but binds to grade ids – use age_from/age_to/age_years")
            for p in ov.get("programs", []):
                if p.get("grades") or p.get("stages"):
                    errs.append(f"program {p['id']}: extends '*' but references grades/stages of a base")
    elif extends_of(m):
        errs.append("base package with `extends`")
    return errs


# ------------------------------------------------------------- planning

def all_packages():
    out = {}
    for f in package_files():
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["meta"]["id"]] = d
    return out


def standard_stacks(pkgs=None):
    """Every stack worth checking and materialising:
    base · base+overlay · base+regional+pedagogical."""
    pkgs = pkgs or all_packages()
    bases = [i for i, d in pkgs.items() if d["meta"].get("kind", "base") == "base"]
    overlays = {i: d for i, d in pkgs.items() if d["meta"].get("kind") == "overlay"}
    def fits(o, b):
        e = extends_of(overlays[o]["meta"])
        return "*" in e or b in e
    regional = [o for o, d in overlays.items() if d["meta"].get("region")]
    pedagogical = [o for o, d in overlays.items() if not d["meta"].get("region")]
    stacks = [[b] for b in sorted(bases)]
    for b in sorted(bases):
        for o in sorted(overlays):
            if fits(o, b):
                stacks.append([b, o])
        for r in sorted(regional):
            if not fits(r, b):
                continue
            for p in sorted(pedagogical):
                if fits(p, b):
                    stacks.append([b, r, p])
    return stacks


# ----------------------------------------------------------------- main

def validate_all(stacks=None):
    """Returns a report dict; report['ok'] is the verdict."""
    v = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
    report = {"files": [], "stacks": [], "ok": True}
    for f in package_files():
        d = json.loads(f.read_text(encoding="utf-8"))
        errs = [e.json_path + ": " + e.message for e in v.iter_errors(d)]
        if d.get("meta", {}).get("id") != f.stem.replace(".pex", ""):
            errs.append(f"meta.id '{d.get('meta', {}).get('id')}' differs from file name")
        errs += check_overlay_alone(d) if "meta" in d else []
        report["files"].append({"file": str(f.relative_to(ROOT)), "errors": errs})
        report["ok"] &= not errs
    for st in stacks or standard_stacks():
        try:
            errs, hints = check_refs(stack(st))
        except Exception as ex:  # noqa: BLE001
            errs, hints = [str(ex)], []
        report["stacks"].append({"stack": st, "errors": errs, "hints": hints})
        report["ok"] &= not errs
    return report


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if not a.startswith("--")]
    report = validate_all([argv] if argv else None)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for f in report["files"]:
            print(f"[schema] {f['file']}: {'OK' if not f['errors'] else f['errors'][0][:200]}")
        for s in report["stacks"]:
            n, h = len(s["errors"]), len(s["hints"])
            print(f"[stack]  {' + '.join(s['stack'])}: {'OK' if not n else f'{n} error(s)'}{f', {h} hint(s)' if h else ''}")
            for e in s["errors"][:12]:
                print(f"           ✗ {e}")
            for e in s["hints"][:12]:
                print(f"           · {e}")
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
