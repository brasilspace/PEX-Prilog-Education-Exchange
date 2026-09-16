# Prilog · PEX – Prilog Education Exchange

**Konzept v0.2 — zur Diskussion** · Stand 16.09.2026

> **Stand nach Schema 2.2 (16.09.2026).** Dieses Konzept ist die Begründung, nicht die Referenz. Wo es vom Repo abweicht, gilt `docs/anleitung.md`: (1) Track-Scopes heißen `learning_group` / `enrollment` / `learner` / `program`, nicht mehr `class` / `subject`. (2) Pädagogik-Overlays binden Fächer über das Alter und passen über **jede** Basis – es gibt kein `waldorf-ch`. (3) Der Sek-I-Abschluss in `ch-de` steht nach `h11`, nicht `g9`. (4) Rechtsbezüge sind kein Nicht-Ziel mehr: v2.1 hat `rules`, `exams`, `legal`, deklarativ mit Quelle. (5) Merge und Prüfung sind implementiert (`tools/validate.py`, `tools/pex.mjs`), nicht nur beschrieben. (6) Die Auswahl je Mandant ist eine **Liste** von Systemen, weil ein Haus zwei Schulsysteme führen kann (ecole).

Ersetzt v0.1 (16.09.2026). Name des Formats seit 16.09.2026: **PEX** (Prilog Education Exchange); Dateien heißen `<id>.pex.json`. Änderungen in Abschnitt 10; das Gegenstück auf Mandantenseite ist das Konzept **Organisationsmodell und Einschreibung v0.1**.

---

## 0. In einem Absatz

Prilog kennt heute implizit ein deutsches Klassenmodell: Klasse 1–13, eine Klassenlehrkraft, Fächer als freier Text. Sobald eine Schweizer Sekundarschule mit Niveauzügen quer zur Klasse oder eine US-High-School mit Credits und GPA kommt, passt das nicht mehr. Statt das Datenmodell je Land umzubauen, bekommt Prilog **PEX-Pakete** (Prilog Education Exchange): JSON-Dateien, die ein Schulsystem beschreiben – Stufen, Jahrgänge, Programme, Züge, Abschlüsse, Fächer, Notenskala, Begriffe, Schuljahresrhythmus. Ein Mandant lädt ein PEX, legt eine kantonale oder bundeslandspezifische Ergänzung darüber und passt den Rest für seine Schule an. Der Code kennt nur das Schema; das Land steckt in den Daten.

**Abgrenzung (neu in v0.2):** Das Paket beschreibt, was ein Bildungssystem *kennt und erlaubt*. Wie eine konkrete Schule organisiert ist – Standorte, Häuser, Lerngruppen, Kurse, wer worin eingeschrieben ist – steht nicht im Paket, sondern im Mandanten. Dafür gibt es das Konzept *Organisationsmodell und Einschreibung*. Diese Trennung ist die wichtigste Regel des Formats: Ein Paket enthält niemals eine Instanz.

Das Konzept liefert das Schema und vier Basis-Pakete: Schweiz (Deutschschweiz, Lehrplan 21 + Gymnasium), Deutschland (Basis), Österreich, USA (K-12) – dazu die Pädagogik-Overlays Waldorf und Montessori.

---

## 1. Was das Paket lösen muss

| Frage aus dem Alltag | Heute | Mit Paket |
|---|---|---|
| Wie heißt die Person, die die Klasse führt? | „Klassenlehrer", fest im Code | `terminology.class_teacher` je Paket: Klassenlehrkraft / Klassenlehrperson / Homeroom Teacher |
| Welche Fächer gibt es in der 8. Klasse? | Freitext, jede Schule tippt selbst | Fachkatalog je Jahrgang aus dem Paket, Schule ergänzt |
| Ist ein Schüler „in der 8b" oder „in Mathe Niveau A"? | Nur Klasse | Zug-Modell mit Geltungsbereich Klasse *oder* Fach |
| Was steht auf dem Zeugnis? | Deutsches Zeugnis | Notenskala, Abschlüsse und Zeugnisrhythmus aus dem Paket |
| Wann beginnt das Schuljahr, wie viele Zeugnisse gibt es? | Fest: August, zwei Halbjahre | `calendar` je Paket: Semester / Quartale / Trimester |
| Elternsprechtag oder Elterngespräch, Ferien oder Vacances? | Deutsch | Begriffe und Sprache aus dem Paket |

