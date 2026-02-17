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
  const [searchMode, setSearchMode] = useState('image');

  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      setFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setSafetyData(null);
    }
  });

  const handleImageScan = async () => {
    if (!file) { alert('Select an image'); return; }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const ocrRes = await axios.post('http://localhost:8000/api/ocr/extract-text', formData);
      setResult(ocrRes.data);
      if (ocrRes.data.ingredients?.length) {
        const safetyRes = await axios.post('http://localhost:8000/api/ocr/batch-check', {
          ingredients: ocrRes.data.ingredients
        });
        setSafetyData(safetyRes.data);
      }
    } catch (error) {
      alert('Scan failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBarcodeLookup = async () => {
    if (!barcode) { alert('Enter barcode'); return; }
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/beauty/lookup/${barcode}`);
      if (res.data.success) {
        setResult({
          success: true,
          extracted_text: res.data.ingredients_text || 'No ingredients',
          ingredients: res.data.ingredients_list || []
        });
        if (res.data.ingredients_list?.length) {
          const safetyRes = await axios.post('http://localhost:8000/api/ocr/batch-check', {
            ingredients: res.data.ingredients_list
          });
          setSafetyData({
            ...safetyRes.data,
            product_info: {
              name: res.data.product_name,
              brand: res.data.brands
            }
          });
        }
      } else {
        alert('Product not found');
      }
    } catch (error) {
      alert('Lookup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Product Scanner</h2>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={() => setSearchMode('image')}
          style={{ 
            padding: '8px 15px', 
            background: searchMode === 'image' ? '#ddd' : '#f5f5f5',
            border: '1px solid #999',
            cursor: 'pointer'
          }}
        >
          Scan Image
        </button>
        <button 
          onClick={() => setSearchMode('barcode')}
          style={{ 
            padding: '8px 15px', 
            background: searchMode === 'barcode' ? '#ddd' : '#f5f5f5',
            border: '1px solid #999',
            cursor: 'pointer'
          }}
        >
          Lookup Barcode
        </button>
      </div>

      {searchMode === 'image' && (
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px' }}>
          <div {...getRootProps()} style={{
            border: '2px dashed #ccc',
            padding: '30px',
            textAlign: 'center',
            cursor: 'pointer',
            background: '#fafafa'
          }}>
            <input {...getInputProps()} />
            <p>Drag image here or click to browse</p>
          </div>

          {preview && (
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <img src={preview} alt="Preview" style={{ maxWidth: '150px', border: '1px solid #ccc' }} />
            </div>
          )}

          <button 
            onClick={handleImageScan}
            disabled={!file || loading}
            style={{
              marginTop: '20px',
              padding: '8px 15px',
              background: '#f0f0f0',
              border: '1px solid #999',
              cursor: loading ? 'default' : 'pointer',
              opacity: (!file || loading) ? 0.5 : 1
            }}
          >
            {loading ? 'Processing...' : 'Scan Product'}
          </button>
        </div>
      )}

      {searchMode === 'barcode' && (
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px', textAlign: 'center' }}>
          <h3>Enter Barcode</h3>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <input
              type="text"
              placeholder="e.g., 4005900001504"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              style={{ padding: '8px', width: '250px', border: '1px solid #ccc' }}
            />
            <button
              onClick={handleBarcodeLookup}
              disabled={!barcode || loading}
              style={{
                padding: '8px 15px',
                background: '#f0f0f0',
                border: '1px solid #999',
                cursor: loading ? 'default' : 'pointer',
                opacity: (!barcode || loading) ? 0.5 : 1
              }}
            >
              {loading ? 'Looking up...' : 'Lookup'}
            </button>
          </div>
          <p style={{ fontSize: '12px', marginTop: '15px' }}>Data from Open Beauty Facts</p>
        </div>
      )}

      {result && (
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h3>Results</h3>
          
          {safetyData?.product_info && (
            <div style={{ background: '#f9f9f9', padding: '10px', marginBottom: '15px' }}>
              <p><strong>{safetyData.product_info.name}</strong> - {safetyData.product_info.brand}</p>
            </div>
          )}
          
          <div style={{ marginBottom: '15px' }}>
            <h4>Ingredients:</h4>
            <p style={{ fontFamily: 'monospace', fontSize: '13px' }}>
              {result.extracted_text || 'None detected'}
            </p>
          </div>

          {safetyData?.results && (
            <>
              <h4>Safety Analysis:</h4>
              <div style={{ background: '#f9f9f9', padding: '10px', marginBottom: '15px' }}>
                <p><strong>Overall: {safetyData.overall_rating || 'Unknown'}</strong> (Score: {safetyData.average_score}/10)</p>
              </div>

              {safetyData.results.map((item, index) => (
                <div key={index} style={{ 
                  border: '1px solid #eee', 
                  padding: '8px', 
                  marginBottom: '5px',
                  fontSize: '13px'
                }}>
                  <strong>{item.ingredient}</strong> - Score: {item.safety_score}/10 ({item.rating})
                  {item.hazards?.length > 0 && (
                    <div style={{ marginTop: '3px', color: '#666' }}>⚠️ {item.hazards.join(', ')}</div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ScannerPage;