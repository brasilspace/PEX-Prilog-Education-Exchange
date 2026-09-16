# Mitwirken an PEX

Danke, dass du ein Paket korrigieren oder ergänzen willst. Kurz, was zu beachten ist.

## Was hierher gehört

- Korrekturen an bestehenden Paketen (falscher Fachname, geänderte Jahrgangsgrenze, neue Verordnung)
- Neue regionale Overlays (`packages/overlays/<land>-<region>.pex.json`)
- Neue Basis-Pakete für ein Land, das noch fehlt
- Verbesserungen am Schema – bitte vorher ein Issue, weil Schema-Änderungen alle Pakete betreffen

## Was nicht hierher gehört

- Instanzen: Schulnamen, Personen, konkrete Ferientermine. PEX beschreibt Systeme, nicht Schulen.
- Logik: Berechnungsregeln, Notenformeln. PEX beschreibt Regeln als Text mit Quelle.
- Stundentafeln mit Wochenstunden.

## So läuft ein Beitrag

1. Fork, Branch, Änderung.
2. `pip install jsonschema && python tools/validate.py` – muss grün sein.
3. Jede neue oder geänderte `rule`, `exam`, `legal` hat eine `source` (Gesetz, Verordnung, Paragraf) und möglichst eine `url`.
4. Pull Request mit einem Satz, *was* sich geändert hat und *wo das steht*.
5. Commits mit `Signed-off-by:` (DCO, `git commit -s`). Damit bestätigst du, dass du den Beitrag unter der jeweiligen Lizenz einbringen darfst.

## Lizenzen

- Schema, Werkzeuge, Dokumentation: Apache 2.0 (`LICENSE`)
- Pakete unter `packages/`: CC BY 4.0 (`packages/LICENSE`)

Mit deinem Beitrag stimmst du zu, dass er unter der Lizenz des jeweiligen Verzeichnisses veröffentlicht wird.

## Stil

- IDs: kleingeschriebene Slugs, stabil, nicht umbenennen. Neue Namen als `aliases`.
- Overlays enthalten nur, was sich ändert. Ausblenden per `"disabled": true`, nie durch Weglassen.
- Labels in allen Sprachen aus `meta.languages`.
- Ein `notes`-Feld erklärt, was ein Mensch wissen muss und die Struktur nicht sagt.

Siehe `docs/anleitung.md` für Aufbau und Logik des Formats.

Fragen: info@prilog.team
