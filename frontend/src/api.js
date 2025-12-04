// src/api.js
import { API_BASE_URL } from "./config";

export function getToken() {
  return localStorage.getItem("token");
}

export async function authFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  return res;
}

// NEW: store current user (from /auth/me) in localStorage
export function setCurrentUser(user) {
  if (!user) {
    localStorage.removeItem("currentUser");
  } else {
    localStorage.setItem("currentUser", JSON.stringify(user));
  }
}

export function getCurrentUser() {
  const raw = localStorage.getItem("currentUser");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}