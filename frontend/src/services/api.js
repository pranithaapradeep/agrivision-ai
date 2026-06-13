import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 60000,
});

// Attach token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('agrivision_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('agrivision_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  login:    (email, password) => {
    const form = new FormData();
    form.append('username', email);
    form.append('password', password);
    return api.post('/auth/token', form);
  },
  register: (data) => api.post('/auth/register', data),
  me:       ()     => api.get('/auth/me'),
};

export const cropAPI = {
  analyze:  (formData)   => api.post('/crop/analyze', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  list:     ()           => api.get('/crop/analyses'),
  get:      (id)         => api.get(`/crop/${id}`),
};

export const soilAPI = {
  analyze:  (formData) => api.post('/soil/analyze', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  demoMap:  ()         => api.get('/soil/demo-map'),
};

export const pestAPI = {
  assess:      (data) => api.post('/pest/assess', data),
  demoHeatmap: ()     => api.get('/pest/demo-heatmap'),
};

export const forecastAPI = {
  predict: (data) => api.post('/forecast/predict', data),
  demo:    ()     => api.get('/forecast/demo'),
};

export const reportsAPI = {
  generate: (data) => api.post('/reports/generate', data, { responseType: 'blob' }),
};

export default api;
