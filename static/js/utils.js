export function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content ?? '';
}

export async function fetchWithCsrf(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers || {});
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    headers.set('X-CSRFToken', getCsrfToken());
  }
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response;
}

export async function postForm(url, formData) {
  return fetchWithCsrf(url, { method: 'POST', body: formData });
}
