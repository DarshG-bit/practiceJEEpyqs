import {
  ArrowLeft,
  ExternalLink,
  BookOpen,
  Play
} from 'lucide-react';
import type { ChapterCatalogItem, SubjectType } from '../types';

interface SubjectIndexViewProps {
  subject: SubjectType;
  chapters: ChapterCatalogItem[];
  onBackToHome: () => void;
  onStartPractice: (chapter: ChapterCatalogItem) => void;
  onStartCbtSprint: (chapter: ChapterCatalogItem) => void;
}

export const SubjectIndexView: React.FC<SubjectIndexViewProps> = ({
  subject,
  chapters,
  onBackToHome,
  onStartPractice,
  onStartCbtSprint
}) => {
  const subjectChapters = chapters.filter(
    (c) => c.subject.toLowerCase() === subject.toLowerCase()
  );

  const getSubjectDetails = () => {
    switch (subject.toLowerCase()) {
      case 'maths':
      case 'mathematics':
        return {
          title: 'Mathematics Syllabus & Chapter Index',
          accent: 'text-blue-600 dark:text-blue-400',
          borderAccent: 'border-blue-600 dark:border-blue-500',
          bgAccent: 'bg-blue-50 dark:bg-blue-950/40',
          legacyUrl: '../Maths/index.html',
          description:
            'Complete JEE Main Calculus, Matrices, Determinants & Functions syllabus with official difficulty ratings and class color codes.'
        };
      case 'physics':
        return {
          title: 'Physics Syllabus & Chapter Index',
          accent: 'text-indigo-600 dark:text-indigo-400',
          borderAccent: 'border-indigo-600 dark:border-indigo-500',
          bgAccent: 'bg-indigo-50 dark:bg-indigo-950/40',
          legacyUrl: '../Physics/index.html',
          description:
            'Mechanics, Electromagnetism, Optics, Modern Physics, Thermal & Waves with ray and circuit diagrams.'
        };
      case 'chemistry':
        return {
          title: 'Chemistry Syllabus & Chapter Index',
          accent: 'text-emerald-600 dark:text-emerald-400',
          borderAccent: 'border-emerald-600 dark:border-emerald-500',
          bgAccent: 'bg-emerald-50 dark:bg-emerald-950/40',
          legacyUrl: '../Chemistry/index.html',
          description:
            'General Organic Chemistry, Kinetics, Coordination, Electrochemistry & Solutions with reaction mechanisms.'
        };
      default:
        return {
          title: `${subject} Syllabus & Chapter Index`,
          accent: 'text-blue-600',
          borderAccent: 'border-blue-600',
          bgAccent: 'bg-blue-50',
          legacyUrl: '../index.html',
          description: 'Chapter directory and active recall sheets.'
        };
    }
  };

  const details = getSubjectDetails();

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Back and Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-slate-200 dark:border-[#222224] gap-3">
        <button
          onClick={onBackToHome}
          className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-700 dark:text-zinc-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors p-2 rounded-lg border border-slate-200 dark:border-[#27272a] hover:bg-slate-50 dark:hover:bg-[#18181c] min-h-[44px] cursor-pointer self-start sm:self-auto"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Main Dashboard</span>
        </button>

        {/* Legacy HTML Index Link */}
        <a
          href={details.legacyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-blue-600 dark:text-blue-400 hover:underline px-3 py-2 rounded-lg border border-blue-200 dark:border-blue-900/50 bg-blue-50 dark:bg-blue-950/30 min-h-[44px]"
        >
          <span>Open Classic {subject} HTML Index with Color Codes</span>
          <ExternalLink className="w-3.5 h-3.5 ml-0.5" />
        </a>
      </div>

      {/* Header Banner */}
      <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl p-6 sm:p-8 shadow-sm mb-8 relative overflow-hidden">
        <div className={`absolute top-0 left-0 right-0 h-1.5 ${details.bgAccent}`} />
        <span className={`text-xs font-bold uppercase tracking-wider ${details.accent}`}>
          {subject} Syllabus Portal
        </span>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mt-1 tracking-tight">
          {details.title}
        </h1>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 mt-2 max-w-2xl leading-relaxed">
          {details.description}
        </p>

        <div className="mt-4 flex items-center gap-4 text-xs font-medium text-slate-500 dark:text-zinc-400">
          <span>{subjectChapters.length} Total Chapters</span>
          <span>&bull;</span>
          <span>
            {subjectChapters.reduce((acc, c) => acc + c.total_questions, 0).toLocaleString()} Verified Questions
          </span>
        </div>
      </div>

      {/* Chapter Cards Grid */}
      <div className="space-y-4">
        {subjectChapters.map((chapter) => (
          <div
            key={chapter.slug}
            className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm hover:border-slate-300 dark:hover:border-[#333] transition-all"
          >
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-[#18181c] text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-[#27272a]">
                  {chapter.class_tier}
                </span>
                <span className="text-xs text-slate-500 dark:text-zinc-400 font-medium tabular-nums">
                  {chapter.total_questions} Questions &bull; {chapter.types_count} Sub-types
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                {chapter.name}
              </h3>

              {/* Difficulty breakdown */}
              <div className="mt-2.5 flex items-center gap-2 flex-wrap text-xs">
                <span className="text-emerald-700 dark:text-emerald-300 font-medium tabular-nums">
                  Easy: {chapter.difficulty_counts.E}
                </span>
                <span>&bull;</span>
                <span className="text-amber-700 dark:text-amber-300 font-medium tabular-nums">
                  Medium: {chapter.difficulty_counts.M}
                </span>
                <span>&bull;</span>
                <span className="text-rose-700 dark:text-rose-300 font-medium tabular-nums">
                  Difficult: {chapter.difficulty_counts.D}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 flex-wrap md:self-center">
              <button
                onClick={() => onStartPractice(chapter)}
                className="py-2.5 px-4 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center gap-1.5 transition-all min-h-[44px] cursor-pointer"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Practice & Learn</span>
              </button>
              <button
                onClick={() => onStartCbtSprint(chapter)}
                className="py-2.5 px-3.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-[#18181c] hover:bg-slate-200 dark:hover:bg-[#222227] text-slate-800 dark:text-zinc-200 border border-slate-200 dark:border-[#27272a] flex items-center gap-1.5 transition-all min-h-[44px] cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                <span>CBT Sprint</span>
              </button>
              {/* Link to legacy HTML practice sheet */}
              <a
                href={`../${chapter.legacy_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-500 hover:text-slate-800 dark:hover:text-white min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
                title="Open Classic HTML File"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
