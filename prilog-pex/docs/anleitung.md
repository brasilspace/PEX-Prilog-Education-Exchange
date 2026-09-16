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
| `schema/pex.schema.json` | JSON-Schema (Draft 2020-12), gegen das jede PEX-Datei geprüft wird. `$id: https://prilog.chat/schemas/pex/v2.1` |
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

### 3.2 Pädagogik-Overlays und `extends`

`extends` nennt die Basis-Pakete, auf die ein Overlay legbar ist – ein String, eine Liste oder `"*"` für alle. Ein Pädagogik-Overlay darf nur Dinge referenzieren, die in **allen** genannten Basen existieren, oder eigene mitbringen. Das Waldorf-Overlay bringt seine Fächer selbst mit (`eu`, `gartenbau`, `ep-*`), referenziert Jahrgänge aber als `g1`…`g13` – deshalb steht dort `extends: ["de"]`. Für die Schweiz (`h3`…`h11`) und Österreich (`s1`…`s13`) braucht es `waldorf-ch` und `waldorf-at`, die dieselben Fächer mit den jeweiligen Jahrgangs-IDs tragen. `montessori` referenziert nur Stufen, die in `de`, `ch-de` und `at` gleich heißen, und steht deshalb auf allen dreien.

Der Validator prüft jeden Stapel aus `extends` und meldet fehlende Referenzen. Ein Overlay auf eine Basis zu legen, die nicht in `extends` steht, ist ein Fehler.

### 3.3 Validierung

Zwei Stufen:

- **Datei-Validierung** gegen `schema/pex.schema.json` – Struktur, Pflichtfelder, erlaubte Werte. Jede Datei einzeln.
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
| Waldorf-Overlay auf `ch-de` legen | Schweizer Jahrgänge heißen `h9`, nicht `g7`; `extends` erlaubt nur `de` | eigenes `waldorf-ch` mit Schweizer Jahrgangs-IDs |
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
