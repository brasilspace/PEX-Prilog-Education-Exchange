# PEX in Prilog einbinden

Stand 16.09.2026 · gilt für Schema 2.2

Ziel: Wenn eine Schule Prilog bestellt, ist ihr Schulsystem in Minuten eingestellt, nicht in Wochen implementiert. Land, Region und Pädagogik sind Daten aus diesem Repo; der Code kennt nur das Schema.

---

## 1. Was heute im Backend liegt – und was daraus wird

| Heute (`prilog-backend-api/src/modules/schulsystem/`) | Morgen |
|---|---|
| `pakete/*.json` – eigene Kopien von `de`, `ch-de`, `at`, `us`, `waldorf.overlay`, `montessori.overlay` (Schema v2, ohne `rules`/`exams`/`legal`) | `pex/` – generiert per `tools/sync-to-prilog.sh`, nie von Hand geändert. Korrekturen gehen ins Repo und kommen per Sync zurück |
| `pakete/schoolsystem.schema.json` (v2) | `pex/schema/pex.schema.json` (v2.2) |
| `pakete-pruefen.ts` – Verweis-Prüfung, Alter→Jahrgang, Fächer je Programm | `pex/tools/pex.mjs` – dieselben Funktionen (`checkRefs`, `gradesForAge`, `subjectsOfProgram`), plus `merge`, `stack`, `effective`, `term`. Die Datei ist ESM ohne Abhängigkeiten; `pex.d.ts` liefert die Typen |
| `programs[].hinweis` (Backend-eigenes Feld) | `programs[].remark` (Schema 2.2; an jedem Element erlaubt) |
| `pakete.service.ts` – Auswahl je Mandant als **Liste** in `schulsystem.systeme`, Schlüssel = Dateiname (`waldorf.overlay`) | bleibt Liste; Schlüssel = `meta.id` (`waldorf`). Einmalige Umschreibung der zwei Overlay-Schlüssel |
| kein Loader, kein Merge | `effective()` aus `pex.mjs`, Ergebnis je Mandant materialisiert und gepinnt |

Die Entscheidungen, die das Backend am 15./16.09. getroffen hat, sind ins Repo übernommen: Liste statt Einzelwert (ecole führt zwei Systeme), Waldorf am Alter statt an `g1…g13`, Montessori ohne Stufen-Verweise, sichtbare Hinweise an dünnen Programmen, `class_model` an jedem Programm. Nichts davon geht beim Umstieg verloren.

---

## 2. Die Registry: `dist/index.json`

Ein Loader liest zuerst `dist/index.json`:

```json
{ "format": "pex-index", "schema_version": "2.2",
  "packages": [ { "id": "de", "kind": "base", "version": "0.3.0", "file": "packages/base/de.pex.json", "sha256": "…" }, … ],
  "stacks":   [ { "id": "de+de-hh+waldorf", "layers": [ {"id":"de","version":"0.3.0"}, … ], "file": "dist/effective/de+de-hh+waldorf.json", "sha256": "…" }, … ] }
```

- `packages` sagt, was es gibt – das ist die Auswahl, die die Oberfläche anbietet (Basis, regionale Overlays je Land, Pädagogik).
- `stacks` sind die vorgerechneten Standard-Kombinationen. Ein Mandant, dessen Auswahl einem Standard-Stapel entspricht, lädt die Datei; für andere Kombinationen (z. B. zwei Basen bei ecole) rechnet `pex.mjs` den Stapel aus den Paketen.
- `sha256` macht ein Update sichtbar: Prüfsumme anders → Version anders → Diff anzeigen.

---

## 3. Der Mandant: Pin, Overrides, effektives PEX

Drei Dinge werden je Mandant gespeichert, alles andere ist abgeleitet:

| Schlüssel (`tenant_settings`) | Inhalt | Beispiel |
|---|---|---|
| `schulsystem.systeme` | gewählte Paket-IDs, in Stapel-Reihenfolge; mehrere Basen erlaubt | `["de","de-sh","waldorf"]` · ecole: `["ch-de","ch-zh","waldorf","us"]` |
| `schulsystem.pin` | Versionen, mit denen der Mandant läuft (`meta.layers` des effektiven PEX) | `[{"id":"de","version":"0.3.0"},…]` |
| `schulsystem.overrides` | Mandanten-Overlay, technisch dasselbe Format (`kind: overlay`, `extends: "*"`) | eigene Fächer, Aliase, ausgeblendete Programme |

