import { useRef, useState } from 'react';
import {
  X,
  History,
  Download,
  Upload,
  Play,
  Eye,
  Trash2,
  FileCheck
} from 'lucide-react';
import type { TestAttempt } from '../types';
import {
  exportAllDataAsJSON,
  importAllDataFromJSON,
  deleteAttempt
} from '../db/db';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  attempts: TestAttempt[];
  onReviewAttempt: (attempt: TestAttempt) => void;
  onContinuePractice: (attempt: TestAttempt) => void;
  onRefreshAttempts: () => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({
  isOpen,
  onClose,
  attempts,
  onReviewAttempt,
  onContinuePractice,
  onRefreshAttempts
}) => {
  if (!isOpen) return null;

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importStatus, setImportStatus] = useState<{
    message: string;
    isError: boolean;
  } | null>(null);

  const handleDelete = async (id: number | undefined) => {
    if (!id) return;
    if (confirm('Are you sure you want to delete this attempt record?')) {
      await deleteAttempt(id);
      onRefreshAttempts();
    }
  };

  const handleExportSingle = (attempt: TestAttempt) => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(attempt, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute(
      'download',
      `${attempt.mode}-${attempt.testId}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleExportAll = async () => {
    const jsonStr = await exportAllDataAsJSON();
    const dataStr =
      'data:text/json;charset=utf-8,' + encodeURIComponent(jsonStr);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute(
      'download',
      `jee-pyq-full-backup-${new Date().toISOString().slice(0, 10)}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const text = event.target?.result as string;
        const res = await importAllDataFromJSON(text, 'merge');
        if (res.success) {
          setImportStatus({ message: res.message, isError: false });
          onRefreshAttempts();
        } else {
          setImportStatus({ message: res.message, isError: true });
        }
      } catch (err: any) {
        setImportStatus({ message: 'Failed to read file: ' + err.message, isError: true });
      }
    };
    reader.readAsText(file);
    // Reset input
    e.target.value = '';
  };

  const formatTimestamp = (iso: string) => {
    try {
      return new Date(iso).toLocaleString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#0a0a0c] border border-slate-200 dark:border-[#222224] rounded-2xl w-full max-w-3xl max-h-[88vh] flex flex-col shadow-2xl transition-colors">
        {/* Header */}
        <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-[#1c1c1f] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Examination & Practice History
              </h2>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Saved attempts, CBT test scores, and chapter practice logs
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-[#18181c] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Import notification */}
        {importStatus && (
          <div
            className={`px-6 py-2.5 text-xs font-semibold flex items-center justify-between ${
              importStatus.isError
                ? 'bg-red-50 dark:bg-red-950/40 text-red-600 border-b border-red-200 dark:border-red-900/40'
                : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 border-b border-emerald-200 dark:border-emerald-900/40'
            }`}
          >
            <span>{importStatus.message}</span>
            <button
              onClick={() => setImportStatus(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              &times;
            </button>
          </div>
        )}

        {/* Attempts List (Fixes Pic 4 & Pic 8) */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-3">
          {attempts.length === 0 ? (
            <div className="text-center py-12 text-slate-400 dark:text-zinc-500">
              <FileCheck className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm font-semibold">No test attempts logged yet</p>
              <p className="text-xs mt-1">
                Start a Real CBT Exam or Practice Sheet to see detailed logs here.
              </p>
            </div>
          ) : (
            attempts.map((att) => {
              const isCbt = att.mode === 'cbt';
              return (
                <div
                  key={att.id || att.testId}
                  className="bg-slate-50 dark:bg-[#111114] border border-slate-200 dark:border-[#1c1c1f] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors"
                >
                  {/* Left Metadata */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                          isCbt
                            ? 'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40'
                            : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900/40'
                        }`}
                      >
                        {isCbt ? 'CBT Exam' : 'Practice & Learn'}
                      </span>
                      <span className="text-xs text-slate-400 dark:text-zinc-500 tabular-nums">
                        {formatTimestamp(att.startedAt)}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                      {att.title}
                    </h4>

                    <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-zinc-400 tabular-nums">
                      <span>
                        Answered: <strong>{att.answeredCount}</strong> / {att.totalQuestions}
                      </span>
                      {isCbt && (
                        <>
                          <span>&bull;</span>
                          <span>
                            Score: <strong className="text-blue-600 dark:text-blue-400">{att.score}</strong> / {att.maxScore}
                          </span>
                        </>
                      )}
                      <span>&bull;</span>
                      <span>Accuracy: <strong>{att.accuracy}%</strong></span>
                    </div>
                  </div>

                  {/* Right Actions per Line (Distinct continuous boxes) */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* CBT: Only Reviewable! Cannot continue! */}
                    {isCbt ? (
                      <button
                        onClick={() => {
                          onClose();
                          onReviewAttempt(att);
                        }}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center gap-1.5 min-h-[38px] cursor-pointer"
                        title="Review Marks and Mistakes"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Review Mistakes</span>
                      </button>
                    ) : (
                      /* Practice: Can Continue anytime! */
                      <button
                        onClick={() => {
                          onClose();
                          onContinuePractice(att);
                        }}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center gap-1.5 min-h-[38px] cursor-pointer"
                        title="Continue this practice session"
                      >
                        <Play className="w-3.5 h-3.5 fill-white" />
                        <span>Continue Practice</span>
                      </button>
                    )}

                    {/* Single Export */}
                    <button
                      onClick={() => handleExportSingle(att)}
                      className="p-2 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-600 dark:text-zinc-400 hover:bg-white dark:hover:bg-[#18181c] min-h-[38px] min-w-[38px] flex items-center justify-center cursor-pointer"
                      title="Save this attempt to a file"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>

                    {/* Delete */}
                    <button
                      onClick={() => handleDelete(att.id)}
                      className="p-2 rounded-lg border border-slate-200 dark:border-[#27272a] text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 min-h-[38px] min-w-[38px] flex items-center justify-center cursor-pointer"
                      title="Delete this record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Bottom Global Export & Import Bar */}
        <div className="p-4 sm:p-5 border-t border-slate-100 dark:border-[#1c1c1f] bg-slate-50 dark:bg-[#0a0a0c] flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-slate-500 dark:text-zinc-400 text-center sm:text-left">
            Your attempts and starred questions are stored safely in your browser.
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportAll}
              className="px-3.5 py-2 rounded-lg text-xs font-semibold border border-slate-200 dark:border-[#27272a] hover:bg-white dark:hover:bg-[#18181c] text-slate-800 dark:text-zinc-200 flex items-center gap-1.5 min-h-[40px] cursor-pointer"
            >
              <Download className="w-4 h-4 text-blue-600" />
              <span>Export All Progress</span>
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3.5 py-2 rounded-lg text-xs font-semibold border border-slate-200 dark:border-[#27272a] hover:bg-white dark:hover:bg-[#18181c] text-slate-800 dark:text-zinc-200 flex items-center gap-1.5 min-h-[40px] cursor-pointer"
            >
              <Upload className="w-4 h-4 text-emerald-600" />
              <span>Import Progress File</span>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
