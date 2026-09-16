# Prilog · Organisationsmodell und Einschreibung

**Konzept v0.1 — zur Diskussion** · Stand 16.09.2026
Gegenstück zu *PEX-Format v0.2* (Prilog Education Exchange). Das PEX sagt, was ein Bildungssystem kennt; dieses Konzept sagt, wie eine konkrete Schule in Prilog organisiert ist und wer worin teilnimmt.

---

## 0. In einem Absatz

Prilog kennt heute einen Satz: *Ein Schüler gehört zu einer Klasse und hat dort Fächer.* Der Satz trägt Grundschule, Waldorf 1–8 und Gymnasium – und bricht bei der deutschen Kursoberstufe, bei Schweizer Niveaufächern, bei einem Internat mit Wohngruppen und bei jeder Schule, in der ein Kind gleichzeitig in einer Stammgruppe, drei Kursen und einer Projektgruppe ist. Dieses Konzept ersetzt den Satz durch einen allgemeineren: *Eine Person ist für einen Zeitraum in Gruppen und Angeboten eingeschrieben.* Die Klasse bleibt – als die häufigste Form einer Lerngruppe, mit allem, was heute an ihr hängt. Aber sie ist nicht mehr das einzige Ding, an dem etwas hängen kann.

Vier Objekte: **Organisationseinheit** (Standort, Abteilung, Haus), **Lerngruppe** (Klasse, Kurs, Projektgruppe, Wohngruppe), **Angebot** (ein Fach, unterrichtet von einer Lehrkraft in einer Gruppe in einem Zeitraum) und **Einschreibung** (Person × Gruppe oder Angebot × Gültigkeit × Niveau). Dazu die eine Tabelle, die alles zusammenhält: welche Gruppenart welchen Kreis, welchen Chat-Space und welche Betreuungsrolle erzeugt.

---

## 1. Warum jetzt, und warum nicht mehr

### 1.1 Die Fälle, die das heutige Modell nicht trägt

| Fall | Was bricht | Wer es braucht |
|---|---|---|
| **Kursoberstufe (DE, Kl. 11–13)** | Kein Klassenverband; Leistungs-/Grundkurs ist eine Eigenschaft der Teilnahme; Tutorium als Stammgruppe | Jede Waldorfschule mit Abitur – also die Bestandskunden |
| **Niveaufächer Sek I (CH)** | Schüler ist in Klasse 8a, aber in Mathe Niveau A und Französisch Niveau B – bei anderen Lehrkräften als die Klasse | Erster Schweizer Sek-Kunde |
| **Internat (ecole)** | Wohngruppe „Haus A" mit Hauseltern ist eine Gruppe mit Betreuungsrolle und eigenem Kreis, aber keine Klasse | ecole-Konzept, Schweizer Markt |
| **Projektgruppen, Klassenspiel, AGs** | Gruppen quer zur Klasse, zeitlich begrenzt, mit Verantwortlichem | Waldorf 8. und 12. Klasse, jede Schule |
| **Altersgemischte Gruppen** | Gruppe ohne Jahrgangsstufe | Montessori, Kindergarten |
| **Kurse ohne Stammgruppe (US High)** | Sechs Kurse, sechs Lehrkräfte, kein Klassenlehrer | Erst bei einem US-Kunden |

Der erste Fall ist der entscheidende: Er betrifft nicht künftige Kunden, sondern die Oberstufe der Schulen, die Prilog heute benutzen. Das Modell ist nicht für Universitäten, sondern für die 12. Klasse.

### 1.2 Was das Modell nicht werden soll