Das effektive PEX ist `effective([...systeme, overrides])`, gegen Schema und `checkRefs` geprüft, im Speicher gecacht (Schlüssel: Hash aus Pin + Overrides). Bei zwei Basen (ecole) gibt es zwei effektive PEX nebeneinander, jede Lerngruppe nennt ihres.

**Vorgabe hält den Bestand.** Leere Liste = „noch nicht gesagt“, keine laufende Installation verschiebt sich. Erst eine gewählte Liste liefert Jahrgänge, Fächer, Begriffe – und auch dann nur an Module, die danach fragen.

**Ein Override liegt über jeder gewählten Basis** (`extends: "*"`). Für ein Haus mit zwei Systemen gilt deshalb dieselbe Regel wie für Pädagogik-Overlays: Fächer über `age_from`/`age_to` binden, nicht über Jahrgangs-IDs, und `domain` nur, wenn es sie in beiden Basen gibt. Anpassungen, die nur ein System betreffen, brauchen Overrides je Basis – erst bauen, wenn eine Schule es braucht.

**Ehrlich zum Pin:** Prilog trägt je Paket genau eine Version (die gesyncte). Der Pin sagt, welchen Stand die Schule bestätigt hat, nicht, welcher zurückgehalten wird; ein Sync mit neuer Version erscheint als `abweichungen` in `GET …/schulsystem/effective`, die Karte zeigt sie und lässt per `PUT …/schulsystem/pin` bestätigen. Ein Versionsarchiv ist eine spätere Entscheidung.

**Update ist ein bewusster Schritt.** Neuer Sync bringt neue Versionen in `pex/`. Der Mandant bleibt auf seinem Pin. Die Stammdaten-Karte zeigt „neu: `de-sh` 0.2.0 – Abitur-Komponenten korrigiert“ mit Diff; ein Klick übernimmt. Kein stiller Austausch.

---

## 4. Etappen

| Etappe | Inhalt | Ergebnis |
|---|---|---|
| **E0 – Sync** ✅ 16.09. (Backend `0602a3c`, hermes) | `tools/sync-to-prilog.sh` einmal laufen lassen; `pakete.service.ts` liest `pex/packages` und nutzt `pex.mjs` statt `pakete-pruefen.ts`; `hinweis`→`remark`; Overlay-Schlüssel `waldorf.overlay`→`waldorf`, `montessori.overlay`→`montessori` einmalig in `schulsystem.systeme` umschreiben; alte `pakete/` und `pakete-pruefen.ts` entfernen, Tests auf `pex.mjs` umziehen | Backend und Repo haben eine Wahrheit. Oberfläche unverändert |
| **E1 – Effektiv + Pin** ✅ 16.09. (Backend `fbbeb3e`, hermes) | `schulsystem.pin` und `schulsystem.overrides`; `GET /platform/v1/schulsystem/effective` liefert das effektive PEX (oder zwei); `PUT …/overrides` validiert gegen Schema + `checkRefs`; Cache | Ein Modul kann fragen: „Welche Fächer hat Jahrgang 8 in diesem Haus?“ |
| **E2 – Verbraucher** ✅ 16./17.09. (Backend `5ae55b6`, Web-Client Branch `pex-e2`): Stammdaten-Karte; Vorlage für die Stammdaten (`GET /schulsystem/vorlage`, `POST …/vorlage/faecher`, `POST …/vorlage/fach-in-klasse`); Landkarte zeigt die Vorlage an Stufe 2 und 4; Begriffe im Client über `useSchulbegriffe`; Klassenname aus dem PEX-Jahrgangs-Label. Nachweis am lebenden Objekt für Klassenname und Fach × Klasse steht aus (Prüfstand führt Kurse) |
| **E3 – Update-Fluss** | Registry-Diff je Mandant, Übernahme mit Bestätigung, Protokoll | Ein Paket-Update ist ein Vorgang, kein Deploy |
| **E4 – Onboarding** | Setup-Assistent: Land → Region → Pädagogik → Stapel; Vorschlag der Lerngruppen aus `programs × grades`; Fächer vorbelegt; Begriffe sofort richtig | Eine neue Schule ist in einer Sitzung eingerichtet |

