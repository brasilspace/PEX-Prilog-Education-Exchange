PEX – Prilog Education Exchange
Guide: Structure, Logic, and Writing Packages
Schema version 2.1 · As of 16 September 2026
---
1. What PEX Is – and What It Is Not
PEX is a JSON format that describes what an education system knows: which stages, grades, and programs exist, which subjects, tracks, and qualifications, how grading works, how the school year is structured, what things are called – and which rules and legal bases apply.
PEX does not describe how a specific school is organized. No class 7b, no course taught by Ms Meier, no individual student, no holiday date. That belongs to the tenant (see Organization Model and Enrollment).
The one rule that supports everything else:
> **A PEX never contains an instance.** It describes types, not things.
If, while writing a package, you want to enter something that exists exactly once (a specific school, a date, a person), it does not belong in PEX.
Second rule:
> **PEX does not calculate.** Rules, examinations, and legal references are stored as text with a source. Prilog reads them, displays them, and links to them. If someone wants to turn a rule into logic, they build a module that reads the rule.
---
2. The Files
File	Role
`pex.schema.json`	JSON Schema (Draft 2020-12) against which every PEX file is validated. `$id: https://prilog.chat/schemas/pex/v2.1`
`<id>.pex.json`	A package. `<id>` is the `meta.id`: `de`, `ch-de`, `de-hh`, `waldorf`
Every PEX file begins with the same two fields:
```json
{
  "meta": {
    "format": "pex",
    "schema": "https://prilog.chat/schemas/pex/v2.1",
    ...
```
This allows a loader to recognize the file by its contents rather than by its filename. A file without `format: "pex"` is rejected.
---
3. The Three Layers
A tenant never uses a single PEX, but rather a stack:
```
  Base PEX             de          ch-de        at          us
      ↓
  Regional overlay     de-hh       ch-zh        at-w        us-ca
      ↓
  Pedagogy overlay     waldorf / montessori   (can be placed on any base)
      ↓
  Tenant overrides     (the school itself, in the admin UI – technically the same format)
      ↓
  = effective PEX      (materialized, validated against the schema, read by the code)
```
All layers have the same structure. An overlay is a PEX with `meta.kind: "overlay"` and `meta.extends`, containing only what it changes or adds.
3.1 Merge Rules
The stack is merged from bottom to top:
Scalar fields (strings, numbers, booleans) – the higher layer overrides.
Objects without `id` (`terminology`, `calendar`, `grading` as a whole) – deep merge; keys from the higher layer override individually, missing keys remain.
Lists with `id` (`stages`, `grades`, `programs`, `tracks`, `qualifications`, `subjects`, `subject_domains`, `rules`, `exams`, `legal`, `scales`, `periods`) – merge by `id`, not append:
same `id` in both layers → the element is deep-merged (fields from the higher layer win, missing fields remain)
`id` only in the higher layer → the element is added
`id` only in the lower layer → the element remains
Hiding is possible only through `"disabled": true` on the element. There is no deletion – this keeps it traceable that Hamburg has abolished the Realschule rather than forgotten it.
Lists without `id` (`grades` on a subject, `aliases`, `levels`? – no, `levels` have `id`) – the higher layer replaces the list completely. If you want to extend a subject by one grade, you rewrite the entire `grades` list.
Example – an overlay changes only one field of a program:
```json
// Base de:
{ "id": "gymnasium", "label": {"de": "Gymnasium"}, "grades": ["g5",…,"g12"], "tracks": ["oberstufe"], … }

// Overlay de-by:
{ "id": "gymnasium", "grades": ["g5",…,"g13"], "tracks": ["gym-zweig", "oberstufe"] }

// Effective:
{ "id": "gymnasium", "label": {"de": "Gymnasium"}, "grades": ["g5",…,"g13"], "tracks": ["gym-zweig", "oberstufe"], … }
```
The label came from the base; `grades` and `tracks` were replaced (lists without `id`); everything else remained.
3.2 Pedagogy Overlays with `extends: "*"`
`waldorf` and `montessori` can be placed on any base. They may therefore only reference things that have the same IDs in all bases – or bring their own things. The Waldorf overlay includes its own subjects (`eu`, `gartenbau`, `ep-*`) and references grades as `g1`…`g13`; this works on `de`, but not on `ch-de` (`h3`…`h11`). This is a known issue: for Switzerland, Waldorf needs either a `waldorf-ch` overlay or a grade translation in the loader. Until that is resolved, the validator checks the stack and reports missing references.
3.3 Validation
Two stages:
File validation against `pex.schema.json` – structure, required fields, allowed values. Each file individually.
Stack validation after the merge – referential validation: every `id` that is referenced (`stage`, `grades[]`, `programs[]`, `tracks[]`, `qualifications[]`, `domain`, `qualification`, `scale`) must exist in the effective PEX and must not be `disabled`. Only then is the effective PEX materialized.
An overlay by itself cannot be validated referentially – it is allowed to reference its base.
---
4. The Building Blocks, in the Order You Read Them
All IDs are lowercase slugs (`^[a-z0-9][a-z0-9-]*$`), stable, and English or neutral (`sek1`, `gym`, `math`, `g7`). Code reads IDs.
All labels are objects such as `{ "de": "…", "fr": "…", "en": "…" }` – with at least one language from `meta.languages`. Humans read labels.
Aliases are free-form strings – alternative names under which the same thing appears in practice. They are used for search and display ("also known as"), never for references.
4.1 `meta` – Package Identity
```json
"meta": {
  "format": "pex", "schema": "…/pex/v2.1",
  "id": "de-hh", "version": "0.1.0",
  "kind": "overlay", "extends": "de",
  "country": "DE", "region": "HH",
  "languages": ["de"],
  "name": { "de": "Hamburg" },
  "source": "HmbSG, APO-GrundStGy …",
  "notes": "Zweigliedrig …"
}
```
`id` = filename without `.pex.json`. Convention: `<country>` for bases, `<country>-<region>` for regional overlays (ISO-3166-2 suffix), one word for pedagogy overlays.
`version` uses semver. Tenants pin a version; an update is a deliberate step with a diff.
`kind` = `base` or `overlay`; `extends` only for overlays.
`source` is the source reference for the whole package; individual `rules`/`exams`/`legal` entries have their own.
4.2 `terminology` – What Things Are Called
A flat object: stable key → multilingual label.
```json
"terminology": {
  "teacher": { "de": "Lehrperson" },
  "class_teacher": { "de": "Klassenlehrperson" },
  "parent_conference": { "de": "Elterngespräch" },
  "report_midyear": { "de": "Schulnachricht" }
}
```
The user interface asks for `terminology.class_teacher` and gets "Klassenleitung" in Hamburg, "Klassenlehrperson" in Zurich, "Klassenvorstand" in Vienna, and "Homeroom Teacher" in Ohio. If a key is missing, the platform default is used. Every package may introduce new keys; the interface uses them as soon as a module asks for them.
4.3 `calendar` – The Rhythm
```json
"calendar": {
  "year_start_month": 8,
  "periods": [ { "id": "s1", "label": {"de": "1. Semester"}, "months": [8, 1] }, … ],
  "report_points": ["s1", "s2"],
  "report_points_by_program": [ { "program": "primar", "report_points": ["s2"] } ],
  "holiday_authority": { "level": "canton", "label": {…}, "url": "…" }
}
```
Only the rhythm, never a specific date. `report_points` states when reports are produced; `holiday_authority` states who determines the holidays and where – the dates themselves are entered by the tenant, and Prilog can suggest them from that source.
4.4 `grading` – How Assessment Works
```json
"grading": {
  "default_scale": "ch-6",
  "scales": [
    { "id": "ch-6", "kind": "numeric", "values": [1,1.5,…,6], "step": 0.5, "best": 6, "pass": 4, "tendencies": false },
    { "id": "letter", "kind": "letter", "values": ["A","B","C","D","F"], "best": "A", "pass": "D", "gpa": {"A": 4.0, …} },
    { "id": "text", "kind": "text" }
  ],
  "head_marks": [ { "id": "sozial", "label": {"de": "Sozialverhalten"}, "scale": "de-6" } ],
  "by_program": [ { "program": "grundschule", "grades": ["g1","g2"], "scale": "text" } ]
}
```
`best` and `pass` are the two values a report module needs in order not to hard-code 6: in Germany, 1 is best; in Switzerland, 6 is best; in Austria, there is no grade 6. `by_program` handles the narrative-report case (text up to grade 2, grades thereafter).
4.5 `stages` and `grades` – The Vertical Axis
```json
"stages": [ { "id": "sec1", "label": {"de": "Sekundarstufe I"}, "ordinal": 3, "grades": ["h9","h10","h11"] } ],
"grades": [ { "id": "h9", "label": {"de": "7. Klasse"}, "ordinal": 9, "stage": "sec1", "typical_age": 12, "aliases": ["1. Sek"] } ]
```
The `id` is the system's stable numbering (`h1`–`h11` under HarmoS in Switzerland, school levels `s1`–`s13` in Austria, `k`,`g1`–`g12` in the USA). The `label` is the everyday numbering. Keeping these separate is intentional: Zurich says "1. Sek", Bern says "7. Klasse"; both refer to `h9`.
`ordinal` is used for sorting and is the only way to compare grades – never parse the `id`.
4.6 `programs` – Education Programs
```json
{ "id": "sek1", "label": {"de": "Sekundarschule"},
  "stages": ["sec1"], "grades": ["h9","h10","h11"],
  "class_model": "homeroom",
  "tracks": ["sek-level", "sek-subject-level"],
  "qualifications": ["sek1-abschluss"],
  "approval": "state",
  "aliases": ["Oberstufe", "Realschule", "Bezirksschule"] }
```
A program is an education pathway known to the system – not a school. A tenant can offer several programs.
`class_model` is the most important field: it tells the organization model what form of learning group this program usually creates.
Value	Meaning
`class`	fixed grade-based class, instruction mainly takes place in the class group
`homeroom`	homeroom group + courses with changing composition
`course`	no homeroom group, courses only
`mixed-age`	mixed-age, no fixed grade
`grades` may be empty – in that case the program has an `age_range`, and the grade level belongs to the individual person (report, transition), not to the group. This is how Montessori and kindergarten work without requiring a special case.
`approval` (relevant only for independent schools) states whether a program is state-run, recognized, approved, or authorized – this determines whether qualifications are examined internally or externally (see `exams`).
4.7 `tracks` – Tracks and Levels
```json
{ "id": "sek-subject-level", "label": {"de": "Niveaufach"},
  "scope": "enrollment",
  "levels": [ {"id": "e", "label": {"de": "erweitert"}}, {"id": "g", "label": {"de": "grundlegend"}} ] }
```
A track is a form of differentiation. What it attaches to is defined by `scope` – this is where PEX goes beyond a German class model:
`scope`	attaches to …	Examples
`learning_group`	the group – everyone in it is in the same track	Sek A/B/C as classes, M-Zug at the Mittelschule
`enrollment`	a person's participation in a course	Math level A, Leistungskurs, Honors/AP, Standard AHS (Austria)
`learner`	the person, independent of group and course	special education focus, accommodation, IEP
`program`	the program variant	long-term/short-term Gymnasium, NTG/SG/WSG in Bavaria
A program lists the tracks it knows. A subject with `tracked: true` states that an `enrollment` track applies to courses in this subject.
Rule of thumb: if two students in the same class can have different levels in one subject, it is `enrollment`. If the level defines the class, it is `learning_group`.
4.8 `qualifications` – Qualifications
```json
{ "id": "matura", "label": {"de": "Reifeprüfung (Matura)"},
  "after_grade": "s12", "programs": ["ahs-o"],
  "grants_access": ["universitaet", "fh", "ph"],
  "requirements": { … free-form … } }
```
`grants_access` is a free-form list of onward destinations – for guidance and display, not logic. `requirements` is a free-form object (credits per domain in the USA, subject requirements for the Abitur) – anything evaluating it must know what is stored there.
4.9 `subject_domains` and `subjects` – Subjects
```json
{ "id": "nt", "label": {"de": "Natur und Technik"}, "domain": "science",
  "grades": ["h9","h10","h11"], "programs": ["sek1"],
  "kind": "core", "tracked": true, "optional": false,
  "credits": 1, "aliases": ["Naturlehre"] }
```
`domain` groups subjects (languages, sciences, etc.) – for timetables, reports, and qualification requirements.
`grades` and `programs` state where the subject occurs. If `programs` is omitted, it applies to all programs containing those grades.
`kind`: `core` (required), `elective` (elective / compulsory elective), `project` (annual project, Matura project, seminar), `remedial` (remedial/support course), `epoch` (Waldorf block/epoch).
`optional: true` means not every person has to take it.
`credits` only where the system uses credits (USA).
The same thing may be one subject in one country and three in another (NT vs. Biology/Chemistry/Physics). This is intentional: PEX represents the system, not a normalized subject catalog. A module searching for "the subject Biology" will not find it in Switzerland – it must use `domain: science`.
4.10 `rules` – Rules with Sources (v2.1)
```json
{ "id": "uebertritt-5", "kind": "transition",
  "label": {"de": "Übertritt nach Jahrgangsstufe 4"},
  "applies_to": { "from_grade": "g4" },
  "mode": "binding-recommendation",
  "summary": {"de": "Übertrittszeugnis im Mai: Gymnasium bei Notenschnitt bis 2,33 …"},
  "source": "BayEUG Art. 44; GrSO §§ 6–8", "url": "…" }
```
`kind` states what the rule concerns (`transition`, `admission`, `compulsory-schooling`, `promotion`, `subject-choice`, `attendance`, `other`). `mode` is a short keyword that makes the rule filterable without turning it into logic (`parent-choice`, `binding-recommendation`, `exam`, `grade-threshold`, etc.). `summary` is the text read by a human. `source` is required.
Prilog displays rules in the appropriate place – in transition counseling, enrollment, or compliance reports. It does not calculate with them.
4.11 `exams` – Examinations (v2.1)
```json
{ "id": "abitur-extern", "label": {"de": "Abitur für andere Bewerber"},
  "qualification": "abitur", "mode": "external", "at_grade": "g13",
  "components": [ {"id": "written", "count": 4}, {"id": "oral", "count": 4} ],
  "summary": {"de": "Waldorfschüler an genehmigten Ersatzschulen legen das Abitur als Externe ab …"},
  "source": "GSO §§ 88 ff." }
```
`mode`: `internal` (in-house), `external` (external candidate examination), `central` (centrally set), `state-recognized` (in-house under state supervision). This is the block that captures the important distinction for independent schools – it determines annual planning and subjects in the final year.
4.12 `legal` – Legal References (v2.1)
```json
{ "id": "schulgesetz", "kind": "school-act",
  "label": {"de": "Hamburgisches Schulgesetz"}, "url": "…",
  "sections": { "schulpflicht": "§§ 37–41", "datenschutz": "§§ 98–100" } }
```
`kind`: `school-act`, `data-protection`, `authority`, `retention`, `reporting`, `private-school`, `other`. This is one place for legal references that would otherwise be repeated in every module – the data protection handbook, concept anchoring, and compliance report read from here.
---
5. The Logic Behind the Decisions
Why English IDs and multilingual labels? So code can ask the same question across countries (`grades` with `stage: sec1`) while the interface can still display "7. Klasse" or "1. Sek".
Why overlays instead of variants? 16 German states × 26 Swiss cantons × Waldorf/Montessori would result in hundreds of packages. As a stack, there are 4 bases + around 50 small overlays + 2 pedagogy overlays. And if Bavaria introduces G9, one line changes in `de-by`, not in every Bavarian Waldorf package.
Why `disabled` instead of deletion? Because the absence of something is itself a statement. "Hamburg has no Realschule" must remain visible.
Why merge lists by `id`? Because an overlay should be able to extend a program by one field without rewriting the whole program – and because this makes it traceable which parts come from the base and which are regional.
Why is `class_model` on the program rather than the school? Because a boarding school may offer Sek I (`homeroom`) and Gymnasium (`class`) at the same time. The form of the group follows the education program.
Why track scopes instead of "track on subject"? Because a level is not a property of the subject Mathematics; it is a property of this student's participation in this course. Once stated that way, it becomes clear that an enrollment object is needed – on the tenant side.
Why rules as text? Because a transition rule involving grade average, trial lessons, and parental choice differs by region and can change with each legislative term. As text with a source, it is maintainable; as logic, it would become a product of its own.
Why no curriculum hour tables? Because weekly lesson hours per subject fluctuate from year to year, may be school-autonomous, and belong in the timetable. PEX says that Mathematics exists in grade 7 – not how often it is taught.
---
6. Writing an Overlay – Step by Step
Choose and read the base. Anything already correct there is not repeated.
Write `meta`: `kind: overlay`, `extends`, `region`, `source`.
What is different? Check in this order: programs (which exist, which do not → `disabled`), grade boundaries (G8/G9, primary school through grade 6), tracks, qualifications and their names, subjects (names as `aliases`, new subjects, different grades), grading scale and report rhythm, terminology.
Rules, examinations, law – one entry each with `source`. Transition, compulsory schooling, qualification exam (internal/external), school act, data protection, supervision, retention.
Change only what changes. An overlay with 300 lines is usually a copied base.
Validate: first the file against the schema, then the stack referentially.
Version it and commit it to the `prilog-pex` repository with review.
Checklist before merge:
[ ] Every `id` that is referenced exists in the base or overlay
[ ] No element with `disabled: true` is still referenced
[ ] Every `rule`, `exam`, and `legal` entry has a `source`
[ ] No instances (school names, dates, persons)
[ ] Labels in all languages from `meta.languages`
[ ] `notes` explains what is not obvious to humans from the structure itself
---
7. How Prilog Reads the Effective PEX
Module	asks for
Tenant setup	`programs`, `class_model`, `grades` → suggestion for learning groups
Create learning group	`programs`, `grades` (or `age_range`), `tracks` with `scope: learning_group`
Enrollment	`tracks` with `scope: enrollment`, `subjects.tracked`
Subject catalog / timetable	`subjects` filtered by program and grade
Report	`grading` (scale, `best`, `pass`, `by_program`, `head_marks`), `calendar.report_points`, `qualifications`, `exams`
User interface	`terminology.*`
Annual cycle	`calendar.periods`
Parent-teacher conference	`terminology.parent_conference`; teachers from enrollments
Transition counseling, admissions	`rules` with `kind: transition
Data protection handbook, compliance report	`legal`
Concept anchoring	`meta.country/region` → editorial team
The code always reads the tenant's materialized effective PEX (`tenant_pex.effective_json`), never the individual files. A tenant sees a package change only after explicitly adopting the new version.
---
8. Common Mistakes
Mistake	Why it is wrong	Correct approach
Searching for the subject "Biology" in the Swiss package	In Switzerland it is called NT and combines three subjects	use `domain: science`
"Extending" `grades` on a subject	Lists without `id` are replaced, not merged	write the entire list in the overlay
Omitting Realschule in Hamburg	The base contains it; omission changes nothing	`{"id": "realschule", "disabled": true}`
Writing the grade average 2.33 as a number in `rules`	PEX does not calculate; the number belongs in the `summary` text	text + `source`
Waldorf overlay references `g7` on `ch-de`	Swiss grades use IDs such as `h9`	separate `waldorf-ch` or grade translation
Holiday dates in the package	Instance	tenant; `holiday_authority.url` as source
`id` with uppercase letters or umlaut	The schema rejects it	`sek-level`, not `Sek_A`
Overlay with 300 lines	copied base	only the changes
---
9. Versions
Schema	Change
v1	`school_types`, track scopes `class`/`subject`
v2	`programs`, optional `grades` + `age_range`, `class_model` with `mixed-age`, track scopes `learning_group`/`enrollment`/`learner`/`program`, required `meta.format`
v2.1	`rules`, `exams`, `legal`; `grading.tendencies`/`head_marks`/`by_program`; `calendar.report_points_by_program`/`holiday_authority`; `programs.approval`
A package names the schema version it was written against in `meta.schema`. The loader accepts v2 and v2.1; v1 is translated during loading.



____________________________________________________________________

# PEX – Prilog Education Exchange
## Anleitung: Aufbau, Logik und Schreiben von Paketen

Schema-Version 2.1 · Stand 16.09.2026

---

## 1. Was PEX ist – und was nicht

PEX ist ein JSON-Format, das beschreibt, **was ein Bildungssystem kennt**: welche Stufen, Jahrgänge und Programme es gibt, welche Fächer, Züge und Abschlüsse, wie benotet wird, wie das Schuljahr getaktet ist, wie die Dinge heißen – und welche Regeln und Rechtsgrundlagen dahinterstehen.

PEX beschreibt **nicht, wie eine konkrete Schule organisiert ist**. Keine Klasse 7b, kein Kurs bei Frau Meier, keine Schülerin, kein Ferientermin. Das ist Sache des Mandanten (siehe *Organisationsmodell und Einschreibung*).

Die eine Regel, die alles andere trägt:

> **Ein PEX enthält niemals eine Instanz.** Es beschreibt Typen, nicht Dinge.

Wenn du beim Schreiben eines Pakets etwas eintragen willst, das es genau einmal gibt (eine bestimmte Schule, ein Datum, eine Person), gehört es nicht ins PEX.

Zweite Regel:

> **PEX rechnet nicht.** Regeln, Prüfungen und Rechtsbezüge stehen als Text mit Quelle. Prilog liest sie an, zeigt sie an und verlinkt sie. Wer aus einer Regel Logik machen will, baut ein Modul, das die Regel liest.

---

## 2. Die Dateien

| Datei | Rolle |
|---|---|
| `pex.schema.json` | JSON-Schema (Draft 2020-12), gegen das jede PEX-Datei geprüft wird. `$id: https://prilog.chat/schemas/pex/v2.1` |
| `<id>.pex.json` | Ein Paket. `<id>` ist die `meta.id`: `de`, `ch-de`, `de-hh`, `waldorf` |

