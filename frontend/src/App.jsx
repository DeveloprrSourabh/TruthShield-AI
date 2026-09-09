import { useEffect, useState } from "react";

function App() {
    const [news, setNews] = useState("");
    const [result, setResult] = useState("");

//  Detect New Function
const detectNews = () => {

  fetch("http://127.0.0.1:5000/detect", {
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

      setResult(
        data.result + " - " + data.confidence + "%"
      );

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

      <button onClick={detectNews}>
        Detect News
      </button>

      <h3>{result}</h3>
    </div>
  );
}

export default App;