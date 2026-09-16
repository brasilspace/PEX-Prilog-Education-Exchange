# Changelog

## 2.2.3 – 2026-09-17
- Mehrsystem-Haus: `stackHouse` (JS) / `stack_house` (Python) baut EIN effektives Paket für ein Haus mit mehreren Schulsystemen – Hauptsystem zuerst (gewinnt bei gleichen ids), weitere Basen dazu, Overlays, die über irgendeine Basis passen, in Reihenfolge; `meta.languages` als Vereinigung. Grund: Ecole (Schweizer Weg + US-Weg) verweist in einem Override auf Jahrgänge beider Systeme
- Prüfung: Regeln und Prüfungen, deren `applies_to`/`qualification`/`at_grade` auf Ausgeblendetes zeigt, sind inaktiv (Hinweis), kein Fehler – wer das Gymnasium ausblendet, muss nicht jede Regel ausblenden, die es nennt

## 2.2.2 – 2026-09-17
- Schema: ein ausgeblendeter Zug braucht weder `scope` noch `levels` (gefunden an `ch-be`: ein Kanton mit nur einem gymnasialen Weg blendet `gym-variant` aus)
- Paket: `ch-be` (Kanton Bern, deutschsprachiger Teil) vom Owner beigesteuert – Real/Sek mit Niveaufächern und drei Zusammenarbeitsmodellen, GYM1–4 mit Schwerpunktfächern, Basisstufe, BVS, Übertritt/Aufnahme/Niveauwechsel als Regeln, Recht (VSG, DVBS, MiSG, KDSG). Nachgezogen: `gym-variant` ausgeblendet (nur ein gymnasialer Weg), Schema-URL, `remark` an Basisstufe und BVS

## 2.2.1 – 2026-09-16
- Prüfung: Listen-Verweise (`grades[]`, `programs[]`, `tracks[]`, `qualifications[]`) dürfen auf ausgeblendete Elemente zeigen und werden beim Lesen gefiltert; Anker (`stage`, `domain`, `after_grade`, `scale`, `period` …) nicht. Grund: Ein Mandanten-Override, das einen Bildungsgang ausblendet, sollte nicht jeden Abschluss umschreiben müssen, der ihn nennt (gefunden bei der Prilog-Anbindung E1)

## 2.2.0 – 2026-09-16

Schema
- `subjects[].age_from` / `age_to` / `age_years`: Altersanker statt Jahrgangs-IDs. Ein Overlay mit `extends: "*"` bindet Fächer nur noch über das Alter und passt damit wirklich über jede Basis (Owner-Entscheid 16.09.2026, zuvor im Prilog-Backend umgesetzt)
- `remark` (mehrsprachig, sichtbar) und `notes` (Pflege, String) an jedem benannten Element; `programs[].hinweis` aus dem Backend heißt hier `remark`
- `qualifications[].after_grade_by_program`: Abschluss nach g12 am Gymnasium, nach g13 an der Stadtteilschule
- `{"id": "…", "disabled": true}` ist ohne `label` gültig
- Alle Objekte sind geschlossen (`unevaluatedProperties: false`): Tippfehler und Fremdfelder fallen jetzt am Schema
- `$id` und `meta.schema` zeigen auf dieses Repo (die alte Adresse `brasilspace/prilog-pex` existierte nicht)

Pakete
- `waldorf` 0.4.0: Fächer am Alter, `extends: "*"`, Labels de/fr/en
- `montessori` 0.3.0: keine Stufen-Verweise, `extends: "*"`, Labels de/en, `remark` je Programm
- `de` 0.3.0: `class_model` an allen Programmen; Gymnasium führt `fhr`
- `ch-de` 0.3.0: `class_model` an allen Programmen; Hinweis Fremdsprachenfolge; `berufslehre` mit `remark`
- `at` 0.3.0: Symmetrie Programm↔Abschluss (`ms`→`pflichtschulabschluss`, `bms`→`brp`); `remark` an Kindergarten und Lehre
- `de-hh` 0.2.0: LK/GK ausgeblendet statt neben eA/gA vererbt; Abitur nach g13 je Programm; „Lernentwicklungsgespräch“ ist kein Fach mehr
- neu: `de-sh` (Schleswig-Holstein, Bestandskunden), `ch-zh` (Kanton Zürich) – Struktur; Regeln und Paragrafen vor Einsatz gegenlesen

Werkzeuge
- `tools/validate.py` prüft zusätzlich: Symmetrie Programm↔Abschluss, `rules.applies_to.programs`, `report_points_by_program`, `after_grade_by_program`, aktive Levels je Zug, Altersanker, Labels an Levels/Skalen/Perioden; Hinweise (nicht blockierend) für dünne Programme und wirkungsloses `tracked`; `--json`
- `tools/pex.mjs` + `pex.d.ts`: dieselbe Logik in JavaScript für Prilog (Laden, Stapeln, Prüfen, Fächer je Programm, Alter→Jahrgang, Begriffe)
- `tools/build.py` schreibt `dist/index.json` (Registry mit Prüfsummen) und `dist/effective/<stapel>.json` für alle 25 Standard-Stapel
- `tools/pex.test.mjs` beweist, dass JavaScript und Python-Referenz identische effektive Pakete liefern
- GitHub Actions: Schema, Stapel, `dist/`-Frische, JS-Parität bei jedem Push

Aufräumen
- Repo-Wurzel: Inhalt aus `prilog-pex/` nach oben gezogen, doppelte Alt-Dateien entfernt

## 2.1.0 – 2026-09-16
- Schema: `rules`, `exams`, `legal` (deklarativ, `source` Pflicht)
- Schema: `grading.tendencies`, `grading.head_marks`, `grading.by_program`
- Schema: `calendar.report_points_by_program`, `calendar.holiday_authority`
- Schema: `programs[].approval`, `meta.license`, `meta.maintainer`
- Pakete: Overlays `de-hh` (Hamburg), `de-by` (Bayern)

## 2.0.0 – 2026-09-16
- `school_types` → `programs`; `grades` je Programm optional, `age_range`
- `class_model` um `mixed-age` ergänzt
- Track-Scopes `learning_group` / `enrollment` / `learner` / `program` (vormals `class` / `subject`)
- `meta.format` und `meta.schema` Pflicht
- Pakete: `at` (Österreich), Overlay `montessori`

## 1.0.0 – 2026-09-16
- Erstes Schema; Pakete `ch-de`, `de`, `us`, Overlay `waldorf`
