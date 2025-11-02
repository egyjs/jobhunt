'use client';

import React from 'react';

export type Job = {
  id: number;
  source: string;
  title: string;
  company: string;
  location?: string | null;
  summary?: string | null;
  url: string;
  match_score?: number | null;
  tags: string[];
};

interface JobCardProps {
  job: Job;
  onApply: (job: Job) => Promise<void>;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onApply }) => {
  const [loading, setLoading] = React.useState(false);
  const handleApply = async () => {
    setLoading(true);
    try {
      await onApply(job);
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">{job.title}</h3>
          <p className="card-meta">
            {job.company} • {job.location ?? 'Remote/Global'}
          </p>
          {job.summary && <p className="card-summary">{job.summary}</p>}
          {job.tags.length > 0 && (
            <ul className="tag-list">
              {job.tags.map((tag) => (
                <li key={tag} className="tag">
                  {tag}
                </li>
              ))}
            </ul>
          )}
        </div>
        <a href={job.url} target="_blank" rel="noreferrer" className="button-link">
          View
        </a>
      </div>
      <div className="card-footer">
        <span className="score-label">
          Match Score: {job.match_score ? (job.match_score * 100).toFixed(0) : '—'}%
        </span>
        <button type="button" onClick={handleApply} disabled={loading} className="button">
          {loading ? 'Preparing…' : 'Apply with AI'}
        </button>
      </div>
    </article>
  );
};
