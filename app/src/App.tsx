import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewDashboard } from './components/OverviewDashboard';
import { SubjectPortals } from './components/SubjectPortals';
import { ChapterFilterGrid } from './components/ChapterFilterGrid';
import { ExamModal } from './components/ExamModal';
import { CbtExamView } from './components/CbtExamView';
import { CbtResultView } from './components/CbtResultView';
import { PracticeView } from './components/PracticeView';
import { HistoryModal } from './components/HistoryModal';
import { SubjectIndexView } from './components/SubjectIndexView';
import type {
  CatalogData,
  ChapterCatalogItem,
  SubjectType,
  TestConfig,
  Question,
  TestAttempt
} from './types';
import {
  getAllAttempts,
  getOverallStats,
  saveAttempt,
  db
} from './db/db';

export function App() {
  const [catalog, setCatalog] = useState<CatalogData | null>(null);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('theme') === 'dark' ||
      (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  const [activeView, setActiveView] = useState<
    'home' | 'subject_index' | 'cbt_exam' | 'cbt_result' | 'practice'
  >('home');

  const [selectedSubject, setSelectedSubject] = useState<SubjectType>('All');
  const [activeSubjectForIndex, setActiveSubjectForIndex] = useState<SubjectType>('Maths');

  const [examModalOpen, setExamModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  const [activeChapter, setActiveChapter] = useState<ChapterCatalogItem | null>(null);
  const [activeQuestions, setActiveQuestions] = useState<Question[]>([]);
  const [activeAttempt, setActiveAttempt] = useState<TestAttempt | null>(null);
  const [examTitle, setExamTitle] = useState('JEE Main CBT Examination');
  const [examDurationMinutes, setExamDurationMinutes] = useState(60);

  const [stats, setStats] = useState({
    totalQuestionsAttempted: 0,
    accuracy: 0,
    totalTimeSec: 0,
    starredCount: 0,
    mistakeCount: 0,
    totalAttempts: 0
  });

  const [allAttempts, setAllAttempts] = useState<TestAttempt[]>([]);

  // Dark mode effect
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Load catalog data
  useEffect(() => {
    async function loadCatalog() {
      try {
        const res = await fetch('data/catalog.json');
        if (res.ok) {
          const data: CatalogData = await res.json();
          setCatalog(data);
        }
      } catch (err) {
        console.error('Failed to load catalog.json:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCatalog();
    refreshStatsAndAttempts();
  }, []);

  const refreshStatsAndAttempts = async () => {
    const s = await getOverallStats();
    setStats(s);
    const atts = await getAllAttempts();
    setAllAttempts(atts);
  };

  const handleToggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Helper to load chapter questions
  const loadChapterQuestions = async (chapter: ChapterCatalogItem): Promise<Question[]> => {
    try {
      const res = await fetch(chapter.data_path);
      if (res.ok) {
        const data = await res.json();
        return data.questions || [];
      }
    } catch (err) {
      console.error('Failed to load questions:', err);
    }
    return [];
  };

  // Start Practice Mode
  const handleStartPractice = async (chapter: ChapterCatalogItem, existingAttempt?: TestAttempt) => {
    const qs = await loadChapterQuestions(chapter);
    if (qs.length === 0) {
      alert(`Could not load questions for ${chapter.name}.`);
      return;
    }
    setActiveChapter(chapter);
    setActiveQuestions(qs);
    setActiveAttempt(existingAttempt || null);
    setActiveView('practice');
  };

  // Start CBT Sprint for a single chapter
  const handleStartCbtSprint = (chapter: ChapterCatalogItem) => {
    setActiveChapter(chapter);
    setExamModalOpen(true);
  };

  // Start Examination from Modal configuration
  const handleStartExamFromConfig = async (config: TestConfig) => {
    if (!catalog) return;
    setExamModalOpen(false);

    let candidateQuestions: Question[] = [];

    // Filter chapters by config.subjectPool
    let targetChapters: ChapterCatalogItem[] = [];
    if (config.subjectPool === 'All') {
      targetChapters = catalog.chapters;
    } else if (
      config.subjectPool === 'Maths' ||
      config.subjectPool === 'Physics' ||
      config.subjectPool === 'Chemistry'
    ) {
      targetChapters = catalog.chapters.filter(
        (c) => c.subject.toLowerCase() === config.subjectPool.toLowerCase()
      );
    } else {
      // Single chapter by slug
      targetChapters = catalog.chapters.filter((c) => c.slug === config.subjectPool);
    }

    // Load questions from target chapters in parallel
    const chaptersQs = await Promise.all(targetChapters.map(loadChapterQuestions));
    candidateQuestions = chaptersQs.flat();

    if (candidateQuestions.length === 0) {
      alert('No questions found for the selected subject pool.');
      return;
    }

    // Shuffle and slice questions according to requested count
    const shuffled = [...candidateQuestions].sort(() => 0.5 - Math.random());
    const finalQuestions = shuffled.slice(0, Math.min(config.questionCount, shuffled.length));

    const title =
      targetChapters.length === 1
        ? `${targetChapters[0].name} (${config.mode === 'cbt' ? 'CBT Exam' : 'Practice'})`
        : config.subjectPool === 'All'
        ? `Full 3-Subject JEE Mock Exam (${finalQuestions.length} Qs)`
        : `${config.subjectPool} CBT Exam (${finalQuestions.length} Qs)`;

    if (config.mode === 'cbt') {
      setExamTitle(title);
      setExamDurationMinutes(config.durationMinutes);
      setActiveQuestions(finalQuestions);
      setActiveView('cbt_exam');
    } else {
      if (targetChapters.length === 1) {
        setActiveChapter(targetChapters[0]);
      } else {
        setActiveChapter({
          name: title,
          subject: 'Maths',
          slug: 'custom-pool',
          class_tier: 'Class B',
          total_questions: finalQuestions.length,
          difficulty_counts: { E: 0, M: 0, D: 0 },
          format_counts: { MCQ: finalQuestions.length, Numerical: 0 },
          types_count: 1,
          data_path: '',
          legacy_url: ''
        });
      }
      setActiveQuestions(finalQuestions);
      setActiveView('practice');
    }
  };

  // Finish CBT Exam
  const handleFinishCbtExam = async (attempt: TestAttempt) => {
    try {
      await saveAttempt(attempt);
      await refreshStatsAndAttempts();
    } catch (err) {
      console.error('Failed to save attempt:', err);
    }
    setActiveAttempt(attempt);
    setActiveView('cbt_result');
  };

  // Subject Counts for Dashboard
  const chapters = catalog?.chapters || [];
  const mathsChapters = chapters.filter((c) => c.subject === 'Maths');
  const physChapters = chapters.filter((c) => c.subject === 'Physics');
  const chemChapters = chapters.filter((c) => c.subject === 'Chemistry');

  const mathsTotalQ = mathsChapters.reduce((acc, c) => acc + c.total_questions, 0);
  const physTotalQ = physChapters.reduce((acc, c) => acc + c.total_questions, 0);
  const chemTotalQ = chemChapters.reduce((acc, c) => acc + c.total_questions, 0);

  const resetAllData = async () => {
    if (confirm('Are you sure you want to reset all your progress, history, and revision bank? This action cannot be undone.')) {
      await db.attempts.clear();
      await db.revision.clear();
      await refreshStatsAndAttempts();
      alert('Data reset successfully.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-black text-slate-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-150">
      {/* Top Navbar */}
      <Navbar
        darkMode={darkMode}
        onToggleDarkMode={handleToggleDarkMode}
        onOpenHistory={() => setHistoryModalOpen(true)}
        onOpenExamModal={() => {
          setActiveChapter(null);
          setExamModalOpen(true);
        }}
        onNavigateHome={() => setActiveView('home')}
        activeView={activeView}
      />

      {/* Main Content Area */}
      <main className="flex-1 w-full">
        {loading ? (
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-semibold text-slate-500 dark:text-zinc-400">
                Loading JEE PYQ Dataset (4,207 verified questions)...
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* VIEW 1: HOME */}
            {activeView === 'home' && (
              <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
                {/* 1. Preparation Overview Card */}
                <OverviewDashboard
                  stats={stats}
                  totalQuestionsInCatalog={catalog?.total_questions || 4207}
                  mathsCount={{ attempted: Math.round(stats.totalQuestionsAttempted * 0.3), total: mathsTotalQ }}
                  physCount={{ attempted: Math.round(stats.totalQuestionsAttempted * 0.45), total: physTotalQ }}
                  chemCount={{ attempted: Math.round(stats.totalQuestionsAttempted * 0.25), total: chemTotalQ }}
                  onResetData={resetAllData}
                />

                {/* 2. Three Big Subject Blocks & Underneath All-3 Exam Box */}
                <SubjectPortals
                  chapterCounts={{
                    maths: mathsChapters.length,
                    physics: physChapters.length,
                    chemistry: chemChapters.length,
                    mathsQuestions: mathsTotalQ,
                    physicsQuestions: physTotalQ,
                    chemQuestions: chemTotalQ
                  }}
                  onSelectSubjectIndex={(subj) => {
                    setActiveSubjectForIndex(subj);
                    setActiveView('subject_index');
                  }}
                  onStartFullExam={() => {
                    setActiveChapter(null);
                    setExamModalOpen(true);
                  }}
                  onScrollToChapters={() => {
                    document.getElementById('chapter-banks')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                />

                {/* 3. Filterable Chapter Practice Banks with Instant Search */}
                <ChapterFilterGrid
                  chapters={chapters}
                  selectedSubject={selectedSubject}
                  onSelectSubject={setSelectedSubject}
                  onStartPractice={handleStartPractice}
                  onStartCbtSprint={handleStartCbtSprint}
                />
              </div>
            )}

            {/* VIEW 2: SUBJECT INDEX PORTAL */}
            {activeView === 'subject_index' && (
              <SubjectIndexView
                subject={activeSubjectForIndex}
                chapters={chapters}
                onBackToHome={() => setActiveView('home')}
                onStartPractice={handleStartPractice}
                onStartCbtSprint={handleStartCbtSprint}
              />
            )}

            {/* VIEW 3: CBT EXAM SIMULATION (Strict integrity, no answer leaks) */}
            {activeView === 'cbt_exam' && (
              <CbtExamView
                title={examTitle}
                questions={activeQuestions}
                durationMinutes={examDurationMinutes}
                onFinishExam={handleFinishCbtExam}
                onExitWithoutSave={() => setActiveView('home')}
              />
            )}

            {/* VIEW 4: CBT RESULT & MISTAKE ANALYSIS */}
            {activeView === 'cbt_result' && activeAttempt && (
              <CbtResultView
                attempt={activeAttempt}
                questions={activeQuestions}
                onBackToHome={() => setActiveView('home')}
                onExportAttemptJSON={() => {
                  const dataStr =
                    'data:text/json;charset=utf-8,' +
                    encodeURIComponent(JSON.stringify(activeAttempt, null, 2));
                  const downloadAnchor = document.createElement('a');
                  downloadAnchor.setAttribute('href', dataStr);
                  downloadAnchor.setAttribute('download', `${activeAttempt.testId}-result.json`);
                  document.body.appendChild(downloadAnchor);
                  downloadAnchor.click();
                  downloadAnchor.remove();
                }}
              />
            )}

            {/* VIEW 5: CHAPTER PRACTICE & LEARN (Instant check, resume anytime) */}
            {activeView === 'practice' && activeChapter && (
              <PracticeView
                chapter={activeChapter}
                questions={activeQuestions}
                onBackToHome={() => setActiveView('home')}
                savedAttempt={activeAttempt || undefined}
              />
            )}
          </>
        )}
      </main>

      {/* Test Creation Modal */}
      <ExamModal
        isOpen={examModalOpen}
        onClose={() => setExamModalOpen(false)}
        onStartExam={handleStartExamFromConfig}
        chapters={chapters}
        initialChapter={activeChapter}
      />

      {/* History & Progress Backup Modal */}
      <HistoryModal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        attempts={allAttempts}
        onReviewAttempt={(attempt) => {
          // Load questions for review
          const chap = chapters.find((c) => c.slug === attempt.chapterSlug);
          if (chap) {
            loadChapterQuestions(chap).then((qs) => {
              setActiveQuestions(qs);
              setActiveAttempt(attempt);
              setActiveView('cbt_result');
            });
          } else {
            setActiveAttempt(attempt);
            setActiveView('cbt_result');
          }
        }}
        onContinuePractice={(attempt) => {
          const chap = chapters.find((c) => c.slug === attempt.chapterSlug);
          if (chap) {
            handleStartPractice(chap, attempt);
          }
        }}
        onRefreshAttempts={refreshStatsAndAttempts}
      />
    </div>
  );
}

export default App;