Jede PEX-Datei beginnt mit denselben zwei Feldern:

```json
{
  "meta": {
    "format": "pex",
    "schema": "https://prilog.chat/schemas/pex/v2.1",
    ...
```

Damit erkennt ein Loader die Datei am Inhalt, nicht am Namen. Eine Datei ohne `format: "pex"` wird abgelehnt.

---

## 3. Die drei Schichten

Ein Mandant benutzt nie ein einzelnes PEX, sondern einen **Stapel**:

```
  Basis-PEX          de          ch-de        at          us
       ↓
  Regionales Overlay de-hh       ch-zh        at-w        us-ca
       ↓
  Pädagogik-Overlay  waldorf / montessori   (auf jede Basis legbar)
       ↓
  Mandanten-Overrides   (die Schule selbst, im Admin-UI – technisch dasselbe Format)
       ↓
  = effektives PEX   (materialisiert, gegen das Schema geprüft, vom Code gelesen)
```

Alle Schichten haben **dieselbe Struktur**. Ein Overlay ist ein PEX mit `meta.kind: "overlay"` und `meta.extends`, das nur enthält, was es ändert oder ergänzt.

### 3.1 Merge-Regeln

Der Stapel wird von unten nach oben zusammengeführt:

1. **Skalare Felder** (Strings, Zahlen, Booleans) – die höhere Schicht überschreibt.
2. **Objekte ohne `id`** (`terminology`, `calendar`, `grading` als Ganzes) – tiefer Merge; Schlüssel der höheren Schicht überschreiben einzeln, fehlende bleiben.
3. **Listen mit `id`** (`stages`, `grades`, `programs`, `tracks`, `qualifications`, `subjects`, `subject_domains`, `rules`, `exams`, `legal`, `scales`, `periods`) – **Merge nach `id`**, nicht Anhängen:
   - gleiche `id` in beiden Schichten → das Element wird tief gemergt (Felder der höheren Schicht gewinnen, fehlende bleiben)
   - `id` nur in der höheren Schicht → Element wird hinzugefügt
   - `id` nur in der tieferen Schicht → Element bleibt
