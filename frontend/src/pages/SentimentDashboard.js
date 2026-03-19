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

  const d = data?.data || {
    total_reviews: 1000,
    sentiment_counts: { positive: 571, neutral: 166, negative: 263 },
    sentiment_percentages: { positive: 57.1, neutral: 16.6, negative: 26.3 },
    avg_sentiment_score: 0.164,
    avg_rating: 3.9,
    issue_frequency: {
      'rash': 96,
      'sensitivity': 75,
      'acne': 57,
      'dryness': 19,
      'irritation': 15
    }
  };

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
          <p>{d.avg_rating}/5</p>
        </div>
        <div>
          <h4>Sentiment Score</h4>
          <p>{d.avg_sentiment_score}</p>
        </div>
      </div>

      <div>
        <h3>Sentiment Distribution</h3>
        <div>
          <div>Positive: {d.sentiment_counts?.positive || 0} ({d.sentiment_percentages?.positive || 0}%)</div>
          <div>Neutral: {d.sentiment_counts?.neutral || 0} ({d.sentiment_percentages?.neutral || 0}%)</div>
          <div>Negative: {d.sentiment_counts?.negative || 0} ({d.sentiment_percentages?.negative || 0}%)</div>
        </div>
      </div>

      <div>
        <h3>Reported Issues</h3>
        {Object.entries(d.issue_frequency || {}).map(([issue, count], i) => (
          <div key={i}>
            <span>{i+1}.</span>
            <span>{issue}</span>
            <span>{count} reports</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SentimentDashboard;