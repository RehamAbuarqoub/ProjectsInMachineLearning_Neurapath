// dev/frontend/src/pages/Upload.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listRoles, uploadResume } from "../api/client.js";

export default function Upload(){
  const nav = useNavigate();
  const [roles,setRoles] = useState([]);
  const [roleId,setRoleId] = useState("");
  const [file,setFile] = useState(null);
  const [err,setErr] = useState("");
  const [loading,setLoading] = useState(false);
  const [loadingRoles,setLoadingRoles] = useState(true);

  async function loadRoles(){
    setLoadingRoles(true);
    setErr("");
    try{
      const r = await listRoles();
      setRoles(r || []);
      setRoleId(r?.[0]?.role_id || "");
    }catch(e){
      setErr("Failed to load roles. Check API is running and /roles returns data.");
    }finally{
      setLoadingRoles(false);
    }
  }

  useEffect(()=>{
    if(!localStorage.getItem("demoAuth")){
      nav("/login",{replace:true});
      return;
    }
    loadRoles();
  },[nav]);

  async function analyze(){
    setErr("");
    if(!file) return setErr("Please choose a .txt resume for this demo.");
    if(!roleId) return setErr("Please select a job title.");
    setLoading(true);
    try{
      const data = await uploadResume(file, roleId);
      nav("/results",{state:data});
    }catch(e){
      setErr(e.message || "Analyze failed.");
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Upload Resume & Select Job</h2>

      {/* Roles state */}
      {loadingRoles ? (
        <div className="small muted" style={{marginTop:8}}>Loading job titles…</div>
      ) : roles.length === 0 ? (
        <div style={{marginTop:8}}>
          <div className="small" style={{color:"#ff6b6b"}}>
            No job titles available. Seed <code>role_templates.json</code> in <code>dev/backend/app/data/</code> and ensure the API is running.
          </div>
          <div className="row" style={{marginTop:8}}>
            <button className="btn" onClick={loadRoles}>Retry</button>
          </div>
        </div>
      ) : null}

      {/* Inputs */}
      <div className="row" style={{marginTop:12}}>
        <input
          type="file"
          className="input"
          accept=".txt,.pdf,.docx"
          onChange={e=>setFile(e.target.files?.[0] ?? null)}
        />

        <select
          className="input"
          value={roleId}
          onChange={e=>setRoleId(e.target.value)}
          disabled={loadingRoles || roles.length===0}
        >
          {roles.length===0 && <option value="">No roles found</option>}
          {roles.map(r => (
            <option key={r.role_id} value={r.role_id}>
              {r.title}
            </option>
          ))}
        </select>

        <button
          className="btn"
          onClick={analyze}
          disabled={loading || loadingRoles || !roleId || !file}
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>

      {/* Hints / Errors */}
      {file && <div className="small muted" style={{marginTop:8}}>Selected: {file.name}</div>}
      {!roleId && roles.length>0 && (
        <div className="small muted" style={{marginTop:8}}>Choose a job title to analyze against.</div>
      )}
      {err && <div className="small" style={{color:"#ff6b6b",marginTop:8}}>{err}</div>}
    </div>
  );
}