- **Kein Hochschul-Modell.** Keine Module mit ECTS, keine Prüfungsordnungen, keine Studiengänge. Wenn ein Objekt nur für Hochschulen gebraucht würde, kommt es nicht rein.
- **Keine Abschaffung der Klasse.** Die Klasse ist die Standard-Lerngruppe. Alles, was heute an ihr hängt, hängt weiter an ihr. Eine Lehrkraft der 3. Klasse sieht keinen Unterschied.
- **Kein zweiter Stundenplan.** Das Angebot sagt, *dass* eine Lehrkraft ein Fach in einer Gruppe unterrichtet, nicht wann. Zeitfenster bleiben beim Stundenplan.
- **Keine Zeugnislogik.** Das Modell liefert dem Zeugnis die Teilnahmen mit Niveau; was daraus wird, entscheidet das Zeugnis-Modul mit dem Paket.

---

## 2. Die vier Objekte

### 2.1 Organisationseinheit (`OrgUnit`)

Der Baum der Einrichtung. Wurzel ist der Mandant; darunter Standorte, Abteilungen, Stufen, Häuser – so tief, wie die Schule es braucht, und nicht tiefer.

```
Freie Schule Musterstadt (Mandant)
├── Kindergarten
├── Schule
│   ├── Unterstufe (1–4)
│   ├── Mittelstufe (5–8)
│   └── Oberstufe (9–13)
└── Internat
    ├── Haus A
    └── Haus B
```

| Glied | Ausprägung |
|---|---|
| Identität | Name, Art (`site`, `department`, `stage`, `house`, `other`), Elternknoten, optional Programm(e) aus dem Paket |
| Träger | Leitung der Einheit (Funktionsrolle, z. B. Oberstufenkonferenz, Internatsleitung) |
| Zustand | `aktiv` · `aufgelöst` (mit Datum) |
| Lebensende | Keins im Schuljahresrhythmus; Einheiten sind stabil |
| Verlauf | Umbenennung, Verschiebung im Baum, Auflösung |
| Sichtbarkeitskreis | Mitarbeiterkreis; Eltern und Schüler sehen nur die Einheiten, in denen sie eingeschrieben sind |

Die Einheit ist der Ort, an dem Zuständigkeit *oberhalb* der Gruppe hängt: Wer die Oberstufe leitet, wer für das Internat verantwortlich ist, welche Räume zu welchem Standort gehören. Heute ist das im Rollenmodell als freie Funktionsrolle ohne Bezug abgebildet; die Einheit gibt der Rolle einen Ort.

### 2.2 Lerngruppe (`LearningGroup`)

Jede benannte Menge von Lernenden, die als Gruppe angesprochen, betreut oder unterrichtet wird.

| Art (`kind`) | Beispiel | Jahrgang | Stammgruppe? | Betreuungsrolle |
|---|---|---|---|---|
| `class` | 7b, Klasse 3 | ja | ja | Klassenlehrer:in / Klassenbetreuer:in |
| `homeroom` | Tutorium 12/Meier, Stammgruppe 9A | ja | ja | Tutor:in / Klassenlehrperson |
| `course` | Mathe LK Schmidt, Französisch Niveau B 8 | Jahrgang oder Jahrgangsband | nein | Kurslehrkraft (über Angebot) |
| `project` | Klassenspiel 8, Jahresarbeit-Gruppe, Chor | optional | nein | Projektleitung |
| `residential` | Haus A | nein | nein | Hauseltern / Betreuer:in |
| `mixed-age` | Lerngruppe Sonnenhaus | nein, `age_range` | ja | Lernbegleiter:in |

| Glied | Ausprägung |
|---|---|
| Identität | Name, Art, Organisationseinheit, Programm (aus dem Paket), Jahrgang(e) oder Altersspanne, Schuljahr, optional Zug mit `scope: learning_group` |
| Träger | Die Betreuungsrolle der Gruppe (bei `course` die Lehrkraft des Angebots); Vertretung nach Plattformregel |
| Zustand | `geplant` · `aktiv` · `abgeschlossen` |
| Lebensende | Schuljahresende für `class`, `homeroom`, `course`; Projektende für `project`; kein Ende für `residential` (aber Einschreibungen enden) |
| Verlauf | Anlegen, Zusammenlegen, Teilen, Umbenennen, Träger-Wechsel |
| Sichtbarkeitskreis | Nach Tabelle in Abschnitt 4 |

