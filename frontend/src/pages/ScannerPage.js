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
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
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
    if (!file) { alert('Select an image'); return; }
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const ocrRes = await axios.post('http://localhost:8000/api/ocr/extract-text', formData);
      setResult(ocrRes.data);
      setLookupSuccess(true);
      if (ocrRes.data.ingredients?.length) {
        const safetyRes = await axios.post('http://localhost:8000/api/ocr/batch-check', {
          ingredients: ocrRes.data.ingredients
        });
        setSafetyData(safetyRes.data);
      }
    } catch (error) {
      setError('Scan failed');
      setLookupSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const handleBarcodeLookup = async () => {
    if (!barcode) { alert('Enter barcode'); return; }
    setLoading(true);
    setResult(null);
    setSafetyData(null);
    setError(null);
    setLookupSuccess(false);
    try {
      const res = await axios.get(`http://localhost:8000/api/beauty/lookup/${barcode}`);
      if (res.data.success) {
        setLookupSuccess(true);
        setResult(res.data);
        if (res.data.ingredients_list?.length) {
          const safetyRes = await axios.post('http://localhost:8000/api/ocr/batch-check', {
            ingredients: res.data.ingredients_list
          });
          setSafetyData({
            ...safetyRes.data,
            product_info: {
              name: res.data.product_name,
              brands: res.data.brands,
              source: res.data.source
            }
          });
        } else {
          setSafetyData({
            product_info: {
              name: res.data.product_name,
              brands: res.data.brands,
              source: res.data.source
            }
          });
        }
      } else {
        setError('Product not found');
      }
    } catch (error) {
      setError('Lookup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Product Scanner</h2>
      
      <div>
        <button onClick={() => setSearchMode('image')}>
          Scan Image
        </button>
        <button onClick={() => setSearchMode('barcode')}>
          Lookup Barcode
        </button>
      </div>

      {error && <div><strong>{error}</strong></div>}

      {searchMode === 'image' && (
        <div>
          <div {...getRootProps()}>
            <input {...getInputProps()} />
            <p>Drag and drop product label image here or click to browse</p>
          </div>

          {preview && (
            <div>
              <h4>Preview:</h4>
              <img src={preview} alt="Preview" style={{ maxWidth: '200px' }} />
              <p>{file?.name}</p>
            </div>
          )}

          <button onClick={handleImageScan} disabled={!file || loading}>
            {loading ? 'Processing...' : 'Scan Product'}
          </button>
        </div>
      )}

      {searchMode === 'barcode' && (
        <div>
          <h3>Enter Barcode</h3>
          <p>Look up product from Open Beauty Facts database</p>
          
          <div>
            <input
              type="text"
              placeholder="e.g., 3560070791460"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              onKeyPress={(e) => { if (e.key === 'Enter') handleBarcodeLookup(); }}
            />
            <button onClick={handleBarcodeLookup} disabled={!barcode || loading}>
              {loading ? 'Looking up...' : 'Lookup'}
            </button>
          </div>
          
          <p>Data provided by Open Beauty Facts</p>
        </div>
      )}

      {lookupSuccess && result && (
        <div>
          <h3>Product Found</h3>
          
          {safetyData?.product_info && (
            <div>
              <h4>{safetyData.product_info.name}</h4>
              <p><strong>Brand:</strong> {safetyData.product_info.brands || 'Unknown'}</p>
              <p><strong>Source:</strong> {safetyData.product_info.source}</p>
            </div>
          )}
          
          {result.rating_data && (
            <div>
              <h4>AI Safety Rating</h4>
              
              <div>
                <div>
                  <span>{result.rating_data.final_score}</span>
                  <span>/100</span>
                </div>
                
                <div>
                  <div>{result.rating_data.rating}</div>
                  <div>{result.rating_data.recommendation}</div>
                </div>
              </div>
              
              <div>
                <div><span>Risky ingredients:</span> {result.rating_data.risk_ingredients}</div>
                <div><span>Beneficial ingredients:</span> {result.rating_data.beneficial_ingredients}</div>
                <div><span>Total ingredients:</span> {result.rating_data.total_ingredients}</div>
              </div>
              
              {result.rating_data.risk_details?.length > 0 && (
                <div>
                  <details>
                    <summary>View risk details ({result.rating_data.risk_details.length})</summary>
                    <div>
                      {result.rating_data.risk_details.map((risk, idx) => (
                        <div key={idx}>
                          <strong>{risk.ingredient}</strong>: {risk.reason}
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
            </div>
          )}
          
          <div>
            <h4>Ingredients:</h4>
            {result.ingredients_list?.length > 0 ? (
              <div>
                <p>{result.ingredients_list.join(', ')}</p>
                <p>Total ingredients: {result.ingredients_list.length}</p>
              </div>
            ) : result.extracted_text ? (
              <p>{result.extracted_text}</p>
            ) : (
              <p>No ingredients information available</p>
            )}
          </div>

          {safetyData?.results && (
            <>
              <h4>Safety Analysis:</h4>
              
              <div>
                <h5>Overall Safety Rating</h5>
                <div>{safetyData.overall_rating || 'Unknown'}</div>
                <div>Score: {safetyData.average_score || '?'}/10</div>
              </div>

              <div>
                <h5>Ingredient Breakdown:</h5>
                {safetyData.results.map((item, index) => (
                  <div key={index}>
                    <div>
                      <strong>{item.ingredient}</strong>
                      <div>
                        <span>Score: {item.safety_score}/10</span>
                        <span>{item.rating}</span>
                      </div>
                    </div>
                    {item.hazards?.length > 0 && (
                      <div>Hazards: {item.hazards.join(', ')}</div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {!lookupSuccess && !loading && !error && searchMode === 'barcode' && (
        <div>
          <p>Enter a barcode above to look up a product</p>
          <p>Try: 3560070791460</p>
        </div>
      )}
    </div>
  );
};

export default ScannerPage;