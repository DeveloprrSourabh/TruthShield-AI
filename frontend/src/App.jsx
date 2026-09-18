import { useState } from "react";

function App() {

  const [news, setNews] = useState("");
  const [result, setResult] = useState(null);

  const verifyNews = () => {

    fetch("http://127.0.0.1:5000/verify", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        news: news
      })

    })
      .then((response) => response.json())

      .then((data) => {
        setResult(data);
      });
  };

  return (

    <div>

      <h1>TruthShield AI</h1>

      <textarea
        placeholder="Enter news here"
        value={news}
        onChange={(e) => setNews(e.target.value)}
      />

      <br />

      <button onClick={verifyNews}>
        Verify News
      </button>

      {result && (

        <div>

          <h2>{result.result}</h2>

          <p>
            AIS Score: {result.ais_score}%
          </p>

          <p>
            Web Sources: {result.web_sources}
          </p>

          <p>
            NLP Score: {result.nlp_score}%
          </p>

          <p>
            Relationship: {result.relationship}
          </p>

          <p>
            Reason: {result.reason}
          </p>

          <h3>Trusted Sources</h3>

          {result.sources &&
            result.sources.map((source, index) => (

              <div key={index}>

                <p>
                  <strong>{index + 1}. {source.title}</strong>
                </p>

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

                <hr />

              </div>

            ))
          }

        </div>

      )}

    </div>

  );
}

export default App;