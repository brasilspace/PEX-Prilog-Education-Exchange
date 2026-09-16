/**
 * Proves that tools/pex.mjs and tools/validate.py agree – and pins the
 * merge semantics that the documentation promises.
 * Run: node --test tools/pex.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadAll, merge, stack, checkRefs, standardStacks, gradesForAge, subjectsOfProgram, effective, term } from './pex.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const packages = loadAll();

test('merge: scalars overwrite, id-lists merge by id, other lists replace', () => {
  const base = { a: 1, list: [{ id: 'x', l: 1, keep: true }, { id: 'y' }], plain: [1, 2, 3], obj: { k: 1, m: 2 } };
  const over = { a: 2, list: [{ id: 'x', l: 9 }, { id: 'z' }], plain: [4], obj: { k: 3 } };
  assert.deepEqual(merge(base, over), {
    a: 2, list: [{ id: 'x', l: 9, keep: true }, { id: 'y' }, { id: 'z' }], plain: [4], obj: { k: 3, m: 2 },
  });
});

test('disabled hides, it never deletes', () => {
  const eff = stack(['de', 'de-hh'], packages);
  const rs = eff.programs.find((p) => p.id === 'realschule');
  assert.equal(rs.disabled, true);
  const ob = eff.tracks.find((t) => t.id === 'oberstufe');
  assert.deepEqual(ob.levels.filter((l) => !l.disabled).map((l) => l.id), ['ea', 'ga']);
  assert.deepEqual(checkRefs(eff).errors, []);
});

test('an overlay that extends "*" binds subjects by age and fits every base', () => {
  for (const b of ['de', 'ch-de', 'at', 'us']) {
    const eff = stack([b, 'waldorf'], packages);
    const eu = eff.subjects.find((s) => s.id === 'eu');
    assert.ok(gradesForAge(eff, eu.age_from, eu.age_to).length >= 10, `${b}: eurythmy reaches grades`);
    assert.deepEqual(checkRefs(eff).errors, [], b);
  }
  const ch = stack(['ch-de', 'waldorf'], packages);
  // a 6-year-old is h3 in Switzerland (HarmoS counts kindergarten), g1 in Germany
  assert.deepEqual(gradesForAge(ch, 6, 6), ['h3']);
  assert.deepEqual(gradesForAge(stack(['de'], packages), 6, 6), ['g1']);
});

test('age_range upper bound is exclusive so Montessori programs tile without overlap', () => {
  const eff = stack(['de', 'montessori'], packages);
  const kh = eff.programs.find((p) => p.id === 'kinderhaus');
  const pr = eff.programs.find((p) => p.id === 'mont-primar');
  const a = subjectsOfProgram(eff, kh).map((s) => s.id);
  const b = subjectsOfProgram(eff, pr).map((s) => s.id);
  assert.ok(!a.includes('de'), 'Kinderhaus has no German lessons');
  assert.ok(b.includes('de'));
});

test('hiding a program does not force rewriting what mentions it', () => {
  const pk = new Map(packages);
  pk.set('schule', { meta: { format: 'pex', id: 'schule', version: '0.0.0', kind: 'overlay', extends: '*', country: 'XX', languages: ['de'], name: { de: 'Schule' } },
    programs: [{ id: 'berufslehre', disabled: true }] });
  const { errors } = checkRefs(stack(['ch-de', 'schule'], pk));
  assert.deepEqual(errors, []);
  // but an anchor to a disabled element is still an error
  pk.set('schule2', { meta: { format: 'pex', id: 'schule2', version: '0.0.0', kind: 'overlay', extends: '*', country: 'XX', languages: ['de'], name: { de: 'S' } },
    subject_domains: [{ id: 'music', disabled: true }] });
  assert.ok(checkRefs(stack(['ch-de', 'schule2'], pk)).errors.some((e) => e.includes("subject_domains 'music'")));
});

test('a stack whose references break is refused', () => {
  const broken = new Map(packages);
  broken.set('kaputt', { meta: { format: 'pex', id: 'kaputt', version: '0.0.1', kind: 'overlay', extends: 'de', country: 'DE', languages: ['de'], name: { de: 'x' } },
    subjects: [{ id: 'q', label: { de: 'Q' }, grades: ['g99'] }] });
  assert.throws(() => effective(['de', 'kaputt'], broken), /unknown grades 'g99'/);
});

test('terminology falls back gracefully', () => {
  const eff = stack(['at'], packages);
  assert.equal(term(eff, 'class_teacher', 'de'), 'Klassenvorstand');
  assert.equal(term(eff, 'does_not_exist', 'de', 'Standard'), 'Standard');
});

test('every standard stack is error-free', () => {
  for (const st of standardStacks(packages)) {
    const { errors } = checkRefs(stack(st, packages));
    assert.deepEqual(errors, [], st.join('+'));
  }
});

test('JavaScript and the Python reference produce identical effective packages (dist/)', () => {
  const index = JSON.parse(readFileSync(join(ROOT, 'dist', 'index.json'), 'utf8'));
  assert.equal(index.format, 'pex-index');
  const js = standardStacks(packages).map((s) => s.join('+')).sort();
  assert.deepEqual(index.stacks.map((s) => s.id).sort(), js, 'same set of stacks');
  for (const s of index.stacks) {
    const file = join(ROOT, s.file);
    assert.ok(existsSync(file), s.file);
    const py = JSON.parse(readFileSync(file, 'utf8'));
    const mine = stack(s.id.split('+'), packages);
    assert.deepEqual(mine, py, `effective ${s.id}`);
    assert.equal(checkRefs(mine).hints.length, s.hints, `hints ${s.id}`);
  }
});
