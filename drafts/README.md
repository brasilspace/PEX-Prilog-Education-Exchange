# Entwürfe (nicht freigegeben)

Overlays, die nach Fachkenntnis geschrieben, aber **nicht amtlich geprüft**
sind. Sie liegen bewusst ausserhalb von `packages/`: der Validator, der Build
und der Sync nach Prilog sehen sie nicht. Ein Entwurf wird zum Paket, indem
jemand mit Kenntnis des Landes oder Kantons Struktur, Regeln, Prüfungen und
Paragrafen gegen den aktuellen Verordnungstext liest und die Datei nach
`packages/overlays/` verschiebt (danach `python tools/build.py`).

Prüfen lassen sich Entwürfe trotzdem – in einer Kopie:

    cp -r . /tmp/pex && cp drafts/*.pex.json /tmp/pex/packages/overlays/ && (cd /tmp/pex && python tools/validate.py)

| Entwurf | Basis | Stand | Was vor der Freigabe zu prüfen ist |
|---|---|---|---|
| `de-nw` Nordrhein-Westfalen | `de` | 18.09.2026 | Paragrafen SchulG NRW, APO-SI/APO-GOSt; ZP10-Fächer; G9-Übergang (erste G9-Abiturjahrgänge) |
| `de-bw` Baden-Württemberg | `de` | 18.09.2026 | G9-Rückkehr ab 2025/26 (Jahrgänge), Grundschulempfehlung nach der Reform 2024/25, Niveaustufen G/M/E, Paragrafen SchG |
| `ch-ag` Aargau | `ch-de` | 18.09.2026 | Oberstufen-Typen (Real/Sek/Bez) und Übertrittsverfahren, Abschlusszertifikat Volksschule, SAR-Nummern |