E0 ist klein und ohne sichtbare Änderung. E2 ist der Grund für das Ganze.

---

## 5. Onboarding einer neuen Schule (Zielbild E4)

1. **Wo steht die Schule?** Land, Region, Pädagogik ankreuzen → `schulsystem.systeme = ["de","de-sh","waldorf"]`. Fehlt ein regionales Overlay, läuft die Schule auf der Basis; das Overlay wird als Beitrag ins Repo nachgeliefert (40–120 Zeilen), nicht als Sonderfall im Mandanten.
2. **Was führt sie davon?** Programme abwählen, die das Haus nicht hat (`disabled` im Override) – die Waldorfschule ohne Kindergarten, das Gymnasium ohne Oberstufe.
3. **Eigene Fächer und Namen** als Override: `aliases`, zusätzliche `subjects`, `remark`.
4. **Lerngruppen vorschlagen**: je Programm und Jahrgang eine Klasse (`class_model: class`), Stammgruppe plus Kurse (`homeroom`), altersgemischt (`mixed-age`) – nach *Organisationsmodell und Einschreibung*.
5. **Fertig.** Begriffe, Fächerkatalog, Zeugnisrhythmus, Notenskala, Rechtsbezüge stehen. Was fehlt, ist ein Beitrag ans Repo – und beim nächsten Kunden im selben Land schon da.

---

## 6. Terminologie-Katalog

Schlüssel, die die Oberfläche kennt und über `term(pex, key, lang)` liest. Fehlt ein Schlüssel im effektiven PEX, greift der Plattform-Standard (heute: die deutschen Begriffe). Pakete dürfen weitere Schlüssel einführen; die Oberfläche benutzt sie, sobald ein Modul danach fragt.

| Schlüssel | de (Basis `de`) | Beispiele anderswo |
|---|---|---|
| `teacher` | Lehrkraft | Lehrperson (CH, AT), Teacher |
| `class_teacher` | Klassenleitung | Klassenlehrperson (CH), Klassenvorstand (AT), Homeroom Teacher (US), Lernbegleiter:in (Montessori) |
| `head` | Schulleitung | Direktion (AT), Principal (US), Schulführungskonferenz (Waldorf) |
| `class` | Klasse | Lerngruppe (Montessori), Homeroom (US) |
| `grade` | Jahrgangsstufe | Klassenstufe (CH), Schulstufe (AT), Grade (US) |
| `student` | Schülerin / Schüler | Student |
| `parents` | Erziehungsberechtigte | Parents / Guardians |
| `report` | Zeugnis | Entwicklungsbericht (Montessori), Report Card (US) |
| `report_midyear` | – | Halbjahreszeugnis (HH), Zwischenzeugnis (BY), Schulnachricht (AT) |
| `parent_conference` | Elternsprechtag | Elterngespräch (CH), Parent-Teacher Conference (US) |
| `parent_evening` | Elternabend | Back-to-School Night (US) |
| `holidays` | Ferien | Break (US) |
| `lesson` | Unterrichtsstunde | Lektion (CH), Period (US), Stunde (Waldorf) |
| `subject` | Fach | Unterrichtsgegenstand (AT), Course (US) |
| `track` | Kurs | Niveau (CH), Anforderungsstufe (ZH), Leistungsniveau (AT), Level (US) |

---

## 7. Was bewusst nicht in dieses Repo gehört

- Mandanten-Overrides (Instanzen einer Schule) – sie leben in `tenant_settings`.
- Das Organisationsmodell (Lerngruppe, Angebot, Einschreibung) – es liest PEX, ist aber Prilog-Code.
- Die alten Kopien in `prilog_docs/umsetzung/Schulsystem-Pakete/` – ersetzen durch einen Verweis hierher, sonst gibt es wieder zwei Wahrheiten.
