'use client';

import React from 'react';
import useSWR from 'swr';
import { JobCard, Job } from './components/JobCard';
import { applyToJob, fetchMatches } from './lib/api';

interface MatchResponse {
  jobs: Job[];
  total: number;
}

const fetcher = async (): Promise<MatchResponse> => fetchMatches();

export default function DashboardPage() {
  const { data, error, isLoading, mutate } = useSWR<MatchResponse>('jobs-match', fetcher, {
    refreshInterval: 60_000,
  });
  const [message, setMessage] = React.useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const handleApply = async (job: Job) => {
    setMessage(null);
    try {
      const response = await applyToJob(job.id);
      setMessage({
        text: `Prepared application for ${job.title}. Resume: ${response.resume_path}`,
        type: 'success',
      });
      await mutate();
    } catch (err) {
      setMessage({ text: (err as Error).message, type: 'error' });
    }
  };

  return (
    <div>
      <header>
        <h1 className="page-title">JobApply AI Dashboard</h1>
        <p className="page-subtitle">
          Review the highest ranking opportunities and trigger tailored applications in one click.
        </p>
      </header>

      {message && (
        <div className={`message-banner ${message.type === 'error' ? 'message-error' : 'message-success'}`}>
          {message.text}
        </div>
      )}

      {error && <div className="message-banner message-error">{error.message}</div>}
      {isLoading && <p className="empty-state">Loading matches…</p>}

      <section className="job-grid" style={{ marginTop: '24px' }}>
        {data?.jobs?.map((job) => (
          <JobCard key={job.id} job={job} onApply={handleApply} />
        ))}
        {!isLoading && (data?.jobs?.length ?? 0) === 0 && (
          <p className="empty-state">No matches yet. Trigger a fetch via the API or wait for the scheduler.</p>
        )}
      </section>
    </div>
  );
}
