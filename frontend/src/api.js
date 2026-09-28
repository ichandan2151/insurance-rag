const API = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    ...options,
  });
  if (res.status === 401) {
    if (!window.location.pathname.startsWith('/login')) {
      window.location.href = '/login';
    }
    throw new Error('Authentication required');
  }
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

export function login(username, password) {
  return request('/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
}

export function logout() {
  return request('/logout/', { method: 'POST' });
}

export function getMe() {
  return request('/me/');
}

export function getStats() {
  return request('/stats/');
}

export function getDocuments() {
  return request('/documents/');
}

export function getDocument(id) {
  return request(`/documents/${id}/`);
}

export function uploadDocument(formData) {
  return fetch(`${API}/documents/upload/`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  }).then(async (res) => {
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Upload failed');
    return data;
  });
}

export function queryRAG(question, topK = 8) {
  return request('/query/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  });
}

export function getAuditLogs() {
  return request('/audit/');
}
