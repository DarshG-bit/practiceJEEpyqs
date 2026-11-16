import { useState } from 'react';
import { X, CheckCircle2 } from 'lucide-react';
import type { ChapterCatalogItem, TestConfig } from '../types';

interface ExamModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartExam: (config: TestConfig) => void;
  chapters: ChapterCatalogItem[];
  initialChapter?: ChapterCatalogItem | null;
}

export const ExamModal: React.FC<ExamModalProps> = ({
  isOpen,
  onClose,
  onStartExam,
  chapters,
  initialChapter
}) => {
  if (!isOpen) return null;

  const [mode, setMode] = useState<'cbt' | 'practice'>('cbt');
  const [subjectPool, setSubjectPool] = useState<string>(
    initialChapter ? initialChapter.slug : 'All'
  );
  const [questionCountType, setQuestionCountType] = useState<string>('25');
  const [customQuestionCount, setCustomQuestionCount] = useState<number>(30);
  const [durationPreset, setDurationPreset] = useState<string>('60');
  const [customDurationMinutes, setCustomDurationMinutes] = useState<number>(45);

  const handleStart = () => {
    let finalCount = 25;
    if (questionCountType === '15') finalCount = 15;
    else if (questionCountType === '25') finalCount = 25;
    else if (questionCountType === '30') finalCount = 30;
    else if (questionCountType === '50') finalCount = 50;
    else if (questionCountType === '75') finalCount = 75;
    else if (questionCountType === 'all') finalCount = 9999;
    else if (questionCountType === 'custom') finalCount = customQuestionCount || 25;

    let finalDuration = 60;
    if (durationPreset === '30') finalDuration = 30;
    else if (durationPreset === '60') finalDuration = 60;
    else if (durationPreset === '90') finalDuration = 90;
    else if (durationPreset === '180') finalDuration = 180;
    else if (durationPreset === 'untimed') finalDuration = 0;
    else if (durationPreset === 'custom') finalDuration = customDurationMinutes || 60;

    onStartExam({
      mode,
      subjectPool,
      questionCount: finalCount,
      durationMinutes: finalDuration
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl p-5 sm:p-6 transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-[#1c1c1f]">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Simulate Examination or Practice Test
            </h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Configure timing, question pool, and authentic test parameters
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="py-4 space-y-6">
          {/* 1. Test Mode */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
              1. Test Mode:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* CBT Card */}
              <div
                onClick={() => setMode('cbt')}
                className={`p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                  mode === 'cbt'
                    ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-950/30'
                    : 'border-slate-200 dark:border-[#222224] hover:border-slate-300 dark:hover:border-[#333]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    Real CBT Exam Mode
                  </span>
                  {mode === 'cbt' && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
                </div>
                <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 leading-relaxed">
                  +4 / −1 marking &bull; NTA palette &bull; No instant answers &bull; Strict exam timer
                </p>
              </div>

              {/* Practice Card */}
              <div
                onClick={() => setMode('practice')}
                className={`p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                  mode === 'practice'
                    ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-950/30'
                    : 'border-slate-200 dark:border-[#222224] hover:border-slate-300 dark:hover:border-[#333]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    Practice & Learn Mode
                  </span>
                  {mode === 'practice' && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
                </div>
                <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 leading-relaxed">
                  Instant check &bull; Retry wrong options &bull; Immediate explanations &bull; Leave & continue anytime
                </p>
              </div>
            </div>
          </div>

          {/* 2. Choose Subject / Chapter Pool */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
              2. Choose Subject Pool:
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
              {[
                { id: 'All', label: 'All Subjects (27)' },
                { id: 'Physics', label: 'Physics (14)' },
                { id: 'Chemistry', label: 'Chemistry (8)' },
                { id: 'Maths', label: 'Maths (5)' }
              ].map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSubjectPool(item.id)}
                  className={`py-2 px-2.5 rounded-lg text-xs font-semibold border transition-all min-h-[44px] cursor-pointer ${
                    subjectPool === item.id
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                      : 'bg-slate-50 dark:bg-[#111114] text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-[#27272a] hover:bg-slate-100 dark:hover:bg-[#18181c]'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {/* Or choose specific chapter */}
            <div className="mt-2">
              <select
                value={subjectPool.startsWith('All') || subjectPool === 'Physics' || subjectPool === 'Chemistry' || subjectPool === 'Maths' ? '' : subjectPool}
                onChange={(e) => {
                  if (e.target.value) setSubjectPool(e.target.value);
                }}
                className="w-full py-2 px-3 rounded-lg text-xs bg-white dark:bg-[#111114] border border-slate-200 dark:border-[#27272a] text-slate-800 dark:text-zinc-200 focus:outline-none focus:border-blue-500 min-h-[44px]"
              >
                <option value="">&mdash; Or pick a single specific chapter &mdash;</option>
                {chapters.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    [{c.subject}] {c.name} ({c.total_questions} Qs)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 3. Number of Questions */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
              3. Number of Questions:
            </label>
            <div className="flex flex-wrap gap-2">
              {['15', '25', '30', '50', '75', 'all', 'custom'].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setQuestionCountType(val)}
                  className={`py-2 px-3 rounded-lg text-xs font-semibold border transition-all min-h-[44px] cursor-pointer ${
                    questionCountType === val
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                      : 'bg-slate-50 dark:bg-[#111114] text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-[#27272a] hover:bg-slate-100 dark:hover:bg-[#18181c]'
                  }`}
                >
                  {val === '75'
                    ? '75 (Full JEE Exam)'
                    : val === 'all'
                    ? 'All in Pool'
                    : val === 'custom'
                    ? 'Custom Number'
                    : `${val} Questions`}
                </button>
              ))}
            </div>

            {/* Custom Question Count Input */}
            {questionCountType === 'custom' && (
              <div className="mt-2.5 flex items-center gap-2">
                <input
                  type="number"
                  min="5"
                  max="500"
                  value={customQuestionCount}
                  onChange={(e) => setCustomQuestionCount(parseInt(e.target.value) || 20)}
                  className="w-32 py-2 px-3 rounded-lg text-xs sm:text-sm bg-white dark:bg-[#111114] border border-slate-200 dark:border-[#27272a] text-slate-900 dark:text-white focus:outline-none focus:border-blue-500 tabular-nums min-h-[44px]"
                  placeholder="e.g. 40"
                />
                <span className="text-xs text-slate-500 dark:text-zinc-400 font-medium">
                  questions
                </span>
              </div>
            )}
          </div>

          {/* 4. Test Duration (with Custom Time Option!) */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 block mb-2">
              4. Test Duration:
            </label>
            <div className="flex flex-wrap gap-2">
              {['30', '60', '90', '180', 'untimed', 'custom'].map((dur) => (
                <button
                  key={dur}
                  type="button"
                  onClick={() => setDurationPreset(dur)}
                  className={`py-2 px-3 rounded-lg text-xs font-semibold border transition-all min-h-[44px] cursor-pointer ${
                    durationPreset === dur
                      ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                      : 'bg-slate-50 dark:bg-[#111114] text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-[#27272a] hover:bg-slate-100 dark:hover:bg-[#18181c]'
                  }`}
                >
                  {dur === 'untimed'
                    ? 'Untimed'
                    : dur === '180'
                    ? '180 min (Full Exam)'
                    : dur === 'custom'
                    ? 'Custom Time'
                    : `${dur} Minutes`}
                </button>
              ))}
            </div>

            {/* Custom Time Option Input (Fixes Pic 2!) */}
            {durationPreset === 'custom' && (
              <div className="mt-2.5 flex items-center gap-2">
                <input
                  type="number"
                  min="5"
                  max="360"
                  value={customDurationMinutes}
                  onChange={(e) => setCustomDurationMinutes(parseInt(e.target.value) || 30)}
                  className="w-32 py-2 px-3 rounded-lg text-xs sm:text-sm bg-white dark:bg-[#111114] border border-slate-200 dark:border-[#27272a] text-slate-900 dark:text-white focus:outline-none focus:border-blue-500 tabular-nums min-h-[44px]"
                  placeholder="Minutes"
                />
                <span className="text-xs text-slate-500 dark:text-zinc-400 font-medium">
                  minutes total duration
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-slate-100 dark:border-[#1c1c1f] flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 rounded-lg text-xs sm:text-sm font-medium text-slate-600 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleStart}
            className="px-6 py-2.5 rounded-lg text-xs sm:text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] min-h-[44px] cursor-pointer"
          >
            <span>Start {mode === 'cbt' ? 'Examination' : 'Practice'} &rarr;</span>
          </button>
        </div>
      </div>
    </div>
  );
};