**Die Klasse ist `kind: class`.** Sie hat einen Jahrgang, ist Stammgruppe, hat Klassenbetreuung, erzeugt Elternkreis und Klassen-Space. Nichts daran ändert sich. Was sich ändert: Die Stammgruppen-Eigenschaft ist jetzt ein Merkmal (`is_home: true`), und andere Gruppenarten können es auch haben (`homeroom`, `mixed-age`) oder nicht (`course`, `project`, `residential`).

**Eine Person hat höchstens eine Stammgruppe je Schuljahr.** Das ist die Regel, die das Modell einfach hält: Elternkreis, Klassenliste, Rücklauf und Sprechtag-Zuständigkeit leiten sich aus der Stammgruppe ab. Kurse und Projekte kommen dazu, ersetzen sie aber nicht. Für `class_model: course` (US High) ist die Stammgruppe optional – dann übernimmt die Organisationseinheit „Jahrgang 10" die Rolle des Kreises. Das ist der eine Fall, der bewusst unvollständig bleibt (Abschnitt 9).

### 2.3 Angebot (`Offering`)

Ein Fach, unterrichtet von einer Lehrkraft in einer Lerngruppe in einem Zeitraum.

```
Offering: Mathematik · Klasse 7b · Frau Meier · SJ 2026/27
Offering: Mathematik Niveau A · Kurs Mathe-A-8 · Herr Ott · SJ 2026/27, 1. Semester
Offering: Eurythmie · Klasse 3 · Frau Kunz · Epoche 3 (Nov–Dez)
```

| Glied | Ausprägung |
|---|---|
| Identität | Fach (aus dem Paket, oder schuleigen), Lerngruppe, Lehrkraft(e), Zeitraum (Schuljahr, Semester, Epoche), Zug-Level wenn das Fach `tracked` ist und der Zug an der Gruppe hängt |
| Träger | Die Lehrkraft |
| Zustand | `geplant` · `läuft` · `beendet` |
| Lebensende | Zeitraumende |
| Verlauf | Lehrkraft-Wechsel, Vertretung, Zeitraum-Änderung |
| Sichtbarkeitskreis | Teilnehmende und deren Eltern sehen Fach und Lehrkraft; Mitarbeiterkreis alles |

Das Angebot ist die Antwort auf „welche Lehrkräfte hat dieses Kind?" – die Frage, die der Elternsprechtag, die Zeugniskonferenz und der Vertretungsplan stellen. Heute wird sie über den Stundenplan beantwortet, was falsch ist, sobald eine Lehrkraft eine Klasse in zwei Fächern hat oder ein Fach epochenweise wechselt.

Für `class`-Gruppen wird das Angebot **aus dem Paket vorbelegt**: Beim Anlegen der 7b entstehen die Angebote aller Pflichtfächer des Jahrgangs, Lehrkraft leer. Das ist der Schritt, der das Modell für Grundschulen unsichtbar macht: Die Sekretärin legt eine Klasse an und trägt Lehrkräfte ein, wie heute.

### 2.4 Einschreibung (`Enrollment`)

Die Teilnahme einer Person an einer Lerngruppe oder einem Angebot, mit Gültigkeit.

```
Enrollment: Lea M. · Klasse 8a · 01.08.2026 – 31.07.2027 · Rolle: Schülerin
Enrollment: Lea M. · Kurs Mathe-A-8 · 01.08.2026 – 31.01.2027 · Niveau: A
Enrollment: Lea M. · Kurs Mathe-B-8 · 01.02.2027 – 31.07.2027 · Niveau: B
Enrollment: Lea M. · Haus A · 01.08.2026 – offen · Rolle: Bewohnerin
Enrollment: Frau Meier · Klasse 7b · SJ 2026/27 · Rolle: Klassenlehrerin
```

