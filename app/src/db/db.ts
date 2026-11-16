import Dexie, { type Table } from 'dexie';
import type { TestAttempt, RevisionItem } from '../types';

export interface UserSetting {
  key: string;
  value: any;
}

export class JEEPYQDatabase extends Dexie {
  attempts!: Table<TestAttempt, number>;
  revision!: Table<RevisionItem, number>;
  userSettings!: Table<UserSetting, string>;

  constructor() {
    super('JEEPYQDatabase');
    this.version(1).stores({
      attempts: '++id, testId, mode, subject, startedAt, completedAt, isCompleted',
      revision: '++id, &[chapterSlug+questionId+kind], chapterSlug, questionId, kind, subject, addedAt',
      userSettings: '&key'
    });
  }
}

export const db = new JEEPYQDatabase();

// --- Attempts API ---
export async function saveAttempt(attempt: TestAttempt): Promise<number> {
  if (attempt.id) {
    await db.attempts.put(attempt);
    return attempt.id;
  }
  const id = await db.attempts.add(attempt);
  return id as number;
}

export async function getAttempt(id: number): Promise<TestAttempt | undefined> {
  return await db.attempts.get(id);
}

export async function getAttemptByTestId(testId: string): Promise<TestAttempt | undefined> {
  return await db.attempts.where('testId').equals(testId).first();
}

export async function getAllAttempts(): Promise<TestAttempt[]> {
  return await db.attempts.reverse().sortBy('startedAt');
}

export async function deleteAttempt(id: number): Promise<void> {
  await db.attempts.delete(id);
}

// --- Revision Bank API ---
export async function toggleStar(chapterSlug: string, questionId: number, subject: string): Promise<boolean> {
  const existing = await db.revision
    .where(['chapterSlug', 'questionId', 'kind'])
    .equals([chapterSlug, questionId, 'starred'])
    .first();

  if (existing && existing.id) {
    await db.revision.delete(existing.id);
    return false;
  } else {
    await db.revision.add({
      chapterSlug,
      questionId,
      subject,
      kind: 'starred',
      addedAt: new Date().toISOString()
    });
    return true;
  }
}

export async function isStarred(chapterSlug: string, questionId: number): Promise<boolean> {
  const existing = await db.revision
    .where(['chapterSlug', 'questionId', 'kind'])
    .equals([chapterSlug, questionId, 'starred'])
    .first();
  return !!existing;
}

export async function addMistake(chapterSlug: string, questionId: number, subject: string, note?: string): Promise<void> {
  const existing = await db.revision
    .where(['chapterSlug', 'questionId', 'kind'])
    .equals([chapterSlug, questionId, 'mistake'])
    .first();

  if (!existing) {
    await db.revision.add({
      chapterSlug,
      questionId,
      subject,
      kind: 'mistake',
      addedAt: new Date().toISOString(),
      note
    });
  }
}

export async function getRevisionCounts(): Promise<{ starredCount: number; mistakeCount: number }> {
  const starredCount = await db.revision.where('kind').equals('starred').count();
  const mistakeCount = await db.revision.where('kind').equals('mistake').count();
  return { starredCount, mistakeCount };
}

// --- Overall Dashboard Aggregate ---
export async function getOverallStats() {
  const attempts = await db.attempts.toArray();
  const { starredCount, mistakeCount } = await getRevisionCounts();

  let totalQuestionsAttempted = 0;
  let totalCorrect = 0;
  let totalTimeSec = 0;

  for (const a of attempts) {
    totalQuestionsAttempted += a.answeredCount || 0;
    totalCorrect += a.correctCount || 0;
    totalTimeSec += a.timeSpentSec || 0;
  }

  const accuracy = totalQuestionsAttempted > 0
    ? Math.round((totalCorrect / totalQuestionsAttempted) * 100)
    : 0;

  return {
    totalQuestionsAttempted,
    accuracy,
    totalTimeSec,
    starredCount,
    mistakeCount,
    totalAttempts: attempts.length
  };
}

// --- Import / Export Backup API ---
export async function exportAllDataAsJSON(): Promise<string> {
  const attempts = await db.attempts.toArray();
  const revision = await db.revision.toArray();
  const settings = await db.userSettings.toArray();

  const exportPayload = {
    version: 1,
    exportedAt: new Date().toISOString(),
    platform: 'JEE Main PYQ Practice Platform',
    data: {
      attempts,
      revision,
      settings
    }
  };

  return JSON.stringify(exportPayload, null, 2);
}

export async function importAllDataFromJSON(
  jsonString: string,
  mode: 'merge' | 'replace' = 'merge'
): Promise<{ success: boolean; message: string; count: { attempts: number; revision: number } }> {
  try {
    const parsed = JSON.parse(jsonString);
    if (!parsed || !parsed.data) {
      throw new Error('Invalid backup file format: missing "data" property.');
    }

    const { attempts = [], revision = [], settings = [] } = parsed.data;

    await db.transaction('rw', db.attempts, db.revision, db.userSettings, async () => {
      if (mode === 'replace') {
        await db.attempts.clear();
        await db.revision.clear();
        await db.userSettings.clear();
      }

      for (const a of attempts) {
        // Strip auto-increment ID to prevent primary key collision in merge mode
        const { id, ...rest } = a;
        if (mode === 'replace' && id) {
          await db.attempts.put(a);
        } else {
          // Check if testId already exists
          const existing = await db.attempts.where('testId').equals(a.testId).first();
          if (!existing) {
            await db.attempts.add(rest as TestAttempt);
          }
        }
      }

      for (const r of revision) {
        const { id, ...rest } = r;
        if (mode === 'replace' && id) {
          await db.revision.put(r);
        } else {
          const existing = await db.revision
            .where(['chapterSlug', 'questionId', 'kind'])
            .equals([r.chapterSlug, r.questionId, r.kind])
            .first();
          if (!existing) {
            await db.revision.add(rest as RevisionItem);
          }
        }
      }

      for (const s of settings) {
        await db.userSettings.put(s);
      }
    });

    return {
      success: true,
      message: `Successfully imported ${attempts.length} attempts and ${revision.length} revision records.`,
      count: { attempts: attempts.length, revision: revision.length }
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.message || 'Failed to parse or save backup data.',
      count: { attempts: 0, revision: 0 }
    };
  }
}
