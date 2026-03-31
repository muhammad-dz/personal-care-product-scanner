import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const ScannerPage = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [safetyData, setSafetyData] = useState(null);
  const [barcode, setBarcode] = useState('');
  const [searchMode, setSearchMode] = useState('barcode');
  const [error, setError] = useState(null);
  const [skinType, setSkinType] = useState('normal');
  const [concerns, setConcerns] = useState([]);
  const [availableConcerns, setAvailableConcerns] = useState([]);
  const [showPersonalization, setShowPersonalization] = useState(true);

  React.useEffect(() => {
    axios.get('http://localhost:8000/api/concerns')
      .then(res => {
        if (res.data.success) {
          setAvailableConcerns(res.data.concerns);
        }
      })
      .catch(err => console.error('Failed to fetch concerns:', err));
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      setFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setSafetyData(null);
      setError(null);
    }
  });

  const handleBarcodeLookup = async () => {
    if (!barcode) { alert('Enter barcode'); return; }
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`http://localhost:8000/api/beauty/lookup/${barcode}`);
      setResult(res.data);
      
      if (res.data.success && res.data.ingredients_list) {
        const ratingRes = await axios.post('http://localhost:8000/api/rating/rate-product-personalized', {
          product_name: res.data.product_name,
          ingredients: res.data.ingredients_list,
          skin_type: skinType,
          concerns: concerns
        });
        if (ratingRes.data.success) {
          setResult(prev => ({ ...prev, rating_data: ratingRes.data.data }));
        }
      }
    } catch (err) {
      setError('Lookup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImageScan = async () => {
    if (!file) { alert('Select an image'); return; }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('http://localhost:8000/api/ocr/extract-text', formData);
      setResult(res.data);
      
      if (res.data.success && res.data.ingredients) {
        const ratingRes = await axios.post('http://localhost:8000/api/rating/rate-product-personalized', {
          product_name: res.data.product_name,
          ingredients: res.data.ingredients,
          skin_type: skinType,
          concerns: concerns
        });
        if (ratingRes.data.success) {
          setResult(prev => ({ ...prev, rating_data: ratingRes.data.data }));
        }
      }
    } catch (err) {
      setError('Scan failed');
    } finally {
      setLoading(false);
    }
  };

  const handleConcernToggle = (concern) => {
    setConcerns(prev =>
      prev.includes(concern) ? prev.filter(c => c !== concern) : [...prev, concern]
    );
  };

  const getScoreColor = (score) => {
    if (score >= 8) return '#4caf50';
    if (score >= 6) return '#8bc34a';
    if (score >= 4) return '#ffc107';
    return '#f44336';
  };

  const SkinTypeDescriptions = {
    normal: "Works well with most formulas",
    dry: "Needs intense hydration and barrier repair",
    oily: "Benefits from exfoliants and lightweight formulas",
    combination: "Needs balance of hydration and oil control",
    sensitive: "Needs gentle, fragrance-free products"
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '900px', margin: '0 auto' }}>
      <h2>Product Scanner</h2>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={() => setSearchMode('image')} style={{ padding: '10px 20px', cursor: 'pointer', background: searchMode === 'image' ? '#2c3e50' : '#f5f5f5', color: searchMode === 'image' ? 'white' : '#333', border: '1px solid #ccc' }}>
          Scan Image
        </button>
        <button onClick={() => setSearchMode('barcode')} style={{ padding: '10px 20px', cursor: 'pointer', background: searchMode === 'barcode' ? '#2c3e50' : '#f5f5f5', color: searchMode === 'barcode' ? 'white' : '#333', border: '1px solid #ccc' }}>
          Lookup Barcode
        </button>
        <button onClick={() => setShowPersonalization(!showPersonalization)} style={{ padding: '10px 20px', cursor: 'pointer', background: '#f0f0f0', border: '1px solid #ccc' }}>
          {showPersonalization ? 'Hide' : 'Show'} Personalization
        </button>
      </div>

      {showPersonalization && (
        <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #e0e0e0' }}>
          <h3>Personalize Your Analysis</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Your Skin Type:</label>
            <select value={skinType} onChange={(e) => setSkinType(e.target.value)} style={{ padding: '8px', width: '200px', border: '1px solid #ccc', borderRadius: '4px' }}>
              <option value="normal">Normal</option>
              <option value="dry">Dry</option>
              <option value="oily">Oily</option>
              <option value="combination">Combination</option>
              <option value="sensitive">Sensitive</option>
            </select>
            <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>{SkinTypeDescriptions[skinType]}</p>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Your Skin Concerns:</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {availableConcerns.map(concern => (
                <button key={concern} onClick={() => handleConcernToggle(concern)} style={{
                  padding: '5px 12px',
                  background: concerns.includes(concern) ? '#2c3e50' : '#e9ecef',
                  color: concerns.includes(concern) ? 'white' : '#333',
                  border: 'none',
                  borderRadius: '20px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}>
                  {concern.charAt(0).toUpperCase() + concern.slice(1)}
                </button>
              ))}
            </div>
            {concerns.length > 0 && <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>Selected: {concerns.join(', ')}</p>}
          </div>
        </div>
      )}

      {error && <div style={{ marginBottom: '20px', padding: '10px', background: '#ffebee', border: '1px solid #ffcdd2', color: '#c62828' }}>{error}</div>}

      {searchMode === 'image' && (
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px' }}>
          <div {...getRootProps()} style={{ border: '2px dashed #ccc', padding: '40px', textAlign: 'center', cursor: 'pointer', background: '#fafafa' }}>
            <input {...getInputProps()} />
            <p>Drag and drop product label image here or click to browse</p>
          </div>
          {preview && <div style={{ marginTop: '20px', textAlign: 'center' }}><img src={preview} alt="Preview" style={{ maxWidth: '200px', border: '1px solid #ccc' }} /><p style={{ fontSize: '12px', color: '#666' }}>{file?.name}</p></div>}
          <button onClick={handleImageScan} disabled={!file || loading} style={{ marginTop: '20px', padding: '10px 20px', background: '#2c3e50', color: 'white', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', opacity: (!file || loading) ? 0.6 : 1 }}>
            {loading ? 'Processing...' : 'Scan Product'}
          </button>
        </div>
      )}

      {searchMode === 'barcode' && (
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px', textAlign: 'center' }}>
          <h3>Enter Barcode</h3>
          <p style={{ fontSize: '14px', color: '#666' }}>Look up product from Open Beauty Facts database</p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <input type="text" placeholder="e.g., 3560070791460" value={barcode} onChange={(e) => setBarcode(e.target.value)} onKeyPress={(e) => { if (e.key === 'Enter') handleBarcodeLookup(); }} style={{ padding: '10px', width: '280px', border: '1px solid #ccc', borderRadius: '4px' }} />
            <button onClick={handleBarcodeLookup} disabled={!barcode || loading} style={{ padding: '10px 20px', background: '#2c3e50', color: 'white', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', opacity: (!barcode || loading) ? 0.6 : 1 }}>
              {loading ? 'Looking up...' : 'Lookup'}
            </button>
          </div>
          <p style={{ fontSize: '11px', color: '#999', marginTop: '15px' }}>Data from Open Beauty Facts</p>
        </div>
      )}

      {result && result.success && (
        <div style={{ border: '1px solid #4caf50', padding: '20px', marginTop: '20px', borderTop: '4px solid #4caf50' }}>
          <h3>Product Found</h3>
          <p><strong>{result.product_name || result.name}</strong></p>
          <p>Brand: {result.brands || 'Unknown'}</p>
          
          {result.rating_data && (
            <div>
              <div style={{ background: '#f5f5f5', padding: '15px', margin: '15px 0', borderRadius: '8px' }}>
                <h4>Standard Safety Rating</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: getScoreColor(result.rating_data.standard_score) }}>{result.rating_data.standard_score}/100</div>
                  <div><div style={{ fontSize: '24px', fontWeight: 'bold' }}>{result.rating_data.standard_rating}</div><div style={{ fontSize: '14px' }}>General population rating</div></div>
                </div>
              </div>
              
              {showPersonalization && (
                <div style={{ background: '#e8f5e9', padding: '15px', margin: '15px 0', borderRadius: '8px', borderLeft: `4px solid ${getScoreColor(result.rating_data.personalized_score)}` }}>
                  <h4>Personalized for {skinType} skin {concerns.length > 0 ? `+ ${concerns.join(', ')}` : ''}</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ fontSize: '36px', fontWeight: 'bold', color: getScoreColor(result.rating_data.personalized_score) }}>{result.rating_data.personalized_score}/100</div>
                    <div><div style={{ fontSize: '24px', fontWeight: 'bold' }}>{result.rating_data.personalized_rating}</div><div style={{ fontSize: '14px' }}>{result.rating_data.score_difference > 0 ? '+' : ''}{result.rating_data.score_difference} points vs standard</div></div>
                  </div>
                  <div style={{ marginTop: '10px', fontSize: '14px', padding: '10px', background: 'white', borderRadius: '5px' }}>{result.rating_data.recommendation}</div>
                </div>
              )}
              
              <div style={{ marginTop: '15px', display: 'flex', gap: '20px', fontSize: '12px', color: '#666' }}>
                <span>Risky ingredients: {result.rating_data.risk_ingredients}</span>
                <span>Beneficial ingredients: {result.rating_data.beneficial_ingredients}</span>
                <span>Total ingredients: {result.rating_data.total_ingredients}</span>
              </div>
            </div>
          )}
          
          <h4>Ingredients:</h4>
          {result.ingredients_list?.length > 0 ? (
            <div>
              <p style={{ background: '#f5f5f5', padding: '15px', borderRadius: '5px', fontFamily: 'monospace', fontSize: '12px', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{result.ingredients_list.join(', ')}</p>
              <p style={{ fontSize: '11px', color: '#666' }}>Total ingredients: {result.ingredients_list.length}</p>
            </div>
          ) : result.extracted_text ? (
            <p style={{ background: '#f5f5f5', padding: '15px', borderRadius: '5px' }}>{result.extracted_text}</p>
          ) : (
            <p>No ingredients information available</p>
          )}
        </div>
      )}

      {!result && !loading && !error && (
        <div style={{ border: '1px dashed #ccc', padding: '30px', textAlign: 'center', background: '#fafafa' }}>
          <p>Enter a barcode above to look up a product</p>
          <p style={{ fontSize: '12px', color: '#999' }}>Try: 3560070791460</p>
        </div>
      )}
    </div>
  );
};

export default ScannerPage;