| Glied | Ausprägung |
|---|---|
| Identität | Person, Ziel (Gruppe *oder* Angebot), Rolle (`learner`, `teacher`, `assistant`, `mentor`, `resident`), Gültigkeit von–bis, Zug-Level wenn `scope: enrollment` |
| Träger | Wer die Einschreibung verantwortet: Sekretariat für Stammgruppen, Fachkonferenz/Stufenleitung für Kurse, Internatsleitung für Wohngruppen |
| Zustand | `geplant` · `aktiv` · `beendet` · `abgebrochen` |
| Lebensende | Gültigkeitsende; danach nur noch im Verlauf der Person |
| Verlauf | Anlegen, Niveauwechsel, vorzeitiges Ende mit Grund (`Umzug`, `Wechsel`, `Abschluss`) |
| Sichtbarkeitskreis | Die Person, ihre Sorgeberechtigten, die Träger der Gruppe, Sekretariat |

Drei Regeln, die das Objekt tragen:

1. **Auch Lehrkräfte sind eingeschrieben.** „Frau Meier ist Klassenlehrerin der 7b" ist eine Einschreibung mit Rolle `teacher` und Merkmal `is_lead: true` – keine separate Tabelle. Damit haben Klassenbetreuungsliste, Hauseltern und Projektleitung eine Struktur, und die Vertretung ist ein befristetes zweites Enrollment.
2. **Die Gültigkeit ist Pflicht und hat Tagesgenauigkeit.** Kein Enrollment ohne `valid_from`; `valid_to` darf offen sein (Wohngruppe), ist aber für Schuljahresgruppen vorbelegt. Der Niveauwechsel im Februar ist ein Ende und ein Anfang, kein Update – so bleibt nachvollziehbar, was im Zeugnis des ersten Semesters stand.
3. **Das Niveau lebt hier.** `sek-subject-level: A` steht an Leas Einschreibung in den Mathe-Kurs, nicht an Lea und nicht am Fach. Das ist die Konsequenz aus PEX v0.2, Abschnitt 3.2.

---

## 3. Die Zeit

Das heutige Modell kennt die Zeit nur als Schuljahr im Hintergrund. Das neue macht sie explizit, weil drei Vorgänge sonst nicht abbildbar sind:

**Versetzung.** Zum Schuljahreswechsel enden alle Einschreibungen in Jahrgangsgruppen; für jede `class`/`homeroom` entsteht eine Nachfolgegruppe (7b → 8b) mit neuen Einschreibungen für alle, die versetzt sind. Das ist ein Assistent im Sekretariat, kein Automatismus: Vorschlag „8b aus 7b, 31 von 32 übernommen", Bestätigung, fertig. Wiederholer und Abgänger werden einzeln behandelt.

**Wechsel im Jahr.** Niveauwechsel, Klassenwechsel, Kurswechsel: altes Enrollment endet mit Grund, neues beginnt. Das Zeugnis liest für jeden Zeitraum, was galt.

**Stichtagsfragen.** „Wer war am 15.03. in der 8a?" ist eine Abfrage über die Gültigkeit – wichtig für Nachweise, Meldungen und den Datenschutz (Elternkreis-Zugriff endet mit dem Enrollment des Kindes).

Der Schuljahreswechsel ist damit der einzige Moment, an dem das Modell Aufwand macht – und genau dort ist er heute auch: Klassen umbenennen, Schüler umhängen, Klassenlehrer neu setzen. Der Assistent macht es zu einem Vorgang statt zu drei.

---

## 4. Die Tabelle, die alles zusammenhält: Gruppenart → Kreis, Space, Rolle

Das ist der Teil, den das Review unterschätzt hat und der die eigentliche Arbeit ist. Heute erzeugt eine Klasse implizit: einen Elternkreis, einen Schülerkreis, einen Klassen-Space im Chat (Eltern und Schüler getrennt), die Klassenbetreuungsrolle, Sichtbarkeit in Rücklauf, Klassen-Menü, Sprechtag. Mit mehreren Gruppenarten muss das je Art entschieden sein:

