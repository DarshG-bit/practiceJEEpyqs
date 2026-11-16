import { ArrowRight, Play } from 'lucide-react';
import type { SubjectType } from '../types';

interface SubjectPortalsProps {
  onSelectSubjectIndex: (subject: SubjectType) => void;
  onStartFullExam: () => void;
  onScrollToChapters: () => void;
  chapterCounts: {
    maths: number;
    physics: number;
    chemistry: number;
    mathsQuestions: number;
    physicsQuestions: number;
    chemQuestions: number;
  };
}

export const SubjectPortals: React.FC<SubjectPortalsProps> = ({
  onSelectSubjectIndex,
  onStartFullExam,
  onScrollToChapters,
  chapterCounts
}) => {
  return (
    <section className="mb-10">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
            Subject Syllabus Portals
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400 mt-0.5">
            Dedicated chapter indexes with official class difficulty color codes & formula strips
          </p>
        </div>
      </div>

      {/* 3 Big Blocks for Each Subject */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* 1. Mathematics Card */}
        <div
          onClick={() => onSelectSubjectIndex('Maths')}
          className="group relative bg-white dark:bg-[#0a0a0c] hover:bg-slate-50/80 dark:hover:bg-[#111114] border border-slate-200 dark:border-[#222224] hover:border-blue-500/50 dark:hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-blue-600 dark:bg-blue-500 rounded-t-xl" />
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                Mathematics
              </h3>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40 tabular-nums">
                {chapterCounts.maths} Chapters
              </span>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1.5 leading-relaxed">
              Calculus, Matrices, Determinants, Limits, Functions &amp; Definite Integration with official difficulty ratings.
            </p>
            <div className="mt-3 flex items-center gap-1.5 text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              <span className="inline-block w-2 h-2 rounded-full bg-blue-500" />
              <span>{chapterCounts.mathsQuestions.toLocaleString()} Verified PYQs</span>
            </div>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 dark:border-[#1c1c1f] flex items-center justify-between text-xs font-semibold text-blue-600 dark:text-blue-400 group-hover:translate-x-0.5 transition-transform">
            <span>Explore Mathematics Index</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </div>
        </div>

        {/* 2. Physics Card */}
        <div
          onClick={() => onSelectSubjectIndex('Physics')}
          className="group relative bg-white dark:bg-[#0a0a0c] hover:bg-slate-50/80 dark:hover:bg-[#111114] border border-slate-200 dark:border-[#222224] hover:border-indigo-500/50 dark:hover:border-indigo-500/50 rounded-xl p-5 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-indigo-600 dark:bg-indigo-500 rounded-t-xl" />
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                Physics
              </h3>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900/40 tabular-nums">
                {chapterCounts.physics} Chapters
              </span>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1.5 leading-relaxed">
              Mechanics, Electromagnetism, Optics, Modern Physics, Thermal &amp; Waves with ray &amp; circuit diagrams.
            </p>
            <div className="mt-3 flex items-center gap-1.5 text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              <span className="inline-block w-2 h-2 rounded-full bg-indigo-500" />
              <span>{chapterCounts.physicsQuestions.toLocaleString()} Verified PYQs</span>
            </div>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 dark:border-[#1c1c1f] flex items-center justify-between text-xs font-semibold text-indigo-600 dark:text-indigo-400 group-hover:translate-x-0.5 transition-transform">
            <span>Explore Physics Index</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </div>
        </div>

        {/* 3. Chemistry Card */}
        <div
          onClick={() => onSelectSubjectIndex('Chemistry')}
          className="group relative bg-white dark:bg-[#0a0a0c] hover:bg-slate-50/80 dark:hover:bg-[#111114] border border-slate-200 dark:border-[#222224] hover:border-emerald-500/50 dark:hover:border-emerald-500/50 rounded-xl p-5 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-600 dark:bg-emerald-500 rounded-t-xl" />
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                Chemistry
              </h3>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900/40 tabular-nums">
                {chapterCounts.chemistry} Chapters
              </span>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1.5 leading-relaxed">
              General Organic Chemistry, Kinetics, Coordination, Electrochemistry, Ionic Equilibrium, Mole Concept &amp; Solutions.
            </p>
            <div className="mt-3 flex items-center gap-1.5 text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" />
              <span>{chapterCounts.chemQuestions.toLocaleString()} Verified PYQs</span>
            </div>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 dark:border-[#1c1c1f] flex items-center justify-between text-xs font-semibold text-emerald-600 dark:text-emerald-400 group-hover:translate-x-0.5 transition-transform">
            <span>Explore Chemistry Index</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </div>
        </div>
      </div>

      {/* Underneath: Long Box with Option for All 3 */}
      <div className="bg-gradient-to-r from-blue-900/10 via-indigo-900/10 to-emerald-900/10 dark:from-blue-950/30 dark:via-indigo-950/30 dark:to-emerald-950/30 border border-slate-200 dark:border-[#222224] rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
              Full Syllabus Simulation
            </span>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200">
              NTA CBT Engine
            </span>
          </div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mt-1">
            Simulate All 3 Subjects Full CBT Exam
          </h3>
          <p className="text-xs text-slate-600 dark:text-zinc-300 mt-0.5">
            Complete mock examination across Maths, Physics, and Chemistry (+4/−1 marking &bull; 75 Qs &bull; Official timer)
          </p>
        </div>

        <div className="flex items-center gap-2.5 sm:self-center">
          <button
            onClick={onStartFullExam}
            className="px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Simulate All 3 Subjects Exam &rarr;</span>
          </button>
          <button
            onClick={onScrollToChapters}
            className="px-3.5 py-2.5 rounded-lg text-xs sm:text-sm font-medium bg-white dark:bg-[#111114] hover:bg-slate-50 dark:hover:bg-[#18181c] border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 transition-colors min-h-[44px] cursor-pointer"
          >
            Browse 33 Chapters &darr;
          </button>
        </div>
      </div>
    </section>
  );
};
