# PEX · Regionale Varianz – was Bundesländer und Kantone wirklich unterscheidet

**Analyse und Schema-Erweiterung v2.1** · Stand 16.09.2026
Ergänzt *Konzept PEX-Format v0.2*. Beantwortet: Was variiert in Deutschland je Bundesland, in der Schweiz je Kanton, in Österreich je Bundesland – und kann ein PEX-Overlay das alles tragen?

---

## 0. Kurzantwort

Ja, aber nicht mit v2 allein. Etwa zwei Drittel der regionalen Unterschiede sind **Strukturunterschiede** (andere Schulformen, andere Jahrgangsgrenzen, andere Fächernamen, andere Notenskalen) – die trägt ein Overlay mit dem Schema v2 vollständig. Das restliche Drittel sind **Regeln und Rechtsbezüge** (Übertrittsverfahren, Prüfungsordnungen, Schulpflicht, Meldepflichten, Ferienhoheit), für die v2 keinen Ort hat. Dafür kommen in v2.1 vier Blöcke dazu: `rules`, `exams`, `legal` und Erweiterungen an `grading` und `calendar`. Alle vier sind **deklarativ**: Sie beschreiben, was gilt, mit Quelle – sie sind keine Logik. Prilog liest sie an, zeigt sie an und verlinkt sie; es rechnet nicht mit ihnen.

Die Länder unterscheiden sich stark darin, *wie viel* variiert: Deutschland viel (16 Schulgesetze), die Schweiz sehr viel bei Struktur und Übertritt (26 Kantone, HarmoS nur angeglichen), Österreich fast gar nicht (Bundesrecht; Overlays sind Termine und Bezeichnungen).

---

## 1. Deutschland – was je Bundesland variiert

