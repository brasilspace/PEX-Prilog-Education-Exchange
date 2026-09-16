#!/usr/bin/env python3
"""Materialise every standard stack into dist/ so that a consumer (Prilog)
can load an effective PEX without merging – and write dist/index.json, the
registry a loader reads first.

    python tools/build.py          # writes dist/
    python tools/build.py --check  # exit 1 if dist/ is stale (CI)

No timestamps are written; the output is a pure function of packages/.

SPDX-License-Identifier: Apache-2.0
"""
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as V  # noqa: E402

DIST = V.ROOT / "dist"


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def dump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build():
    pkgs = V.all_packages()
    files = {}
    index = {
        "format": "pex-index",
        "schema": V.SCHEMA["$id"],
        "schema_version": "2.2",
        "packages": [],
        "stacks": [],
    }
    for f in V.package_files():
        d = json.loads(f.read_text(encoding="utf-8"))
        m = d["meta"]
        index["packages"].append({
            "id": m["id"], "kind": m.get("kind", "base"), "version": m["version"],
            "extends": V.extends_of(m) or None, "country": m["country"],
            "region": m.get("region"), "languages": m["languages"], "name": m["name"],
            "file": str(f.relative_to(V.ROOT)), "sha256": sha(f.read_bytes()),
        })
    for st in V.standard_stacks(pkgs):
        eff = V.stack(st)
        errs, hints = V.check_refs(eff)
        if errs:
            raise SystemExit(f"stack {'+'.join(st)} has errors – run tools/validate.py")
        name = "+".join(st)
        data = dump(eff)
        files[f"effective/{name}.json"] = data
        index["stacks"].append({
            "id": name, "layers": eff["meta"]["layers"],
            "file": f"dist/effective/{name}.json", "sha256": sha(data), "hints": len(hints),
        })
    files["index.json"] = dump(index)
    return files


def main(argv):
    files = build()
    if "--check" in argv:
        stale = []
        for rel, data in files.items():
            p = DIST / rel
            if not p.exists() or p.read_bytes() != data:
                stale.append(rel)
        extra = [str(p.relative_to(DIST)) for p in DIST.rglob("*.json") if str(p.relative_to(DIST)) not in files]
        if stale or extra:
            print("dist/ is stale – run `python tools/build.py`")
            for s in stale: print("  changed:", s)
            for e in extra: print("  orphan: ", e)
            sys.exit(1)
        print(f"dist/ is up to date ({len(files)} files)")
        return
    (DIST / "effective").mkdir(parents=True, exist_ok=True)
    for p in DIST.rglob("*.json"):
        p.unlink()
    for rel, data in files.items():
        (DIST / rel).write_bytes(data)
    print(f"wrote {len(files)} files to dist/")


if __name__ == "__main__":
    main(sys.argv[1:])
