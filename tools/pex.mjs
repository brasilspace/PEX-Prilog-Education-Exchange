/**
 * PEX – Prilog Education Exchange: loader, merge and checks in JavaScript.
 *
 * This is the implementation Prilog uses. It mirrors tools/validate.py
 * (the reference) function by function; tools/pex.test.mjs proves on every
 * CI run that both produce byte-identical effective packages for every
 * standard stack. Zero dependencies, Node ≥ 20, ESM.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ID_LISTS = ['stages', 'grades', 'programs', 'tracks', 'qualifications',
  'subject_domains', 'subjects', 'rules', 'exams', 'legal'];

const HERE = dirname(fileURLToPath(import.meta.url));
export const DEFAULT_PACKAGES_DIR = join(HERE, '..', 'packages');

const clone = (x) => (x === undefined ? undefined : JSON.parse(JSON.stringify(x)));
const isObj = (x) => x !== null && typeof x === 'object' && !Array.isArray(x);

/** ids named in `meta.extends`, normalised to an array. */
export function extendsOf(meta) {
  const e = meta?.extends;
  if (e === undefined || e === null) return [];
  return Array.isArray(e) ? e : [e];
}

/** Read every *.pex.json below `dir` (base/ and overlays/), keyed by meta.id. */
export function loadAll(dir = DEFAULT_PACKAGES_DIR) {
  const out = new Map();
  for (const sub of ['base', 'overlays']) {
    const d = join(dir, sub);
    if (!existsSync(d)) continue;
    for (const f of readdirSync(d).sort()) {
      if (!f.endsWith('.pex.json')) continue;
      const p = JSON.parse(readFileSync(join(d, f), 'utf8'));
      if (p?.meta?.format !== 'pex') throw new Error(`${f}: not a PEX file (meta.format)`);
      out.set(p.meta.id, p);
    }
  }
  return out;
}

/**
 * Deep merge: objects merge key by key; arrays whose items all carry an `id`
 * merge by id (same id → merged, new id → appended, missing id → kept);
 * every other array is replaced by the upper layer.
 */
export function merge(base, over) {
  if (isObj(base) && isObj(over)) {
    const out = clone(base);
    for (const [k, v] of Object.entries(over)) out[k] = k in base ? merge(base[k], v) : clone(v);
    return out;
  }
  if (Array.isArray(base) && Array.isArray(over)
      && [...base, ...over].every((x) => isObj(x) && 'id' in x)) {
    const out = new Map(base.map((x) => [x.id, clone(x)]));
    for (const x of over) out.set(x.id, out.has(x.id) ? merge(out.get(x.id), x) : clone(x));
    return [...out.values()];
  }
  return clone(over);
}

/**
 * Merge a stack bottom-up: `ids[0]` must be a base, the rest overlays that
 * extend it. `meta` stays the base's; `meta.layers` records the layers.
 */
export function stack(ids, packages) {
  const get = (id) => {
    const p = packages.get(id);
    if (!p) throw new Error(`unknown package '${id}'`);
    return clone(p);
  };
  let eff = get(ids[0]);
  if ((eff.meta.kind ?? 'base') !== 'base') throw new Error(`${ids[0]} is not a base package`);
  const layers = [{ id: eff.meta.id, version: eff.meta.version }];
  for (const id of ids.slice(1)) {
    const ov = get(id);
    if (ov.meta.kind !== 'overlay') throw new Error(`${id} is not an overlay`);
    const ex = extendsOf(ov.meta);
    if (!ex.includes('*') && !ex.includes(ids[0])) throw new Error(`${id} extends ${JSON.stringify(ex)}, not ${ids[0]}`);
    layers.push({ id: ov.meta.id, version: ov.meta.version });
    delete ov.meta;
    eff = merge(eff, ov);
  }
  eff.meta.layers = layers;
  return eff;
}

