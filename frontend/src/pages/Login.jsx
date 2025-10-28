import React, { useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";

export default function Login(){
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState("");
  const nav = useNavigate();
  const loc = useLocation();
  const from = loc.state?.from || "/";

  function submit(e){
    e.preventDefault();
    if (user === "user" && pass === "pass"){
      localStorage.setItem("demoAuth", "1");
      nav("/upload", { replace:true });
    } else {
      setErr("Invalid credentials. Try user / pass");
    }
  }

  return (
    <>
      <h1>Demo Login</h1>
      <div className="card" style={{maxWidth:420}}>
        <form onSubmit={submit} className="column">
          <label className="small muted">Username</label>
          <input className="input" value={user} onChange={e=>setUser(e.target.value)} placeholder="user" />
          <label className="small muted mt8">Password</label>
          <input className="input" type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="pass" />
          {err && <div className="small mt8" style={{color:"#ff6b6b"}}>{err}</div>}
          <button className="btn mt16" type="submit">Sign in</button>
          <div className="small muted mt8">Hint: user / pass</div>
        </form>
      </div>
      <div className="small mt16">Back to <Link to="/">Home</Link></div>
    </>
  );
}