| `kind` | Elternkreis | Schülerkreis | Chat-Space | Betreuungsrolle mit Durchgriff | Rücklauf / Klassenliste | Sprechtag-Zuständigkeit |
|---|---|---|---|---|---|---|
| `class` | ja | ja | ja (Eltern + Schüler getrennt) | Klassenbetreuung | ja | Klassenbetreuung + alle Angebots-Lehrkräfte |
| `homeroom` | ja | ja | ja | Tutor:in | ja | Tutor:in + Angebots-Lehrkräfte der Kurse |
| `course` | nein (Eltern sehen Angebot über das Kind) | optional (Kurs-Space für Oberstufe) | optional, Schüler | Kurslehrkraft ohne Betreuungs-Durchgriff | nein | Kurslehrkraft als Fachlehrkraft |
| `project` | nein | ja, befristet | ja, befristet, Schüler | Projektleitung, befristet | nein | nein |
| `residential` | ja (Eltern der Bewohner) | ja | ja (Bewohner; Eltern optional) | Hauseltern, mit Durchgriff auf Bewohner-Anliegen | ja (Anwesenheit) | nein |
| `mixed-age` | ja | ja | ja | Lernbegleitung | ja | wie `class` |

Regeln dahinter:

- **Kreise entstehen nur an Stammgruppen und Wohngruppen.** Ein Kurs erzeugt keinen Elternkreis – die Eltern eines Kindes im Mathe-LK sind schon im Elternkreis seines Tutoriums. Sonst wäre eine Oberstufenmutter in acht Kreisen.
- **Betreuungs-Durchgriff (Anliegen, Fallakte, Chronik) hat nur, wer Stammgruppe oder Wohngruppe trägt.** Die Kurslehrkraft sieht ihre Teilnehmenden und deren Eltern-Kontakte für das Angebot, nicht die Akte.
- **Ein Kind mit Stammgruppe und Wohngruppe hat zwei Betreuungsrollen** – Klassenlehrerin und Hauseltern. Beide sehen den Fall-Kontext des Kindes; wer ein Anliegen anlegt, wählt, ob es die Schule oder das Internat betrifft. Das ist der Grund, warum das Internat nicht als „noch eine Klasse" gebaut werden darf.
- **Spaces folgen dem Enrollment.** Endet die Einschreibung, endet die Mitgliedschaft im Space – über das geplante Synapse-Modul (managed rooms), das den Homeserver als Projektion hält.

---

## 5. Was daraus für die Bestandsmodule folgt

| Modul | Heute | Mit dem Modell |
|---|---|---|
| **Klassen-Menü „Meine Klasse"** | an Klasse | an jeder Gruppe, deren Träger man ist; Titel aus `kind` und Paket-Terminologie („Mein Tutorium", „Mein Haus") |
| **Rücklauf** | je Klasse | je Stammgruppe oder Wohngruppe; unverändert für Grundschulen |
| **Elternsprechtag** | Lehrkräfte je Klasse | Lehrkräfte je Kind aus dessen Angeboten; Oberstufe funktioniert damit erstmals |
| **Stundenplan** | Fach × Klasse × Lehrkraft × Zeit | liest Angebote als Vorgabe (welche Kombinationen es gibt) und plant nur noch die Zeit |
| **Zeugnis** | Fächer der Klasse | Angebote der Person im Zeitraum, mit Niveau aus dem Enrollment |
| **Vertretung** | Lehrkraft-Ebene | befristetes Enrollment mit Rolle `teacher` an Angebot oder Gruppe – auditiert wie alle Durchgriffe |
| **Konferenzen** | Themen je Klasse/Stufe | Themen je Gruppe oder Organisationseinheit (Oberstufenkonferenz = Einheit) |
| **Rollen / Sphären** | vier Kreise, Klasse als Bezug | vier Kreise bleiben; Bezug ist Gruppe oder Einheit; Funktionsrollen bekommen optional einen Ort im Baum |
| **E-Mail-Verteiler** | „Klasse 7a (Eltern)" | jeder Kreis einer Gruppe oder Einheit ist ein Adressat-Knoten: „Haus A (Eltern)", „Oberstufe (Schüler)" |