/** Grade ids whose typical_age lies in [from, to] (inclusive) or in `years`. */
export function gradesForAge(eff, from, to, years) {
  if (from === undefined && to === undefined && !(years?.length)) return [];
  const wanted = years?.length ? new Set(years) : undefined;
  const out = [];
  for (const g of eff.grades ?? []) {
    if (g.disabled) continue;
    const a = g.typical_age;
    if (a === undefined) continue;
    if (wanted) { if (wanted.has(a)) out.push(g.id); }
    else if ((from === undefined || a >= from) && (to === undefined || a <= to)) out.push(g.id);
  }
  return out;
}

/** Effective grade ids of a subject: explicit `grades`, else its age anchor. */
export function subjectGrades(eff, s) {
  if (s.grades?.length) return [...s.grades];
  return gradesForAge(eff, s.age_from, s.age_to, s.age_years);
}

/** Grade ids of a program: explicit `grades`, else age_range [from, to). */
export function programGrades(eff, p) {
  if (p.grades?.length) return [...p.grades];
  const a = p.age_range;
  if (Array.isArray(a) && a.length === 2) return gradesForAge(eff, a[0], a[1] - 1);
  return [];
}

/**
 * Subjects of a program: a subject naming `programs` belongs only to those;
 * a program scoped by grades or age_range takes the subjects whose grades
 * intersect its own (a scope resolving to nothing takes none); a program
 * without any scope takes every subject not restricted elsewhere.
 */
export function subjectsOfProgram(eff, p) {
  const scoped = Boolean(p.grades?.length) || Array.isArray(p.age_range);
  const pg = new Set(programGrades(eff, p));
  const out = [];
  for (const s of eff.subjects ?? []) {
    if (s.disabled) continue;
    const named = s.programs ?? [];
    if (named.length && !named.includes(p.id)) continue;
    if (!scoped) { out.push(s); continue; }
    const sg = subjectGrades(eff, s);
    if ((!sg.length && named.includes(p.id)) || sg.some((g) => pg.has(g))) out.push(s);
  }
  return out;
}

/** Terminology lookup with fallback chain: effective PEX → default → key. */
export function term(eff, key, lang, fallback) {
  const l = eff.terminology?.[key];
  if (!l) return fallback ?? key;
  return l[lang] ?? l.de ?? l.en ?? Object.values(l)[0] ?? fallback ?? key;
}

/**
 * Referential and semantic checks on an effective PEX.
 * Returns { errors, hints }. Errors block loading; hints do not.
 */
