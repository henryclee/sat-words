import { useState, useEffect} from "react";
// import { AuthContext } from "./AuthContext";
import "./VocabularyApp.css";

const VocabularyApp = () => {
  const [word, setWord] = useState(null);
  const [definition, setDefinition] = useState(null);
  const [reviewCount, setReviewCount] = useState(0);
  const [showScale, setShowScale] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    fetchNewWord();
  }, []);

  const fetchNewWord = async () => {
    const token = localStorage.getItem("token"); // Get the token
  
    const response = await fetch(`${API_BASE_URL}/api/word`, {
        method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // Send token in header
      },
    });

    console.log("Response status:", response.status);
  
    if (response.status === 401) {
      console.error("Unauthorized: Token is missing or invalid");
      handleLogout();
      return;
    }
  
    const data = await response.json();
    setWord(data.word);
    setDefinition(null);
  };
  
  const revealDefinition = async () => {
    if (!word) return;
    const token = localStorage.getItem("token"); // Get the token
  
    const response = await fetch(`${API_BASE_URL}/api/definition/${word}`, {
        method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`, // Send token in header
      },
    });
  
    if (response.status === 401) {
      console.error("Unauthorized: Token is missing or invalid");
      handleLogout();
      return;
    }
  
    const data = await response.json();

    // underline vocab words
    const sentence1_emphasis = data.sentence1.replace(word, `<i>${word}</i>`);
    const sentence2_emphasis = data.sentence2.replace(word, `<i>${word}</i>`);
    setDefinition({...data, sentence1: sentence1_emphasis, sentence2: sentence2_emphasis});
  };

  const submitRecallRating = async (rating) => {
    if (!word) return;
    const token = localStorage.getItem("token"); // Get the token
    const response = await fetch(`${API_BASE_URL}/api/rate`, {
        method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ word, rating }),
    });

    const data = await response.json();
    console.log(data);

    setReviewCount(reviewCount + 1);
    fetchNewWord();
  };

  const handleShowScale = () => {
    setShowScale(!showScale);
  }

  const handleLogout = () => {
    console.warn("Logging out...");
    localStorage.removeItem("token"); // Remove token
    window.location.replace("/login"); // Redirect to login page
  };

  return (
    <div className="app-container">
      <div className="card">
        <h1>SAT Vocabulary Review</h1>

        <div className="word-display">{word || "Loading..."}</div>

        {definition ? (
          <div>
            <p className="definition">
              <b>Definition:</b><br/> 
              {definition.definition} <br/>
              <b>Synonyms:</b><br/> 
              {definition.synonym1}, {definition.synonym2} <br/>
              <b>Context:</b><br/>
              1. <span dangerouslySetInnerHTML={{ __html: definition.sentence1 }} /><br/>
              2. <span dangerouslySetInnerHTML={{ __html: definition.sentence2 }} />
            </p>
            <p>How difficult was it to recall the word <b>{word}</b>?</p>
            <div className="button-group">
              {[0, 1, 2, 3, 4, 5].map((num) => (
                <button key={num} className="btn secondary" onClick={() => submitRecallRating(num)}>
                  {num}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <button className="btn primary" onClick={revealDefinition}>
            Reveal Definition
          </button>
        )}

        {showScale ? (
          <div className="difficulty-section">
            <button className="show_scale success" onClick={handleShowScale}>Hide Difficulty Scale</button>
            <ol start="0">
              <li>I had no idea</li>
              <li>I've seen it before, but don't know the meaning</li>
              <li>I thought I knew it, but was incorrect</li>
              <li>I vaguely knew the definition</li>
              <li>I had a pretty good idea, but still learned something</li> 
              <li>I knew it instantly and confidently</li>
            </ol>
          </div>
        ) : (
          <div className="difficulty-section">
            <button className="show_scale success" onClick={handleShowScale}>Show Difficulty Scale</button>
          </div>
        )}  
        <button className="logout-button logout" onClick={handleLogout}>Logout</button>

        <p className="session-info">Words reviewed this session: {reviewCount}</p>
      </div>
    </div>
  );
};

export default VocabularyApp;
