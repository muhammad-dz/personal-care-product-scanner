import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SentimentDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSentimentData();
  }, []);

  const fetchSentimentData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/sentiment/summary');
      setData(response.data);
    } catch (err) {
      setError('Failed to load sentiment data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <p>Loading sentiment data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: '#f44336' }}>
        <h3>{error}</h3>
      </div>
    );
  }

  const sentimentData = data?.data || {
    total_reviews: 17,
    sentiment_distribution: { positive: 10, neutral: 3, negative: 4 },
    percentages: { positive: 58.8, neutral: 17.6, negative: 23.5 },
    average_sentiment_score: 0.245,
    average_rating: 3.8,
    top_issues: [
      { issue: "rash", count: 3 },
      { issue: "acne", count: 2 },
      { issue: "dryness", count: 2 },
      { issue: "irritation", count: 2 },
      { issue: "sensitivity", count: 1 }
    ]
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ color: '#333', marginBottom: '20px' }}>Sentiment Analysis Dashboard</h2>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '20px',
        marginBottom: '30px'
      }}>
        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '5px',
          border: '1px solid #ddd',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#666', margin: '0 0 10px', fontSize: '16px' }}>Total Reviews</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, color: '#2c3e50' }}>
            {sentimentData.total_reviews}
          </p>
        </div>

        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '5px',
          border: '1px solid #ddd',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#666', margin: '0 0 10px', fontSize: '16px' }}>Average Rating</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, color: '#2c3e50' }}>
            {sentimentData.average_rating}/5
          </p>
        </div>

        <div style={{
          background: 'white',
          padding: '20px',
          borderRadius: '5px',
          border: '1px solid #ddd',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#666', margin: '0 0 10px', fontSize: '16px' }}>Sentiment Score</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, color: '#2c3e50' }}>
            {sentimentData.average_sentiment_score}
          </p>
        </div>
      </div>

      <div style={{
        background: 'white',
        borderRadius: '5px',
        padding: '20px',
        border: '1px solid #ddd',
        marginBottom: '30px'
      }}>
        <h3 style={{ color: '#333', marginTop: 0 }}>Sentiment Distribution</h3>
        
        <div style={{ display: 'flex', gap: '20px' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Positive</span>
              <span>{sentimentData.percentages.positive}%</span>
            </div>
            <div style={{ height: '20px', background: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{
                width: `${sentimentData.percentages.positive}%`,
                height: '100%',
                background: '#4caf50',
                borderRadius: '3px'
              }}></div>
            </div>
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Neutral</span>
              <span>{sentimentData.percentages.neutral}%</span>
            </div>
            <div style={{ height: '20px', background: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{
                width: `${sentimentData.percentages.neutral}%`,
                height: '100%',
                background: '#ff9800',
                borderRadius: '3px'
              }}></div>
            </div>
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Negative</span>
              <span>{sentimentData.percentages.negative}%</span>
            </div>
            <div style={{ height: '20px', background: '#f0f0f0', borderRadius: '3px' }}>
              <div style={{
                width: `${sentimentData.percentages.negative}%`,
                height: '100%',
                background: '#f44336',
                borderRadius: '3px'
              }}></div>
            </div>
          </div>
        </div>
      </div>

      <div style={{
        background: 'white',
        borderRadius: '5px',
        padding: '20px',
        border: '1px solid #ddd'
      }}>
        <h3 style={{ color: '#333', marginTop: 0 }}>Most Reported Issues</h3>
        
        <div>
          {sentimentData.top_issues.map((issue, index) => (
            <div key={index} style={{
              display: 'flex',
              alignItems: 'center',
              padding: '8px',
              background: '#f8f9fa',
              borderRadius: '3px',
              marginBottom: '5px'
            }}>
              <span style={{ 
                width: '24px', 
                height: '24px', 
                background: '#f44336', 
                color: 'white',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '10px',
                fontSize: '12px'
              }}>
                {index + 1}
              </span>
              <span style={{ flex: 1 }}>{issue.issue}</span>
              <span style={{ 
                background: '#e0e0e0', 
                padding: '2px 10px', 
                borderRadius: '3px',
                fontSize: '12px'
              }}>
                {issue.count} reports
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SentimentDashboard;