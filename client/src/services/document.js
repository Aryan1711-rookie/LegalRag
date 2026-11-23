
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
import { apiFetch } from "./apiFetch";
// ------------------------------
// Authenticated API request helper
// ------------------------------

async function documentRequest(endpoint, options = {}) {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    throw new Error("You must be logged in to access documents.");
  }

  let response;

  try {
    response = await apiFetch(`${API_BASE_URL}/api/v1/documents${endpoint}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${accessToken}`,
        ...options.headers,
      },
    });
  }  catch (error) {
  if (error.name === "AbortError") {
    throw error;
  }

  throw new Error(
    "Cannot connect to the server. Check whether the backend is running."
  );
}
  

  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    sessionStorage.clear();
    throw new Error("Your session has expired. Please log in again.");
  }

  if (!response.ok) {
    throw new Error(data.detail || "Document request failed.");
  }

  return data;
}

// ------------------------------
// Upload PDF
// ------------------------------

export async function uploadDocument(file, title = "") {
  const formData = new FormData();

  formData.append("file", file);

  if (title.trim()) {
    formData.append("title", title.trim());
  }

  return documentRequest("/upload", {
    method: "POST",
    body: formData,
  });
}

// ------------------------------
// Get documents
// ------------------------------

export async function getDocuments({
  limit = 10,
  offset = 0,
  search,
  status,
} = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  if (search?.trim()) {
    params.append("search", search.trim());
  }

  if (status) {
    params.append("status", status);
  }

  return documentRequest(`/?${params.toString()}`);
}

// ------------------------------
// Get a single document
// ------------------------------

export async function getDocument(documentId, signal) {
  return documentRequest(
    `/${encodeURIComponent(documentId)}`,
    { signal }
  );
}

// ------------------------------
// Delete document
// ------------------------------

export async function deleteDocument(documentId) {
  return documentRequest(`/${encodeURIComponent(documentId)}`, {
    method: "DELETE",
  });
}
