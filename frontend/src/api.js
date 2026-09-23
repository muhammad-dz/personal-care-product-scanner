import axios from 'axios';

const client = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 20000,
});

// turn FastAPI's {"detail": "..."} into a readable message
function message(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (error.code === 'ECONNABORTED') return 'The request timed out.';
  if (!error.response) return "Can't reach the server. Is the backend running?";
  return 'Something went wrong.';
}

async function call(request) {
  try {
    const res = await request;
    return res.data;
  } catch (error) {
    throw new Error(message(error));
  }
}

export const lookupBarcode = (barcode) => call(client.get(`/api/products/${barcode}`));

export const scanLabel = (file) => {
  const form = new FormData();
  form.append('file', file);
  return call(client.post('/api/scan', form));
};

export const getReviewSummary = () => call(client.get('/api/reviews/summary'));
