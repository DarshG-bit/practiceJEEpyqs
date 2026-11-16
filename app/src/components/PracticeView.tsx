import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Save
} from 'lucide-react';
import type { Question, ChapterCatalogItem, QuestionSessionState, TestAttempt } from '../types';
import { toggleStar, isStarred, addMistake, saveAttempt } from '../db/db';

interface PracticeViewProps {
  chapter: ChapterCatalogItem;
  questions: Question[];
  onBackToHome: () => void;
  savedAttempt?: TestAttempt;
}

export const PracticeView: React.FC<PracticeViewProps> = ({
  chapter,
  questions,
  onBackToHome,
  savedAttempt
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sessionStates, setSessionStates] = useState<Record<number, QuestionSessionState>>(() => {
    if (savedAttempt?.sessionStates) {
      return savedAttempt.sessionStates;
    }
    const initial: Record<number, QuestionSessionState> = {};
    questions.forEach((q) => {
      initial[q.id] = {
        questionId: q.id,
        status: 'not_visited',
        timeSpentSec: 0
      };
    });
    return initial;
  });

  const [isQuestionStarred, setIsQuestionStarred] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [saveToast, setSaveToast] = useState(false);

  const filteredQuestions = questions.filter((q) => {
    if (selectedDifficulty === 'all') return true;
    return q.difficulty === selectedDifficulty;
  });

  const currentQ = filteredQuestions[currentIndex] || questions[0];
  const currentState = sessionStates[currentQ.id] || {
    questionId: currentQ.id,
    status: 'not_visited',
    timeSpentSec: 0
  };

  // Check if current question is starred
  useEffect(() => {
    isStarred(chapter.slug, currentQ.id).then(setIsQuestionStarred);
    setShowSolution(false);
  }, [currentQ.id, chapter.slug]);

  // Persist practice progress in IndexedDB on change
  useEffect(() => {
    const autoSave = async () => {
      let answeredCount = 0;
      let correctCount = 0;
      let incorrectCount = 0;

      questions.forEach((q) => {
        const st = sessionStates[q.id];
        if (st?.checkedImmediate) {
          answeredCount++;
          if (st.isCorrect) correctCount++;
          else incorrectCount++;
        }
      });

      const attempt: TestAttempt = {
        id: savedAttempt?.id,
        testId: savedAttempt?.testId || `practice-${chapter.slug}-${Date.now()}`,
        title: `${chapter.name} (Practice Sheet)`,
        mode: 'practice',
        subject: chapter.subject,
        chapterSlug: chapter.slug,
        totalQuestions: questions.length,
        answeredCount,
        correctCount,
        incorrectCount,
        score: correctCount * 4 - incorrectCount * 1,
        maxScore: questions.length * 4,
        accuracy: answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0,
        timeSpentSec: 0,
        durationMinutes: 0,
        startedAt: savedAttempt?.startedAt || new Date().toISOString(),
        isCompleted: false, // In practice mode, can always continue!
        sessionStates,
        questionIds: questions.map((q) => q.id)
      };

      await saveAttempt(attempt);
    };

    const timer = setTimeout(autoSave, 1500);
    return () => clearTimeout(timer);
  }, [sessionStates, chapter, questions, savedAttempt]);

  // Option select
  const handleSelectOption = (label: string) => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        selectedOption: label,
        checkedImmediate: false
      }
    }));
  };

  // Numerical change
  const handleNumericalChange = (val: string) => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        numericalAnswer: val,
        checkedImmediate: false
      }
    }));
  };

  // Immediate Answer Check (Allowed in Practice Mode!)
  const handleCheckAnswer = async () => {
    const userAns =
      currentQ.kind === 'single'
        ? currentState.selectedOption
        : currentState.numericalAnswer?.trim();

    if (!userAns) return;

    const isCorrect =
      String(userAns).trim().toLowerCase() === String(currentQ.answer).trim().toLowerCase();

    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        isCorrect,
        checkedImmediate: true,
        status: isCorrect ? 'answered' : 'not_answered'
      }
    }));

    if (!isCorrect) {
      await addMistake(chapter.slug, currentQ.id, chapter.subject);
    }
  };

  // Toggle Star
  const handleToggleStar = async () => {
    const nextStarred = await toggleStar(chapter.slug, currentQ.id, chapter.subject);
    setIsQuestionStarred(nextStarred);
  };

  const handleManualSave = async () => {
    setSaveToast(true);
    setTimeout(() => setSaveToast(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-slate-200 dark:border-[#222224] gap-3">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToHome}
            className="p-2 rounded-lg border border-slate-200 dark:border-[#27272a] hover:bg-slate-100 dark:hover:bg-[#18181c] text-slate-700 dark:text-zinc-200 min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
            title="Back to All Chapters"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                {chapter.subject} &bull; Practice & Learn
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900/40">
                Auto-Saved
              </span>
            </div>
            <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight">
              {chapter.name}
            </h1>
          </div>
        </div>

        {/* Filter and Save feedback */}
        <div className="flex items-center gap-2">
          {saveToast && (
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 animate-in fade-in">
              Progress Saved!
            </span>
          )}
          <button
            onClick={handleManualSave}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-[#27272a] hover:bg-slate-100 dark:hover:bg-[#18181c] text-xs font-semibold text-slate-700 dark:text-zinc-200 flex items-center gap-1.5 min-h-[40px] cursor-pointer"
          >
            <Save className="w-4 h-4 text-blue-600" />
            <span>Save Progress</span>
          </button>
        </div>
      </div>

      {/* Difficulty Filter Pills */}
      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1 text-xs">
        <span className="font-semibold text-slate-500 dark:text-zinc-400">Filter:</span>
        {['all', 'E', 'M', 'D'].map((d) => (
          <button
            key={d}
            onClick={() => {
              setSelectedDifficulty(d);
              setCurrentIndex(0);
            }}
            className={`px-3 py-1.5 rounded-md font-semibold border transition-colors cursor-pointer min-h-[36px] ${
              selectedDifficulty === d
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white dark:bg-[#0a0a0c] text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-[#27272a]'
            }`}
          >
            {d === 'all'
              ? 'All Difficulties'
              : d === 'E'
              ? 'Easy'
              : d === 'M'
              ? 'Medium'
              : 'Difficult'}
          </button>
        ))}
      </div>

      {/* Question Card */}
      <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl p-5 sm:p-7 shadow-sm mb-6">
        {/* Card Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100 dark:border-[#1c1c1f]">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 tabular-nums">
              Question {currentIndex + 1} of {filteredQuestions.length}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40">
              {currentQ.type_name || `Type ${currentQ.type_id}`}
            </span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500">
              {currentQ.source}
            </span>
          </div>

          <button
            onClick={handleToggleStar}
            className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors cursor-pointer"
            title={isQuestionStarred ? 'Starred' : 'Star this question'}
          >
            <Bookmark
              className={`w-5 h-5 ${
                isQuestionStarred
                  ? 'fill-amber-400 text-amber-400'
                  : 'text-slate-400 dark:text-zinc-500'
              }`}
            />
          </button>
        </div>

        {/* Stem */}
        <div
          className="text-sm sm:text-base text-slate-900 dark:text-zinc-100 leading-relaxed math-stem mb-6"
          dangerouslySetInnerHTML={{ __html: currentQ.stem_html }}
        />

        {/* Options / Input */}
        {currentQ.kind === 'single' ? (
          <div className="space-y-3 mb-6">
            {currentQ.options.map((opt) => {
              const isSelected = currentState.selectedOption === opt.label;
              return (
                <div
                  key={opt.label}
                  onClick={() => handleSelectOption(opt.label)}
                  className={`flex items-start gap-3 p-3.5 sm:p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    isSelected
                      ? 'border-blue-600 bg-blue-50/60 dark:bg-blue-950/40 text-blue-950 dark:text-blue-100'
                      : 'border-slate-200 dark:border-[#222224] bg-white dark:bg-[#0a0a0c] hover:border-slate-300 dark:hover:border-[#333]'
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border transition-colors shrink-0 mt-0.5 ${
                      isSelected
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : 'border-slate-300 dark:border-zinc-700 text-slate-700 dark:text-zinc-300'
                    }`}
                  >
                    {opt.label}
                  </div>
                  <div
                    className="text-xs sm:text-sm font-medium leading-relaxed math-stem flex-1"
                    dangerouslySetInnerHTML={{ __html: opt.html }}
                  />
                </div>
              );
            })}
          </div>
        ) : (
          /* Numerical Input */
          <div className="bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#222224] rounded-xl p-4 sm:p-5 mb-6">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
              Enter Numerical Answer:
            </label>
            <input
              type="text"
              value={currentState.numericalAnswer || ''}
              onChange={(e) => handleNumericalChange(e.target.value)}
              placeholder="e.g. 4"
              className="w-48 py-2.5 px-3.5 rounded-lg text-base font-semibold bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#27272a] text-slate-900 dark:text-white focus:outline-none focus:border-blue-500 tabular-nums min-h-[44px]"
            />
          </div>
        )}

        {/* Immediate Feedback Box (When Checked) */}
        {currentState.checkedImmediate && (
          <div
            className={`p-4 rounded-xl border mb-6 flex items-start gap-3 animate-in fade-in ${
              currentState.isCorrect
                ? 'bg-emerald-50 dark:bg-[#052e16] border-emerald-300 dark:border-[#16a34a] text-emerald-800 dark:text-[#bbf7d0]'
                : 'bg-red-50 dark:bg-[#450a0a] border-red-300 dark:border-[#dc2626] text-red-800 dark:text-[#fecaca]'
            }`}
          >
            {currentState.isCorrect ? (
              <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            )}
            <div className="text-xs sm:text-sm">
              <span className="font-bold block">
                {currentState.isCorrect ? 'Correct Answer!' : 'Incorrect Answer'}
              </span>
              <span className="mt-0.5 block">
                Official Answer Key: <strong className="font-mono">{currentQ.answer}</strong>
              </span>
            </div>
          </div>
        )}

        {/* Action Buttons: Check Answer & Show Solution */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-[#1c1c1f]">
          <div className="flex items-center gap-2">
            <button
              onClick={handleCheckAnswer}
              className="px-4 py-2 rounded-lg text-xs sm:text-sm font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
            >
              Check Answer
            </button>
            <button
              onClick={() => setShowSolution(!showSolution)}
              className="px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] cursor-pointer"
            >
              {showSolution ? 'Hide Solution' : 'Show Solution / Key'}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              disabled={currentIndex === 0}
              onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              className="p-2.5 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] disabled:opacity-30 disabled:pointer-events-none min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
              title="Previous Question"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              disabled={currentIndex === filteredQuestions.length - 1}
              onClick={() => setCurrentIndex((prev) => Math.min(filteredQuestions.length - 1, prev + 1))}
              className="p-2.5 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] disabled:opacity-30 disabled:pointer-events-none min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
              title="Next Question"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Solution Box */}
        {showSolution && (
          <div className="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#222224] text-xs leading-relaxed animate-in fade-in">
            <h4 className="font-bold text-slate-900 dark:text-white mb-1">Official Solution & Key</h4>
            <p className="text-slate-700 dark:text-zinc-300">
              The verified answer is: <strong className="font-mono text-emerald-600 dark:text-emerald-400">{currentQ.answer}</strong>.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
