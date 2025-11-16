import React, { useState } from "react";
import { uploadResume } from "../api/client.js";

export default function DevRun(){
  const [text, setText] = useState(
`Jane Doe
Email: jane@example.com | 555-555-1212
Skills: Python, SQL, Pandas, NumPy, Matplotlib, Communication, Git
Built dashboards and data visualization in Python.`
  );
  const [json, setJson] = useState(null);
  const [loading, setLoading] = useState(false);

  async function run(){
    setLoading(true);
    const blob = new Blob([text], { type: "text/plain" });
    const file = new File([blob], "dev-run.txt", { type: "text/plain" });
    try{ setJson(await uploadResume(file, "")); }
    catch(e){ setJson({ error: e.message }); }
    finally{ setLoading(false); }
  }

  return (
    <>
      <h1>Dev Run</h1>
      <div className="card mt16">
        <textarea rows={10} className="input" style={{width:"100%"}} value={text} onChange={e=>setText(e.target.value)} />
        <div className="row mt16" style={{justifyContent:"space-between"}}>
          <span className="small">Send a quick snippet to /resumes.</span>
          <button className="btn" onClick={run} disabled={loading}>{loading ? "Running…" : "Run"}</button>
        </div>
      </div>
      {json && <pre className="card mt16 small" style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(json,null,2)}</pre>}
    </>
  );
}
