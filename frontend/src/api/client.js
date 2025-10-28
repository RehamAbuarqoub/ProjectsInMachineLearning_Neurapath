const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function listRoles(){ return (await fetch(`${API}/roles`)).json(); }

export async function uploadResume(file, roleId){
  const fd = new FormData();
  fd.append("file", file);
  if (roleId) fd.append("role_id", roleId);
  const r = await fetch(`${API}/resumes`, { method: "POST", body: fd });
  if (!r.ok) throw new Error(`Upload failed: ${r.status}`);
  return r.json();
}

export async function listServices(){
  const r = await fetch(`${API}/services`);
  if (!r.ok) throw new Error(`Failed to fetch services: ${r.status}`);
  return r.json();
}
