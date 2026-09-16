# PEX – Prilog Education Exchange

**Ein offenes Format, das beschreibt, was ein Schulsystem kennt** – Stufen, Jahrgänge, Bildungsgänge, Fächer, Züge, Abschlüsse, Notenskalen, Begriffe, Regeln und Rechtsgrundlagen. Ein Land, ein Bundesland, ein Kanton, eine Pädagogik: jeweils eine JSON-Datei, die sich übereinanderlegen lässt.

*An open, layered JSON format describing education systems (stages, grades, programs, subjects, tracks, qualifications, grading, terminology, rules, legal references) for Germany, Switzerland, Austria and the US, with pedagogical overlays. Documentation is in German; the schema is language-neutral.*

```
Basis-PEX          de · ch-de · at · us
   ↓
Regional-Overlay   de-hh · de-by · de-sh · ch-zh …
   ↓
Pädagogik-Overlay  waldorf · montessori          (am Alter verankert, passt über jede Basis)
   ↓
Mandanten-Overrides (die Schule selbst)
   ↓
= effektives Schulsystem eines Mandanten
```

## Grundregeln

1. **Ein PEX enthält niemals eine Instanz.** Es beschreibt Typen (das Gymnasium), nicht Dinge (die Klasse 7b).
2. **PEX rechnet nicht.** Regeln, Prüfungen und Rechtsbezüge stehen als Text mit Quelle.
3. **Ausblenden statt löschen.** Ein Overlay entfernt nichts; es setzt `disabled: true`. So bleibt sichtbar, dass Hamburg die Realschule *abgeschafft* hat.
4. **Pädagogik hängt am Alter.** Waldorf und Montessori gibt es in jedem Land; die Länder zählen Jahrgänge verschieden, das Alter deckt sich.

## Inhalt

| Pfad | Was |
|---|---|
| `schema/pex.schema.json` | JSON-Schema (Draft 2020-12), **Version 2.2** |
| `packages/base/` | Basis-Pakete: `de`, `ch-de`, `at`, `us` |
| `packages/overlays/` | Regional: `de-hh`, `de-by`, `de-sh`, `ch-zh` · Pädagogik: `waldorf`, `montessori` |
| `dist/index.json` | Registry aller Pakete und Standard-Stapel mit Versionen und Prüfsummen – das liest ein Loader zuerst |
| `dist/effective/` | 25 materialisierte Stapel (`de+de-hh+waldorf.json` …), fertig zum Laden |
| `tools/validate.py` | Referenz: Datei gegen Schema, Stapel referenziell und semantisch |
| `tools/pex.mjs` + `pex.d.ts` | Dieselbe Logik in JavaScript, ohne Abhängigkeiten – das nutzt Prilog |
| `tools/build.py` | Schreibt `dist/` |
| `tools/sync-to-prilog.sh` | Kopiert Schema, Pakete, `dist/` und Loader in das Prilog-Backend |
| `docs/anleitung.md` | Aufbau und Logik des Formats – **hier anfangen** |
| `docs/integration-prilog.md` | Wie Prilog PEX einbindet: Registry, Pinnen, Overrides, Onboarding einer neuen Schule |
| `docs/konzept-pex-format.md` | Konzept v0.2: warum das Format so gebaut ist (mit Stand-Kasten) |
| `docs/regionale-varianz.md` | Was in DE/CH/AT regional variiert und wie PEX es trägt |
| `docs/konzept-organisationsmodell.md` | Gegenstück auf der Anwendungsseite: wie eine Schule auf ein PEX abgebildet wird |

## Schnellstart

```bash
pip install jsonschema
python tools/validate.py              # alles: Schema, 25 Stapel
python tools/validate.py de de-hh     # ein Stapel
python tools/build.py                 # dist/ neu schreiben
node --test tools/pex.test.mjs        # JS-Implementierung gegen die Referenz
```

Ein effektives PEX in JavaScript:

```js
import { loadAll, effective, subjectsOfProgram, term } from './tools/pex.mjs';
const { effective: pex, hints } = effective(['de', 'de-hh', 'waldorf'], loadAll());
term(pex, 'class_teacher', 'de');                       // "Klassenlehrer:in / Klassenbetreuer:in ab der Oberstufe"
subjectsOfProgram(pex, pex.programs.find(p => p.id === 'waldorf-ersatzschule')).length;
```

Ein minimales Paket:

```json
{
  "meta": {
    "format": "pex",
    "schema": "https://raw.githubusercontent.com/brasilspace/PEX-Prilog-Education-Exchange/main/schema/pex.schema.json",
    "id": "xx", "version": "0.1.0", "kind": "base",
    "country": "XX", "languages": ["de"], "name": { "de": "Beispielland" }
  },
  "grades": [ { "id": "g1", "label": { "de": "1. Klasse" }, "ordinal": 1, "typical_age": 6 } ],
  "programs": [ { "id": "primar", "label": { "de": "Primarschule" }, "grades": ["g1"], "class_model": "class" } ]
}
```

## Status

| Paket | Version | Stand | Geprüft mit Schule? |
|---|---|---|---|
| `de` | 0.3.0 | Basis nach KMK, generisch | Bestandskunden HH/SH |
| `de-hh` | 0.2.0 | Struktur + Regeln + Recht | nein – Rechtslage vor Einsatz gegenlesen |
| `de-sh` | 0.1.0 | Struktur + Regeln + Recht; Paragrafen in `notes` markiert | nein – Bestandskunden SH als Erste |
| `de-by` | 0.1.1 | Struktur + Regeln + Recht | nein |
| `ch-de` | 0.3.0 | Lehrplan 21, Gymnasium nach MAR | nein |
| `ch-zh` | 0.1.0 | Sek A/B + Anforderungsstufen, Lang-/Kurzgymnasium, ZAP | nein |
| `at` | 0.3.0 | Lehrpläne 2023 | nein |
| `us` | 0.2.1 | generisches K-12 | nein |
| `waldorf` | 0.4.0 | Pädagogik-Overlay, Alter statt Jahrgang, de/fr/en | Waldorf: Bestandskunden |
| `montessori` | 0.3.0 | Pädagogik-Overlay, altersgemischt | nein |

Fehlende Overlays sind kein Hindernis: Ein Mandant ohne Overlay läuft auf dem Basis-Paket und ergänzt selbst. Was eine Schule ergänzt, kommt als Beitrag hierher zurück – nicht als Sonderlocke im Mandanten.

## Mitwirken

Korrekturen und neue Overlays sind willkommen – siehe `CONTRIBUTING.md`. Jede Regel braucht eine Quelle; jeder Commit ein `Signed-off-by`. CI prüft Schema, alle Stapel, die Frische von `dist/` und die Gleichheit von JavaScript und Python.

## Lizenz

- Schema, Werkzeuge, Dokumentation: **Apache 2.0** (`LICENSE`)
- Pakete unter `packages/` und `dist/`: **CC BY 4.0** (`packages/LICENSE`) – Nutzung und Änderung frei, Namensnennung „Prilog / PEX" erforderlich

„PEX" und „Prilog Education Exchange" sind Bezeichnungen von Prilog. Die Apache-Lizenz räumt keine Markenrechte ein: Implementieren darf jeder, ein abweichendes Format darf nicht „PEX" heißen.

## Kontakt

Prilog · [prilog.chat](https://prilog.chat) · info@prilog.team