Nichts davon muss am ersten Tag umgestellt sein. Die Klasse bleibt `class`, und jedes Modul, das heute „Klasse" liest, liest morgen „Gruppe mit `kind: class`" – ein Alias, kein Umbau.

---

## 6. Migration

Der Bestand (fünf Mandanten, Klassen mit Schülerlisten, Klassenlehrkräften, Familien) wird nicht umgebaut, sondern **übersetzt**:

1. Mandant wird Wurzel-OrgUnit; keine weiteren Einheiten (die Schule legt sie später an, wenn sie will).
2. Jede Klasse wird `LearningGroup(kind: class, is_home: true)` mit Jahrgang aus dem Klassennamen (wo eindeutig) und dem laufenden Schuljahr.
3. Jede Schüler-Klassen-Zuordnung wird `Enrollment(role: learner, valid_from: Schuljahresbeginn, valid_to: Schuljahresende)`.
4. Jede Klassenbetreuungs-Zuordnung wird `Enrollment(role: teacher, is_lead: true)`.
5. Angebote werden **nicht** erzeugt – erst wenn eine Schule den Fachkatalog aktiviert. Bis dahin beantwortet der Stundenplan wie heute „welche Lehrkräfte hat das Kind".
6. Alle bestehenden Kreise, Spaces und Rollen bleiben an der Gruppe mit derselben ID hängen.

Die Migration ist eine Schema-Migration plus Datenübersetzung, ohne Nutzer-sichtbare Änderung. Das ist die Bedingung, unter der sie überhaupt gemacht werden darf.

---

## 7. Technischer Rahmen

**Datenmodell (Prisma, Skizze):**

```
OrgUnit          id, tenantId, parentId, name, kind(site|department|stage|house|other),
                 programIds[], leadRoleId, status, dissolvedAt
LearningGroup    id, tenantId, orgUnitId, name, kind(class|homeroom|course|project|residential|mixed-age),
                 isHome, programId, gradeIds[], ageMin, ageMax, schoolYearId,
                 trackId, trackLevelId, status, successorOfId
Offering         id, tenantId, groupId, subjectId, periodKind(year|semester|epoch|custom),
                 validFrom, validTo, trackLevelId, status
OfferingTeacher  offeringId, personId, isLead, validFrom, validTo     // Vertretung = 2. Zeile befristet
Enrollment       id, tenantId, personId, targetKind(group|offering), targetId,
                 role(learner|teacher|assistant|mentor|resident), isLead,
                 validFrom, validTo, trackLevelId, endReason, status
SchoolYear       id, tenantId, label, startsOn, endsOn
```

Invarianten (datenbankseitig, nicht nur im Code):
- Je Person, Schuljahr und Mandant höchstens ein aktives `learner`-Enrollment in einer Gruppe mit `isHome: true` (partieller Unique-Index über `personId, schoolYearId` where `isHome and role = learner and status = aktiv`).
- Enrollments derselben Person am selben Ziel dürfen sich zeitlich nicht überlappen (Exclusion-Constraint über `tstzrange(validFrom, validTo)`).
- `trackLevelId` an einem Enrollment nur, wenn der Track `scope: enrollment` hat; an einer Gruppe nur bei `scope: learning_group`. Geprüft gegen das effektive Paket des Mandanten.

