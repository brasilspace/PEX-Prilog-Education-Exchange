# Changelog

## 2.1.0 – 2026-09-16
- Schema: `rules`, `exams`, `legal` (deklarativ, `source` Pflicht)
- Schema: `grading.tendencies`, `grading.head_marks`, `grading.by_program`
- Schema: `calendar.report_points_by_program`, `calendar.holiday_authority`
- Schema: `programs[].approval`, `meta.license`, `meta.maintainer`
- Pakete: Overlays `de-hh` (Hamburg), `de-by` (Bayern)

## 2.0.0 – 2026-09-16
- `school_types` → `programs`; `grades` je Programm optional, `age_range`
- `class_model` um `mixed-age` ergänzt
- Track-Scopes `learning_group` / `enrollment` / `learner` / `program` (vormals `class` / `subject`)
- `meta.format` und `meta.schema` Pflicht
- Pakete: `at` (Österreich), Overlay `montessori`

## 1.0.0 – 2026-09-16
- Erstes Schema; Pakete `ch-de`, `de`, `us`, Overlay `waldorf`