export function checkRefs(eff) {
  const errors = [];
  const hints = [];
  const ids = Object.fromEntries(ID_LISTS.map((k) => [k, new Set((eff[k] ?? []).filter((x) => !x.disabled).map((x) => x.id))]));
  const scales = new Set((eff.grading?.scales ?? []).filter((x) => !x.disabled).map((x) => x.id));
  const periods = new Set((eff.calendar?.periods ?? []).filter((x) => !x.disabled).map((x) => x.id));
  const tracks = new Map((eff.tracks ?? []).filter((t) => !t.disabled).map((t) => [t.id, t]));
  const alle = Object.fromEntries(ID_LISTS.map((k) => [k, new Set((eff[k] ?? []).map((x) => x.id))]));
  /** Anchor reference: target must exist and must not be disabled. */
  const need = (kind, ref, ctx) => { if (!ids[kind]?.has(ref)) errors.push(`${ctx}: unknown or disabled ${kind} '${ref}'`); };
  /** Membership reference (grades[], programs[], tracks[], qualifications[]): target must exist;
   *  a disabled target is allowed and filtered when reading – a school can hide a program
   *  without rewriting every subject and qualification that mentions it. */
  const member = (kind, ref, ctx) => { if (!alle[kind]?.has(ref)) errors.push(`${ctx}: unknown ${kind} '${ref}'`); };
  const needScale = (ref, ctx) => { if (!scales.has(ref)) errors.push(`${ctx}: unknown scale '${ref}'`); };

  for (const st of eff.stages ?? []) { if (st.disabled) continue; for (const g of st.grades ?? []) member('grades', g, `stage ${st.id}`); }
  for (const g of eff.grades ?? []) { if (g.disabled) continue; if ('stage' in g) need('stages', g.stage, `grade ${g.id}`); }

  const progs = new Map((eff.programs ?? []).filter((p) => !p.disabled).map((p) => [p.id, p]));
  const quals = new Map((eff.qualifications ?? []).filter((q) => !q.disabled).map((q) => [q.id, q]));

  for (const p of progs.values()) {
    const ctx = `program ${p.id}`;
    for (const g of p.grades ?? []) member('grades', g, ctx);
    for (const s of p.stages ?? []) need('stages', s, ctx);
    for (const t of p.tracks ?? []) member('tracks', t, ctx);
    for (const q of p.qualifications ?? []) {
      member('qualifications', q, ctx);
      if (quals.has(q) && !(quals.get(q).programs ?? []).includes(p.id)) {
        errors.push(`${ctx} lists qualification '${q}', but qualification '${q}' does not list the program`);
      }
    }
    if (!(p.grades?.length) && !p.age_range) hints.push(`${ctx}: neither grades nor age_range – groups can be tied to neither a grade nor an age`);
    if (!subjectsOfProgram(eff, p).length && !p.remark) hints.push(`${ctx}: no subject and no remark – intentionally thin or forgotten? Say so in \`remark\``);
  }
  const enrollmentProgs = [...progs.values()].filter((p) => (p.tracks ?? []).some((t) => tracks.get(t)?.scope === 'enrollment'));
  for (const s of eff.subjects ?? []) {
    if (s.tracked && !s.disabled && !enrollmentProgs.some((p) => subjectsOfProgram(eff, p).includes(s))) {
      hints.push(`subject ${s.id}: \`tracked\`, but no program with an enrollment track contains it`);
    }
  }

  for (const q of quals.values()) {
    const ctx = `qualification ${q.id}`;
    if ('after_grade' in q) need('grades', q.after_grade, ctx);
    for (const p of q.programs ?? []) {
      member('programs', p, ctx);
      if (progs.has(p) && !(progs.get(p).qualifications ?? []).includes(q.id)) {
        errors.push(`${ctx} lists program '${p}', but program '${p}' does not list the qualification`);
      }
    }
    for (const x of q.after_grade_by_program ?? []) {
      member('programs', x.program, `${ctx}.after_grade_by_program`);
      need('grades', x.after_grade, `${ctx}.after_grade_by_program`);
    }
  }

  for (const t of tracks.values()) {
    if ((t.levels ?? []).filter((l) => !l.disabled).length < 2) errors.push(`track ${t.id}: fewer than two active levels`);
  }

  for (const s of eff.subjects ?? []) {
    if (s.disabled) continue;
    const ctx = `subject ${s.id}`;
    if ('domain' in s) need('subject_domains', s.domain, ctx);
    for (const g of s.grades ?? []) member('grades', g, ctx);
    for (const p of s.programs ?? []) member('programs', p, ctx);
    const hasAge = ['age_from', 'age_to', 'age_years'].some((k) => k in s);
    if (hasAge && s.grades?.length) errors.push(`${ctx}: both grades and an age anchor – choose one`);
    if (hasAge) {
      if (s.age_from !== undefined && s.age_to !== undefined && s.age_from > s.age_to) errors.push(`${ctx}: age_from > age_to`);
      else if (!subjectGrades(eff, s).length) hints.push(`${ctx}: age anchor matches no grade of this base`);
    }
  }

  for (const e of eff.exams ?? []) {
    if (e.disabled) continue;
    need('qualifications', e.qualification, `exam ${e.id}`);
    if ('at_grade' in e) need('grades', e.at_grade, `exam ${e.id}`);
  }
  for (const r of eff.rules ?? []) {
    if (r.disabled) continue;
    const a = r.applies_to ?? {};
    for (const k of ['from_grade', 'to_grade']) if (k in a) need('grades', a[k], `rule ${r.id}`);
    for (const k of ['from_program', 'to_program']) if (k in a) need('programs', a[k], `rule ${r.id}`);
    for (const p of a.programs ?? []) member('programs', p, `rule ${r.id}`);
  }

  const gr = eff.grading ?? {};
  if ('default_scale' in gr) needScale(gr.default_scale, 'grading.default_scale');
  for (const bp of gr.by_program ?? []) {
    member('programs', bp.program, 'grading.by_program');
    needScale(bp.scale, 'grading.by_program');
    for (const g of bp.grades ?? []) member('grades', g, `grading.by_program[${bp.program}]`);
  }
  for (const hm of gr.head_marks ?? []) if ('scale' in hm && !hm.disabled) needScale(hm.scale, `head_mark ${hm.id}`);
  const cal = eff.calendar ?? {};
  for (const rp of cal.report_points ?? []) if (!periods.has(rp)) errors.push(`calendar.report_points: unknown period '${rp}'`);
  for (const x of cal.report_points_by_program ?? []) {
    member('programs', x.program, 'calendar.report_points_by_program');
    for (const rp of x.report_points ?? []) if (!periods.has(rp)) errors.push(`calendar.report_points_by_program[${x.program}]: unknown period '${rp}'`);
  }

  const langs = new Set(eff.meta?.languages ?? []);
  const checkLabel = (x, ctx) => {
    if (x.disabled) return;
    if (x.label && !Object.keys(x.label).some((l) => langs.has(l))) errors.push(`${ctx}: label has none of ${JSON.stringify([...langs].sort())}`);
    if (x.remark && !Object.keys(x.remark).some((l) => langs.has(l))) errors.push(`${ctx}: remark has none of ${JSON.stringify([...langs].sort())}`);
  };
  for (const k of ID_LISTS) for (const x of eff[k] ?? []) {
    checkLabel(x, `${k} ${x.id}`);
    if (k === 'tracks') for (const l of x.levels ?? []) checkLabel(l, `track ${x.id} level ${l.id}`);
  }
  for (const x of gr.scales ?? []) checkLabel(x, `scale ${x.id}`);
  for (const x of cal.periods ?? []) checkLabel(x, `period ${x.id}`);
  return { errors, hints };
}

