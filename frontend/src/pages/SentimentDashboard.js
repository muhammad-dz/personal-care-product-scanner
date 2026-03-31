import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SentimentDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wordCloudImage, setWordCloudImage] = useState(null);
  const [wordCloudFilter, setWordCloudFilter] = useState('all');
  const [wordCloudLoading, setWordCloudLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    fetchWordCloud();
  }, [wordCloudFilter]);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/sentiment/summary');
      setData(response.data);
    } catch (err) {
      console.error('Error fetching sentiment:', err);
      setError('Failed to load sentiment data');
    } finally {
      setLoading(false);
    }
  };

  const fetchWordCloud = async () => {
    setWordCloudLoading(true);
    try {
      let url = 'http://localhost:8000/api/sentiment/wordcloud';
      if (wordCloudFilter !== 'all') {
        url += `?sentiment=${wordCloudFilter}`;
      }
      const response = await axios.get(url);
      if (response.data.success && response.data.image) {
        setWordCloudImage(response.data.image);
      } else {
        setWordCloudImage(null);
      }
    } catch (err) {
      console.error('Error fetching word cloud:', err);
      setWordCloudImage(null);
    } finally {
      setWordCloudLoading(false);
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading sentiment data...</div>;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>{error}</div>;

  const d = data?.data || {
    total_reviews: 1000,
    sentiment_counts: { positive: 571, neutral: 166, negative: 263 },
    sentiment_percentages: { positive: 57.1, neutral: 16.6, negative: 26.3 },
    avg_sentiment_score: 0.164,
    avg_rating: 3.9,
    issue_frequency: { rash: 96, sensitivity: 75, acne: 57, dryness: 19, irritation: 15 }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Sentiment Dashboard</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '30px' }}>
        <div style={{ border: '1px solid #ccc', padding: '20px', textAlign: 'center' }}>
          <h4>Total Reviews</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.total_reviews}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '20px', textAlign: 'center' }}>
          <h4>Avg Rating</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.avg_rating}/5</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '20px', textAlign: 'center' }}>
          <h4>Sentiment Score</h4>
          <p style={{ fontSize: '28px', margin: '5px 0' }}>{d.avg_sentiment_score}</p>
        </div>
      </div>

      <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '30px' }}>
        <h3>Sentiment Distribution</h3>
        <div style={{ marginBottom: '15px' }}>
          <div>Positive: {d.sentiment_counts.positive} ({d.sentiment_percentages.positive}%)</div>
          <div style={{ height: '20px', background: '#f0f0f0', marginTop: '5px' }}>
            <div style={{ width: `${d.sentiment_percentages.positive}%`, height: '100%', background: '#666' }}></div>
          </div>
        </div>
        <div style={{ marginBottom: '15px' }}>
          <div>Neutral: {d.sentiment_counts.neutral} ({d.sentiment_percentages.neutral}%)</div>
          <div style={{ height: '20px', background: '#f0f0f0', marginTop: '5px' }}>
            <div style={{ width: `${d.sentiment_percentages.neutral}%`, height: '100%', background: '#999' }}></div>
          </div>
        </div>
        <div>
          <div>Negative: {d.sentiment_counts.negative} ({d.sentiment_percentages.negative}%)</div>
          <div style={{ height: '20px', background: '#f0f0f0', marginTop: '5px' }}>
            <div style={{ width: `${d.sentiment_percentages.negative}%`, height: '100%', background: '#ccc' }}></div>
          </div>
        </div>
      </div>

      <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '30px' }}>
        <h3>Word Cloud</h3>
        <p style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
          Most common words in reviews (filtered by sentiment)
        </p>
        
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button onClick={() => setWordCloudFilter('all')} style={{ padding: '5px 12px', background: wordCloudFilter === 'all' ? '#2c3e50' : '#f0f0f0', color: wordCloudFilter === 'all' ? 'white' : '#333', border: '1px solid #ccc', cursor: 'pointer' }}>
            All Reviews
          </button>
          <button onClick={() => setWordCloudFilter('positive')} style={{ padding: '5px 12px', background: wordCloudFilter === 'positive' ? '#2c3e50' : '#f0f0f0', color: wordCloudFilter === 'positive' ? 'white' : '#333', border: '1px solid #ccc', cursor: 'pointer' }}>
            Positive Only
          </button>
          <button onClick={() => setWordCloudFilter('negative')} style={{ padding: '5px 12px', background: wordCloudFilter === 'negative' ? '#2c3e50' : '#f0f0f0', color: wordCloudFilter === 'negative' ? 'white' : '#333', border: '1px solid #ccc', cursor: 'pointer' }}>
            Negative Only
          </button>
        </div>
        
        {wordCloudLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f5f5f5' }}>
            <p>Generating word cloud...</p>
          </div>
        ) : wordCloudImage ? (
          <div style={{ textAlign: 'center' }}>
            <img src={`data:image/png;base64,${wordCloudImage}`} alt="Word Cloud" style={{ maxWidth: '100%', border: '1px solid #eee' }} />
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f5f5f5' }}>
            <p>No data available for word cloud</p>
          </div>
        )}
      </div>

      <div style={{ border: '1px solid #ccc', padding: '20px' }}>
        <h3>Reported Issues</h3>
        {Object.entries(d.issue_frequency || {}).map(([issue, count], index) => (
          <div key={issue} style={{ display: 'flex', marginBottom: '8px', padding: '8px', background: '#f9f9f9' }}>
            <span style={{ width: '30px' }}>{index + 1}.</span>
            <span style={{ flex: 1 }}>{issue}</span>
            <span>{count} reports</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SentimentDashboard;