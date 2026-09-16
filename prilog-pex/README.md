# PEX – Prilog Education Exchange

**Ein offenes Format, das beschreibt, was ein Schulsystem kennt** – Stufen, Jahrgänge, Bildungsgänge, Fächer, Züge, Abschlüsse, Notenskalen, Begriffe, Regeln und Rechtsgrundlagen. Ein Land, ein Bundesland, ein Kanton, eine Pädagogik: jeweils eine JSON-Datei, die sich übereinanderlegen lässt.

*An open, layered JSON format describing education systems (stages, grades, programs, subjects, tracks, qualifications, grading, terminology, rules, legal references) for Germany, Switzerland, Austria and the US, with pedagogical overlays. Documentation is in German; the schema is language-neutral.*

```
Basis-PEX          de · ch-de · at · us
   ↓
Regional-Overlay   de-hh · de-by · ch-zh …
   ↓
Pädagogik-Overlay  waldorf · montessori
   ↓
= effektives Schulsystem eines Mandanten
```

## Grundregeln

1. **Ein PEX enthält niemals eine Instanz.** Es beschreibt Typen (das Gymnasium), nicht Dinge (die Klasse 7b).
2. **PEX rechnet nicht.** Regeln, Prüfungen und Rechtsbezüge stehen als Text mit Quelle.

## Inhalt

| Pfad | Was |
|---|---|
| `schema/pex.schema.json` | JSON-Schema (Draft 2020-12), Version 2.1 |
| `packages/base/` | Basis-Pakete: `de`, `ch-de`, `at`, `us` |
| `packages/overlays/` | Regionale Overlays (`de-hh`, `de-by`) und Pädagogik-Overlays (`waldorf`, `montessori`) |
| `docs/anleitung.md` | Aufbau und Logik des Formats – **hier anfangen** |
| `docs/konzept-pex-format.md` | Konzept v0.2: warum das Format so gebaut ist |
| `docs/regionale-varianz.md` | Was in DE/CH/AT regional variiert und wie PEX es trägt |
| `docs/konzept-organisationsmodell.md` | Gegenstück auf der Anwendungsseite: wie eine Schule auf ein PEX abgebildet wird |
| `tools/validate.py` | Validierung: Datei gegen Schema, Stapel referenziell |

## Schnellstart

```bash
pip install jsonschema
python tools/validate.py              # alles
python tools/validate.py de de-hh     # ein Stapel
```

Ein minimales Paket:

```json
{
  "meta": {
    "format": "pex",
    "schema": "https://raw.githubusercontent.com/brasilspace/prilog-pex/main/schema/pex.schema.json",
    "id": "xx", "version": "0.1.0", "kind": "base",
    "country": "XX", "languages": ["de"], "name": { "de": "Beispielland" }
  },
  "grades": [ { "id": "g1", "label": { "de": "1. Klasse" }, "ordinal": 1 } ],
  "programs": [ { "id": "primar", "label": { "de": "Primarschule" }, "grades": ["g1"], "class_model": "class" } ]
}
```

## Status

| Paket | Stand | Geprüft mit Schule? |
|---|---|---|
| `de` | Basis nach KMK, generisch | Bestandskunden HH/SH |
| `de-hh`, `de-by` | Struktur + Regeln + Recht | nein – Rechtslage vor Einsatz gegenlesen |
| `ch-de` | Lehrplan 21, Gymnasium nach MAR | nein |
| `at` | Lehrpläne 2023 | nein |
| `us` | generisches K-12 | nein |
| `waldorf`, `montessori` | Pädagogik-Overlay | Waldorf: Bestandskunden |

Fehlende Overlays sind kein Hindernis: Ein Mandant ohne Overlay läuft auf dem Basis-Paket.

## Mitwirken

Korrekturen und neue Overlays sind willkommen – siehe `CONTRIBUTING.md`. Jede Regel braucht eine Quelle; jeder Commit ein `Signed-off-by`.

## Lizenz

- Schema, Werkzeuge, Dokumentation: **Apache 2.0** (`LICENSE`)
- Pakete unter `packages/`: **CC BY 4.0** (`packages/LICENSE`) – Nutzung und Änderung frei, Namensnennung „Prilog / PEX" erforderlich

„PEX" und „Prilog Education Exchange" sind Bezeichnungen von Prilog. Die Apache-Lizenz räumt keine Markenrechte ein: Implementieren darf jeder, ein abweichendes Format darf nicht „PEX" heißen.

## Kontakt

Prilog · [prilog.chat](https://prilog.chat) · info@prilog.team
