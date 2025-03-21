import { useState, useEffect, useContext} from "react";
import { AuthContext } from "./AuthContext";
import "./VocabularyApp.css"; // Importing the CSS file

const VocabularyApp = () => {
  const { setToken } = useContext(AuthContext);
  const [word, setWord] = useState(null);
  const [definition, setDefinition] = useState(null);
  const [reviewCount, setReviewCount] = useState(0);

  useEffect(() => {
    fetchNewWord();
  }, []);

  const fetchNewWord = async () => {
    const token = localStorage.getItem("token"); // Get the token

    console.log("Fetching new word with token:", token); // Debugging

  
    const response = await fetch("http://localhost:5000/api/word", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // ✅ Send token in header
      },
    });

    console.log("Response status:", response.status);
  
    if (response.status === 401) {
      console.error("Unauthorized: Token is missing or invalid");
      return;
    }
  
    const data = await response.json();
    setWord(data.word);
    setDefinition(null);
  };
  
  const revealDefinition = async () => {
    if (!word) return;
    const token = localStorage.getItem("token"); // Get the token
  
    const response = await fetch(`http://localhost:5000/api/definition/${word}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // ✅ Send token in header
      },
    });
  
    if (response.status === 401) {
      console.error("Unauthorized: Token is missing or invalid");
      return;
    }
  
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

  const handleLogout = () => {
    console.warn("Logging out...");
    localStorage.removeItem("token"); // ✅ Remove token
    setToken(null); // ✅ Clear token in context
    window.location.href = "/login"; // ✅ Redirect to login page
  };

  return (
    <div className="app-container">
      <div className="card">
        <h1>SAT Vocabulary Review</h1>

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

        <button className="btn success" onClick={fetchNewWord}>Next Word</button>
        <button className="logout-button" onClick={handleLogout}>Logout</button>

        <p className="session-info">Words reviewed this session: {reviewCount}</p>
      </div>
    </div>
  );
};

export default VocabularyApp;