Nicht-Ziele: Kein Lehrplan-Inhalt (Kompetenzen, Lernziele), keine Stundentafeln mit Lektionenzahlen (das ist Stundenplan-Sache), keine Ferientermine (Mandantendaten), keine Schulgesetze, keine Instanzen (Klassen, Kurse, Gruppen, Personen).

---

## 2. Schichtenmodell

Drei Schichten, jede überschreibt die vorige, jede ist dieselbe JSON-Struktur:

```
  Basis-Paket      ch-de   de   us          ← von Prilog gepflegt, versioniert
      ↓
  Overlay          ch-zh   de-hh   us-ca    ← von Prilog gepflegt, kleiner
      ↓
  Mandanten-Overrides                        ← die Schule selbst, im Admin-UI
```

Regeln:

- Ein Overlay enthält nur, was es ändert oder hinzufügt. Ein leeres Overlay ist erlaubt.
- Alle drei Schichten werden zur Laufzeit zu einem **effektiven Schulsystem** zusammengefügt (deep merge auf `id`-Ebene; Listen werden nach `id` gemischt, nicht angehängt).
- Ein Element lässt sich in einer höheren Schicht mit `"disabled": true` ausblenden, aber nicht löschen – so bleibt die Herkunft nachvollziehbar.
- Das effektive System wird beim Speichern gegen das JSON-Schema validiert; die Schule kann nichts Ungültiges erzeugen.

Warum kein eigenes Format (YAML, TOML, DSL): JSON hat ein Schema, jede Sprache liest es, der Admin-UI-Editor braucht keinen Parser, und Overlays sind ein Merge, den es fertig gibt.

---

## 3. Das Schema (Übersicht)

Alle IDs sind stabile, sprechende Slugs in Englisch (`sec1`, `gym`, `math`), alle Anzeigetexte sind mehrsprachige Objekte `{ "de": "...", "fr": "...", "en": "..." }`. Code liest IDs, Menschen lesen Labels.

```
SchoolSystemPackage
├── meta            id, version, country, region, languages, extends, name
├── terminology     Begriffe: teacher, class_teacher, class, grade, report, parent_conference, ...
├── calendar        year_start_month, periods (semester/quarter/trimester), report_points
├── grading         scales[]  (id, values, best, pass, direction)
├── stages          [] id, label, ordinal, grades[]         Stufen
├── grades          [] id, label, ordinal, typical_age      Jahrgänge
├── programs        [] id, label, stages[], grades[] (optional), age_range, class_model, tracks[], qualifications[]
├── tracks          [] id, label, scope: learning_group | enrollment | learner | program, levels[]
├── qualifications  [] id, label, after_grade, programs[], grants_access[]
├── subject_domains [] id, label
└── subjects        [] id, label, domain, grades[], programs[], kind, tracked, optional
```

### 3.1 Programme (`programs`) – vormals `school_types`

Ein Programm ist ein Bildungsgang, den das System kennt: Gymnasium, Sekundarschule, Fachmittelschule, High School, Kinderhaus. Der Begriff ist bewusst weiter als „Schultyp", weil ein Mandant mehrere Programme führen kann (Internat mit Sek I, Gymnasium und Berufsvorbereitung) und weil ein Programm nicht zwingend Jahrgänge hat.

```json
{ "id": "sek1", "label": {"de": "Sekundarschule"},
  "stages": ["sec1"], "grades": ["h9","h10","h11"],
  "class_model": "homeroom",
  "tracks": ["sek-level", "sek-subject-level"],
  "qualifications": ["sek1-abschluss"] }
```

`class_model` sagt dem Organisationsmodell, welche Form von Lerngruppe dieses Programm im Normalfall bildet:

| `class_model` | Bedeutung | Beispiel |
|---|---|---|
| `class` | feste Jahrgangsklasse, Unterricht überwiegend im Klassenverband | Grundschule, Waldorf 1–8, Gymnasium CH |
| `homeroom` | Stammgruppe plus Kurse in wechselnder Zusammensetzung | Sek I mit Niveaufächern, US Middle School, Kursoberstufe mit Tutorium |
| `course` | keine Stammgruppe, nur Kurse | US High School (Variante), Berufsschule im Blockmodell |
| `mixed-age` | altersgemischte Gruppe ohne feste Jahrgangsstufe | Montessori, Kindergarten |

`grades` darf leer sein. Dann trägt das Programm eine `age_range`, und die Jahrgangsstufe ist keine Eigenschaft der Gruppe, sondern – falls überhaupt – der einzelnen Person (Zeugnis, Übertritt). Das ist die eine strukturelle Öffnung gegenüber v0.1, und sie kostet Deutschland und die Schweiz nichts.

### 3.2 Das Zug-Modell (`tracks`)

Ein Zug ist eine Differenzierung nach Anforderung oder Weg. Woran er hängt, sagt `scope` – und diese Frage ist in v0.2 neu beantwortet:

```json
{ "id": "sek-subject-level", "label": {"de": "Niveaufach"},
  "scope": "enrollment",
  "levels": [ {"id": "e", "label": {"de": "erweitert"}},
              {"id": "g", "label": {"de": "grundlegend"}} ] }
```

| `scope` | Der Zug hängt an … | Beispiele |
|---|---|---|
| `learning_group` | der Lerngruppe – alle darin sind im selben Zug | Sek A/B/C als eigene Klassen, Realschule als Schultyp-Zug |
| `enrollment` | der Teilnahme einer Person an einem Kurs | Mathe Niveau A, Leistungskurs, Honors/AP |
| `learner` | der Person, unabhängig von Gruppe und Kurs | individueller Förderplan, Nachteilsausgleich-Profil, IEP |
| `program` | der Programmvariante | Langzeit- vs. Kurzzeitgymnasium |

v0.1 kannte `class` und `subject`. `class` ist jetzt `learning_group`. `subject` war ungenau: Ein Niveau ist keine Eigenschaft des Fachs Mathematik, sondern der Teilnahme *dieses Schülers* am Mathematikkurs – also der Einschreibung. Genau deshalb braucht die Mandantenseite ein Einschreibungs-Objekt, und genau das liefert das Organisationsmodell.

`tracked: true` an einem Fach heißt: Für Kurse dieses Fachs ist ein `enrollment`-Zug vorgesehen.

### 3.3 Fächer

```json
{ "id": "nt", "label": {"de": "Natur und Technik"}, "domain": "science",
  "grades": ["h9","h10","h11"], "programs": ["sek1"],
  "kind": "core", "tracked": true, "optional": false,
  "aliases": ["Naturlehre"] }
```

`kind` ∈ `core | elective | project | remedial`. `tracked: true` heißt: Für Kurse dieses Fachs gilt ein `enrollment`-Zug. `aliases` fängt die kantonalen Namen ab, ohne die ID zu ändern.

### 3.4 Abschlüsse

```json
{ "id": "gym-matura", "label": {"de": "Gymnasiale Maturität"},
  "after_grade": "s2-4", "programs": ["gym"],
  "grants_access": ["university", "fh", "ph"] }
```

`grants_access` ist eine freie Liste von Tertiär-Zielen; sie dient Beratungs- und Übertrittsfunktionen, nicht der Logik.

### 3.5 Kalender

```json
{ "year_start_month": 8,
  "periods": [ {"id": "s1", "label": {"de": "1. Semester"}, "months": [8,1]},
               {"id": "s2", "label": {"de": "2. Semester"}, "months": [2,7]} ],
  "report_points": ["s1", "s2"] }
```

Konkrete Daten (erster Schultag, Ferien) bleiben Mandantendaten. Das Paket sagt nur, *welchen Rhythmus* es gibt – das steuert Zeugnisdruck, Konferenzvorlagen und den Jahreslauf.

