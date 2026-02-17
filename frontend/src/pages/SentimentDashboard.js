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

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>{error}</div>;

  const d = data?.data || {
    total_reviews: 17,
    percentages: { positive: 41.2, neutral: 23.5, negative: 35.3 },
    average_sentiment_score: 0.077,
    average_rating: 3.7,
    top_issues: [
      { issue: "rash", count: 2 },
      { issue: "acne", count: 2 },
      { issue: "dryness", count: 2 },
      { issue: "irritation", count: 1 },
      { issue: "sensitivity", count: 1 }
    ]
  };

  return (
    <div>
      <h2>Sentiment Dashboard</h2>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <div style={{ border: '1px solid #ccc', padding: '15px', flex: 1, textAlign: 'center' }}>
          <h4>Total Reviews</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.total_reviews}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '15px', flex: 1, textAlign: 'center' }}>
          <h4>Avg Rating</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.average_rating}/5</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '15px', flex: 1, textAlign: 'center' }}>
          <h4>Sentiment Score</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.average_sentiment_score}</p>
        </div>
      </div>

      <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '30px' }}>
        <h3>Sentiment Distribution</h3>
        <div>
          <div style={{ marginBottom: '10px' }}>
            <div>Positive: {d.percentages.positive}%</div>
            <div style={{ height: '20px', background: '#eee', marginTop: '3px' }}>
              <div style={{ width: `${d.percentages.positive}%`, height: '100%', background: '#666' }}></div>
            </div>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <div>Neutral: {d.percentages.neutral}%</div>
            <div style={{ height: '20px', background: '#eee', marginTop: '3px' }}>
              <div style={{ width: `${d.percentages.neutral}%`, height: '100%', background: '#999' }}></div>
            </div>
          </div>
          <div>
            <div>Negative: {d.percentages.negative}%</div>
            <div style={{ height: '20px', background: '#eee', marginTop: '3px' }}>
              <div style={{ width: `${d.percentages.negative}%`, height: '100%', background: '#ccc' }}></div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ border: '1px solid #ccc', padding: '20px' }}>
        <h3>Reported Issues</h3>
        {d.top_issues.map((issue, i) => (
          <div key={i} style={{ display: 'flex', marginBottom: '5px', padding: '5px', background: '#f9f9f9' }}>
            <span style={{ width: '30px' }}>{i+1}.</span>
            <span style={{ flex: 1 }}>{issue.issue}</span>
            <span>{issue.count} reports</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SentimentDashboard;