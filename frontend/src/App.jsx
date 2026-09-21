import { useState } from "react";


function App() {

  const [news, setNews] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const verifyNews = async () => {

    if (!news.trim()) {
      setError("Please enter some news.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/verify",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            news: news
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Verification failed"
        );
      }

      setResult(data);

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  };


  return (

    <div
      style={{
        maxWidth: "900px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial"
      }}
    >

      <h1>TruthShield AI</h1>

      <p>
        AI-based Fake News Verification System
      </p>


      <textarea
        rows="8"
        value={news}
        onChange={(e) => setNews(e.target.value)}
        placeholder="Enter news or claim here..."
        style={{
          width: "100%",
          padding: "15px",
          fontSize: "16px",
          boxSizing: "border-box"
        }}
      />

      <br />
      <br />


      <button
        onClick={verifyNews}
        disabled={loading}
        style={{
          padding: "12px 25px",
          fontSize: "16px",
          cursor: "pointer"
        }}
      >

        {loading ? "Verifying..." : "Verify News"}

      </button>


      {error && (

        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            background: "#ffe5e5"
          }}
        >

          {error}

        </div>

      )}


      {result && (

        <div style={{ marginTop: "30px" }}>

          <h2>
            Result: {result.result}
          </h2>

          <p>
            <strong>Claim Type:</strong>{" "}
            {result.claim_type}
          </p>

          <p>
            <strong>AIS Score:</strong>{" "}
            {result.ais_score}%
          </p>

          <p>
            <strong>Web Sources:</strong>{" "}
            {result.web_sources}
          </p>

          <p>
            <strong>NLP Score:</strong>{" "}
            {result.nlp_score}%
          </p>

          <p>
            <strong>Relationship:</strong>{" "}
            {result.relationship}
          </p>

          <p>
            <strong>Reason:</strong>{" "}
            {result.reason}
          </p>


          {result.evidence && (

            <div>

              <h3>Best Evidence</h3>

              <p>
                <strong>
                  {result.evidence.title}
                </strong>
              </p>

              <p>
                {result.evidence.content}
              </p>

              <a
                href={result.evidence.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Open Evidence
              </a>

            </div>

          )}


          <h3>Trusted Sources</h3>

          {result.sources &&
            result.sources.map(
              (source, index) => (

                <div
                  key={index}
                  style={{
                    border: "1px solid #ddd",
                    padding: "15px",
                    marginBottom: "15px"
                  }}
                >

                  <strong>
                    {index + 1}.{" "}
                    {source.title}
                  </strong>

                  <p>
                    {source.content}
                  </p>

                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Open Source
                  </a>

                </div>

              )
            )
          }

        </div>

      )}

    </div>

  );
}


export default App;