Das vollständige Schema liegt unter `schema/pex.schema.json` (Stand: v2.2, `$id` = Roh-URL im Repo). Jede PEX-Datei trägt `meta.format: "pex"` und `meta.schema`, damit ein Loader sie ohne Dateinamen erkennt.

---

## 4. Wie Prilog das Paket benutzt

| Baustein | Nutzt |
|---|---|
| Mandanten-Setup | Wahl Basis + Overlay; erzeugt Stufen, Jahrgänge, Fachkatalog |
| Lerngruppen anlegen | Programm aus `programs`, Jahrgang aus `grades` (falls das Programm welche hat), Gruppenform aus `class_model`, Zug wenn `scope: learning_group` |
| Einschreibung | Niveau je Teilnahme wenn `scope: enrollment`; Fachkatalog bestimmt, welche Kurse ein Programm anbieten kann |
| Fächer / Stundenplan | Fachkatalog nach Jahrgang und Programm gefiltert; Schule kann ergänzen |
| Zeugnis | `grading`, `report_points`, `qualifications` |
| Rollen und Oberfläche | `terminology` für alle sichtbaren Begriffe (Lehrperson vs. Lehrkraft) |
| Jahreslauf-Vorlagen | `calendar.periods` als Taktgeber |
| Elternsprechtag | `terminology.parent_conference`; Fachlehrkräfte je Schüler aus dessen Einschreibungen |
| Konzept-Verankerung / Schutzkonzept | `meta.country/region` wählt die passende Fachredaktion (R1) |

Der Datenbankeintrag ist klein: `pex_package(id, version, json)` für die gepflegten Pakete, `tenant_pex(tenant_id, base_id, overlay_ids[], overrides_json, effective_json, effective_hash)`. `effective_json` ist eine materialisierte Sicht – neu berechnet bei jeder Änderung, damit kein Request zur Laufzeit mergt.

