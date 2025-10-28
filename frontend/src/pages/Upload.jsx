import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listRoles, uploadResume } from "../api/client.js";

export default function Upload(){
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const nav = useNavigate();

  useEffect(()=>{
    listRoles().then(r=>{
      setRoles(r||[]);
      if (r?.length) setRole(r[0].role_id);
    }).catch(()=>setRoles([]));
  }, []);

  async function analyze(){
    setError("");
    if (!file) return setError("Choose a resume (.pdf, .docx or .txt).");
    setLoading(true);
    try {
      const data = await uploadResume(file, role);
      nav("/results", { state: data });
    } catch(e){ setError(e.message); }
    finally { setLoading(false); }
  }

  return (
    <>
      <h1>Upload Resume</h1>
      <div className="card mt16">
        <div className="row">
          <input type="file" className="input" accept=".pdf,.docx,.txt" onChange={e=>setFile(e.target.files?.[0]??null)} />
          <select className="input" value={role} onChange={e=>setRole(e.target.value)}>
            {roles.map(r=> <option key={r.role_id} value={r.role_id}>{r.title}</option>)}
          </select>
          <button className="btn" onClick={analyze} disabled={loading}>{loading ? "Analyzing…" : "Analyze"}</button>
        </div>
        {file && <div className="small mt8">Selected: {file.name}</div>}
        {error && <div className="small mt8" style={{color:"#ff6b6b"}}>{error}</div>}
      </div>
      <div className="small mt16">We’ll compute match % vs the chosen job, show gaps, and recommend other jobs.</div>
    </>
  );
}
