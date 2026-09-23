import React, { useEffect, useState } from 'react';

import { getReviewSummary } from '../api';

const LABELS = ['positive', 'neutral', 'negative'];

export default function SentimentDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getReviewSummary().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Loading…</p>;

  const maxIssue = Math.max(1, ...data.top_issues.map((i) => i.count));

  return (
    <div>
      {data.data_source === 'synthetic' && (
        <p className="notice">
          This is generated sample data for demonstrating the pipeline, not real customer reviews.
        </p>
      )}

      <div className="stats">
        <div className="card stat"><span>{data.total_reviews}</span>reviews</div>
        <div className="card stat"><span>{data.average_rating ?? '–'}</span>average rating</div>
        <div className="card stat"><span>{data.average_score ?? '–'}</span>average sentiment</div>
      </div>

      <section className="card">
        <h3>Sentiment</h3>
        <div className="split-bar">
          {LABELS.map((label) => (
            <div
              key={label}
              className={`split-${label}`}
              style={{ width: `${data.sentiment[label].percent}%` }}
              title={`${label}: ${data.sentiment[label].count}`}
            />
          ))}
        </div>
        <ul className="legend">
          {LABELS.map((label) => (
            <li key={label}>
              <span className={`dot split-${label}`} /> {label} {data.sentiment[label].percent}%
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h3>Problems mentioned in reviews</h3>
        {data.top_issues.length === 0 && <p className="muted">None found.</p>}
        {data.top_issues.map(({ issue, count }) => (
          <div key={issue} className="bar-row">
            <span className="bar-label">{issue}</span>
            <div className="bar"><div style={{ width: `${(count / maxIssue) * 100}%` }} /></div>
            <span className="bar-value">{count}</span>
          </div>
        ))}
      </section>
    </div>
  );
}
