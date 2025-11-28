import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Home() {
  const nav = useNavigate();

  return (
    <>
      {/* ===== HERO ===== */}
      <section className="hp-hero">
        <div className="container">
          <div className="hp-hero__grid">
            <div className="hp-hero__copy">
              <div className="badge ghost">NeuraPath · Use Case 1</div>
              <h1 className="hp-hero__title">
                Turn your <span className="accent">resume</span> into a
                job-ready <span className="accent">skill profile</span>
              </h1>
              <p className="muted hp-hero__subtitle">
                Upload your resume, select a role, and instantly see a
                <b> suitability score</b>, <b>skill gaps</b>, and
                <b> alternative jobs</b>. Powered by BERT-NER + SBERT +
                alias mapping.
              </p>

              <div className="row mt16">
                <button className="btn" onClick={() => nav("/login")}>
                  Try the Demo
                </button>
                <a className="btn secondary" href="#usecase">
                  How it works
                </a>
              </div>

              <div className="row hp-hero__kpis">
                <div className="kpi">
                  <div className="kpi-value">~1s</div>
                  <div className="kpi-label">Extraction</div>
                </div>
                <div className="kpi">
                  <div className="kpi-value">Top-5</div>
                  <div className="kpi-label">Job suggestions</div>
                </div>
                <div className="kpi">
                  <div className="kpi-value">Explainable</div>
                  <div className="kpi-label">Coverage + Gaps</div>
                </div>
              </div>
            </div>

            <div className="hp-hero__card">
              <div className="card hp-hero__cardInner">
                <div className="small muted">Pipeline</div>
                <ul className="pipeline">
                  <li>Resume parsing (PDF / DOCX / TXT)</li>
                  <li>Skill extraction (BERT-NER)</li>
                  <li>Catalog mapping (SBERT similarity)</li>
                  <li>Role scoring (required / nice coverage)</li>
                  <li>Gaps + other job recommendations</li>
                </ul>

                <div className="stack mt16">
                  <span className="badge">FastAPI</span>
                  <span className="badge">React + Vite</span>
                  <span className="badge">Transformers</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* subtle background ornaments */}
        <div className="hp-hero__bgDecor" aria-hidden="true" />
      </section>

      {/* ===== VALUE HIGHLIGHTS ===== */}
      <section className="section">
        <div className="container grid-3">
          <div className="card feature">
            <div className="feature__icon ring brand">✓</div>
            <h3>Transparent</h3>
            <p className="muted">
              Evidence-backed skills with coverage metrics so you know exactly
              why you scored what you scored.
            </p>
          </div>
          <div className="card feature">
            <div className="feature__icon ring green">⚙</div>
            <h3>Dataset-Driven</h3>
            <p className="muted">
              The skill catalog is generated from your job dataset, not a
              generic list. Less noise, more relevance.
            </p>
          </div>
          <div className="card feature">
            <div className="feature__icon ring">↗</div>
            <h3>Actionable</h3>
            <p className="muted">
              See gaps with priority. If the match is low, we show the best
              role and a “Recommended Course” button.
            </p>
          </div>
        </div>
      </section>

      {/* ===== USE CASE & FLOW ===== */}
      <section className="section" id="usecase">
        <div className="container grid-2">
          <div>
            <h2>Use Case 1 — Skill Gap Analysis</h2>
            <p className="muted">
              We convert unstructured resumes into structured skill profiles
              and compare them to role templates derived from your dataset of
              jobs (required + nice-to-have).
            </p>
            <ul className="bullets">
              <li>Structured extraction of hard skills</li>
              <li>Suitability score + label</li>
              <li>Gaps with priority + advice</li>
              <li>Top alternative roles you can apply for</li>
            </ul>
            <div className="row mt16">
              <Link to="/login" className="btn">
                Start Demo
              </Link>
              <Link to="/services" className="btn ghost">
                API Catalog
              </Link>
            </div>
          </div>

          <div className="card timeline">
            <h3>How it works</h3>
            <ol>
              <li>
                <span className="tl-dot" />
                <div>
                  <b>Upload resume</b> — PDF, DOCX, or TXT.
                </div>
              </li>
              <li>
                <span className="tl-dot" />
                <div>
                  <b>Extract skills</b> — BERT-NER + semantic mapping to your
                  catalog.
                </div>
              </li>
              <li>
                <span className="tl-dot" />
                <div>
                  <b>Score vs. role</b> — required/nice coverage with small
                  evidence bonus.
                </div>
              </li>
              <li>
                <span className="tl-dot" />
                <div>
                  <b>See gaps & suggestions</b> — and explore other roles.
                </div>
              </li>
            </ol>
          </div>
        </div>
      </section>

      {/* ===== TEAM ===== */}
      <section className="section">
        <div className="container">
          <h2>The Team</h2>
          <div className="grid-3 mt16">
            <div className="card team">
              <div className="avatar">A</div>
              <div>
                <div className="team-name">A. Lead</div>
                <div className="small muted">ML · Skill Extraction</div>
              </div>
            </div>
            <div className="card team">
              <div className="avatar">B</div>
              <div>
                <div className="team-name">B. Builder</div>
                <div className="small muted">Backend · FastAPI</div>
              </div>
            </div>
            <div className="card team">
              <div className="avatar">C</div>
              <div>
                <div className="team-name">C. Creator</div>
                <div className="small muted">Frontend · React</div>
              </div>
            </div>
          </div>
          <p className="small muted mt8">
            This project is a focused research prototype for NeuraPath.
          </p>
        </div>
      </section>

      {/* ===== CTA ===== */}
      <section className="section">
        <div className="container">
          <div className="card cta">
            <div>
              <h3>Ready to check your match?</h3>
              <p className="muted">
                Use the demo credentials (<b>user</b> / <b>pass</b>) to try the
                end-to-end flow.
              </p>
            </div>
            <Link to="/login" className="btn">
              Demo Login
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
