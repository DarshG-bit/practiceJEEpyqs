import { Moon, Sun, History } from 'lucide-react';

interface NavbarProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onOpenHistory: () => void;
  onOpenExamModal: () => void;
  onNavigateHome: () => void;
  activeView: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  darkMode,
  onToggleDarkMode,
  onOpenHistory,
  onOpenExamModal,
  onNavigateHome,
  activeView
}) => {
  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-white/80 dark:bg-black/80 border-b border-slate-200 dark:border-[#222224] transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand / Logo */}
        <div
          onClick={onNavigateHome}
          className="flex items-center gap-3 cursor-pointer group select-none"
        >
          <div className="w-9 h-9 rounded-lg bg-blue-600 dark:bg-blue-500 flex items-center justify-center text-white font-bold text-lg shadow-sm group-hover:scale-105 transition-transform">
            J
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold tracking-tight text-slate-900 dark:text-white leading-tight">
              JEE Main PYQ Portal
            </h1>
            <p className="text-xs text-slate-500 dark:text-zinc-400 font-medium hidden sm:block">
              Authentic NTA CBT Simulation & Active Recall
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {activeView === 'home' && (
            <button
              onClick={onOpenExamModal}
              className="px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] flex items-center justify-center cursor-pointer"
            >
              Simulate Exam
            </button>
          )}

          {/* Test History Button */}
          <button
            onClick={onOpenHistory}
            title="Test & Practice History"
            aria-label="Test and Practice History"
            className="p-2 sm:px-3 sm:py-2 rounded-lg text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] border border-slate-200 dark:border-[#27272a] transition-colors flex items-center gap-1.5 min-h-[44px] min-w-[44px] justify-center cursor-pointer"
          >
            <History className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="text-xs sm:text-sm font-medium hidden md:inline">History</span>
          </button>

          {/* Dark Mode Outline Toggle (Clean SVG, No Emojis) */}
          <button
            onClick={onToggleDarkMode}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2.5 rounded-lg text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] border border-slate-200 dark:border-[#27272a] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
          >
            {darkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-600" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
