import { useState } from "react";
import "./App.css";

function App() {
  const [news, setNews] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showEvidence, setShowEvidence] = useState(false);
  const [openSources, setOpenSources] = useState({});

  const verifyNews = async () => {
    if (!news.trim()) {
      setError("Please enter some news or claim first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setShowEvidence(false);
    setOpenSources({});

    try {
      const response = await fetch("http://127.0.0.1:5000/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          news: news.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Verification failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to TruthShield AI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setNews("");
    setResult(null);
    setError("");
    setShowEvidence(false);
    setOpenSources({});
  };

  const handleKeyDown = (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      verifyNews();
    }
  };

  const getResultClass = () => {
    if (result?.result === "REAL") return "real";
    if (result?.result === "FAKE") return "fake";
    return "uncertain";
  };

  const getResultIcon = () => {
    if (result?.result === "REAL") return "✓";
    if (result?.result === "FAKE") return "!";
    return "?";
  };

  const getDomain = (url) => {
    if (!url) return "Source";

    try {
      return new URL(url).hostname.replace("www.", "");
    } catch {
      return "Source";
    }
  };

  const getEvidenceText = () => {
    if (!result?.evidence) return "";

    if (typeof result.evidence === "string") {
      return result.evidence;
    }

    return result.evidence.content || "";
  };

  const getEvidenceTitle = () => {
    if (!result?.evidence) return "Best Evidence";

    if (typeof result.evidence === "object") {
      return result.evidence.title || "Best Evidence";
    }

    return "Best Evidence";
  };

  const getEvidenceUrl = () => {
    if (!result?.evidence || typeof result.evidence !== "object") {
      return "";
    }

    return result.evidence.url || "";
  };

  const toggleSource = (index) => {
    setOpenSources((previous) => ({
      ...previous,
      [index]: !previous[index],
    }));
  };

  const sourceCount =
    result?.sources?.length ||
    result?.web_sources ||
    0;

  return (
    <div className="app">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            TS
          </div>

          <div>
            <div className="brand-name">
              TruthShield <span>AI</span>
            </div>
            <div className="brand-subtitle">
              Intelligent News Verification
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          AI SYSTEM ONLINE
        </div>
      </header>

      <main className="main-container">
        <section className="hero-section">
          <div className="hero-badge">
            <span>✦</span>
            AI-POWERED VERIFICATION
          </div>

          <h1>
            Know what's
            <span> true.</span>
          </h1>

          <p className="hero-description">
            Verify news and claims using Artificial Immune
            System analysis, trusted web evidence, and
            Natural Language Inference.
          </p>
        </section>

        <section className="verification-card">
          <div className="card-heading">
            <div>
              <h2>Verify a News Claim</h2>
              <p>
                Paste a news article, headline, or claim below.
              </p>
            </div>

            <div className="secure-badge">
              <span>●</span>
              SECURE
            </div>
          </div>

          <div className="input-wrapper">
            <textarea
              value={news}
              onChange={(event) => setNews(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Example: India won the 2024 T20 World Cup."
              maxLength={5000}
            />

            <div className="input-footer">
              <span>
                {news.length} / 5000 characters
              </span>

              <span className="shortcut">
                Ctrl + Enter to verify
              </span>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">!</span>
              <span>{error}</span>
            </div>
          )}

          <div className="action-row">
            <button
              className="clear-button"
              onClick={clearAll}
              disabled={loading || (!news && !result)}
            >
              Clear
            </button>

            <button
              className="verify-button"
              onClick={verifyNews}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>
                  Verify Claim
                  <span className="button-arrow">→</span>
                </>
              )}
            </button>
          </div>
        </section>

        {loading && (
          <section className="loading-card">
            <div className="loading-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div>
              <strong>Analyzing your claim</strong>
              <p>
                Checking AI patterns, web evidence and semantic
                relationships...
              </p>
            </div>
          </section>
        )}

        {result && !loading && (
          <section className="results-section">
            <div className="section-label">
              VERIFICATION REPORT
            </div>

            <div className={`result-banner ${getResultClass()}`}>
              <div className="result-icon">
                {getResultIcon()}
              </div>

              <div className="result-main">
                <span className="result-label">
                  VERIFICATION RESULT
                </span>

                <h2>{result.result || "UNCERTAIN"}</h2>

                <p>
                  {result.result === "REAL" &&
                    "The available evidence supports this claim."}

                  {result.result === "FAKE" &&
                    "The available evidence contradicts this claim."}

                  {(!result.result ||
                    result.result === "UNCERTAIN") &&
                    "The available evidence is not sufficient for a clear conclusion."}
                </p>
              </div>

              <div className="relationship-pill">
                {result.relationship || "UNCERTAIN"}
              </div>
            </div>

            <div className="score-grid">
              <div className="score-card">
                <div className="score-top">
                  <span className="score-icon ais-icon">
                    A
                  </span>
                  <span className="score-name">
                    AIS Analysis
                  </span>
                </div>

                <div className="score-value">
                  {Number(result.ais_score || 0).toFixed(2)}
                  <small>%</small>
                </div>

                <div className="score-bar">
                  <div
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, Number(result.ais_score || 0))
                      )}%`,
                    }}
                  ></div>
                </div>

                <p>Pattern-based immune detection</p>
              </div>

              <div className="score-card">
                <div className="score-top">
                  <span className="score-icon web-icon">
                    W
                  </span>
                  <span className="score-name">
                    Web Evidence
                  </span>
                </div>

                <div className="score-value">
                  {Number(result.web_score || 0).toFixed(2)}
                  <small>%</small>
                </div>

                <div className="score-bar">
                  <div
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, Number(result.web_score || 0))
                      )}%`,
                    }}
                  ></div>
                </div>

                <p>
                  {sourceCount} trusted source
                  {Number(sourceCount) === 1 ? "" : "s"} found
                </p>
              </div>

              <div className="score-card">
                <div className="score-top">
                  <span className="score-icon nlp-icon">
                    N
                  </span>
                  <span className="score-name">
                    NLP Analysis
                  </span>
                </div>

                <div className="score-value">
                  {Number(result.nlp_score || 0).toFixed(2)}
                  <small>%</small>
                </div>

                <div className="score-bar">
                  <div
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, Number(result.nlp_score || 0))
                      )}%`,
                    }}
                  ></div>
                </div>

                <p>Semantic evidence relationship</p>
              </div>
            </div>

            <div className="analysis-card">
              <div className="analysis-heading">
                <div>
                  <span className="mini-label">
                    AI REASONING
                  </span>
                  <h3>Why did TruthShield decide this?</h3>
                </div>

                <div className="relationship-tag">
                  {result.relationship || "UNCERTAIN"}
                </div>
              </div>

              <p className="reason-text">
                {result.reason ||
                  "No detailed reasoning was returned."}
              </p>
            </div>

            {getEvidenceText() && (
              <div className="evidence-card">
                <div className="evidence-heading">
                  <div className="evidence-title-area">
                    <div className="evidence-icon">
                      ◈
                    </div>

                    <div>
                      <span className="mini-label">
                        BEST MATCHED EVIDENCE
                      </span>

                      <h3>{getEvidenceTitle()}</h3>
                    </div>
                  </div>

                  <button
                    className="view-button"
                    onClick={() =>
                      setShowEvidence(!showEvidence)
                    }
                  >
                    {showEvidence
                      ? "Hide Evidence"
                      : "View Evidence"}
                    <span>
                      {showEvidence ? "↑" : "↓"}
                    </span>
                  </button>
                </div>

                {showEvidence && (
                  <div className="evidence-content">
                    <p>{getEvidenceText()}</p>

                    {getEvidenceUrl() && (
                      <a
                        className="source-link"
                        href={getEvidenceUrl()}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Open Evidence Source
                        <span>↗</span>
                      </a>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="sources-section">
              <div className="sources-header">
                <div>
                  <span className="mini-label">
                    WEB VERIFICATION
                  </span>

                  <h3>Trusted Sources</h3>

                  <p>
                    Evidence collected from relevant trusted
                    sources.
                  </p>
                </div>

                <div className="source-count">
                  {sourceCount}
                  <span>
                    source
                    {Number(sourceCount) === 1
                      ? ""
                      : "s"}
                  </span>
                </div>
              </div>

              {result.sources &&
              result.sources.length > 0 ? (
                <div className="source-list">
                  {result.sources.map(
                    (source, index) => (
                      <div
                        className="source-card"
                        key={`${source.url || index}-${index}`}
                      >
                        <div className="source-number">
                          {String(index + 1).padStart(2, "0")}
                        </div>

                        <div className="source-details">
                          <div className="source-topline">
                            <span className="source-domain">
                              {getDomain(source.url)}
                            </span>

                            {source.trusted && (
                              <span className="trusted-label">
                                ✓ TRUSTED
                              </span>
                            )}
                          </div>

                          <h4>
                            {source.title ||
                              "Untitled Source"}
                          </h4>

                          <div className="source-meta">
                            {source.score !== undefined && (
                              <span>
                                Relevance{" "}
                                {(
                                  Number(source.score) * 100
                                ).toFixed(0)}
                                %
                              </span>
                            )}
                          </div>

                          {openSources[index] && (
                            <div className="source-preview">
                              {source.content ||
                                "No preview available."}
                            </div>
                          )}

                          <div className="source-actions">
                            <button
                              className="preview-button"
                              onClick={() =>
                                toggleSource(index)
                              }
                            >
                              {openSources[index]
                                ? "Hide Preview"
                                : "Preview Evidence"}
                            </button>

                            {source.url && (
                              <a
                                className="open-source-button"
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                Open Source
                                <span>↗</span>
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="no-sources">
                  <span>○</span>
                  No trusted web sources were found for this
                  claim.
                </div>
              )}
            </div>
          </section>
        )}

        <section className="how-it-works">
          <div className="section-label">
            HOW IT WORKS
          </div>

          <div className="steps-grid">
            <div className="step">
              <span className="step-number">01</span>
              <h3>AI Pattern Scan</h3>
              <p>
                AIS detects patterns associated with
                previously identified fake news.
              </p>
            </div>

            <div className="step">
              <span className="step-number">02</span>
              <h3>Web Verification</h3>
              <p>
                Relevant evidence is gathered from trusted
                online sources.
              </p>
            </div>

            <div className="step">
              <span className="step-number">03</span>
              <h3>Semantic Analysis</h3>
              <p>
                NLP compares the claim with evidence to
                determine support or contradiction.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div>
          <strong>TruthShield AI</strong>
          <span> • AI-based Fake News Verification</span>
        </div>

        <span>
          Built with React + Flask + AI
        </span>
      </footer>
    </div>
  );
}

export default App;
