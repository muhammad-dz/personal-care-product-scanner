import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';

import { lookupBarcode, scanLabel } from '../api';
import RatingCard from '../components/RatingCard';

function BarcodeForm({ onResult, onError, busy, setBusy }) {
  const [barcode, setBarcode] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      onResult(await lookupBarcode(barcode.trim()));
    } catch (err) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="row" onSubmit={submit}>
      <input
        inputMode="numeric"
        placeholder="Barcode, e.g. 3600523614417"
        value={barcode}
        onChange={(e) => setBarcode(e.target.value)}
      />
      <button type="submit" disabled={busy || !/^\d{8,14}$/.test(barcode.trim())}>
        {busy ? 'Looking up…' : 'Look up'}
      </button>
    </form>
  );
}

function PhotoForm({ onResult, onError, busy, setBusy }) {
  const [file, setFile] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    onDrop: (files) => setFile(files[0] || null),
  });

  const submit = async () => {
    setBusy(true);
    try {
      onResult(await scanLabel(file));
    } catch (err) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div {...getRootProps({ className: `dropzone ${isDragActive ? 'active' : ''}` })}>
        <input {...getInputProps()} />
        {file ? <p>{file.name}</p> : <p>Drop a photo of the ingredient list here, or click to choose one</p>}
      </div>
      <button onClick={submit} disabled={busy || !file}>
        {busy ? 'Reading label…' : 'Scan label'}
      </button>
    </div>
  );
}

export default function ScannerPage() {
  const [mode, setMode] = useState('barcode');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const handlers = {
    busy,
    setBusy,
    onResult: (data) => { setResult(data); setError(''); },
    onError: (msg) => { setResult(null); setError(msg); },
  };

  const switchMode = (next) => {
    setMode(next);
    setResult(null);
    setError('');
  };

  return (
    <div>
      <div className="tabs">
        <button className={mode === 'barcode' ? 'tab active' : 'tab'} onClick={() => switchMode('barcode')}>
          Barcode
        </button>
        <button className={mode === 'photo' ? 'tab active' : 'tab'} onClick={() => switchMode('photo')}>
          Label photo
        </button>
      </div>

      <section className="card">
        {mode === 'barcode' ? <BarcodeForm {...handlers} /> : <PhotoForm {...handlers} />}
        {mode === 'barcode' && <p className="muted small">Product data from Open Beauty Facts.</p>}
      </section>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          {result.product_name && (
            <section className="card product">
              {result.image_url && <img src={result.image_url} alt="" />}
              <div>
                <h2>{result.product_name}</h2>
                {result.brands && <p className="muted">{result.brands}</p>}
                <p className="muted small">Source: {result.source}</p>
              </div>
            </section>
          )}

          {result.rating
            ? <RatingCard rating={result.rating} />
            : <p className="muted">This product has no ingredient list in the database yet.</p>}
        </>
      )}
    </div>
  );
}
