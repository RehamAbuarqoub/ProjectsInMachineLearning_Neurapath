import React, { useState } from "react";
import { startTraining, getModelStatus } from "../api/client.js";

export default function Orchestrator(){
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  async function train(){
    setLoading(true);
    try { setStatus(await startTraining({ threshold: 0.35 })); }
    catch(e){ setStatus({ state:"error", message:e.message }); }
    finally{ setLoading(false); }
  }
  async function refresh(){ try{ setStatus(await getModelStatus()); }catch(e){ setStatus({state:"error", message:e.message}); } }

  return (
    <>
      <h1>Orchestrator</h1>
      <div className="small mt8">Train TF-IDF + RandomForest when you have labeled resumes.</div>
      <div className="row mt16">
        <button className="btn" onClick={train} disabled={loading}>{loading ? "Starting…" : "Start Training"}</button>
        <button className="btn" onClick={refresh}>Refresh Status</button>
      </div>
      {status && <pre className="card mt16 small" style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(status,null,2)}</pre>}
    </>
  );
}
