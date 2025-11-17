// dev/frontend/src/api/client.js

// Use VITE_API_BASE if defined, otherwise default to local FastAPI backend
// Example .env value:
// VITE_API_BASE="http://127.0.0.1:8000"
const API = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// ---- Roles ----
export async function listRoles() {
  const res = await fetch(`${API}/roles`);

  if (!res.ok) {
    console.error("Failed to fetch roles:", res.status);
    // Return an empty array so roles.map(...) in Upload.jsx never crashes
    return [];
  }

  const data = await res.json();

  // Backend might return a plain list [...] or { roles: [...] }
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.roles)) return data.roles;

  return [];
}

// ---- Upload resume ----
export async function uploadResume(file, roleId) {
  const fd = new FormData();
  fd.append("file", file);
  if (roleId) fd.append("role_id", roleId);

  const res = await fetch(`${API}/resumes`, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    console.error("Upload failed:", res.status);
    throw new Error(`Upload failed: ${res.status}`);
  }

  return res.json();
}

// ---- Services ----
export async function listServices() {
  const res = await fetch(`${API}/services`);

  if (!res.ok) {
    console.error("Failed to fetch services:", res.status);
    return [];
  }

  const data = await res.json();

  // Same idea: accept either [...] or { services: [...] }
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.services)) return data.services;

  return [];
}
