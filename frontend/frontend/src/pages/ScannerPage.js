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
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
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
    if (!file) {
      alert('Please select an image first');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const ocrResponse = await axios.post('http://localhost:8000/api/ocr/extract-text', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(ocrResponse.data);
      
      if (ocrResponse.data.ingredients && ocrResponse.data.ingredients.length > 0) {
        const safetyResponse = await axios.post('http://localhost:8000/api/ocr/batch-check', {
          ingredients: ocrResponse.data.ingredients
        });
        setSafetyData(safetyResponse.data);
      }
      
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to scan product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBarcodeLookup = async () => {
    if (!barcode) {
      alert('Please enter a barcode');
      return;
    }

    setLoading(true);
    setResult(null);
    setSafetyData(null);

    try {
      const response = await axios.get(`http://localhost:8000/api/beauty/lookup/${barcode}`);
      
      if (response.data.success) {
        setResult({
          success: true,
          filename: 'Barcode Scan',
          message: 'Product found in Open Beauty Facts database',
          extracted_text: response.data.ingredients_text || 'No ingredients listed',
          ingredients: response.data.ingredients_list || []
        });

        if (response.data.ingredients_list && response.data.ingredients_list.length > 0) {
          const safetyResponse = await axios.post('http://localhost:8000/api/ocr/batch-check', {
            ingredients: response.data.ingredients_list
          });
          setSafetyData(safetyResponse.data);
        }

        setSafetyData(prev => ({
          ...prev,
          product_info: {
            name: response.data.product_name,
            brand: response.data.brands,
            source: response.data.source
          }
        }));

      } else {
        alert('Product not found in database. Try image scan instead.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to lookup barcode. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return '#4caf50';
    if (score >= 6) return '#8bc34a';
    if (score >= 4) return '#ffc107';
    return '#f44336';
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ color: '#333', marginBottom: '20px' }}>Product Scanner</h2>
      
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '20px',
        background: '#f5f5f5',
        padding: '10px',
        borderRadius: '5px'
      }}>
        <button
          onClick={() => setSearchMode('image')}
          style={{
            flex: 1,
            padding: '10px',
            background: searchMode === 'image' ? '#2c3e50' : 'white',
            color: searchMode === 'image' ? 'white' : '#333',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Scan Label Image
        </button>
        <button
          onClick={() => setSearchMode('barcode')}
          style={{
            flex: 1,
            padding: '10px',
            background: searchMode === 'barcode' ? '#2c3e50' : 'white',
            color: searchMode === 'barcode' ? 'white' : '#333',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Lookup by Barcode
        </button>
      </div>

      {searchMode === 'image' && (
        <div style={{
          background: 'white',
          borderRadius: '5px',
          padding: '30px',
          border: '1px solid #ddd',
          marginBottom: '20px'
        }}>
          <div {...getRootProps()} style={{
            border: '2px dashed #ccc',
            borderRadius: '5px',
            padding: '40px',
            textAlign: 'center',
            cursor: 'pointer',
            background: '#fafafa'
          }}>
            <input {...getInputProps()} />
            <p style={{ color: '#666' }}>
              Drag & drop product label image here
            </p>
            <p style={{ fontSize: '14px', color: '#999' }}>
              or click to browse (PNG, JPG, JPEG)
            </p>
          </div>

          {preview && (
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <h3>Preview:</h3>
              <img 
                src={preview} 
                alt="Preview" 
                style={{ 
                  maxWidth: '200px', 
                  maxHeight: '200px',
                  border: '1px solid #ddd'
                }} 
              />
              <p style={{ color: '#666', fontSize: '14px' }}>{file?.name}</p>
            </div>
          )}

          <button 
            onClick={handleImageScan}
            disabled={!file || loading}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              background: '#2c3e50',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: (!file || loading) ? 0.7 : 1
            }}
          >
            {loading ? 'Processing...' : 'Scan Product'}
          </button>
        </div>
      )}

      {searchMode === 'barcode' && (
        <div style={{
          background: 'white',
          borderRadius: '5px',
          padding: '30px',
          border: '1px solid #ddd',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          <h3>Enter Product Barcode</h3>
          <p style={{ color: '#666', fontSize: '14px', marginBottom: '20px' }}>
            Look up product from Open Beauty Facts database
          </p>
          
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <input
              type="text"
              placeholder="e.g., 4005900001504"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              style={{
                padding: '10px',
                width: '300px',
                border: '1px solid #ccc',
                borderRadius: '5px'
              }}
            />
            <button
              onClick={handleBarcodeLookup}
              disabled={!barcode || loading}
              style={{
                padding: '10px 20px',
                background: '#2c3e50',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: (!barcode || loading) ? 0.7 : 1
              }}
            >
              {loading ? 'Looking up...' : 'Lookup Product'}
            </button>
          </div>
          
          <p style={{ fontSize: '12px', color: '#999', marginTop: '20px' }}>
            Data provided by Open Beauty Facts
          </p>
        </div>
      )}

      {result && (
        <div style={{
          background: 'white',
          borderRadius: '5px',
          padding: '20px',
          border: '1px solid #ddd'
        }}>
          <h3>Analysis Results</h3>
          
          {safetyData?.product_info && (
            <div style={{
              background: '#f8f9fa',
              padding: '15px',
              borderRadius: '5px',
              marginBottom: '20px'
            }}>
              <h4 style={{ margin: '0 0 5px' }}>{safetyData.product_info.name}</h4>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>Brand: {safetyData.product_info.brand}</p>
              <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>Source: {safetyData.product_info.source}</p>
            </div>
          )}
          
          <div style={{ marginBottom: '20px' }}>
            <h4>Extracted Ingredients:</h4>
            <p style={{ 
              background: '#f5f5f5', 
              padding: '10px', 
              borderRadius: '5px',
              fontFamily: 'monospace',
              fontSize: '14px'
            }}>
              {result.extracted_text || 'No ingredients detected'}
            </p>
          </div>

          {safetyData && safetyData.results && (
            <>
              <h4>Ingredient Safety Analysis:</h4>
              
              <div style={{
                background: '#f8f9fa',
                padding: '15px',
                borderRadius: '5px',
                marginBottom: '20px'
              }}>
                <h5 style={{ margin: '0 0 5px' }}>Overall Safety Rating</h5>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                  {safetyData.overall_rating || 'Unknown'}
                </div>
                <div style={{ fontSize: '18px', marginTop: '5px' }}>
                  Score: {safetyData.average_score || '?'}/10
                </div>
              </div>

              <div>
                {safetyData.results.map((item, index) => (
                  <div key={index} style={{
                    border: '1px solid #eee',
                    borderRadius: '5px',
                    padding: '10px',
                    marginBottom: '10px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong>{item.ingredient}</strong>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{
                          background: getScoreColor(item.safety_score),
                          color: 'white',
                          padding: '3px 8px',
                          borderRadius: '3px',
                          fontSize: '12px'
                        }}>
                          Score: {item.safety_score}/10
                        </span>
                        <span style={{
                          background: '#f0f0f0',
                          padding: '3px 8px',
                          borderRadius: '3px',
                          fontSize: '12px'
                        }}>
                          {item.rating}
                        </span>
                      </div>
                    </div>
                    {item.hazards && item.hazards.length > 0 && (
                      <div style={{ marginTop: '5px' }}>
                        <span style={{ color: '#f44336', fontSize: '12px' }}>
                          Hazards: {item.hazards.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ScannerPage;