4. **Ausblenden** geht nur über `"disabled": true` am Element. Es gibt kein Löschen – so bleibt nachvollziehbar, dass Hamburg die Realschule *abgeschafft* hat und nicht *vergessen*.
5. **Listen ohne `id`** (`grades` an einem Fach, `aliases`, `levels`? – nein, `levels` haben `id`) – die höhere Schicht **ersetzt** die Liste komplett. Wer ein Fach um einen Jahrgang erweitern will, schreibt die ganze `grades`-Liste neu.

Beispiel – Overlay ändert nur ein Feld eines Programms:

```json
// Basis de:
{ "id": "gymnasium", "label": {"de": "Gymnasium"}, "grades": ["g5",…,"g12"], "tracks": ["oberstufe"], … }

// Overlay de-by:
{ "id": "gymnasium", "grades": ["g5",…,"g13"], "tracks": ["gym-zweig", "oberstufe"] }

// effektiv:
{ "id": "gymnasium", "label": {"de": "Gymnasium"}, "grades": ["g5",…,"g13"], "tracks": ["gym-zweig", "oberstufe"], … }
```

Das Label kam aus der Basis, `grades` und `tracks` wurden ersetzt (Listen ohne `id`), alles andere blieb.

### 3.2 Pädagogik-Overlays mit `extends: "*"`

