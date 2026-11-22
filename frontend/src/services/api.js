/**
 * Cliente de API nativo utilizando a Fetch API (Axios estritamente proibido).
 * Gerencia tokens SimpleJWT e injeção de cabeçalhos de autenticação.
 *
 * BASE_URL:
 *   - Produção/Deploy via Django:  usa URL RELATIVA '/api/v1'
 *     → mesma origin, sem CORS, funciona em qualquer host/porta.
 *   - Dev com Vite separado (npm run dev): define VITE_API_URL=http://localhost:8000/api/v1
 *     no arquivo frontend/.env.local → o Vite injeta em build time.
 */
const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const token = localStorage.getItem('access_token');
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Se o token expirou (401), tenta refresh
  if (response.status === 401 && !options._retry && localStorage.getItem('refresh_token')) {
    const refreshed = await refreshToken();
    if (refreshed) {
      return request(endpoint, { ...options, _retry: true });
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      throw new Error('Sessão expirada. Faça login novamente.');
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.detail || errorData.message || `Erro HTTP ${response.status}`);
    error.status = response.status;
    error.data = errorData;
    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  try {
    const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export const api = {
  get: (endpoint, options = {}) => request(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options = {}) => request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint, body, options = {}) => request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: (endpoint, body, options = {}) => request(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' }),
};
