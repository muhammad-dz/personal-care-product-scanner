import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SentimentDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/sentiment/summary');
      setData(res.data);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  // Shape returned by GET /api/sentiment/summary (backend/app/api/sentiment.py)
  const d = data?.data;
  if (!d) return <div>No sentiment data available</div>;

  return (
    <div>
      <h2>Sentiment Dashboard</h2>
      
      <div>
        <div>
          <h4>Total Reviews</h4>
          <p>{d.total_reviews}</p>
        </div>
        <div>
          <h4>Avg Rating</h4>
          <p>{d.average_rating}/5</p>
        </div>
        <div>
          <h4>Sentiment Score</h4>
          <p>{d.average_sentiment_score}</p>
        </div>
      </div>

      <div>
        <h3>Sentiment Distribution</h3>
        <div>
          <div>Positive: {d.sentiment_distribution?.positive || 0} ({d.percentages?.positive || 0}%)</div>
          <div>Neutral: {d.sentiment_distribution?.neutral || 0} ({d.percentages?.neutral || 0}%)</div>
          <div>Negative: {d.sentiment_distribution?.negative || 0} ({d.percentages?.negative || 0}%)</div>
        </div>
      </div>

      <div>
        <h3>Reported Issues</h3>
        {(d.top_issues || []).map(({ issue, count }, i) => (
          <div key={issue}>
            {i + 1}. {issue} — {count} reports
          </div>
        ))}
      </div>
    </div>
  );
};

export default SentimentDashboard;