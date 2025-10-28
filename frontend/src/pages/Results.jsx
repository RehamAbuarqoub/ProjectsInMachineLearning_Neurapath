// frontend/src/pages/Results.jsx
import React from "react";
import { useLocation, Link } from "react-router-dom";

function SuitabilityBadge({ score, label }) {
  const bg =
    score >= 80 ? "#19c37d" :
    score >= 60 ? "#58a6ff" :
    score >= 40 ? "#f0ad4e" : "#ff6b6b";
  return (
    <span className="badge" style={{ background: bg, color: "#041017", fontWeight: 800 }}>
      {Math.round(score)}% · {label}
    </span>
  );
}

function fmtPct(v) {
  if (v == null) return "0%";
  return `${Math.round(v * 100)}%`;
}

export default function Results() {
  const { state } = useLocation();
  if (!state) {
    return (
      <div className="card">
        No results to display. <Link to="/">Go back</Link>
      </div>
    );
  }

  const d = state;
  const primary = d.selected_role;
  const others = d.other_recommendations || [];
  const noGood = !!d.no_good_match;

  return (
    <>
      <h1>Results</h1>

      {/* Best match */}
      <div className="card">
        {primary ? (
          <>
            <div className="row" style={{ justifyContent: "space-between", alignItems: "baseline" }}>
              <div>
                <div className="small">Best match</div>
                <h2 style={{ margin: "4px 0" }}>{primary.title}</h2>
                <div className="small">
                  Required coverage: {fmtPct(primary.required_coverage)} •{" "}
                  Nice coverage: {fmtPct(primary.nice_coverage)}
                </div>
              </div>
              <SuitabilityBadge score={primary.score} label={primary.suitability} />
            </div>

            {noGood && (
              <div className="card mt16" style={{ background: "#121922" }}>
                <b>Heads up:</b> your best match is still low. Consider upskilling, then re-apply.
                <div className="mt8">
                  <button className="btn" onClick={() => { /* placeholder */ }}>
                    Recommended Course
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div>No role detected for this resume.</div>
        )}
      </div>

      {/* Skills & Gaps */}
      <div className="row mt16">
        <div className="card" style={{ flex: 1 }}>
          <h3>Top Skills</h3>
          <div className="row mt8">
            {(d.skills || []).slice(0, 18).map((s, i) => {
              const inferred = !s.evidence_offsets?.length;
              return (
                <span
                  key={i}
                  className="badge"
                  title={inferred ? "Semantic/NER inference" : "Direct evidence in resume"}
                >
                  {s.skill} · {(s.score * 100).toFixed(0)}%
                  {inferred ? " (semantic/ner)" : ""}
                </span>
              );
            })}
          </div>
        </div>

        <div className="card" style={{ flex: 1 }}>
          <h3>Skill Gaps (priority)</h3>
          {!d.gaps?.length ? (
            <p className="small">No required-skill gaps for this role.</p>
          ) : (
            // Let <ol> handle numbering; do not print "1. " inside each item.
            <ol className="mt8">
              {[...d.gaps]
                .sort((a, b) => (a.priority ?? 0) - (b.priority ?? 0))
                .map((g, i) => (
                  <li key={i}>{g.skill}</li>
                ))}
            </ol>
          )}
        </div>
      </div>

      {/* Other roles */}
      <div className="card mt16">
        <h3>Other jobs you can apply for</h3>
        {!others.length ? (
          <p className="small">No additional recommendations.</p>
        ) : (
          <div className="row mt8">
            {others.map((r, i) => (
              <div key={i} className="card" style={{ minWidth: 280 }}>
                <div className="row" style={{ justifyContent: "space-between", alignItems: "baseline" }}>
                  <div style={{ fontWeight: 700 }}>{r.title}</div>
                  <SuitabilityBadge score={r.score} label={r.suitability} />
                </div>
                <div className="small mt8">
                  Req. {fmtPct(r.required_coverage)} • Nice {fmtPct(r.nice_coverage)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Critique */}
      <div className="card mt16">
        <b>{d.critique?.summary || "Summary unavailable."}</b>
        <ul className="mt8">
          {(d.critique?.bullets || []).map((b, i) => (
            <li key={i} className="small">
              {b}
            </li>
          ))}
        </ul>
      </div>

      {/* Text preview */}
      <details className="mt16">
        <summary>Text preview (PII redacted)</summary>
        <div className="card mt8" style={{ whiteSpace: "pre-wrap" }}>
          {d.text_preview || ""}
        </div>
      </details>

      <div className="small mt16">
        <Link to="/">← Analyze another</Link>
      </div>
    </>
  );
}
