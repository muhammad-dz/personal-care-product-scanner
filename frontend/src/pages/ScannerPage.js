import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const ScannerPage = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      setFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  });

  const handleScan = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/ocr/extract-text', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(response.data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ success: false, message: 'Scan failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧴 Cosmetic Product Scanner</h1>
      
      <div style={{ margin: '20px 0' }}>
        <div {...getRootProps()} style={{
          border: '2px dashed #ccc',
          borderRadius: '10px',
          padding: '40px',
          textAlign: 'center',
          cursor: 'pointer'
        }}>
          <input {...getInputProps()} />
          <p>Drag & drop product label image here, or click to select</p>
        </div>
      </div>

      {preview && (
        <div style={{ margin: '20px 0' }}>
          <h3>Preview:</h3>
          <img src={preview} alt="Preview" style={{ maxWidth: '300px', maxHeight: '300px' }} />
          <p>{file.name}</p>
        </div>
      )}

      <button 
        onClick={handleScan}
        disabled={!file || loading}
        style={{
          padding: '10px 20px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Scanning...' : '🔍 Scan Product'}
      </button>

      {result && (
        <div style={{ marginTop: '30px', padding: '20px', background: '#f8f9fa', borderRadius: '10px' }}>
          <h3>Scan Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
          
          {result.ingredients && (
            <div>
              <h4>Detected Ingredients:</h4>
              <ul>
                {result.ingredients.map((ing, idx) => (
                  <li key={idx}>{ing}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ScannerPage;