| Bereich | Beispiele | PEX-Ort (v2) | Trägt v2? |
|---|---|---|---|
| **Dauer der Grundschule** | 4 Jahre fast überall; **6 Jahre** in Berlin und Brandenburg | `programs.grundschule.grades` | ja |
| **Schulformen Sek I** | Stadtteilschule (HH), Gemeinschaftsschule (SH, BW, SL, TH), Oberschule (NI, SN, HB), Mittelschule (BY), Regelschule (TH), Regionale Schule (MV), Sekundarschule (ST, NRW), Realschule plus (RP), Integrierte Sekundarschule (BE); Haupt-/Realschule teils abgeschafft | `programs` mit `disabled` und neuen Programmen | ja |
| **Gymnasium G8/G9** | G9 Rückkehr in BY, NI, NRW, SH, HE (wahlweise); G8 in HH, BE… – Abitur nach 12 oder 13 | `programs.gymnasium.grades`, `qualifications.abitur.after_grade` | ja |
| **Oberstufe** | Profiloberstufe (HH, SH: Profilfach + Kernfächer), Kurssystem mit LK/GK (NRW), Seminar-Fächer (BY W-/P-Seminar), Q-Phase-Namen (Q1–Q4, 12/1–13/2) | `tracks.oberstufe`, `grades.aliases`, `subjects` | ja |
| **Abschlussbezeichnungen** | ESA/MSA (HH, SH), Hauptschulabschluss/Mittlere Reife (BY), Berufsbildungsreife/eBBR (BE), Erweiterter Sekundarabschluss I (NI), Qualifizierender Abschluss (BY „Quali") | `qualifications` mit `aliases`, zusätzliche Abschlüsse | ja |
| **Fächernamen und -zuschnitt** | PGW (HH), Politik-Wirtschaft (NI), Sozialkunde (BY, RP), Gemeinschaftskunde (BW); Werte und Normen (NI) / Praktische Philosophie (NRW) / Ethik (BY) / LER (BB); NaWi-Verbund 5–6 (HH, BE); WAT (BE) | `subjects` mit `aliases`, Overlay-Fächer | ja |
| **Fremdsprachenbeginn** | Englisch ab Kl. 1 (BW bis 2018, dann Kl. 3), ab Kl. 3 (meist), Französisch am Oberrhein | `subjects.grades` | ja |
| **Religion / Ethik** | Ethik als Ersatzfach Pflicht (BY, SN) vs. Wahl (HH: Religion für alle); Konfessionsbindung | `subjects.optional`, `rules` | v2.1 |
| **Notenskala** | 1–6 überall; **Tendenzen (+/–)** in Zeugnissen mancher Länder; Punkte 0–15 Oberstufe; **Berichtszeugnisse** bis Kl. 2 oder 3 (länderspezifisch); Noten ab Kl. 3 oder 4 | `grading` | teilweise – Tendenzen fehlen |
| **Kopfnoten** | Arbeits- und Sozialverhalten benotet (NRW bis 2011, SN, BB, ST, TH) oder als Text | – | **fehlt** → `grading.head_marks` |
| **Zeugnistermine und -arten** | Halbjahresinformation (BW) vs. Halbjahreszeugnis; Zeugnis Ende Januar vs. Ende Februar | `calendar.report_points`, `terminology` | ja |
| **Übertritt nach Kl. 4** | Bindende Empfehlung (BY: Notenschnitt 2,33; SN, TH), Elternwille (NRW, HH, BE, NI…), Probeunterricht (BY), Beratungsverfahren (BW) | – | **fehlt** → `rules` |
| **Schulpflicht** | 9 oder 10 Vollzeitjahre, plus Berufsschulpflicht bis 18; Einschulungsstichtag (30.6. / 30.9. / Korridor) | – | **fehlt** → `rules` |
| **Ferien** | Länderhoheit, KMK-Rotation für Sommerferien; Herbst-/Winterferien je Land | `calendar` (nur Rhythmus) | teilweise → `calendar.holiday_authority` |
| **Freie Schulen / Ersatzschulen** | Waldorf-Abschlüsse als **Externenprüfung** (Schulfremdenprüfung) in manchen Ländern, als anerkannte Ersatzschule mit eigener Prüfung in anderen; Genehmigungsstatus | – | **fehlt** → `exams`, `legal` |
| **Datenschutz / Recht** | Landes-Schulgesetz §§, Landesdatenschutzgesetz, Schulstatistik-Formate, Meldepflichten (IfSG-Ausführung), Aufbewahrungsfristen Schülerakte | – | **fehlt** → `legal` |
| **Inklusion** | Förderschwerpunkte (LES, GE, KM, SE, HK…) als KMK-Standard, Umsetzung je Land (Förderschule vs. Gemeinsames Lernen) | `tracks` mit `scope: learner` | ja, mit v2.1-Katalog |

Fazit Deutschland: Struktur ist mit v2 abgedeckt und braucht **je Bundesland ein Overlay von 40–120 Zeilen**. Regeln, Prüfungen, Recht brauchen v2.1.

---

## 2. Schweiz – was je Kanton variiert

| Bereich | Beispiele | PEX-Ort (v2) | Trägt v2? |
|---|---|---|---|
| **HarmoS-Beitritt** | 15 Kantone drin, u. a. AG, LU, NW, TG, ZG, GR, UR nicht – dennoch faktisch angeglichen (11 Jahre obligatorisch) | `meta.notes` | ja |
| **Sek-I-Modell** | geteilt (Sek A/B/C als Klassen: ZH), kooperativ (Stammklassen + Niveaufächer: LU, SG), integriert (eine Klasse, Niveaus in D/F/E/M: BS, BL, FR…) | `programs.sek1.class_model`, `tracks.sek-level` (`learning_group`) vs. `sek-subject-level` (`enrollment`) | ja |
| **Zug-Bezeichnungen** | Sek A/B/C (ZH), Sekundar-/Realschule (BE, LU, SG, SO), Bezirksschule (AG), Progymnasium (BE alt), Niveau e/g | `tracks.levels.label`, `aliases` | ja |
| **Gymnasium** | Langzeit ab 7. Klasse (ZH, ZG, LU teils), Kurzzeit ab 9. (BE: „Quarta" nach 8. Klasse, GYM1–GYM4), Dauer 3 vs. 4 Jahre | `programs.gym.grades`, `tracks.gym-variant` | ja |
| **Gym-Klassennamen** | Quarta/Tertia/Sekunda/Prima (BE, BS), 1.–4. Gym (SG), 1.–6. Klasse Langgymi (ZH) | `grades.aliases` je Overlay | ja |
| **Aufnahme ins Gymnasium** | Prüfung ohne Noten (ZH), Empfehlung + Probezeit (BE, SG), Notenschnitt (LU) | – | **fehlt** → `rules` |
| **Fremdsprachenfolge** | Französisch ab 3., Englisch ab 5. (Westkantone, BE, BS, SO); **Englisch ab 3., Französisch ab 5.** (ZH, Zentral- und Ostschweiz); Italienisch (GR, TI) | `subjects.grades` | ja |
| **Kindergarten** | 2 Jahre obligatorisch (meist), 1 Jahr (einige Nicht-HarmoS-Kantone), Basisstufe/Grundstufe (KG + 1./2. Klasse gemischt: BE, LU, TG teils) | `programs` mit `mixed-age` | ja |
| **Noten** | 1–6, halbe Noten; Viertelnoten im Gym mancher Kantone; Noten ab 2./3./4. Klasse, davor Lernbericht; Zeugnis jährlich (Primar) vs. semesterlich | `grading.step`, `report_points` je Programm | teilweise – `report_points` je Programm fehlt |
| **Abschlusszertifikat Sek I** | ohne (meist), mit kantonalem Zertifikat/Prüfung (ZH Stellwerk-Test, GE Certificat) | `qualifications`, `exams` | v2.1 |
| **Lehrpläne** | Lehrplan 21 mit kantonaler Stundentafel (D-CH), PER (Romandie), Piano di studio (TI) – **andere Fächerbündelung** | eigene Basis-PEX `ch-fr`, `ch-it` | ja, als eigene Basis |
| **Ferien** | Kantonal, teils gemeindlich; Sportwoche | `calendar.holiday_authority` | v2.1 |
| **Schuljahresbeginn** | Mitte August, kantonal um bis zu zwei Wochen versetzt | `calendar.year_start_month` | ja (Monat), Tag ist Mandant |
| **Recht** | Kantonale Volksschulgesetze, kantonale Datenschutzgesetze (nicht das eidgenössische DSG für öffentliche Schulen!), Privatschulbewilligung | – | **fehlt** → `legal` |
| **Sprache** | Zweisprachige Kantone (BE, FR, VS), Rätoromanisch (GR) | `meta.languages`, mehrsprachige `label` | ja |

Fazit Schweiz: Mehr Strukturvarianz als Deutschland, aber v2 trägt sie – **weil das Zug-Modell mit zwei Scopes genau für die drei Sek-Modelle gebaut ist**. Aufnahmeverfahren und Recht brauchen v2.1. Romandie und Tessin sind eigene Basis-PEX, keine Overlays.

---

## 3. Österreich – was je Bundesland variiert

Kurz: fast nichts Strukturelles. Schulorganisation, Lehrpläne, Prüfungen und Notenskala sind Bundesrecht.

| Bereich | Beispiele | Trägt v2? |
|---|---|---|
| **Schuljahresbeginn** | 1. Montag im September (W, NÖ, B) vs. 2. Montag (übrige) | `calendar` + `holiday_authority` (v2.1) |
| **Semesterferien** | 1. Februarwoche (W, NÖ) vs. 2. (übrige) | Mandant / v2.1 |
| **Schulversuche** | Modellregionen Gemeinsame Schule (VBG Diskussion), Ganztagsformen | Overlay-Programm |
| **Bezeichnungen** | Mittelschule vs. „Neue Mittelschule" im Sprachgebrauch | `aliases` |
| **Trägerschaft** | Pflichtschulen (VS, MS, PTS, ASO) sind Landessache, AHS/BHS Bundessache – wirkt auf Dienstrecht und Schulaufsicht, nicht auf Struktur | `legal` (v2.1) |
| **Bildungsdirektionen** | je Land eine; Zuständigkeit für Meldungen | `legal.authority` (v2.1) |

Fazit Österreich: Ein Bundesland-Overlay ist unter 20 Zeilen. Wichtiger als Bundesland-Overlays sind hier **Schultyp-Overlays** für BHS-Fachrichtungen.

---

## 4. Schema-Erweiterung v2.1

Vier Blöcke, alle optional, alle deklarativ. Die Regel bleibt: PEX beschreibt, Prilog rechnet nicht mit Rechtstexten.

### 4.1 `rules[]` – benannte Regeln mit Quelle

```json
{ "id": "uebertritt-gym",
  "kind": "transition",
  "label": { "de": "Übertritt ans Gymnasium nach Klasse 4" },
  "applies_to": { "from_grade": "g4", "to_program": "gymnasium" },
  "mode": "binding-recommendation",
  "summary": { "de": "Übertrittszeugnis mit Notenschnitt ≤ 2,33 in D/M/HSU; sonst Probeunterricht" },
  "source": "BayEUG Art. 44, GrSO §§ 6–8",
  "url": "https://www.gesetze-bayern.de/..." }
```

`kind` ∈ `transition | admission | compulsory-schooling | promotion | subject-choice | attendance | other`. `mode` ist eine kleine geschlossene Liste je `kind` (bei `transition`: `parent-choice | binding-recommendation | exam | recommendation-with-probation`). Der Rest ist Text mit Quelle. Prilog zeigt Regeln an der passenden Stelle (Übertrittsberatung, Anmeldung) und im Nachweisbericht – mehr nicht.

### 4.2 `exams[]` – Prüfungen und Abschlussverfahren

```json
{ "id": "abitur-extern",
  "label": { "de": "Abiturprüfung für Schulfremde (Waldorf)" },
  "qualification": "abitur",
  "mode": "external",
  "components": [ { "id": "written", "count": 4 }, { "id": "oral", "count": 4 } ],
  "at_grade": "g13",
  "summary": { "de": "Waldorfschüler legen das Abitur als Externe an einer staatlichen Schule ab; 8 Prüfungsfächer statt 4–5" },
  "source": "SchG BW § 88; APO" }
```

`mode` ∈ `internal | external | central | state-recognized`. Das ist der Block, der für Waldorf- und andere freie Schulen den Unterschied macht: Ob ein Abschluss im Haus oder als Externenprüfung stattfindet, entscheidet über Jahresplanung, Fächer der 12./13. Klasse und Kommunikation mit Eltern.

### 4.3 `legal[]` – Rechtsgrundlagen und Zuständigkeiten

```json
{ "id": "schulgesetz", "kind": "school-act", "label": { "de": "Hamburgisches Schulgesetz (HmbSG)" },
  "url": "https://www.landesrecht-hamburg.de/...", "sections": { "datenschutz": "§ 98–100", "schulpflicht": "§ 37–41" } },
{ "id": "datenschutz", "kind": "data-protection", "label": { "de": "HmbDSG + HmbSG § 98 ff." } },
{ "id": "aufsicht", "kind": "authority", "label": { "de": "Behörde für Schule und Berufsbildung" }, "url": "…" },
{ "id": "aufbewahrung", "kind": "retention", "summary": { "de": "Schülerakte 10 Jahre nach Abgang, Zeugnisse 50 Jahre" }, "source": "…" }
```

`kind` ∈ `school-act | data-protection | authority | retention | reporting | private-school | other`. Das ist die Brücke zum Datenschutz-Handbuch und zur Konzept-Verankerung (R1: kuratierter Fachinhalt je Bundesland) – ein Ort, an dem die Rechtsbezüge einmal stehen statt in jedem Modul neu.

### 4.4 Erweiterungen an bestehenden Blöcken

- `grading.scales[].tendencies: true` – Zeugnisnoten mit + / –
- `grading.head_marks[]` – Kopfnoten (Arbeits-, Sozialverhalten) mit eigener Skala oder Text
- `grading.by_program` – Skala und Zeugnisart je Programm/Jahrgang (Berichtszeugnis bis Kl. 2, Noten ab Kl. 3)
- `calendar.report_points_by_program` – Zeugnisrhythmus je Programm (Primar jährlich, Sek semesterlich)
- `calendar.holiday_authority` – wer die Ferien festlegt (`state | canton | municipality | school`) mit `url` zum amtlichen Kalender; die Termine selbst bleiben Mandantendaten, aber Prilog kann sie von dort **vorschlagen**
- `programs[].approval` – für freie Schulen: `state | private-recognized | private-approved | private-licensed` (Ersatz-/Ergänzungsschule, Privatschulbewilligung)
- `tracks` bekommen im Basis-PEX `de` einen Katalog der KMK-Förderschwerpunkte als `scope: learner`

### 4.5 Was bewusst **nicht** ins Schema kommt

- Stundentafeln mit Wochenstunden je Fach – das ist Stundenplan-Sache und ändert sich jährlich
- Prüfungs-Berechnungsregeln (Abiturnotenberechnung, Bestehensregeln) – Logik, kein Format
- Lehrplaninhalte
- Ferientermine – Mandant, mit Vorschlag aus `holiday_authority.url`
- Dienstrecht der Lehrkräfte

---

## 5. Wie viele Overlays, wer pflegt sie

| Land | Basis-PEX | Overlays | Größe je Overlay | Pflegeaufwand |
|---|---|---|---|---|
| DE | `de` | 16 Bundesländer | 40–120 Zeilen | hoch: jede Legislatur ändert etwas (G8/G9, Kopfnoten, Übertritt) |
| CH | `ch-de`, `ch-fr`, `ch-it` | ~20 Kantone (D-CH), ~6 (Romandie), 1 (TI) | 30–80 Zeilen | mittel: Struktur stabil, Fremdsprachen und Übertritt in Bewegung |
| AT | `at` | 9 Bundesländer | < 20 Zeilen | gering |
| Pädagogik | – | `waldorf`, `montessori` | 30–60 Zeilen | gering |

Priorität nach Kunden: `de-hh` und `de-sh` (Bestand), `de-by` als Gegenpol (bindender Übertritt, G9, Mittelschule), `ch-zh` und `ch-be` (Schweiz-Einstieg, zwei verschiedene Sek-Modelle), dann nach Nachfrage. Ein vollständiger Satz aller 16 + 26 + 9 Overlays ist **keine Voraussetzung** für den Betrieb – ein Mandant ohne Overlay läuft auf dem Basis-PEX und ergänzt selbst.

Pflege im Repo `prilog-pex` mit Review; Änderungen an Overlays sind versioniert, Mandanten pinnen. Für DE lohnt ein jährlicher Abgleich im Juli (Schuljahreswechsel, neue Verordnungen).

---

## 6. Was das für das Format bedeutet

Drei Sätze, die in die Beschreibung von PEX gehören:

1. **PEX trägt Struktur vollständig und Regeln deklarativ.** Ein Overlay kann Schulformen, Jahrgänge, Fächer, Abschlüsse und Skalen ändern; Regeln und Recht stehen als Text mit Quelle dabei.
2. **Overlays sind klein, weil das Basis-PEX generisch ist.** Nicht die Bundesländer sind die Ausnahme, sondern der Bund ist die Abstraktion.
3. **PEX rechnet nicht.** Wer eine Übertrittsempfehlung berechnen will, baut ein Modul, das die Regel aus PEX liest – die Regel selbst bleibt Text.

---

## 7. Selbstprüfung

- Die Tabellen in 1–3 sind aus Fachkenntnis erstellt, nicht aus einem Abgleich mit 16 + 26 + 9 aktuellen Rechtsquellen. Einzelne Zuordnungen (etwa welche Länder Kopfnoten noch führen) können veraltet sein – gerade das ist der Grund, warum `source` und `url` in v2.1 Pflichtfelder für `rules`, `exams` und `legal` sind.
- Die Beispiel-Overlays `de-hh` und `de-by` (beigelegt) prüfen das Schema, nicht die Rechtslage. Vor dem Einsatz an einer Schule gehört jede `rules`-Zeile gegen den aktuellen Verordnungstext gelesen.
- `rules.mode` als geschlossene Liste ist ein Kompromiss: Er macht die Regel filterbar, ohne Logik zu sein. Ob die Listen reichen, zeigt sich am dritten Bundesland.
- Nicht behandelt: Schulen im Ausland mit deutschem Abschluss (DSD, Deutsche Auslandsschulen) und internationale Programme (IB) – beide wären Overlays auf `de` bzw. eigene Basis-PEX; kein Bedarf bekannt.
