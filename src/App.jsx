import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import BrandedLayout from './components/BrandedLayout';
import VoiceAgentInterface from './components/VoiceAgentInterface';
import OnboardingFlow from './components/onboarding/OnboardingFlow';
import './App.css';

const Dashboard = React.lazy(() => import('./components/Dashboard'));
const Agents = React.lazy(() => import('./components/Agents'));
const Workflows = React.lazy(() => import('./components/Workflows'));

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      fetch('/api/user/profile', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(error => {
        console.error('Failed to fetch user profile:', error);
        setIsAuthenticated(false);
      });
    }
  }, []);

  const PrivateRoute = ({ children }) => {
    return isAuthenticated ? children : <Navigate to="/login" />;
  };

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <BrandedLayout>
                <Routes>
                  <Route
                    path="/"
                    element={
                      <PrivateRoute>
                        <Dashboard />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/dashboard"
                    element={
                      <PrivateRoute>
                        <Dashboard />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/agents"
                    element={
                      <PrivateRoute>
                        <Agents />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/workflows"
                    element={
                      <PrivateRoute>
                        <Workflows />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/voice-agent"
                    element={
                      <PrivateRoute>
                        <VoiceAgentInterface />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/onboarding"
                    element={
                      <PrivateRoute>
                        <OnboardingFlow userId={user?.id} />
                      </PrivateRoute>
                    }
                  />
                </Routes>
              </BrandedLayout>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.token);
      window.location.href = '/';
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Welcome to OrchestrateX</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-button">Login</button>
        </form>
        <p className="forgot-password">Forgot password?</p>
      </div>
    </div>
  );
};

export default App;