/** Every stack worth checking: base · base+overlay · base+regional+pedagogical. */
export function standardStacks(packages) {
  const bases = [...packages].filter(([, d]) => (d.meta.kind ?? 'base') === 'base').map(([id]) => id).sort();
  const overlays = [...packages].filter(([, d]) => d.meta.kind === 'overlay');
  const fits = (o, b) => { const e = extendsOf(packages.get(o).meta); return e.includes('*') || e.includes(b); };
  const regional = overlays.filter(([, d]) => d.meta.region).map(([id]) => id).sort();
  const pedagogical = overlays.filter(([, d]) => !d.meta.region).map(([id]) => id).sort();
  const all = overlays.map(([id]) => id).sort();
  const out = bases.map((b) => [b]);
  for (const b of bases) {
    for (const o of all) if (fits(o, b)) out.push([b, o]);
    for (const r of regional) {
      if (!fits(r, b)) continue;
      for (const p of pedagogical) if (fits(p, b)) out.push([b, r, p]);
    }
  }
  return out;
}

/**
 * Convenience for a consumer: build and check one stack in one call.
 * Throws when the stack has errors – a package whose references point
 * nowhere must not be loaded.
 */
export function effective(ids, packages = loadAll()) {
  const eff = stack(ids, packages);
  const { errors, hints } = checkRefs(eff);
  if (errors.length) throw new Error(`stack ${ids.join('+')} has ${errors.length} error(s):\n  ${errors.join('\n  ')}`);
  return { effective: eff, hints };
}
