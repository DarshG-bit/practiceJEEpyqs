export type SubjectType = 'Maths' | 'Physics' | 'Chemistry' | 'All';

export interface ChapterCatalogItem {
  name: string;
  subject: 'Maths' | 'Physics' | 'Chemistry';
  slug: string;
  class_tier: string;
  total_questions: number;
  difficulty_counts: { E: number; M: number; D: number };
  format_counts: { MCQ: number; Numerical: number };
  types_count: number;
  data_path: string;
  legacy_url: string;
}

export interface CatalogData {
  platform: string;
  total_chapters: number;
  total_questions: number;
  chapters: ChapterCatalogItem[];
}

export interface QuestionOption {
  label: string;
  html: string;
}

export interface Question {
  id: number;
  type_id: number;
  type_name: string;
  kind: 'single' | 'int';
  source: string;
  difficulty: 'E' | 'M' | 'D';
  expected_time_sec: number;
  stem_html: string;
  options: QuestionOption[];
  answer: string;
  solution_html?: string;
}

export interface ChapterData {
  name: string;
  subject: 'Maths' | 'Physics' | 'Chemistry';
  slug: string;
  class_tier: string;
  total_questions: number;
  difficulty_counts: { E: number; M: number; D: number };
  format_counts: { MCQ: number; Numerical: number };
  types: { id: string | number; name: string }[];
  expected_times: Record<string, number>;
  questions: Question[];
}

export type NtaStatus = 'not_visited' | 'not_answered' | 'answered' | 'marked' | 'answered_marked';

export interface QuestionSessionState {
  questionId: number;
  status: NtaStatus;
  selectedOption?: string;
  numericalAnswer?: string;
  timeSpentSec: number;
  isCorrect?: boolean;
  checkedImmediate?: boolean;
}

export interface TestAttempt {
  id?: number;
  testId: string;
  title: string;
  mode: 'cbt' | 'practice';
  subject: string;
  chapterSlug?: string;
  totalQuestions: number;
  answeredCount: number;
  correctCount: number;
  incorrectCount: number;
  score: number;
  maxScore: number;
  accuracy: number;
  timeSpentSec: number;
  durationMinutes: number; // 0 = untimed
  startedAt: string;
  completedAt?: string;
  isCompleted: boolean;
  sessionStates: Record<number, QuestionSessionState>;
  questionIds: number[];
  chapterSlugsIncluded?: string[];
}

export interface RevisionItem {
  id?: number;
  chapterSlug: string;
  questionId: number;
  subject: string;
  kind: 'starred' | 'mistake';
  addedAt: string;
  note?: string;
}

export interface TestConfig {
  mode: 'cbt' | 'practice';
  subjectPool: 'All' | 'Maths' | 'Physics' | 'Chemistry' | string; // or specific chapter slug
  questionCount: number; // 15, 25, 30, 75, or total
  durationMinutes: number; // 30, 60, 90, 180, custom, 0 = untimed
  selectedTypes?: number[];
  difficulties?: ('E' | 'M' | 'D')[];
  formats?: ('MCQ' | 'Numerical')[];
}
