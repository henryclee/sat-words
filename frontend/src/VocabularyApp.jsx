import { useState, useEffect } from "react";
import "./VocabularyApp.css"; // Importing the CSS file

const VocabularyApp = () => {
  const [word, setWord] = useState(null);
  const [definition, setDefinition] = useState(null);
  const [reviewCount, setReviewCount] = useState(0);

  useEffect(() => {
    fetchNewWord();
  }, []);

  const fetchNewWord = async () => {
    const response = await fetch("http://localhost:5000/api/word");
    const data = await response.json();
    setWord(data.word);
    setDefinition(null);
  };

  const revealDefinition = async () => {
    if (!word) return;
    const response = await fetch(`http://localhost:5000/api/definition/${word}`);
    const data = await response.json();
    setDefinition(data.definition);
  };

  const submitRecallRating = async (rating) => {
    if (!word) return;
    await fetch("http://localhost:5000/api/rate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word, rating }),
    });
    setReviewCount(reviewCount + 1);
    fetchNewWord();
  };

  return (
    <div className="app-container">
      <div className="card">
        <h1>Vocabulary Memory Aid</h1>

        <div className="word-display">{word || "Loading..."}</div>

        {definition ? (
          <p className="definition">{definition}</p>
        ) : (
          <button className="btn primary" onClick={revealDefinition}>
            Reveal Definition
          </button>
        )}

        <div className="difficulty-section">
          <p>How difficult was it to recall?</p>
          <div className="button-group">
            {[0, 1, 2, 3, 4, 5].map((num) => (
              <button key={num} className="btn secondary" onClick={() => submitRecallRating(num)}>
                {num}
              </button>
            ))}
          </div>
        </div>

        <button className="btn success" onClick={fetchNewWord}>
          Next Word
        </button>

        <p className="session-info">Words reviewed this session: {reviewCount}</p>
      </div>
    </div>
  );
};

export default VocabularyApp;
