"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STEP_LABELS = ["Signals", "Research", "Email", "Sent"];

export default function Home() {
  const [form, setForm] = useState({
    icp: "",
    company: "",
    email: "",
  });
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(-1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const canSubmit = form.icp.trim() && form.company.trim() && form.email.trim();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || loading) return;

    setLoading(true);
    setResult(null);
    setError("");

    // Animate steps while waiting
    setActiveStep(0);
    const stepTimer1 = setTimeout(() => setActiveStep(1), 2000);
    const stepTimer2 = setTimeout(() => setActiveStep(2), 5000);

    try {
      const res = await fetch(`${API_URL}/run-agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          icp: form.icp,
          company: form.company,
          email: form.email,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const data = await res.json();
      setActiveStep(3);
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Is the backend running?");
      setActiveStep(-1);
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setLoading(false);
    }
  }

  function handleChange(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  function handleReset() {
    setResult(null);
    setError("");
    setActiveStep(-1);
  }

  return (
    <div className="container">
      {/* ── Header ─────────────────────────────────── */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🔥</span>
          <h1>FireReach</h1>
        </div>
        <p className="subtitle">
          Autonomous signal-driven outreach engine
        </p>
      </header>

      {/* ── Form ───────────────────────────────────── */}
      {!result && (
        <form onSubmit={handleSubmit}>
          <div className="form-card">
            <div className="field">
              <label htmlFor="company">Company</label>
              <input
                id="company"
                type="text"
                placeholder="e.g. Snyk"
                value={form.company}
                onChange={handleChange("company")}
                disabled={loading}
              />
            </div>

            <div className="field">
              <label htmlFor="email">Recipient Email</label>
              <input
                id="email"
                type="email"
                placeholder="e.g. founder@snyk.io"
                value={form.email}
                onChange={handleChange("email")}
                disabled={loading}
              />
            </div>

            <div className="field">
              <label htmlFor="icp">Ideal Customer Profile</label>
              <textarea
                id="icp"
                placeholder="e.g. We sell cybersecurity training to Series B startups"
                value={form.icp}
                onChange={handleChange("icp")}
                disabled={loading}
                rows={3}
              />
            </div>
          </div>

          <button
            type="submit"
            className="run-btn"
            disabled={!canSubmit || loading}
          >
            {loading ? "Running agent…" : "Run FireReach Agent"}
          </button>
        </form>
      )}

      {/* ── Step tracker ───────────────────────────── */}
      {(loading || result) && (
        <div className="steps">
          {STEP_LABELS.map((label, i) => (
            <div
              key={label}
              className={`step ${activeStep === i ? "active" : activeStep > i ? "done" : ""
                }`}
            >
              <span className="step-num">
                {activeStep > i ? "✓" : i + 1}
              </span>
              {label}
            </div>
          ))}
        </div>
      )}

      {/* ── Loading ────────────────────────────────── */}
      {loading && (
        <div className="loader">
          <div className="spinner" />
          <p>Agent is working…</p>
        </div>
      )}

      {/* ── Error ──────────────────────────────────── */}
      {error && <div className="error-card">{error}</div>}

      {/* ── Results ────────────────────────────────── */}
      {result && (
        <div className="results">
          {/* Signals */}
          <div className="result-card">
            <div className="result-header">
              <span className="icon">📡</span> Signals Detected
            </div>
            <div className="result-body">
              {result.signals?.length > 0 ? (
                <ul className="signal-list">
                  {result.signals.map((s, i) => (
                    <li key={i} className="signal-item">
                      <span className="signal-dot" />
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="brief-text" style={{ color: "var(--text-muted)" }}>
                  No signals detected.
                </p>
              )}
            </div>
          </div>

          {/* Account Brief */}
          <div className="result-card">
            <div className="result-header">
              <span className="icon">🧠</span> Account Brief
            </div>
            <div className="result-body">
              <p className="brief-text">{result.account_brief}</p>
            </div>
          </div>

          {/* Email */}
          <div className="result-card">
            <div className="result-header">
              <span className="icon">📧</span> Outreach Email
            </div>
            <div className="result-body">
              <p className="email-text">{result.email_content}</p>
            </div>
          </div>

          {/* Reset */}
          <button className="run-btn" onClick={handleReset}>
            ← Run Again
          </button>
        </div>
      )}
    </div>
  );
}