**Abgeleitete Sichten (materialisiert, bei Änderung neu):**
- `person_groups_current`: Person → aktive Gruppen mit Art und Rolle. Das ist, was jede Berechtigungsprüfung liest.
- `person_teachers_current`: Person → Lehrkräfte aus aktiven Angeboten. Das ist, was der Sprechtag liest.
- `group_circles`: Gruppe → Eltern-/Schülerkreis-Mitglieder. Das ist, was Verteiler und Spaces lesen.

**API (v1, Owner-Prinzip):**

```
GET/POST   /v1/org-units                          Baum lesen / Einheit anlegen
GET/POST   /v1/groups                             Gruppen (Filter: kind, schoolYear, orgUnit)
POST       /v1/groups/:id/succeed                 Nachfolgegruppe fürs neue Schuljahr (Versetzungsassistent)
GET/POST   /v1/groups/:id/offerings               Angebote einer Gruppe; POST legt an, ggf. aus Paket vorbelegt
GET/POST   /v1/enrollments                        Einschreibungen (Filter: person, target, valid_at)
PATCH      /v1/enrollments/:id/end                Beenden mit Grund und Datum
POST       /v1/enrollments/:id/move               Beenden + neues Enrollment in einem Schritt (Niveau-/Kurswechsel)
GET        /v1/persons/:id/groups?at=YYYY-MM-DD   Stichtag
GET        /v1/persons/:id/teachers?at=           Lehrkräfte aus Angeboten
```

**Datenschutz:**
- Eine Einschreibung ist ein personenbezogenes Datum mit Aufbewahrungspflicht (Schülerakte). Sie wird nie gelöscht, sondern beendet; die Löschung folgt der Aufbewahrungsfrist der Akte.
- `endReason` ist eine geschlossene Liste (`Schuljahresende`, `Versetzung`, `Wechsel`, `Umzug`, `Abschluss`, `Abbruch`); kein Freitext, damit keine Begründungen über Kinder entstehen.
- Zug-Level ist ein pädagogisches Datum – sichtbar für die Person, ihre Sorgeberechtigten, die Lehrkräfte des Angebots und die Stammgruppen-Betreuung; nicht für den Elternkreis der Gruppe.
- Wohngruppen-Enrollments (`residential`) sind für den Schulteil nur als „ist Internatsschüler" sichtbar, nicht mit Haus – außer für die Betreuungsrollen. Umgekehrt sehen Hauseltern die Stammgruppe, nicht die Kurse.
- DSB-Gate vor P1 für die Sichtbarkeitsregeln in Abschnitt 4.

---

## 8. Fahrplan

| Stufe | Inhalt | Ergebnis |
|---|---|---|
| **P0** | Schema, Migration (Abschnitt 6), `LearningGroup(kind: class)` und `Enrollment` als Ersatz für Klasse/Schülerliste/Klassenlehrer; Schuljahr als Objekt; Versetzungsassistent | Bestand läuft unverändert; Schuljahreswechsel wird ein Vorgang |
| **P1** | `Offering` mit Vorbelegung aus dem Paket; Sprechtag und Zeugnis lesen Lehrkräfte aus Angeboten; Vertretung als befristetes Enrollment | „Welche Lehrkräfte hat dieses Kind" hat eine Wahrheit |
| **P2** | `kind: homeroom` und `course` mit `enrollment`-Zug; Kursoberstufe und Niveaufächer; Kreis-/Space-Regeln nach Abschnitt 4 im Synapse-Modul | Oberstufe der Bestandskunden und CH-Sek tragen |
| **P3** | `OrgUnit`-Baum mit Leitungsrollen; `residential` mit Hauseltern; `project` befristet; `mixed-age` | Internat und Waldorf-Projektgruppen |
| **P4** | `class_model: course` ohne Stammgruppe (US) – nur bei Kunde | – |

P0 ist die Übersetzung ohne sichtbare Änderung. P2 ist der Grund für das ganze Konzept.

---

## 9. Offene Punkte (Owner-Entscheidungen)

