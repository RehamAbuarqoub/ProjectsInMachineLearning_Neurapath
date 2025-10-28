import React, { useEffect, useState } from "react";
import { listServices } from "../api/client.js";

export default function Services(){
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(()=>{
    listServices().then(setRows).catch(e=>setErr(e.message));
  }, []);

  return (
    <>
      <h1>Service Catalog</h1>
      {err && <div className="small" style={{color:"#ff6b6b"}}>{err}</div>}
      {!rows.length ? <div className="card small mt16">No services found. Ensure your CSV/XLSX exists in backend/app/data.</div> :
        <div className="card mt16" style={{overflowX:"auto"}}>
          <table style={{width:"100%", borderCollapse:"collapse"}}>
            <thead>
              <tr className="small" style={{textAlign:"left"}}>
                <th>Service</th><th>Method</th><th>Path</th><th>Summary</th><th>Owner</th><th>Version</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r,i)=>(
                <tr key={i} className="small" style={{borderTop:"1px solid var(--border)"}}>
                  <td>{r.service_name}</td>
                  <td>{r.method}</td>
                  <td>{r.path}</td>
                  <td>{r.summary ?? ""}</td>
                  <td>{r.owner ?? ""}</td>
                  <td>{r.version ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>}
    </>
  );
}
