import { Bookmark, Trash2 } from 'lucide-react';

interface OverviewDashboardProps {
  stats: {
    totalQuestionsAttempted: number;
    accuracy: number;
    totalTimeSec: number;
    starredCount: number;
    mistakeCount: number;
    totalAttempts: number;
  };
  totalQuestionsInCatalog: number;
  mathsCount: { attempted: number; total: number };
  physCount: { attempted: number; total: number };
  chemCount: { attempted: number; total: number };
  onResetData: () => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  stats,
  totalQuestionsInCatalog,
  mathsCount,
  physCount,
  chemCount,
  onResetData
}) => {
  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  const mathPct = mathsCount.total > 0 ? Math.round((mathsCount.attempted / mathsCount.total) * 100) : 0;
  const physPct = physCount.total > 0 ? Math.round((physCount.attempted / physCount.total) * 100) : 0;
  const chemPct = chemCount.total > 0 ? Math.round((chemCount.attempted / chemCount.total) * 100) : 0;

  return (
    <section className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-xl p-5 sm:p-6 shadow-sm mb-8 transition-colors">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 dark:border-[#1c1c1f] gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
            Preparation Overview
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Aggregated progress and mastery across all 27 chapters
          </p>
        </div>
        <button
          onClick={onResetData}
          className="text-xs font-semibold text-slate-500 hover:text-red-600 dark:text-zinc-400 dark:hover:text-red-400 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-[#27272a] hover:border-red-200 dark:hover:border-red-900/50 transition-colors self-start sm:self-auto min-h-[38px] cursor-pointer flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Reset Data
        </button>
      </div>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 my-5">
        {/* Questions Attempted */}
        <div className="bg-slate-50 dark:bg-[#111114] border border-slate-100 dark:border-[#18181c] rounded-lg p-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Questions Attempted
          </span>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tabular-nums">
            {stats.totalQuestionsAttempted}
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5 block">
            across {totalQuestionsInCatalog.toLocaleString()} PYQs
          </span>
        </div>

        {/* First-Try Accuracy */}
        <div className="bg-slate-50 dark:bg-[#111114] border border-slate-100 dark:border-[#18181c] rounded-lg p-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            First-Try Accuracy
          </span>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 tabular-nums">
            {stats.accuracy}%
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5 block">
            target: &ge; 80% for 99th %ile
          </span>
        </div>

        {/* Study Time Logged */}
        <div className="bg-slate-50 dark:bg-[#111114] border border-slate-100 dark:border-[#18181c] rounded-lg p-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Study Time Logged
          </span>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1 tabular-nums">
            {formatTime(stats.totalTimeSec)}
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5 block">
            active testing & practice
          </span>
        </div>

        {/* Revision Bank */}
        <div className="bg-slate-50 dark:bg-[#111114] border border-slate-100 dark:border-[#18181c] rounded-lg p-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Revision Bank
          </span>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-500 dark:text-amber-400 mt-1 tabular-nums">
            {stats.starredCount + stats.mistakeCount}
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            <span className="flex items-center gap-0.5">
              <Bookmark className="w-3 h-3 text-amber-500" /> {stats.starredCount} Starred
            </span>
            <span>&middot;</span>
            <span className="text-red-500 dark:text-red-400">
              {stats.mistakeCount} Mistakes
            </span>
          </div>
        </div>
      </div>

      {/* Subject Syllabus Meters */}
      <div className="pt-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Maths */}
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5 font-medium">
              <span className="text-blue-600 dark:text-blue-400 font-bold">Mathematics</span>
              <span className="text-slate-500 dark:text-zinc-400 tabular-nums">
                {mathsCount.attempted} / {mathsCount.total} ({mathPct}%)
              </span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-[#1c1c20] h-2 rounded-full overflow-hidden">
              <div
                className="bg-blue-600 dark:bg-blue-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(mathPct, 100)}%` }}
              />
            </div>
          </div>

          {/* Physics */}
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5 font-medium">
              <span className="text-indigo-600 dark:text-indigo-400 font-bold">Physics</span>
              <span className="text-slate-500 dark:text-zinc-400 tabular-nums">
                {physCount.attempted} / {physCount.total} ({physPct}%)
              </span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-[#1c1c20] h-2 rounded-full overflow-hidden">
              <div
                className="bg-indigo-600 dark:bg-indigo-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(physPct, 100)}%` }}
              />
            </div>
          </div>

          {/* Chemistry */}
          <div>
            <div className="flex justify-between items-center text-xs mb-1.5 font-medium">
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">Chemistry</span>
              <span className="text-slate-500 dark:text-zinc-400 tabular-nums">
                {chemCount.attempted} / {chemCount.total} ({chemPct}%)
              </span>
            </div>
            <div className="w-full bg-slate-100 dark:bg-[#1c1c20] h-2 rounded-full overflow-hidden">
              <div
                className="bg-emerald-600 dark:bg-emerald-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(chemPct, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
