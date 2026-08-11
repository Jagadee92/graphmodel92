const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("talentgraph_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `Request failed: ${response.status}`;

    try {
      const data = await response.json();
      errorMessage =
        data.detail || data.message || errorMessage;
    } catch {
      // Response wasn't JSON
    }

    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  async me() {
    return request("/auth/me");
  },

  async login(data) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async register(data) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async jobs() {
    return request("/jobs");
  },

  async recommendations() {
    return request("/recommendations");
  },

  async applications() {
    return request("/applications");
  },
};