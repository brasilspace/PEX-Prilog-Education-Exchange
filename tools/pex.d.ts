/** Type declarations for tools/pex.mjs – keep in step with schema/pex.schema.json. */
export type Label = Record<string, string>;
export interface Named { id: string; label?: Label; disabled?: boolean; notes?: string; remark?: Label }
export interface Stage extends Named { ordinal?: number; grades?: string[] }
export interface Grade extends Named { ordinal?: number; stage?: string; typical_age?: number; aliases?: string[] }
export interface Level extends Named {}
export interface Track extends Named { scope: 'learning_group' | 'enrollment' | 'learner' | 'program'; levels: Level[] }
export interface Program extends Named {
  stages?: string[]; grades?: string[]; tracks?: string[]; qualifications?: string[];
  class_model?: 'class' | 'homeroom' | 'course' | 'mixed-age'; aliases?: string[];
  age_range?: [number, number]; duration_years?: number;
  approval?: 'state' | 'private-recognized' | 'private-approved' | 'private-licensed';
}
export interface Qualification extends Named {
  after_grade?: string; after_grade_by_program?: Array<{ program: string; after_grade: string }>;
  grants_access?: string[]; requirements?: Record<string, unknown>; programs?: string[]; aliases?: string[];
}
export interface Subject extends Named {
  domain?: string; grades?: string[]; age_from?: number; age_to?: number; age_years?: number[];
  kind?: 'core' | 'elective' | 'project' | 'remedial' | 'epoch'; tracked?: boolean; optional?: boolean;
  credits?: number; aliases?: string[]; short?: Label; programs?: string[];
}
export interface Rule {
  id: string; kind: 'transition' | 'admission' | 'compulsory-schooling' | 'promotion' | 'subject-choice' | 'attendance' | 'other';
  label: Label; applies_to?: { from_grade?: string; to_grade?: string; from_program?: string; to_program?: string; programs?: string[] };
  mode?: string; summary: Label; source: string; url?: string; disabled?: boolean; notes?: string;
}
export interface Exam {
  id: string; label: Label; qualification: string; mode: 'internal' | 'external' | 'central' | 'state-recognized';
  at_grade?: string; components?: Array<{ id: 'written' | 'oral' | 'practical' | 'presentation' | 'thesis'; count?: number; label?: Label }>;
  summary?: Label; source: string; url?: string; disabled?: boolean; notes?: string;
}
export interface Legal {
  id: string; kind: 'school-act' | 'data-protection' | 'authority' | 'retention' | 'reporting' | 'private-school' | 'other';
  label: Label; summary?: Label; source?: string; url?: string; sections?: Record<string, string>; disabled?: boolean; notes?: string;
}
export interface Scale extends Named { kind: 'numeric' | 'letter' | 'points' | 'percent' | 'text'; values?: Array<string | number>; step?: number; best?: string | number; pass?: string | number; gpa?: Record<string, number>; tendencies?: boolean }
export interface Meta {
  format: 'pex'; schema?: string; id: string; version: string; kind?: 'base' | 'overlay'; extends?: string | string[];
  country: string; region?: string; languages: string[]; name: Label; source?: string; notes?: string; license?: string; maintainer?: string;
  /** only on an effective PEX: the layers it was built from */
  layers?: Array<{ id: string; version: string }>;
}
export interface Pex {
  meta: Meta; terminology?: Record<string, Label>;
  calendar?: { year_start_month?: number; periods?: Array<Named & { months: [number, number] }>; report_points?: string[];
    report_points_by_program?: Array<{ program: string; report_points: string[] }>;
    holiday_authority?: { level?: 'state' | 'canton' | 'municipality' | 'school' | 'federal'; label?: Label; url?: string } };
  grading?: { default_scale?: string; scales?: Scale[]; head_marks?: Array<Named & { scale?: string }>; by_program?: Array<{ program: string; grades?: string[]; scale: string }> };
  stages?: Stage[]; grades?: Grade[]; programs?: Program[]; tracks?: Track[]; qualifications?: Qualification[];
  subject_domains?: Named[]; subjects?: Subject[]; rules?: Rule[]; exams?: Exam[]; legal?: Legal[];
}
export const ID_LISTS: string[];
export const DEFAULT_PACKAGES_DIR: string;
export function extendsOf(meta: Meta | undefined): string[];
export function loadAll(dir?: string): Map<string, Pex>;
export function merge<T>(base: T, over: T): T;
export function stack(ids: string[], packages: Map<string, Pex>): Pex;
export function gradesForAge(eff: Pex, from?: number, to?: number, years?: number[]): string[];
export function subjectGrades(eff: Pex, s: Subject): string[];
export function programGrades(eff: Pex, p: Program): string[];
export function subjectsOfProgram(eff: Pex, p: Program): Subject[];
export function term(eff: Pex, key: string, lang: string, fallback?: string): string;
export function checkRefs(eff: Pex): { errors: string[]; hints: string[] };
export function standardStacks(packages: Map<string, Pex>): string[][];
export function effective(ids: string[], packages?: Map<string, Pex>): { effective: Pex; hints: string[] };