`waldorf` und `montessori` legen sich auf **jede** Basis. Sie dürfen deshalb nur Dinge referenzieren, die in allen Basen gleich heißen – oder eigene Dinge mitbringen. Das Waldorf-Overlay bringt seine Fächer selbst mit (`eu`, `gartenbau`, `ep-*`) und referenziert Jahrgänge als `g1`…`g13`; das funktioniert auf `de`, aber **nicht** auf `ch-de` (`h3`…`h11`). Das ist ein bekannter Punkt: Für die Schweiz braucht Waldorf entweder ein `waldorf-ch`-Overlay oder eine Jahrgangs-Übersetzung im Loader. Solange das offen ist, prüft der Validator beim Stapeln und meldet fehlende Referenzen.

### 3.3 Validierung

Zwei Stufen:

- **Datei-Validierung** gegen `pex.schema.json` – Struktur, Pflichtfelder, erlaubte Werte. Jede Datei einzeln.
- **Stapel-Validierung** nach dem Merge – referenzielle Prüfung: Jede `id`, auf die verwiesen wird (`stage`, `grades[]`, `programs[]`, `tracks[]`, `qualifications[]`, `domain`, `qualification`, `scale`), muss im effektiven PEX existieren und nicht `disabled` sein. Erst danach wird das effektive PEX materialisiert.

