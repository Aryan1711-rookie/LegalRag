
export async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers);

  headers.set("ngrok-skip-browser-warning", "true");

  return fetch(url, {
    ...options,
    headers,
    cache: options.cache ?? "no-store",
  });
}
