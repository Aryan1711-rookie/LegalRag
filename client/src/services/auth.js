
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
// ------------------------------
// API request helper
// ------------------------------

async function authRequest(endpoint, payload) {
  // #const {login, isLoading} = useAuth();
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/auth/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error(
      "Cannot connect to the server. Check whether the backend is running."
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Authentication failed."
    );
  }

  return data;
}

// ------------------------------
// Session management
// ------------------------------

function saveSession(data) {
  if (data.access_token) {
    sessionStorage.setItem("access_token", data.access_token);
  }

  if (data.refresh_token) {
    sessionStorage.setItem("refresh_token", data.refresh_token);
  }

  if (data.user_id) {
    sessionStorage.setItem("user_id", data.user_id);
  }

  if (data.email) {
    sessionStorage.setItem("user_email", data.email);
  }
}

export function logoutUser() {
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
  sessionStorage.removeItem("user_id");
  sessionStorage.removeItem("user_email");
}

// ------------------------------
// Authentication
// ------------------------------

export async function loginUser(credentials) {
  const data = await authRequest("login", credentials);

  saveSession(data);

  return data;
}

export async function registerUser(credentials) {
  const data = await authRequest("register", credentials);

  saveSession(data);

  return data;
}

// ------------------------------
// Get authenticated user
// ------------------------------

export async function getCurrentUser() {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    return null;
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    throw new Error(
      "Cannot connect to the server. Check whether the backend is running."
    );
  }

  const data = await response.json().catch(() => ({}));

  // Invalid or expired access token
  if (response.status === 401) {
    logoutUser();
    return null;
  }

  if (!response.ok) {
    throw new Error(
      data.detail || "Unable to retrieve authenticated user."
    );
  }

  return data;
}