Ein Overlay allein ist referenziell **nicht** prüfbar – es darf auf die Basis verweisen.

---

## 4. Die Bausteine, in der Reihenfolge, in der man sie liest

Alle **IDs** sind kleingeschriebene Slugs (`^[a-z0-9][a-z0-9-]*$`), stabil und englisch oder neutral (`sek1`, `gym`, `math`, `g7`). Code liest IDs.
Alle **Labels** sind Objekte `{ "de": "…", "fr": "…", "en": "…" }` – mindestens eine Sprache aus `meta.languages`. Menschen lesen Labels.
**Aliases** sind freie Strings – andere Namen, unter denen dasselbe Ding in der Praxis vorkommt. Sie dienen der Suche und der Anzeige („auch bekannt als"), nie der Referenz.

### 4.1 `meta` – Identität des Pakets

```json
"meta": {
  "format": "pex", "schema": "…/pex/v2.1",
  "id": "de-hh", "version": "0.1.0",
  "kind": "overlay", "extends": "de",
  "country": "DE", "region": "HH",
  "languages": ["de"],
  "name": { "de": "Hamburg" },
  "source": "HmbSG, APO-GrundStGy …",
  "notes": "Zweigliedrig …"
}
```

- `id` = Dateiname ohne `.pex.json`. Konvention: `<land>` für Basen, `<land>-<region>` für regionale Overlays (ISO-3166-2-Suffix), ein Wort für Pädagogik-Overlays.
- `version` semver. Mandanten pinnen eine Version; ein Update ist ein bewusster Schritt mit Diff.
- `kind` = `base` oder `overlay`; `extends` nur bei Overlay.
- `source` ist die Quellenangabe für das ganze Paket; einzelne `rules`/`exams`/`legal` haben ihre eigene.

### 4.2 `terminology` – wie die Dinge heißen

Ein flaches Objekt: stabiler Schlüssel → mehrsprachiges Label.

```json
"terminology": {
  "teacher": { "de": "Lehrperson" },
  "class_teacher": { "de": "Klassenlehrperson" },
  "parent_conference": { "de": "Elterngespräch" },
  "report_midyear": { "de": "Schulnachricht" }
}
```

Die Oberfläche fragt `terminology.class_teacher` und bekommt in Hamburg „Klassenleitung", in Zürich „Klassenlehrperson", in Wien „Klassenvorstand", in Ohio „Homeroom Teacher". Fehlt ein Schlüssel, greift der Plattform-Standard. Neue Schlüssel darf jedes Paket einführen; die Oberfläche benutzt sie, sobald ein Modul danach fragt.

### 4.3 `calendar` – der Takt

```json
"calendar": {
  "year_start_month": 8,
  "periods": [ { "id": "s1", "label": {"de": "1. Semester"}, "months": [8, 1] }, … ],
  "report_points": ["s1", "s2"],
  "report_points_by_program": [ { "program": "primar", "report_points": ["s2"] } ],
  "holiday_authority": { "level": "canton", "label": {…}, "url": "…" }
}
```

Nur der **Rhythmus**, nie ein Datum. `report_points` sagt, wann Zeugnisse entstehen; `holiday_authority` sagt, wer die Ferien festlegt und wo – die Termine selbst trägt der Mandant ein, Prilog kann sie von dort vorschlagen.

### 4.4 `grading` – wie bewertet wird

```json
"grading": {
  "default_scale": "ch-6",
  "scales": [
    { "id": "ch-6", "kind": "numeric", "values": [1,1.5,…,6], "step": 0.5, "best": 6, "pass": 4, "tendencies": false },
    { "id": "letter", "kind": "letter", "values": ["A","B","C","D","F"], "best": "A", "pass": "D", "gpa": {"A": 4.0, …} },
    { "id": "text", "kind": "text" }
  ],
  "head_marks": [ { "id": "sozial", "label": {"de": "Sozialverhalten"}, "scale": "de-6" } ],
  "by_program": [ { "program": "grundschule", "grades": ["g1","g2"], "scale": "text" } ]
}
```

`best` und `pass` sind die zwei Zahlen, die ein Zeugnismodul braucht, um nicht die 6 hart zu codieren: In Deutschland ist 1 best, in der Schweiz 6, in Österreich gibt es keine 6. `by_program` löst den Berichtszeugnis-Fall (Text bis Klasse 2, Noten danach).

### 4.5 `stages` und `grades` – die vertikale Achse

```json
"stages": [ { "id": "sec1", "label": {"de": "Sekundarstufe I"}, "ordinal": 3, "grades": ["h9","h10","h11"] } ],
"grades": [ { "id": "h9", "label": {"de": "7. Klasse"}, "ordinal": 9, "stage": "sec1", "typical_age": 12, "aliases": ["1. Sek"] } ]
```

Die `id` ist die stabile Zählung des Systems (HarmoS `h1`–`h11` in der Schweiz, Schulstufen `s1`–`s13` in Österreich, `k`,`g1`–`g12` in den USA). Das `label` ist die Alltagszählung. Beides zu trennen ist Absicht: Zürich sagt „1. Sek", Bern „7. Klasse", beide meinen `h9`.

`ordinal` ist die Sortierung und der einzige Weg, Jahrgänge zu vergleichen – nie die `id` parsen.

### 4.6 `programs` – die Bildungsgänge

```json
{ "id": "sek1", "label": {"de": "Sekundarschule"},
  "stages": ["sec1"], "grades": ["h9","h10","h11"],
  "class_model": "homeroom",
  "tracks": ["sek-level", "sek-subject-level"],
  "qualifications": ["sek1-abschluss"],
  "approval": "state",
  "aliases": ["Oberstufe", "Realschule", "Bezirksschule"] }
```

Ein Programm ist ein Bildungsgang, den das System kennt – nicht eine Schule. Ein Mandant kann mehrere führen.

**`class_model`** ist die wichtigste Angabe: Sie sagt dem Organisationsmodell, welche Form von Lerngruppe dieses Programm normalerweise bildet.

| Wert | Bedeutung |
|---|---|
| `class` | feste Jahrgangsklasse, Unterricht überwiegend im Verband |
| `homeroom` | Stammgruppe + Kurse in wechselnder Zusammensetzung |
| `course` | keine Stammgruppe, nur Kurse |
| `mixed-age` | altersgemischt, keine feste Jahrgangsstufe |

**`grades` darf leer sein** – dann trägt das Programm eine `age_range`, und die Jahrgangsstufe ist Sache der einzelnen Person (Zeugnis, Übertritt), nicht der Gruppe. So funktionieren Montessori und Kindergarten ohne Sonderfall.

**`approval`** (nur für freie Schulen relevant) sagt, ob ein Programm staatlich, anerkannt, genehmigt oder bewilligt ist – das entscheidet, ob Abschlüsse im Haus oder extern geprüft werden (siehe `exams`).

### 4.7 `tracks` – Züge und Niveaus

```json
{ "id": "sek-subject-level", "label": {"de": "Niveaufach"},
  "scope": "enrollment",
  "levels": [ {"id": "e", "label": {"de": "erweitert"}}, {"id": "g", "label": {"de": "grundlegend"}} ] }
```

Ein Zug ist eine Differenzierung. **Woran er hängt, sagt `scope`** – das ist die Stelle, an der PEX mehr kann als ein deutsches Klassenmodell:

| `scope` | hängt an … | Beispiele |
|---|---|---|
| `learning_group` | der Gruppe – alle darin sind im selben Zug | Sek A/B/C als Klassen, M-Zug an der Mittelschule |
| `enrollment` | der Teilnahme einer Person an einem Kurs | Mathe Niveau A, Leistungskurs, Honors/AP, Standard AHS (Österreich) |
| `learner` | der Person, unabhängig von Gruppe und Kurs | Förderschwerpunkt, Nachteilsausgleich, IEP |
| `program` | der Programmvariante | Langzeit-/Kurzzeitgymnasium, NTG/SG/WSG in Bayern |

Ein Programm listet die Züge, die es kennt. Ein Fach mit `tracked: true` sagt: Für Kurse dieses Fachs gilt ein `enrollment`-Zug.

Faustregel: Wenn zwei Schüler derselben Klasse in einem Fach verschiedene Niveaus haben können, ist es `enrollment`. Wenn das Niveau die Klasse definiert, ist es `learning_group`.

### 4.8 `qualifications` – Abschlüsse

```json
{ "id": "matura", "label": {"de": "Reifeprüfung (Matura)"},
  "after_grade": "s12", "programs": ["ahs-o"],
  "grants_access": ["universitaet", "fh", "ph"],
  "requirements": { … frei … } }
```

`grants_access` ist eine freie Liste von Anschlusszielen – für Beratung und Anzeige, keine Logik. `requirements` ist ein freies Objekt (Credits je Domain in den USA, Fächerbindung beim Abitur) – wer es auswertet, muss wissen, was drinsteht.

### 4.9 `subject_domains` und `subjects` – die Fächer

```json
{ "id": "nt", "label": {"de": "Natur und Technik"}, "domain": "science",
  "grades": ["h9","h10","h11"], "programs": ["sek1"],
  "kind": "core", "tracked": true, "optional": false,
  "credits": 1, "aliases": ["Naturlehre"] }
```

- `domain` gruppiert (Sprachen, Naturwissenschaften …) – für Stundentafeln, Zeugnisse, Abschlussanforderungen.
- `grades` und `programs` sagen, wo das Fach vorkommt. Fehlt `programs`, gilt es für alle Programme, die diese Jahrgänge haben.
- `kind`: `core` (Pflicht), `elective` (Wahl/Wahlpflicht), `project` (Jahresarbeit, Maturaarbeit, Seminar), `remedial` (Förder-/Stützkurs), `epoch` (Waldorf-Epoche).
- `optional: true` heißt: Es muss nicht jede Person belegen.
- `credits` nur, wo das System in Credits rechnet (USA).

Dieselbe Sache, die in einem Land ein Fach ist, ist im anderen drei (NT vs. Biologie/Chemie/Physik). Das ist gewollt: PEX bildet das System ab, nicht eine Norm-Fächerliste. Ein Modul, das „das Fach Biologie" sucht, sucht in der Schweiz vergebens – es muss über `domain: science` gehen.

### 4.10 `rules` – Regeln mit Quelle (v2.1)

```json
{ "id": "uebertritt-5", "kind": "transition",
  "label": {"de": "Übertritt nach Jahrgangsstufe 4"},
  "applies_to": { "from_grade": "g4" },
  "mode": "binding-recommendation",
  "summary": {"de": "Übertrittszeugnis im Mai: Gymnasium bei Notenschnitt bis 2,33 …"},
  "source": "BayEUG Art. 44; GrSO §§ 6–8", "url": "…" }
```

`kind` sagt, wovon die Regel handelt (`transition`, `admission`, `compulsory-schooling`, `promotion`, `subject-choice`, `attendance`, `other`). `mode` ist ein kurzes Stichwort, das die Regel filterbar macht, ohne sie zur Logik zu machen (`parent-choice`, `binding-recommendation`, `exam`, `grade-threshold` …). `summary` ist der Text, den ein Mensch liest. `source` ist Pflicht.

Prilog zeigt Regeln an der passenden Stelle – im Übertrittsgespräch, in der Anmeldung, im Nachweisbericht. Es rechnet nicht mit ihnen.

### 4.11 `exams` – Prüfungen (v2.1)

```json
{ "id": "abitur-extern", "label": {"de": "Abitur für andere Bewerber"},
  "qualification": "abitur", "mode": "external", "at_grade": "g13",
  "components": [ {"id": "written", "count": 4}, {"id": "oral", "count": 4} ],
  "summary": {"de": "Waldorfschüler an genehmigten Ersatzschulen legen das Abitur als Externe ab …"},
  "source": "GSO §§ 88 ff." }
```

`mode`: `internal` (im Haus), `external` (Schulfremdenprüfung), `central` (zentral gestellt), `state-recognized` (im Haus unter staatlichem Vorsitz). Das ist der Block, der für freie Schulen den Unterschied macht – er bestimmt Jahresplanung und Fächer der Abschlussklasse.

### 4.12 `legal` – Rechtsbezüge (v2.1)

```json
{ "id": "schulgesetz", "kind": "school-act",
  "label": {"de": "Hamburgisches Schulgesetz"}, "url": "…",
  "sections": { "schulpflicht": "§§ 37–41", "datenschutz": "§§ 98–100" } }
```

`kind`: `school-act`, `data-protection`, `authority`, `retention`, `reporting`, `private-school`, `other`. Ein Ort für die Rechtsbezüge, die sonst in jedem Modul neu stehen – Datenschutz-Handbuch, Konzept-Verankerung und Nachweisbericht lesen von hier.

---

## 5. Die Logik hinter den Entscheidungen

**Warum IDs englisch und Labels mehrsprachig?** Damit Code über Länder hinweg dieselbe Frage stellen kann (`grades` mit `stage: sec1`) und die Oberfläche trotzdem „7. Klasse" oder „1. Sek" zeigt.

**Warum Overlays statt Varianten?** 16 Bundesländer × 26 Kantone × Waldorf/Montessori wären hunderte Pakete. Als Stapel sind es 4 Basen + ~50 kleine Overlays + 2 Pädagogik-Overlays. Und: Wenn Bayern G9 einführt, ändert sich eine Zeile in `de-by`, nicht in jedem bayerischen Waldorf-Paket.

**Warum `disabled` statt Löschen?** Weil die Abwesenheit einer Sache eine Aussage ist. „Hamburg hat keine Realschule" muss man sehen können.

**Warum Listen-Merge nach `id`?** Weil ein Overlay ein Programm um ein Feld erweitern soll, ohne es ganz neu zu schreiben – und weil sich so nachvollziehen lässt, was aus der Basis kommt und was regional ist.

**Warum `class_model` am Programm und nicht an der Schule?** Weil ein Internat Sek I (`homeroom`) und Gymnasium (`class`) zugleich führt. Die Form der Gruppe folgt dem Bildungsgang.

**Warum Zug-Scopes statt „Zug am Fach"?** Weil ein Niveau keine Eigenschaft des Fachs Mathematik ist, sondern der Teilnahme *dieser* Schülerin an *diesem* Kurs. Sobald man das so sagt, ist klar, dass es ein Einschreibungs-Objekt braucht – auf der Mandantenseite.

**Warum Regeln als Text?** Weil eine Übertrittsregel mit Notenschnitt, Probeunterricht und Elternwille als Logik in jedem Bundesland anders wäre und sich jede Legislatur ändert. Als Text mit Quelle ist sie pflegbar; als Logik wäre sie ein eigenes Produkt.

**Warum keine Stundentafeln?** Weil Wochenstunden je Fach jährlich schwanken, schulautonom sind und in den Stundenplan gehören. PEX sagt, dass es Mathematik in der 7. gibt – nicht, wie oft.

---

## 6. Ein Overlay schreiben – Schritt für Schritt

1. **Basis wählen** und lesen. Alles, was dort schon stimmt, wird nicht wiederholt.
2. `meta` schreiben: `kind: overlay`, `extends`, `region`, `source`.
3. **Was ist anders?** In dieser Reihenfolge prüfen: Programme (welche gibt es, welche nicht → `disabled`), Jahrgangsgrenzen (G8/G9, Grundschule 6), Züge, Abschlüsse und ihre Namen, Fächer (Namen als `aliases`, neue Fächer, andere Jahrgänge), Notenskala und Zeugnisrhythmus, Begriffe.
4. **Regeln, Prüfungen, Recht** – je eine Zeile mit `source`. Übertritt, Schulpflicht, Abschlussprüfung (intern/extern), Schulgesetz, Datenschutz, Aufsicht, Aufbewahrung.
5. **Nur ändern, was sich ändert.** Ein Overlay mit 300 Zeilen ist meist eine kopierte Basis.
6. **Validieren**: Datei gegen das Schema, dann den Stapel referenziell.
7. **Versionieren** und ins Repo `prilog-pex` mit Review.

Checkliste vor dem Merge:

- [ ] Jede `id`, auf die verwiesen wird, existiert in Basis oder Overlay
- [ ] Kein Element mit `disabled: true` wird noch referenziert
- [ ] Jede `rule`, `exam`, `legal` hat `source`
- [ ] Keine Instanzen (Schulnamen, Daten, Personen)
- [ ] Labels in allen Sprachen aus `meta.languages`
- [ ] `notes` erklärt, was für Menschen nicht aus der Struktur ersichtlich ist

---

## 7. Wie Prilog das effektive PEX liest

| Modul | fragt |
|---|---|
| Mandanten-Setup | `programs`, `class_model`, `grades` → Vorschlag für Lerngruppen |
| Lerngruppe anlegen | `programs`, `grades` (oder `age_range`), `tracks` mit `scope: learning_group` |
| Einschreibung | `tracks` mit `scope: enrollment`, `subjects.tracked` |
| Fachkatalog / Stundenplan | `subjects` gefiltert nach Programm und Jahrgang |
| Zeugnis | `grading` (Skala, `best`, `pass`, `by_program`, `head_marks`), `calendar.report_points`, `qualifications`, `exams` |
| Oberfläche | `terminology.*` |
| Jahreslauf | `calendar.periods` |
| Elternsprechtag | `terminology.parent_conference`; Lehrkräfte aus Einschreibungen |
| Übertrittsberatung, Anmeldung | `rules` mit `kind: transition | admission` |
| Datenschutz-Handbuch, Nachweisbericht | `legal` |
| Konzept-Verankerung | `meta.country/region` → Fachredaktion |

Der Code liest immer das **materialisierte effektive PEX** des Mandanten (`tenant_pex.effective_json`), nie die Einzeldateien. Ein Mandant sieht eine Änderung an einem Paket erst, wenn er die neue Version bewusst übernimmt.

---

## 8. Häufige Fehler

| Fehler | Warum falsch | Richtig |
|---|---|---|
| Fach „Biologie" im Schweizer Paket suchen | In der Schweiz heißt es NT und umfasst drei Fächer | über `domain: science` gehen |
| `grades` an einem Fach „ergänzen" | Listen ohne `id` werden ersetzt, nicht gemergt | die ganze Liste im Overlay schreiben |
| Realschule in Hamburg weglassen | Basis hat sie, Weglassen ändert nichts | `{"id": "realschule", "disabled": true}` |
| Notenschnitt 2,33 als Zahl in `rules` | PEX rechnet nicht; die Zahl gehört in den `summary`-Text | Text + `source` |
| Waldorf-Overlay referenziert `g7` auf `ch-de` | Schweizer Jahrgänge heißen `h9` | eigenes `waldorf-ch` oder Jahrgangs-Übersetzung |
| Ferientermine im Paket | Instanz | Mandant; `holiday_authority.url` als Quelle |
| `id` mit Großbuchstaben oder Umlaut | Schema lehnt ab | `sek-level`, nicht `Sek_A` |
| Overlay mit 300 Zeilen | kopierte Basis | nur die Änderungen |

---

## 9. Versionen

| Schema | Änderung |
|---|---|
| v1 | `school_types`, Track-Scopes `class`/`subject` |
| v2 | `programs`, `grades` optional + `age_range`, `class_model` mit `mixed-age`, Track-Scopes `learning_group`/`enrollment`/`learner`/`program`, `meta.format` Pflicht |
| v2.1 | `rules`, `exams`, `legal`; `grading.tendencies`/`head_marks`/`by_program`; `calendar.report_points_by_program`/`holiday_authority`; `programs.approval` |

Ein Paket nennt in `meta.schema` die Version, gegen die es geschrieben ist. Der Loader akzeptiert v2 und v2.1; v1 wird beim Laden übersetzt.
