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
  const [error, setError] = useState(null);
  const [lookupSuccess, setLookupSuccess] = useState(false);

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
      setError(null);
      setLookupSuccess(false);
    }
  });

  const handleImageScan = async () => {
    if (!file) {
      alert('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const ocrResponse = await axios.post('http://localhost:8000/api/ocr/extract-text', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(ocrResponse.data);
      setLookupSuccess(true);
      
      if (ocrResponse.data.ingredients && ocrResponse.data.ingredients.length > 0) {
        const safetyResponse = await axios.post('http://localhost:8000/api/ocr/batch-check', {
          ingredients: ocrResponse.data.ingredients
        });
        setSafetyData(safetyResponse.data);
      }
      
    } catch (error) {
      console.error('Error:', error);
      setError('Scan failed. Please try again.');
      setLookupSuccess(false);
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
    setError(null);
    setLookupSuccess(false);

    try {
      console.log(`Looking up barcode: ${barcode}`);
      const response = await axios.get(`http://localhost:8000/api/beauty/lookup/${barcode}`);
      
      if (response.data.success) {
        console.log('Product found:', response.data);
        setLookupSuccess(true);
        
        setResult(response.data);

        if (response.data.ingredients_list && response.data.ingredients_list.length > 0) {
          try {
            const safetyResponse = await axios.post('http://localhost:8000/api/ocr/batch-check', {
              ingredients: response.data.ingredients_list
            });
            
            setSafetyData({
              ...safetyResponse.data,
              product_info: {
                name: response.data.product_name,
                brands: response.data.brands,
                source: response.data.source
              }
            });
          } catch (safetyError) {
            console.error('Safety check error:', safetyError);
            setSafetyData({
              product_info: {
                name: response.data.product_name,
                brands: response.data.brands,
                source: response.data.source
              }
            });
          }
        } else {
          setSafetyData({
            product_info: {
              name: response.data.product_name,
              brands: response.data.brands,
              source: response.data.source
            }
          });
        }
        
      } else {
        console.log('Product not found');
        setError('Product not found in database');
        setLookupSuccess(false);
      }
    } catch (error) {
      console.error('Lookup error:', error);
      setError('Lookup failed. Could not connect to server.');
      setLookupSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ color: '#333', marginBottom: '20px', fontWeight: 'normal' }}>Product Scanner</h2>
      
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '20px',
        background: '#f5f5f5',
        padding: '10px',
        borderRadius: '5px'
      }}>
        <button
          onClick={() => {
            setSearchMode('image');
            setError(null);
            setResult(null);
            setSafetyData(null);
            setLookupSuccess(false);
          }}
          style={{
            flex: 1,
            padding: '10px',
            background: searchMode === 'image' ? '#999' : 'white',
            color: searchMode === 'image' ? 'white' : '#333',
            border: '1px solid #ccc',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Scan Image
        </button>
        <button
          onClick={() => {
            setSearchMode('barcode');
            setError(null);
            setResult(null);
            setSafetyData(null);
            setLookupSuccess(false);
          }}
          style={{
            flex: 1,
            padding: '10px',
            background: searchMode === 'barcode' ? '#999' : 'white',
            color: searchMode === 'barcode' ? 'white' : '#333',
            border: '1px solid #ccc',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Lookup Barcode
        </button>
      </div>

      {/* Error Message Display */}
      {error && (
        <div style={{
          marginBottom: '20px',
          padding: '12px',
          background: '#f5f5f5',
          border: '1px solid #ccc',
          borderRadius: '5px',
          color: '#666'
        }}>
          <strong>{error}</strong>
        </div>
      )}

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
              Drag and drop product label image here
            </p>
            <p style={{ fontSize: '14px', color: '#999' }}>
              or click to browse (PNG, JPG, JPEG)
            </p>
          </div>

          {preview && (
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <h4 style={{ fontWeight: 'normal', color: '#666' }}>Preview:</h4>
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
              background: !file || loading ? '#f0f0f0' : '#999',
              color: !file || loading ? '#999' : 'white',
              border: '1px solid #ccc',
              borderRadius: '5px',
              cursor: loading ? 'not-allowed' : 'pointer'
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
          <h3 style={{ fontWeight: 'normal', color: '#333' }}>Enter Barcode</h3>
          <p style={{ color: '#666', fontSize: '14px', marginBottom: '20px' }}>
            Look up product from Open Beauty Facts database
          </p>
          
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <input
              type="text"
              placeholder="e.g., 3560070791460"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              style={{
                padding: '10px',
                width: '300px',
                border: '1px solid #ccc',
                borderRadius: '5px'
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleBarcodeLookup();
                }
              }}
            />
            <button
              onClick={handleBarcodeLookup}
              disabled={!barcode || loading}
              style={{
                padding: '10px 20px',
                background: !barcode || loading ? '#f0f0f0' : '#999',
                color: !barcode || loading ? '#999' : 'white',
                border: '1px solid #ccc',
                borderRadius: '5px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Looking up...' : 'Lookup'}
            </button>
          </div>
          
          <p style={{ fontSize: '12px', color: '#999', marginTop: '20px' }}>
            Data provided by Open Beauty Facts
          </p>
        </div>
      )}

      {/* Results Section */}
      {lookupSuccess && result && (
        <div style={{
          background: 'white',
          borderRadius: '5px',
          padding: '20px',
          border: '1px solid #ccc',
          borderTop: '4px solid #999'
        }}>
          <h3 style={{ marginTop: 0, color: '#333', fontWeight: 'normal' }}>Product Found</h3>
          
          {safetyData?.product_info && (
            <div style={{
              background: '#f5f5f5',
              padding: '15px',
              borderRadius: '5px',
              marginBottom: '20px'
            }}>
              <h4 style={{ margin: '0 0 5px', fontSize: '18px', fontWeight: 'normal', color: '#333' }}>{safetyData.product_info.name}</h4>
              <p style={{ margin: '5px 0', fontSize: '14px', color: '#666' }}>
                <strong>Brand:</strong> {safetyData.product_info.brands || 'Unknown'}
              </p>
              <p style={{ margin: '5px 0', fontSize: '12px', color: '#999' }}>
                <strong>Source:</strong> {safetyData.product_info.source}
              </p>
            </div>
          )}
          
          {/* AI Rating Algorithm Display - Simplified */}
          {result.rating_data && (
            <div style={{
              background: '#f5f5f5',
              padding: '20px',
              borderRadius: '8px',
              marginBottom: '25px',
              border: '1px solid #ccc'
            }}>
              <h4 style={{ margin: '0 0 15px', color: '#333', fontWeight: 'normal' }}>AI Safety Rating</h4>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '30px', flexWrap: 'wrap' }}>
                {/* Score Circle - Gray */}
                <div style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  background: '#999',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white'
                }}>
                  <span style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.rating_data.final_score}
                  </span>
                  <span style={{ fontSize: '14px' }}>/100</span>
                </div>
                
                {/* Rating Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '5px', color: '#333' }}>
                    {result.rating_data.rating}
                  </div>
                  <div style={{ fontSize: '16px', color: '#666', lineHeight: '1.5' }}>
                    {result.rating_data.recommendation}
                  </div>
                </div>
              </div>
              
              {/* Risk and Benefit Summary */}
              <div style={{ 
                display: 'flex', 
                gap: '30px', 
                marginTop: '20px', 
                paddingTop: '20px', 
                borderTop: '1px solid #ccc',
                flexWrap: 'wrap'
              }}>
                <div>
                  <span style={{ fontWeight: 'bold', color: '#666' }}>Risky ingredients: </span>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#666' }}>{result.rating_data.risk_ingredients}</span>
                </div>
                <div>
                  <span style={{ fontWeight: 'bold', color: '#666' }}>Beneficial ingredients: </span>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#666' }}>{result.rating_data.beneficial_ingredients}</span>
                </div>
                <div>
                  <span style={{ fontWeight: 'bold', color: '#666' }}>Total ingredients: </span>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#666' }}>{result.rating_data.total_ingredients}</span>
                </div>
              </div>
              
              {/* Risk Details (if any) */}
              {result.rating_data.risk_details && result.rating_data.risk_details.length > 0 && (
                <div style={{ marginTop: '15px' }}>
                  <details>
                    <summary style={{ cursor: 'pointer', color: '#666', fontWeight: 'bold' }}>
                      View risk details ({result.rating_data.risk_details.length})
                    </summary>
                    <div style={{ marginTop: '10px', maxHeight: '200px', overflowY: 'auto' }}>
                      {result.rating_data.risk_details.map((risk, idx) => (
                        <div key={idx} style={{
                          padding: '8px',
                          background: '#f5f5f5',
                          borderRadius: '4px',
                          marginBottom: '5px',
                          fontSize: '13px',
                          color: '#666'
                        }}>
                          <strong>{risk.ingredient}</strong>: {risk.reason}
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
            </div>
          )}
          
          {/* Ingredients Section */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontWeight: 'normal', color: '#333' }}>Ingredients:</h4>
            {result.ingredients_list && result.ingredients_list.length > 0 ? (
              <div>
                <p style={{ 
                  background: '#f5f5f5', 
                  padding: '15px', 
                  borderRadius: '5px',
                  fontFamily: 'monospace',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  color: '#666'
                }}>
                  {result.ingredients_list.join(', ')}
                </p>
                <p style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
                  Total ingredients: {result.ingredients_list.length}
                </p>
              </div>
            ) : result.extracted_text ? (
              <p style={{ 
                background: '#f5f5f5', 
                padding: '15px', 
                borderRadius: '5px',
                fontFamily: 'monospace',
                fontSize: '14px',
                lineHeight: '1.6',
                color: '#666'
              }}>
                {result.extracted_text}
              </p>
            ) : (
              <p style={{ 
                background: '#f5f5f5', 
                padding: '15px', 
                borderRadius: '5px',
                fontStyle: 'italic',
                color: '#999'
              }}>
                No ingredients information available for this product
              </p>
            )}
          </div>

          {safetyData && safetyData.results && (
            <>
              <h4 style={{ fontWeight: 'normal', color: '#333' }}>Safety Analysis:</h4>
              
              <div style={{
                background: '#f5f5f5',
                padding: '15px',
                borderRadius: '5px',
                marginBottom: '20px',
                borderLeft: '4px solid #999'
              }}>
                <h5 style={{ margin: '0 0 5px', fontWeight: 'normal', color: '#666' }}>Overall Safety Rating</h5>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  {safetyData.overall_rating || 'Unknown'}
                </div>
                <div style={{ fontSize: '18px', marginTop: '5px', color: '#666' }}>
                  Score: {safetyData.average_score || '?'}/10
                </div>
              </div>

              <div>
                <h5 style={{ fontWeight: 'normal', color: '#333' }}>Ingredient Breakdown:</h5>
                {safetyData.results.map((item, index) => (
                  <div key={index} style={{
                    border: '1px solid #eee',
                    borderRadius: '5px',
                    padding: '12px',
                    marginBottom: '8px',
                    background: '#fff'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ color: '#333' }}>{item.ingredient}</strong>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{
                          background: '#999',
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
                          fontSize: '12px',
                          color: '#666'
                        }}>
                          {item.rating}
                        </span>
                      </div>
                    </div>
                    {item.hazards && item.hazards.length > 0 && (
                      <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed #eee' }}>
                        <span style={{ color: '#666', fontSize: '13px' }}>
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

      {/* Show message when no results yet */}
      {!lookupSuccess && !loading && !error && searchMode === 'barcode' && (
        <div style={{
          background: '#f5f5f5',
          borderRadius: '5px',
          padding: '30px',
          textAlign: 'center',
          border: '1px dashed #ccc'
        }}>
          <p style={{ color: '#666' }}>Enter a barcode above to look up a product</p>
          <p style={{ fontSize: '13px', color: '#999' }}>Try: 3560070791460</p>
        </div>
      )}
    </div>
  );
};

export default ScannerPage;