Versionierung: Pakete sind semver-versioniert. Ein Mandant pinnt eine Version; ein Update ist ein bewusster Schritt mit Diff-Anzeige („neu: Fach Medien und Informatik in 8. Klasse"), kein stiller Austausch.

---

## 5. Die vier Basis-PEX (Kurzfassung)

### 5.1 Schweiz – `ch-de` (Deutschschweiz)

- Stufen: Kindergarten (2 J.), Primar (6 J.), Sek I (3 J.), Sek II
- Jahrgänge nach HarmoS 1–11, Labels aber in Alltagszählung (KG1, KG2, 1.–9. Klasse), Sek II als Jahr 1–4 des jeweiligen Typs
- Programme: `kg`, `primar`, `sek1` (`homeroom`), `gym` (`class`, Variante Kurz-/Langzeit als `program`-Zug), `fms`, `berufslehre` (nur als Anschluss, nicht als geführte Schule)
- Züge: `sek-level` (A/B/C, `scope: learning_group`), `sek-subject-level` (e/g, `scope: enrollment` für Niveaufächer), `gym-variant` (`scope: program`)
- Fächer Sek I komplett nach Lehrplan 21; Gymnasium mit Grundlagen-, Schwerpunkt- und Ergänzungsfächern
- Abschlüsse: Sek-I-Abschluss (kein Zertifikat, `after_grade` g9), Fachmittelschulausweis, Fachmaturität, gymnasiale Maturität, Berufsmaturität
- Noten 1–6, 6 ist best, 4 genügend, halbe Noten
- Semester; Begriffe: Lehrperson, Schulleitung, Klassenlehrperson, Elterngespräch, Zeugnis
- Overlay `ch-zh`: Sek A/B/C explizit, Langzeitgymnasium ab 7. Klasse, Aufnahmeprüfung

### 5.2 Deutschland – `de` (Basis)

- Stufen: Primar (1–4), Sek I (5–10), Sek II (11–13), Fachliches nur bis Gymnasium
- Programme im Basis-Paket bewusst generisch: `grundschule`, `gymnasium`, `gesamtschule`, `realschule`, `hauptschule`, `foerderschule` – Overlays schalten aus und um (Hamburg: Stadtteilschule statt Real/Haupt; Bayern: Mittelschule; Sachsen: Oberschule)
- Züge: Gesamtschule mit G/E-Kursen und Oberstufe mit Grund-/Leistungskurs – beide `scope: enrollment`; die Oberstufe ist damit der erste Fall in Deutschland, der das Einschreibungs-Objekt zwingend braucht
- Fächer als deutsche Standardliste, in Klassenstufen gegliedert; Wahlpflicht ab 7
- Abschlüsse: ESA/MSA (bundeslandweise anders benannt, im Overlay), Fachhochschulreife, Abitur
- Noten 1–6, 1 ist best; Oberstufe 0–15 Punkte als zweite Skala
- Halbjahre; Begriffe: Lehrkraft, Klassenleitung, Elternsprechtag, Zeugnis
- Overlay `de-hh`: Stadtteilschule, Jahrgang 5–13, Abitur nach 12 (Gy) / 13 (StS)

### 5.3 USA – `us` (Basis)

- Stufen: Elementary (K–5), Middle (6–8), High (9–12) – Aufteilung variiert stark, Overlay-Sache
- Jahrgänge K, 1–12; High School zusätzlich mit Klassennamen Freshman/Sophomore/Junior/Senior
- Programme: `elementary` (`class`), `middle` (`homeroom`), `high` (`course`), `k8`, `k12`
- Zug `course-level` mit `scope: enrollment`: Regular / Honors / AP / IB je Teilnahme
- Fächer als Kurse mit Credits: Kernfächer plus typische Electives; Prilog behandelt einen US-Kurs als Fach mit `credits`-Attribut
- Abschlüsse: High School Diploma, mit `requirements` als Credit-Summen je Domain (Overlay je Bundesstaat)
- Noten: Buchstaben A–F mit GPA-Punkten 4.0; Prozentskala als zweite Skala
- Semester oder Quarter (Overlay); Begriffe: Teacher, Homeroom Teacher, Principal, Parent-Teacher Conference, Report Card
- Overlay `us-ca`: a-g-Requirements für UC/CSU-Zugang, Semester

---

### 5.4 Österreich – `at`

- Bundesweit einheitlich (SchOG), daher kaum Overlay-Bedarf; Bundesländer unterscheiden sich nur in Bezeichnungen und Schulversuchen
- Zählung: **Schulstufen 1–13** als IDs (`s1`…`s13`); die AHS zählt intern 1.–8. Klasse, die BHS 1.–5. Jahrgang – beides als `aliases`, damit die Oberfläche „5. Klasse" zeigen kann, wenn die Schule so spricht
- Programme: `vs` (`class`), `ms` Mittelschule (`homeroom`), `ahs-u` und `ahs-o` (`class`, Schulform G/RG/ORG/WRG als `program`-Zug), `bhs` (fünf Jahrgänge, `class`), `bms`, `pts`, `lehre` (nur Anschluss), `sonderschule`
- Der interessante Fall ist die **Mittelschule**: ab der 7. Schulstufe Leistungsniveaus *Standard* und *Standard AHS* in Deutsch, Mathematik und Englisch – **je Gegenstand**, nicht je Klasse. Das ist exakt der Schweizer Niveaufächer-Fall und bestätigt, dass `scope: enrollment` kein Sonderweg ist, sondern in drei von vier Ländern gebraucht wird
- Abschlüsse: Reifeprüfung (Matura) nach 12, Reife- und Diplomprüfung (BHS) nach 13, Berufsreifeprüfung („Lehre mit Matura"), Lehrabschlussprüfung, Pflichtschulabschluss
- Noten 1–5, 1 ist best, 4 genügend – **nicht** 1–6 wie in Deutschland; die Skala hat eine ID weniger, und ein Zeugnismodul, das 6 hart codiert, bricht hier
- Zwei Zeugnisse: Schulnachricht (Wintersemester) und Jahreszeugnis – im Paket als zwei `report_points`; `terminology.report_midyear` ist neu und nur hier belegt
- Schuljahr beginnt im September, mit Bundesländer-Versatz (Wien/NÖ/Burgenland eine Woche früher) – ein Overlay-Detail, kein Paket-Detail
- Fächer nach den Lehrplänen 2023: „Kunst und Gestaltung" statt Bildnerische Erziehung, „Technik und Design" statt Werken, „Digitale Grundbildung" ab 5. Schulstufe; alte Namen als `aliases`
- BHS-Fachrichtungen (HTL Elektrotechnik, HAK, HLW) sind bewusst nicht als eigene Programme im Basis-Paket – das wären dreißig; eine BHS legt ihre Fachrichtung als schuleigenes Programm-Override an

## 6. PEX-Overlays für Pädagogik: Waldorf und Montessori

Waldorfschulen laufen quer zu allen drei Ländern: Klasse 1–8 bei einer Klassenlehrkraft, Epochenunterricht, Textzeugnisse, Eurythmie. Das ist ein **PEX-Overlay** (`waldorf.pex.json`), das über jedes Basis-Paket gelegt werden kann und das Fächer hinzufügt (Eurythmie, Epochen als `kind: "epoch"`), Begriffe ändert (Klassenlehrer 1–8 / Klassenbetreuer ab 9) und die Notenskala um `text` ergänzt. Damit ist die Waldorfschule Hamburg `de` + `de-hh` + `waldorf`, ein Waldorf-Internat in der Schweiz `ch-de` + `ch-be` + `waldorf`.

**Montessori** (`montessori`, neu in v0.2) ist das Gegenbeispiel, das die Öffnung in 3.1 rechtfertigt: Programme `kinderhaus`, `mont-primar`, `mont-sek` mit `class_model: mixed-age`, leeren `grades` und einer `age_range`. Die Jahrgänge des Basis-Pakets bleiben verfügbar – für Zeugnis, Übertritt und Schulpflicht braucht auch eine Montessori-Schule die Klassenstufe eines Kindes –, aber sie tragen nicht die Gruppe. Das Overlay ist bewusst klein; wenn es größer werden müsste, wäre das ein Zeichen, dass das Schema noch nicht allgemein genug ist.

---

## 7. Fahrplan

| Stufe | Inhalt |
|---|---|
| P0 | Schema v2, Loader, Merge, Validierung; Pakete `de` + `de-hh` + `at` + `waldorf`; `terminology` und `calendar` im Web-Client verdrahtet; `programs` und `class_model` als Stammdaten der Lerngruppe |
| P1 | Fachkatalog aus Paket in Lerngruppen/Stundenplan; Zug-Scope `learning_group`; Paket `ch-de` + `ch-zh` |
| P2 | Zug-Scope `enrollment` – setzt das Organisationsmodell (Einschreibung) voraus; Zeugnis liest `grading` und `report_points`; Paket `us` + `us-ca` |
| P3 | Zug-Scopes `learner` und `program`; Admin-UI-Editor für Overrides mit Diff; Paket-Update mit Versionsdiff; Romandie `ch-fr` (PER) |

P0 ist klein, weil `de` das ist, was heute implizit im Code steckt – das Paket macht es nur explizit.

---

## 8. Offene Punkte

1. **HarmoS-Zählung oder Alltagszählung als ID?** Vorschlag: ID nach HarmoS (`h7`), Label nach Alltag („7. Klasse", in ZH „1. Sek"). Das trennt Stabilität von Anzeige.
2. **Wer pflegt die Pakete?** Ein Repo `prilog-pex` mit Review-Pflicht; Schulen liefern Korrekturen als Issue, nicht als Override – sonst hat jede Schule ihre eigene Wahrheit.
3. **Kurs-Modell für die USA** ist mit v0.2 auf der Paketseite beantwortet (`class_model: course`, Zug `enrollment`); die Umsetzung liegt im Organisationsmodell. Offen bleibt nur, ob ein US-Kunde vor dem ersten Sek-Kunden mit Niveaufächern kommt – das entscheidet die Reihenfolge, nicht das Modell.
4. **Mehrsprachigkeit der Labels**: Pflicht für `de`, `fr`, `it`, `en` in `ch-*`? Vorschlag: Pflicht nur für die Sprachen in `meta.languages`.
5. **Sonderpädagogik** (Förderschule, integrative Förderung, IEP in den USA): In v0.2 als Programm *oder* als Zug mit `scope: learner` abbildbar. Welches die Schule wählt, ist Sache des Overlays; das Schema erzwingt nichts. Das ist bewusst – integrative Förderung ist kein Schultyp, aber eine Förderschule ist einer.
6. **`stages` ohne `grades`:** Ein Montessori-Programm verweist auf die Stufe `primar`, hat aber keine Jahrgänge. Die Stufe dient dann nur der Einordnung (Schulpflicht, Übertritt). Reicht das, oder braucht die Stufe selbst eine `age_range`?

---

## 9. Selbstprüfung

- Das Schema ist an drei Ländern entworfen, die alle Jahrgangsklassen kennen. Montessori ist in v0.2 als Overlay geprüft; Berufsschule im Blockmodell (Ausbildungsjahr, Kohorte, Blockgruppe) und die Efterskole sind es nicht. Berufsschule ist der nächste Testfall, weil sie in der Schweiz zum Sek-II-Anschluss gehört.
- Die US-Beispiele sind aus allgemeinem Wissen zusammengestellt; vor einem US-Piloten muss ein Bundesstaat mit Quelle gegengelesen werden. Österreich ist nach den Lehrplänen 2023 erstellt, aber die Übergangsregeln (alte Fachnamen laufen an vielen Schulen noch) und die semestrierte Oberstufe sind nicht mit einer Schule geprüft.
- Die Merge-Semantik („Listen nach id mischen") ist beschrieben, nicht implementiert. Der erste Overlay-Test wird zeigen, ob `disabled` reicht oder ob Reihenfolge (`ordinal`) beim Merge Ärger macht.
- v0.2 verschiebt die schwere Arbeit auf das Organisationsmodell. Das Paket ist damit sauber – aber erst zusammen mit dem anderen Konzept vollständig. Wer nur dieses liest, bekommt eine Beschreibung ohne Ort, an dem sie wirkt.
- Schweiz ist nur Deutschschweiz. Romandie und Tessin folgen anderen Lehrplänen und – wichtiger – anderen Übertrittsregeln; `ch-fr` ist keine Übersetzung von `ch-de`.

---

## 10. Änderungen v0.2 gegenüber v0.1

| v0.1 | v0.2 | Warum |
|---|---|---|
| `school_types` | `programs` | Ein Mandant führt mehrere Bildungsgänge; „Schultyp" klingt nach genau einem |
| `grades` an jedem Schultyp Pflicht | `grades` je Programm optional, ersatzweise `age_range` | Montessori und Kindergarten haben Gruppen ohne Jahrgangsstufe; Deutschland und Schweiz merken nichts |
| `class_model`: class / homeroom / course | plus `mixed-age` | altersgemischte Gruppe ist eine vierte Form, keine Variante der drei |
| Track-Scope `class` / `subject` | `learning_group` / `enrollment` / `learner` / `program` | `subject` war falsch adressiert: Das Niveau hängt an der Teilnahme, nicht am Fach. `learner` und `program` sind neue Fälle (Förderplan, Gymnasialtyp) |
| Trennung Paket / Mandant implizit | Ausdrücklich als Regel: „Ein Paket enthält niemals eine Instanz" | Aus dem Review; die Mandantenseite ist jetzt ein eigenes Konzept |
| – | PEX-Overlay `montessori` als Prüfstein | Beweist die Öffnung mit 30 Zeilen statt mit einer Behauptung |
| – | PEX `at` (Österreich) | Vierter DACH-Markt; Mittelschul-Niveaus bestätigen `scope: enrollment` unabhängig von der Schweiz |
| Fahrplan P2 „Zug-Modell subject" | P2 setzt das Organisationsmodell voraus | Ohne Einschreibungs-Objekt gibt es keinen Ort für ein Niveau je Teilnahme |

Unverändert: Schichtenmodell und Merge, Fächer, Abschlüsse, Notenskalen, Kalender, Terminologie, Waldorf-Overlay, Pflege in einem Repo.