1. **Stammgruppe als Pflicht?** Vorschlag: ja für alle Programme außer `class_model: course`. Damit bleibt jedes Kind adressierbar (Elternkreis, Rücklauf, Sprechtag) und die US-Variante ist der einzige Sonderfall.
2. **Vertretung als Enrollment oder als eigenes Objekt?** Vorschlag: Enrollment mit `isLead: false` und Gültigkeit – dann hat die Vertretung dieselben Rechte wie die Lehrkraft am Angebot, aber nur im Zeitraum. Die Plattform-Vertretungsregel (Träger-Vertretung) bleibt daneben für Karten.
3. **Tutorium in der Oberstufe:** `homeroom` mit Elternkreis – oder bleibt der Elternkreis in der Oberstufe beim Jahrgang (OrgUnit)? Waldorfschulen halten die Klasse bis 12; andere lösen sie in 11 auf. Vorschlag: beides erlauben, die Schule wählt je Programm.
4. **Wer darf Kurse anlegen?** Sekretariat, Stufenleitung oder die Lehrkraft selbst? Kurse entstehen bei der Oberstufenplanung in großer Zahl; Vorschlag: Stufenleitung mit Fähigkeit „Kurse verwalten", Lehrkraft kann Teilnehmende sehen, nicht ändern.
5. **Angebot ohne Gruppe?** Einzelunterricht (Instrument, Förderung) ist ein Angebot mit genau einer Person. Vorschlag: Gruppe `kind: course` mit einem Mitglied – kein Sonderfall im Modell, nur in der Oberfläche.
6. **Epochen als Zeitraum:** `periodKind: epoch` reicht für Waldorf; braucht der Stundenplan die Epochenfolge aus dem Angebot, oder umgekehrt? Vorschlag: Angebot sagt „Epoche 3", Stundenplan legt die Wochen fest.
7. **DSB-Gate** für Abschnitt 4 und 7 vor P1.

---

## 10. Selbstprüfung am absoluten Maßstab

- **Der Kern des Modells ist gut begründet; die Kreis-Tabelle in Abschnitt 4 ist es nicht.** Sie ist plausibel, aber aus dem Schreibtisch heraus entstanden. Ob Oberstufenkurse einen Schüler-Space brauchen oder ob das zu Chat-Wildwuchs führt, weiß ich erst nach einem Schuljahr mit einer echten Oberstufe. Die Tabelle sollte als Vorgabe mit Schalter je Mandant gebaut werden, nicht als Gesetz.
- **Zwei Betreuungsrollen je Kind (Schule + Internat) sind eine Behauptung ohne Prüfung.** Wer entscheidet bei Widerspruch? Das ecole-Konzept muss das beantworten, nicht dieses hier.
- **Die Migration klingt harmlos und ist es wahrscheinlich nicht.** Fünf Mandanten mit unterschiedlich gepflegten Klassennamen („7b", „Klasse 7", „7. Klasse Müller") – der Jahrgang lässt sich nicht überall ableiten. P0 braucht einen Migrationsbericht je Mandant, den ein Mensch liest.
- **Der Versetzungsassistent ist der Punkt, an dem Sekretariate das Modell beurteilen werden.** Wenn er schlechter ist als heute „Klasse umbenennen", ist das Modell gescheitert – egal wie sauber es ist. Er braucht einen eigenen Entwurf mit Oberfläche vor P0.
- **`class_model: course` ist bewusst nicht gelöst.** Ein Kind ohne Stammgruppe hat keinen Elternkreis; der Vorschlag „Jahrgang als OrgUnit übernimmt" ist ein Platzhalter. Solange kein US-Kunde da ist, darf das so bleiben – es muss nur klar so heißen.
- **Was das Modell absichtlich nicht kann:** Module mit Credits, Prüfungsordnungen, Kohorten über mehrere Programme, Lernende an mehreren Mandanten. Wenn eines davon gebraucht wird, ist das eine neue Version, nicht ein Overlay.
