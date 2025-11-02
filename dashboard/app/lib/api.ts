import type { Job } from '../components/JobCard';

export type ApplyResponse = {
  job_id: number;
  status: string;
  match_score?: number | null;
  resume_path?: string | null;
  cover_letter_path?: string | null;
  notes?: string | null;
  auto_submitted: boolean;
  submitted_at?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export async function fetchMatches() {
  const response = await fetch(`${API_BASE}/jobs/match`);
  if (!response.ok) {
    throw new Error('Failed to load job matches');
  }
  return (await response.json()) as { jobs: Job[]; total: number };
}

export async function applyToJob(jobId: number) {
  const response = await fetch(`${API_BASE}/jobs/apply`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ job_id: jobId, auto_submit: false }),
  });
  if (!response.ok) {
    throw new Error('Failed to prepare application');
  }
  return (await response.json()) as ApplyResponse;
}
