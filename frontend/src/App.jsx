import React from "react";
import { Routes, Route, NavLink, Navigate, useNavigate } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Upload from "./pages/Upload.jsx";
import Results from "./pages/Results.jsx";
import Services from "./pages/Services.jsx";

function Nav(){
  const nav = useNavigate();
  const authed = !!localStorage.getItem("demoAuth");
  function logout(){
    localStorage.removeItem("demoAuth");
    nav("/", { replace:true });
  }
  return (
    <div style={{borderBottom:"1px solid var(--border)"}}>
      <div className="container row" style={{justifyContent:"space-between"}}>
        <NavLink to="/" style={{fontWeight:700}}>NeuraPath</NavLink>
        <div className="row small">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/services">Services</NavLink>
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/login">Demo Login</NavLink>
          {authed && <button className="btn" onClick={logout}>Logout</button>}
        </div>
      </div>
    </div>
  );
}

function Footer(){
  return (
    <div style={{borderTop:"1px solid var(--border)", marginTop:24}}>
      <div className="container small" style={{display:"flex",justifyContent:"space-between"}}>
        <span>© {new Date().getFullYear()} NeuraPath</span>
        <span>BERT-NER · SBERT · FastAPI · React</span>
      </div>
    </div>
  );
}

export default function App(){
  return (
    <>
      <Nav/>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/login" element={<Login/>}/>
          <Route path="/upload" element={<Upload/>}/>
          <Route path="/results" element={<Results/>}/>
          <Route path="/services" element={<Services/>}/>
          <Route path="*" element={<Navigate to="/" replace/>}/>
        </Routes>
      </div>
      <Footer/>
    </>
  );
}
