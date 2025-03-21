import { useState, useContext } from "react";
import { AuthContext } from "./AuthContext";
import { Link, useNavigate } from "react-router-dom"; // Import useNavigate
import "./AuthForm.css"; // Import the CSS file

const AuthForm = ({ isLogin }) => {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate(); // Initialize useNavigate

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isLogin ? "login" : "register";
    
    const response = await fetch(`http://localhost:5000/api/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    
    if (response.ok && isLogin) {
      login(data.token);
      navigate("/"); // ✅ Redirect user to VocabularyApp after login
    } else {
      setMessage(data.message);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? "Login" : "Register"}</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">{isLogin ? "Login" : "Sign Up"}</button>
        </form>

        {message && <p className="error-message">{message}</p>}

        <p className="auth-switch">
          {isLogin ? (
            <>Don't have an account? <Link to="/register">Sign up</Link></>
          ) : (
            <>Already have an account? <Link to="/login">Log in</Link></>
          )}
        </p>
      </div>
    </div>
  );
};

export default AuthForm;
