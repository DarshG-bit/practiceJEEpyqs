import { useState, useEffect, useRef } from 'react';
import { Search, BookOpen, Play } from 'lucide-react';
import type { ChapterCatalogItem, SubjectType } from '../types';

interface ChapterFilterGridProps {
  chapters: ChapterCatalogItem[];
  selectedSubject: SubjectType;
  onSelectSubject: (subject: SubjectType) => void;
  onStartPractice: (chapter: ChapterCatalogItem) => void;
  onStartCbtSprint: (chapter: ChapterCatalogItem) => void;
}

export const ChapterFilterGrid: React.FC<ChapterFilterGridProps> = ({
  chapters,
  selectedSubject,
  onSelectSubject,
  onStartPractice,
  onStartCbtSprint
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Global '/' keyboard shortcut to focus search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredChapters = chapters.filter((c) => {
    const matchesSubject =
      selectedSubject === 'All' ||
      c.subject.toLowerCase() === selectedSubject.toLowerCase();
    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.subject.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSubject && matchesSearch;
  });

  const getSubjectColor = (subject: string) => {
    switch (subject.toLowerCase()) {
      case 'maths':
      case 'mathematics':
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-900/50';
      case 'physics':
        return 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-900/50';
      case 'chemistry':
        return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900/50';
      default:
        return 'text-slate-600 dark:text-zinc-400 bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-zinc-800';
    }
  };

  const getTierBadge = (cls: string) => {
    if (cls === 'Class A') {
      return 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-900/50';
    }
    return 'bg-slate-50 dark:bg-[#18181c] text-slate-600 dark:text-zinc-400 border-slate-200 dark:border-[#27272a]';
  };

  return (
    <section id="chapter-banks" className="mb-12">
      {/* Section Title & Filter Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
            Chapter Practice Banks
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Individual chapter recall sheets with authentic 2019–2025 JEE Main problems
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-100 dark:bg-[#111114] border border-slate-200 dark:border-[#222224] rounded-lg self-start">
          <button
            onClick={() => onSelectSubject('All')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer min-h-[38px] flex items-center gap-1.5 ${
              selectedSubject === 'All'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            All <span className="text-[11px] opacity-80">(27)</span>
          </button>
          <button
            onClick={() => onSelectSubject('Maths')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer min-h-[38px] flex items-center gap-1.5 ${
              selectedSubject === 'Maths'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Mathematics <span className="text-[11px] opacity-80">(5)</span>
          </button>
          <button
            onClick={() => onSelectSubject('Physics')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer min-h-[38px] flex items-center gap-1.5 ${
              selectedSubject === 'Physics'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Physics <span className="text-[11px] opacity-80">(14)</span>
          </button>
          <button
            onClick={() => onSelectSubject('Chemistry')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer min-h-[38px] flex items-center gap-1.5 ${
              selectedSubject === 'Chemistry'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Chemistry <span className="text-[11px] opacity-80">(8)</span>
          </button>
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="relative mb-6">
        <Search className="w-4 h-4 text-slate-400 dark:text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          ref={searchInputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search chapters, topics, formulas... (Press '/' to focus)"
          className="w-full pl-10 pr-28 py-2.5 rounded-lg bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] focus:border-blue-500 dark:focus:border-blue-500 focus:outline-none text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 transition-colors shadow-sm min-h-[44px]"
        />
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[11px] font-medium text-slate-400 dark:text-zinc-500 tabular-nums">
          Showing {filteredChapters.length} of {chapters.length} chapters
        </div>
      </div>

      {/* Chapter Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredChapters.map((chapter) => (
          <div
            key={chapter.slug}
            className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] hover:border-slate-300 dark:hover:border-[#2f2f35] rounded-xl p-4 sm:p-5 flex flex-col justify-between shadow-sm transition-all duration-150 group"
          >
            <div>
              {/* Card Badges */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <span
                  className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${getSubjectColor(
                    chapter.subject
                  )}`}
                >
                  {chapter.subject}
                </span>
                <span
                  className={`text-[10.5px] font-medium px-2 py-0.5 rounded-md border ${getTierBadge(
                    chapter.class_tier
                  )}`}
                >
                  {chapter.class_tier}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-1">
                {chapter.name}
              </h3>

              {/* Total Questions & Types info */}
              <div className="mt-2 text-xs text-slate-500 dark:text-zinc-400 flex items-center gap-2">
                <span className="font-semibold text-slate-700 dark:text-zinc-200 tabular-nums">
                  {chapter.total_questions} Questions
                </span>
                <span>&bull;</span>
                <span>{chapter.types_count} Sub-types</span>
              </div>

              {/* Difficulty Breakdown Badges */}
              <div className="mt-3 flex items-center gap-1.5 flex-wrap">
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200/60 dark:border-emerald-900/40 tabular-nums">
                  Easy: {chapter.difficulty_counts.E}
                </span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200/60 dark:border-amber-900/40 tabular-nums">
                  Med: {chapter.difficulty_counts.M}
                </span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200/60 dark:border-rose-900/40 tabular-nums">
                  Hard: {chapter.difficulty_counts.D}
                </span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-5 pt-3.5 border-t border-slate-100 dark:border-[#1c1c1f] flex items-center gap-2">
              <button
                onClick={() => onStartPractice(chapter)}
                className="flex-1 py-2 px-3 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center justify-center gap-1.5 transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Practice & Learn</span>
              </button>
              <button
                onClick={() => onStartCbtSprint(chapter)}
                className="py-2 px-3 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-[#18181c] hover:bg-slate-200 dark:hover:bg-[#222227] text-slate-800 dark:text-zinc-200 border border-slate-200 dark:border-[#27272a] flex items-center justify-center gap-1.5 transition-all min-h-[44px] cursor-pointer"
                title="Start CBT Simulation for this chapter"
              >
                <Play className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                <span>CBT</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
