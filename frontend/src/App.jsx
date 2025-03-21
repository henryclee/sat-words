import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider, AuthContext } from "./AuthContext";
import AuthForm from "./AuthForm";
import VocabularyApp from "./VocabularyApp";
import { useContext, useMemo } from "react";
import {jwtDecode} from "jwt-decode";

const ProtectedRoute = ({ children }) => {
  const { token } = useContext(AuthContext);

  const isTokenValid = useMemo(() => {
    if (!token) return false;
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }, [token]);

  if (!isTokenValid) {
    console.warn("Token is missing, expired, or invalid. Redirecting to login...");
    return <Navigate to="/login" replace />;
  }

  return children; 
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<AuthForm isLogin={true} />} />
          <Route path="/register" element={<AuthForm isLogin={false} />} />
          <Route path="/" element={<ProtectedRoute><VocabularyApp /></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
