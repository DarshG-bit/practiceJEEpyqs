import { useState, useEffect } from 'react';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Menu,
  X,
  Bookmark,
  ArrowLeft
} from 'lucide-react';
import type { Question, QuestionSessionState, TestAttempt } from '../types';
import { toggleStar, isStarred } from '../db/db';

interface CbtExamViewProps {
  title: string;
  questions: Question[];
  durationMinutes: number;
  onFinishExam: (attempt: TestAttempt) => void;
  onExitWithoutSave: () => void;
}

export const CbtExamView: React.FC<CbtExamViewProps> = ({
  title,
  questions,
  durationMinutes,
  onFinishExam,
  onExitWithoutSave
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sessionStates, setSessionStates] = useState<Record<number, QuestionSessionState>>(() => {
    const initial: Record<number, QuestionSessionState> = {};
    questions.forEach((q, idx) => {
      initial[q.id] = {
        questionId: q.id,
        status: idx === 0 ? 'not_answered' : 'not_visited',
        timeSpentSec: 0
      };
    });
    return initial;
  });

  const [timeLeftSec, setTimeLeftSec] = useState<number>(
    durationMinutes > 0 ? durationMinutes * 60 : 0
  );
  const [isPaletteOpenMobile, setIsPaletteOpenMobile] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  const [isQuestionStarred, setIsQuestionStarred] = useState(false);

  const currentQ = questions[currentIndex];
  const currentState = sessionStates[currentQ.id] || {
    questionId: currentQ.id,
    status: 'not_answered',
    timeSpentSec: 0
  };

  // Check if current question is starred
  useEffect(() => {
    isStarred('cbt-session', currentQ.id).then(setIsQuestionStarred);
  }, [currentQ.id]);

  // Timer countdown
  useEffect(() => {
    if (durationMinutes === 0) return; // Untimed

    const timer = setInterval(() => {
      setTimeLeftSec((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmitFinal();
          return 0;
        }
        return prev - 1;
      });

      // Track time spent on current question
      setSessionStates((prev) => {
        const cur = prev[currentQ.id];
        if (!cur) return prev;
        return {
          ...prev,
          [currentQ.id]: {
            ...cur,
            timeSpentSec: cur.timeSpentSec + 1
          }
        };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [currentQ.id, durationMinutes]);

  const formatTimer = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, '0')}:${mins
        .toString()
        .padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Option select (MCQ)
  const handleSelectOption = (label: string) => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        selectedOption: label
      }
    }));
  };

  // Numerical change
  const handleNumericalChange = (val: string) => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        numericalAnswer: val
      }
    }));
  };

  // Navigation and State Actions
  const handleSaveAndNext = () => {
    const hasAnswer =
      currentQ.kind === 'single'
        ? !!currentState.selectedOption
        : !!currentState.numericalAnswer?.trim();

    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        status: hasAnswer ? 'answered' : 'not_answered'
      }
    }));

    advanceQuestion(currentIndex + 1);
  };

  const handleSaveAndMarkForReview = () => {
    const hasAnswer =
      currentQ.kind === 'single'
        ? !!currentState.selectedOption
        : !!currentState.numericalAnswer?.trim();

    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        status: hasAnswer ? 'answered_marked' : 'marked'
      }
    }));

    advanceQuestion(currentIndex + 1);
  };

  const handleMarkForReviewAndNext = () => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        status: 'marked'
      }
    }));

    advanceQuestion(currentIndex + 1);
  };

  const handleClearResponse = () => {
    setSessionStates((prev) => ({
      ...prev,
      [currentQ.id]: {
        ...prev[currentQ.id],
        selectedOption: undefined,
        numericalAnswer: undefined,
        status: 'not_answered'
      }
    }));
  };

  const advanceQuestion = (nextIdx: number) => {
    if (nextIdx < questions.length) {
      const nextQ = questions[nextIdx];
      // If next question was not visited, mark it not_answered
      setSessionStates((prev) => {
        const nextState = prev[nextQ.id];
        if (nextState && nextState.status === 'not_visited') {
          return {
            ...prev,
            [nextQ.id]: { ...nextState, status: 'not_answered' }
          };
        }
        return prev;
      });
      setCurrentIndex(nextIdx);
    }
  };

  const handleJumpToQuestion = (idx: number) => {
    const targetQ = questions[idx];
    setSessionStates((prev) => {
      const targetState = prev[targetQ.id];
      if (targetState && targetState.status === 'not_visited') {
        return {
          ...prev,
          [targetQ.id]: { ...targetState, status: 'not_answered' }
        };
      }
      return prev;
    });
    setCurrentIndex(idx);
    setIsPaletteOpenMobile(false);
  };

  // Compute status counts for legend
  const counts = {
    answered: 0,
    not_answered: 0,
    not_visited: 0,
    marked: 0,
    answered_marked: 0
  };

  Object.values(sessionStates).forEach((st) => {
    if (st.status === 'answered') counts.answered++;
    else if (st.status === 'not_answered') counts.not_answered++;
    else if (st.status === 'not_visited') counts.not_visited++;
    else if (st.status === 'marked') counts.marked++;
    else if (st.status === 'answered_marked') counts.answered_marked++;
  });

  // Star question handler
  const handleToggleStar = async () => {
    const nextStarred = await toggleStar('cbt-session', currentQ.id, 'Exam');
    setIsQuestionStarred(nextStarred);
  };

  // Submit Final Examination
  const handleSubmitFinal = () => {
    setShowSubmitModal(false);

    let correctCount = 0;
    let incorrectCount = 0;
    let answeredCount = 0;

    questions.forEach((q) => {
      const state = sessionStates[q.id];
      const hasAnswer =
        q.kind === 'single'
          ? !!state?.selectedOption
          : !!state?.numericalAnswer?.trim();

      if (hasAnswer) {
        answeredCount++;
        const userAns =
          q.kind === 'single' ? state.selectedOption : state.numericalAnswer?.trim();
        const isCorr =
          String(userAns).trim().toLowerCase() === String(q.answer).trim().toLowerCase();

        if (isCorr) {
          correctCount++;
        } else {
          incorrectCount++;
        }
      }
    });

    const score = correctCount * 4 - incorrectCount * 1;
    const maxScore = questions.length * 4;
    const accuracy = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;
    const totalTimeSpent =
      durationMinutes > 0 ? durationMinutes * 60 - timeLeftSec : 0;

    const attempt: TestAttempt = {
      testId: `cbt-${Date.now()}`,
      title: title || 'JEE Main CBT Examination',
      mode: 'cbt',
      subject: 'Mixed',
      totalQuestions: questions.length,
      answeredCount,
      correctCount,
      incorrectCount,
      score,
      maxScore,
      accuracy,
      timeSpentSec: Math.max(totalTimeSpent, 1),
      durationMinutes,
      startedAt: new Date(Date.now() - totalTimeSpent * 1000).toISOString(),
      completedAt: new Date().toISOString(),
      isCompleted: true, // CBT tests cannot be continued once submitted
      sessionStates,
      questionIds: questions.map((q) => q.id)
    };

    onFinishExam(attempt);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-100 dark:bg-black text-slate-900 dark:text-white select-none">
      {/* Top NTA Examination Header */}
      <header className="sticky top-0 z-30 bg-white dark:bg-[#0a0a0c] border-b border-slate-200 dark:border-[#222224] px-4 py-2.5 sm:px-6 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowExitModal(true)}
            className="p-2 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors flex items-center gap-1.5 min-h-[40px] cursor-pointer"
            title="Exit CBT Exam"
            aria-label="Exit CBT Exam"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-xs font-semibold hidden sm:inline">Back</span>
          </button>
          <div className="px-2.5 py-1 rounded bg-blue-600 text-white font-bold text-xs">
            NTA CBT
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-tight">
              {title}
            </h1>
            <span className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium">
              Question {currentIndex + 1} of {questions.length} &bull; Marks: +4.00, −1.00
            </span>
          </div>
        </div>

        {/* Timer & Mobile Palette Trigger */}
        <div className="flex items-center gap-2 sm:gap-4">
          {durationMinutes > 0 && (
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-mono font-bold text-xs sm:text-sm tabular-nums ${
                timeLeftSec < 300
                  ? 'bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 border-red-200 dark:border-red-900/50 animate-pulse'
                  : 'bg-slate-50 dark:bg-[#111114] text-slate-800 dark:text-zinc-200 border-slate-200 dark:border-[#27272a]'
              }`}
            >
              <Clock className="w-4 h-4 text-slate-500 dark:text-zinc-400" />
              <span>{formatTimer(timeLeftSec)}</span>
            </div>
          )}

          {/* Submit Test Button */}
          <button
            onClick={() => setShowSubmitModal(true)}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[40px] flex items-center justify-center cursor-pointer"
          >
            Submit Test
          </button>

          {/* Mobile Palette Toggle Button */}
          <button
            onClick={() => setIsPaletteOpenMobile(!isPaletteOpenMobile)}
            className="lg:hidden p-2 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] min-h-[40px] min-w-[40px] flex items-center justify-center cursor-pointer"
            aria-label="Toggle Question Palette"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Main Examination View Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Question Stem & Options */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 flex flex-col justify-between max-w-4xl mx-auto w-full">
          <div>
            {/* Question Info Bar */}
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 dark:border-[#222224]">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40">
                  {currentQ.type_name || `Type ${currentQ.type_id}`}
                </span>
                <span className="text-xs text-slate-500 dark:text-zinc-400 font-medium">
                  {currentQ.source || 'JEE Main PYQ'}
                </span>
              </div>
              <button
                onClick={handleToggleStar}
                title={isQuestionStarred ? 'Starred' : 'Star this question'}
                className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors cursor-pointer"
              >
                <Bookmark
                  className={`w-4 h-4 ${
                    isQuestionStarred
                      ? 'fill-amber-400 text-amber-400'
                      : 'text-slate-400 dark:text-zinc-500'
                  }`}
                />
              </button>
            </div>

            {/* Question Stem HTML (Supports Math formulas) */}
            <div
              className="text-sm sm:text-base text-slate-900 dark:text-zinc-100 leading-relaxed math-stem mb-6"
              dangerouslySetInnerHTML={{ __html: currentQ.stem_html }}
            />

            {/* Options Area */}
            {currentQ.kind === 'single' ? (
              <div className="space-y-3 mb-8">
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
              /* Numerical Answer Input (Zero White Blinding Darkness!) */
              <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-xl p-5 mb-8">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
                  Enter Your Numerical Answer (Integer):
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={currentState.numericalAnswer || ''}
                    onChange={(e) => handleNumericalChange(e.target.value)}
                    placeholder="Enter whole number"
                    className="w-48 py-2.5 px-3.5 rounded-lg text-base font-semibold bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#27272a] text-slate-900 dark:text-white focus:outline-none focus:border-blue-500 tabular-nums min-h-[44px]"
                  />
                  {currentState.numericalAnswer && (
                    <button
                      onClick={() => handleNumericalChange('')}
                      className="text-xs font-semibold text-slate-500 hover:text-red-500 p-2 cursor-pointer"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Bottom Action Buttons (Touch targets >= 44px) */}
          <div className="pt-4 border-t border-slate-200 dark:border-[#222224] bg-white dark:bg-[#0a0a0c] -mx-4 -mb-4 p-4 sm:-mx-6 sm:-mb-6 sm:p-6 lg:-mx-8 lg:-mb-8 lg:p-8 flex flex-wrap items-center justify-between gap-2.5">
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={handleSaveAndNext}
                className="px-4 py-2.5 rounded-lg text-xs sm:text-sm font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
              >
                Save & Next
              </button>
              <button
                onClick={handleSaveAndMarkForReview}
                className="px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold bg-purple-600 hover:bg-purple-700 text-white shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
              >
                Save & Mark for Review
              </button>
              <button
                onClick={handleMarkForReviewAndNext}
                className="px-3.5 py-2.5 rounded-lg text-xs sm:text-sm font-semibold border border-purple-300 dark:border-purple-800 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40 transition-colors min-h-[44px] cursor-pointer"
              >
                Mark for Review & Next
              </button>
              <button
                onClick={handleClearResponse}
                className="px-3 py-2.5 rounded-lg text-xs sm:text-sm font-medium border border-slate-200 dark:border-[#27272a] text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] cursor-pointer"
              >
                Clear Response
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={currentIndex === 0}
                onClick={() => advanceQuestion(currentIndex - 1)}
                className="p-2.5 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] disabled:opacity-30 disabled:pointer-events-none min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
                title="Previous Question"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                disabled={currentIndex === questions.length - 1}
                onClick={() => advanceQuestion(currentIndex + 1)}
                className="p-2.5 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-700 dark:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] disabled:opacity-30 disabled:pointer-events-none min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
                title="Next Question"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Official NTA Question Palette */}
        <aside
          className={`fixed lg:static top-0 right-0 bottom-0 z-40 w-80 bg-white dark:bg-[#0a0a0c] border-l border-slate-200 dark:border-[#222224] p-4 flex flex-col justify-between transition-transform duration-200 ${
            isPaletteOpenMobile ? 'translate-x-0 shadow-2xl' : 'translate-x-full lg:translate-x-0'
          }`}
        >
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 dark:border-[#222224]">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Question Palette
              </h3>
              <button
                onClick={() => setIsPaletteOpenMobile(false)}
                className="lg:hidden p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Official NTA 5-State Legend */}
            <div className="grid grid-cols-2 gap-2 text-[11px] mb-4 p-2.5 bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#1c1c1f] rounded-lg">
              <div className="flex items-center gap-1.5">
                <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] nta-answered">
                  {counts.answered}
                </span>
                <span className="text-slate-600 dark:text-zinc-400">Answered</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] nta-not-answered">
                  {counts.not_answered}
                </span>
                <span className="text-slate-600 dark:text-zinc-400">Not Answered</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] nta-not-visited">
                  {counts.not_visited}
                </span>
                <span className="text-slate-600 dark:text-zinc-400">Not Visited</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] nta-marked">
                  {counts.marked}
                </span>
                <span className="text-slate-600 dark:text-zinc-400">Marked Review</span>
              </div>
              <div className="col-span-2 flex items-center gap-1.5 pt-1 border-t border-slate-200 dark:border-[#222224]">
                <span className="w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] nta-answered-marked">
                  {counts.answered_marked}
                </span>
                <span className="text-slate-600 dark:text-zinc-400 text-[10.5px]">
                  Ans & Marked for Review
                </span>
              </div>
            </div>

            {/* Palette Grid Buttons */}
            <div className="max-h-[50vh] overflow-y-auto pr-1">
              <div className="grid grid-cols-5 gap-2">
                {questions.map((q, idx) => {
                  const state = sessionStates[q.id];
                  const status = state?.status || 'not_visited';
                  const isCurrent = idx === currentIndex;

                  let statusClass = 'nta-not-visited';
                  if (status === 'answered') statusClass = 'nta-answered';
                  else if (status === 'not_answered') statusClass = 'nta-not-answered';
                  else if (status === 'marked') statusClass = 'nta-marked';
                  else if (status === 'answered_marked') statusClass = 'nta-answered-marked';

                  return (
                    <button
                      key={q.id}
                      onClick={() => handleJumpToQuestion(idx)}
                      className={`h-9 rounded-md font-bold text-xs flex items-center justify-center transition-all cursor-pointer border ${statusClass} ${
                        isCurrent
                          ? 'ring-2 ring-offset-2 ring-blue-500 dark:ring-offset-black scale-105'
                          : 'opacity-90 hover:opacity-100'
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Bottom Palette Actions */}
          <div className="pt-3 border-t border-slate-200 dark:border-[#222224] space-y-2">
            <button
              onClick={() => setShowSubmitModal(true)}
              className="w-full py-2.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center justify-center gap-1.5 transition-all min-h-[44px] cursor-pointer"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Submit Entire Examination</span>
            </button>
            <button
              onClick={onExitWithoutSave}
              className="w-full py-2 rounded-lg text-xs font-semibold text-slate-500 hover:text-red-500 transition-colors min-h-[38px] cursor-pointer"
            >
              Exit Examination
            </button>
          </div>
        </aside>
      </div>

      {/* Confirmation Submit Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl w-full max-w-md p-5 sm:p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-500 mb-3">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Submit Examination?
              </h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed mb-4">
              Are you sure you want to end your examination? Once submitted, answers cannot be modified.
            </p>

            {/* Breakdown table */}
            <div className="bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#1c1c1f] rounded-xl p-3.5 mb-5 space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-600 dark:text-zinc-400">Total Questions:</span>
                <span className="font-bold text-slate-900 dark:text-white tabular-nums">
                  {questions.length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-emerald-600 dark:text-emerald-400 font-medium">Answered:</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  {counts.answered + counts.answered_marked}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-red-600 dark:text-red-400 font-medium">Not Answered:</span>
                <span className="font-bold text-red-600 dark:text-red-400 tabular-nums">
                  {counts.not_answered + counts.not_visited}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-600 dark:text-purple-400 font-medium">Marked for Review:</span>
                <span className="font-bold text-purple-600 dark:text-purple-400 tabular-nums">
                  {counts.marked + counts.answered_marked}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowSubmitModal(false)}
                className="px-4 py-2.5 rounded-lg text-xs font-semibold text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] cursor-pointer"
              >
                Resume Examination
              </button>
              <button
                onClick={handleSubmitFinal}
                className="px-5 py-2.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md transition-all min-h-[44px] cursor-pointer"
              >
                Yes, Final Submit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Exit Modal (Leaving CBT exam warning) */}
      {showExitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-500 mb-3">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Exit CBT Examination?</h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 mb-5 leading-relaxed">
              Leaving the CBT examination will automatically submit your test, finalize your score, and record your performance in Test History. Are you sure you want to submit and exit?
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowExitModal(false)}
                className="px-4 py-2.5 rounded-lg text-xs font-semibold text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] cursor-pointer"
              >
                Cancel (Stay in Exam)
              </button>
              <button
                onClick={() => {
                  setShowExitModal(false);
                  handleSubmitFinal();
                }}
                className="px-5 py-2.5 rounded-lg text-xs font-bold bg-red-600 hover:bg-red-700 text-white shadow-md transition-all min-h-[44px] cursor-pointer"
              >
                Submit &amp; Exit Exam
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
