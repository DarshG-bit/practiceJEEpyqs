import { useState } from 'react';
import {
  Trophy,
  CheckCircle,
  XCircle,
  ArrowLeft,
  Download,
  Bookmark
} from 'lucide-react';
import type { Question, TestAttempt } from '../types';
import { toggleStar } from '../db/db';

interface CbtResultViewProps {
  attempt: TestAttempt;
  questions: Question[];
  onBackToHome: () => void;
  onExportAttemptJSON: () => void;
}

export const CbtResultView: React.FC<CbtResultViewProps> = ({
  attempt,
  questions,
  onBackToHome,
  onExportAttemptJSON
}) => {
  const [filterMode, setFilterMode] = useState<'all' | 'mistakes' | 'correct' | 'unattempted'>('all');
  const [starredMap, setStarredMap] = useState<Record<number, boolean>>({});

  const handleToggleStar = async (qId: number) => {
    const isNowStarred = await toggleStar(attempt.chapterSlug || 'exam', qId, attempt.subject);
    setStarredMap((prev) => ({ ...prev, [qId]: isNowStarred }));
  };

  const filteredQuestions = questions.filter((q) => {
    const state = attempt.sessionStates[q.id];
    const userAns = q.kind === 'single' ? state?.selectedOption : state?.numericalAnswer?.trim();
    const hasAnswer = !!userAns;
    const isCorrect = hasAnswer && String(userAns).trim().toLowerCase() === String(q.answer).trim().toLowerCase();

    if (filterMode === 'mistakes') return hasAnswer && !isCorrect;
    if (filterMode === 'correct') return isCorrect;
    if (filterMode === 'unattempted') return !hasAnswer;
    return true;
  });

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Back to Home & Actions */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBackToHome}
          className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-700 dark:text-zinc-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors p-2 rounded-lg border border-slate-200 dark:border-[#27272a] hover:bg-slate-50 dark:hover:bg-[#18181c] min-h-[44px] cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>
        <button
          onClick={onExportAttemptJSON}
          className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-700 dark:text-zinc-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors px-3 py-2 rounded-lg border border-slate-200 dark:border-[#27272a] hover:bg-slate-50 dark:hover:bg-[#18181c] min-h-[44px] cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Export Test Result (JSON)</span>
        </button>
      </div>

      {/* Hero Score Card */}
      <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl p-6 sm:p-8 shadow-sm mb-8 text-center relative overflow-hidden">
        <div className="inline-flex p-3 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mb-3">
          <Trophy className="w-8 h-8" />
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
          Examination Results Summary
        </h2>
        <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
          {attempt.title} &bull; Official NTA Scoring (+4 for correct, −1 for wrong)
        </p>

        {/* Big Marks Display */}
        <div className="my-6">
          <div className="text-5xl sm:text-6xl font-black text-blue-600 dark:text-blue-400 tabular-nums">
            {attempt.score}{' '}
            <span className="text-xl sm:text-2xl font-bold text-slate-400 dark:text-zinc-500">
              / {attempt.maxScore}
            </span>
          </div>
          <span className="text-xs sm:text-sm font-semibold text-slate-500 dark:text-zinc-400 mt-1 block">
            Marks Scored
          </span>
        </div>

        {/* 4 Stats Chips */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-2xl mx-auto pt-4 border-t border-slate-100 dark:border-[#1c1c1f]">
          <div className="p-3 bg-slate-50 dark:bg-[#111114] rounded-xl border border-slate-100 dark:border-[#18181c]">
            <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Correct (+4)
            </span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-0.5 tabular-nums">
              {attempt.correctCount}
            </div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-[#111114] rounded-xl border border-slate-100 dark:border-[#18181c]">
            <span className="text-[11px] font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">
              Incorrect (−1)
            </span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-0.5 tabular-nums">
              {attempt.incorrectCount}
            </div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-[#111114] rounded-xl border border-slate-100 dark:border-[#18181c]">
            <span className="text-[11px] font-bold text-slate-600 dark:text-zinc-400 uppercase tracking-wider">
              Accuracy
            </span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-0.5 tabular-nums">
              {attempt.accuracy}%
            </div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-[#111114] rounded-xl border border-slate-100 dark:border-[#18181c]">
            <span className="text-[11px] font-bold text-slate-600 dark:text-zinc-400 uppercase tracking-wider">
              Time Taken
            </span>
            <div className="text-xl font-black text-slate-900 dark:text-white mt-0.5 tabular-nums">
              {formatTime(attempt.timeSpentSec)}
            </div>
          </div>
        </div>
      </div>

      {/* Review Questions Section */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Question Analysis & Review
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Inspect your responses, verify answers, and bookmark key problems
            </p>
          </div>

          {/* Filter Chips */}
          <div className="flex flex-wrap items-center gap-1 p-1 bg-slate-100 dark:bg-[#111114] border border-slate-200 dark:border-[#222224] rounded-lg">
            <button
              onClick={() => setFilterMode('all')}
              className={`px-2.5 py-1 rounded text-xs font-semibold cursor-pointer ${
                filterMode === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 dark:text-zinc-400'
              }`}
            >
              All ({questions.length})
            </button>
            <button
              onClick={() => setFilterMode('mistakes')}
              className={`px-2.5 py-1 rounded text-xs font-semibold cursor-pointer ${
                filterMode === 'mistakes'
                  ? 'bg-red-600 text-white'
                  : 'text-slate-600 dark:text-zinc-400'
              }`}
            >
              Mistakes ({attempt.incorrectCount})
            </button>
            <button
              onClick={() => setFilterMode('correct')}
              className={`px-2.5 py-1 rounded text-xs font-semibold cursor-pointer ${
                filterMode === 'correct'
                  ? 'bg-emerald-600 text-white'
                  : 'text-slate-600 dark:text-zinc-400'
              }`}
            >
              Correct ({attempt.correctCount})
            </button>
            <button
              onClick={() => setFilterMode('unattempted')}
              className={`px-2.5 py-1 rounded text-xs font-semibold cursor-pointer ${
                filterMode === 'unattempted'
                  ? 'bg-slate-600 text-white'
                  : 'text-slate-600 dark:text-zinc-400'
              }`}
            >
              Unattempted ({questions.length - attempt.answeredCount})
            </button>
          </div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.map((q, idx) => {
            const state = attempt.sessionStates[q.id];
            const userAns =
              q.kind === 'single' ? state?.selectedOption : state?.numericalAnswer?.trim();
            const hasAnswer = !!userAns;
            const isCorrect =
              hasAnswer &&
              String(userAns).trim().toLowerCase() === String(q.answer).trim().toLowerCase();

            return (
              <div
                key={q.id}
                className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-xl p-5 shadow-sm"
              >
                {/* Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-[#1c1c1f]">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-500 dark:text-zinc-400">
                      Q.{idx + 1}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40">
                      {q.type_name || `Type ${q.type_id}`}
                    </span>
                    <span className="text-[11px] text-slate-400 dark:text-zinc-500">
                      {q.source}
                    </span>
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center gap-2">
                    {hasAnswer ? (
                      isCorrect ? (
                        <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-[#052e16] text-emerald-700 dark:text-[#bbf7d0] border border-emerald-300 dark:border-[#16a34a] flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> Correct (+4)
                        </span>
                      ) : (
                        <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-red-50 dark:bg-[#450a0a] text-red-700 dark:text-[#fecaca] border border-red-300 dark:border-[#dc2626] flex items-center gap-1">
                          <XCircle className="w-3.5 h-3.5" /> Incorrect (−1)
                        </span>
                      )
                    ) : (
                      <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-slate-100 dark:bg-[#18181c] text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-[#27272a]">
                        Unattempted (0)
                      </span>
                    )}

                    <button
                      onClick={() => handleToggleStar(q.id)}
                      className="p-1 text-slate-400 hover:text-amber-500 cursor-pointer"
                      title="Bookmark Question"
                    >
                      <Bookmark
                        className={`w-4 h-4 ${
                          starredMap[q.id]
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-slate-400 dark:text-zinc-500'
                        }`}
                      />
                    </button>
                  </div>
                </div>

                {/* Stem */}
                <div
                  className="text-xs sm:text-sm text-slate-800 dark:text-zinc-200 leading-relaxed math-stem mb-4"
                  dangerouslySetInnerHTML={{ __html: q.stem_html }}
                />

                {/* Answer Summary Card */}
                <div className="bg-slate-50 dark:bg-[#111114] border border-slate-100 dark:border-[#18181c] rounded-lg p-3 text-xs flex flex-wrap items-center gap-4">
                  <div>
                    <span className="text-slate-500 dark:text-zinc-400 font-medium">Your Response: </span>
                    <span
                      className={`font-bold tabular-nums ${
                        hasAnswer
                          ? isCorrect
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-red-600 dark:text-red-400'
                          : 'text-slate-500'
                      }`}
                    >
                      {hasAnswer ? userAns : 'None'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 dark:text-zinc-400 font-medium">Correct Answer: </span>
                    <span className="font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                      {q.answer}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
