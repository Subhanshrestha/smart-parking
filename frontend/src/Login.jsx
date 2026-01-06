import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login({ onLogin }) {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        // Register first
        const registerRes = await fetch('http://127.0.0.1:8000/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, first_name: firstName, last_name: lastName }),
        });
        const registerData = await registerRes.json();
        if (!registerRes.ok) {
          throw new Error(registerData.error || 'Registration failed');
        }
      }

      // Login
      const loginRes = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const loginData = await loginRes.json();

      if (!loginRes.ok) {
        throw new Error(loginData.detail || 'Login failed');
      }

      localStorage.setItem('access_token', loginData.access);
      localStorage.setItem('refresh_token', loginData.refresh);

      // Call onLogin if provided (for modal usage)
      if (onLogin) {
        onLogin();
      }

      // Navigate to dashboard
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isRegister ? 'Create Account' : 'Welcome'}</h2>
        <p className="login-subtitle">
          {isRegister ? 'Sign up for VT Smart Parking' : 'Sign in to VT Smart Parking'}
        </p>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <>
              <input
                type="text"
                placeholder="First Name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
              <input
                type="text"
                placeholder="Last Name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </>
          )}
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

          {error && <p className="error-message">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Please wait...' : isRegister ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <p className="toggle-text">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <span onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Sign In' : 'Sign Up'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;