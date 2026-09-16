# Mitwirken an PEX

Danke, dass du ein Paket korrigieren oder ergänzen willst. Kurz, was zu beachten ist.

## Was hierher gehört

- Korrekturen an bestehenden Paketen (falscher Fachname, geänderte Jahrgangsgrenze, neue Verordnung)
- Neue regionale Overlays (`packages/overlays/<land>-<region>.pex.json`)
- Neue Basis-Pakete für ein Land, das noch fehlt
- Verbesserungen am Schema – bitte vorher ein Issue, weil Schema-Änderungen alle Pakete und beide Implementierungen (`tools/validate.py`, `tools/pex.mjs`) betreffen

## Was nicht hierher gehört

- Instanzen: Schulnamen, Personen, konkrete Ferientermine. PEX beschreibt Systeme, nicht Schulen.
- Logik: Berechnungsregeln, Notenformeln. PEX beschreibt Regeln als Text mit Quelle.
- Stundentafeln mit Wochenstunden.

## So läuft ein Beitrag

1. Fork, Branch, Änderung.
2. `pip install jsonschema && python tools/validate.py` – muss grün sein. Hinweise (`·`) sind erlaubt, Fehler (`✗`) nicht.
3. `python tools/build.py` – schreibt `dist/` neu; `dist/` wird eingecheckt, CI prüft die Frische.
4. `node --test tools/pex.test.mjs` – die JavaScript-Implementierung muss der Referenz weiter gleichen. Wer das Schema ändert, ändert beide.
5. Jede neue oder geänderte `rule`, `exam`, `legal` hat eine `source` (Gesetz, Verordnung, Paragraf) und möglichst eine `url`. Was nicht gegen den Verordnungstext geprüft ist, sagt das in `notes`.
6. `meta.version` des Pakets erhöhen (semver) und `CHANGELOG.md` ergänzen. Mandanten pinnen Versionen; ein Update ist ein bewusster Schritt.
7. Pull Request mit einem Satz, *was* sich geändert hat und *wo das steht*.
8. Commits mit `Signed-off-by:` (DCO, `git commit -s`). Damit bestätigst du, dass du den Beitrag unter der jeweiligen Lizenz einbringen darfst.

## Lizenzen

- Schema, Werkzeuge, Dokumentation: Apache 2.0 (`LICENSE`)
- Pakete unter `packages/` und `dist/`: CC BY 4.0 (`packages/LICENSE`)

Mit deinem Beitrag stimmst du zu, dass er unter der Lizenz des jeweiligen Verzeichnisses veröffentlicht wird.

## Stil

- IDs: kleingeschriebene Slugs, stabil, nicht umbenennen. Neue Namen als `aliases`.
- Overlays enthalten nur, was sich ändert. Ausblenden per `{"id": "…", "disabled": true}`, nie durch Weglassen – das gilt auch für Levels eines Zugs.
- Pädagogik-Overlays (`extends: "*"`) binden Fächer über `age_from`/`age_to`/`age_years`, nie über Jahrgangs-IDs.
- Labels in allen Sprachen aus `meta.languages` der Basis, über der das Overlay liegt.
- `notes` erklärt Pflegenden, was die Struktur nicht sagt; `remark` ist der Satz, den die Schule in der Oberfläche liest.

Siehe `docs/anleitung.md` für Aufbau und Logik des Formats, `docs/integration-prilog.md` für die Anbindung.

Fragen: info@prilog.team
