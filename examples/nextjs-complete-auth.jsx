// Next.js User Authentication with Facebook Integration
// Complete example for your frontend

import { useState, useEffect } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

// Authentication service class
class AuthService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Get stored auth token
  getToken() {
    if (typeof window !== "undefined") {
      return localStorage.getItem("authToken");
    }
    return null;
  }

  // Store auth token
  setToken(token) {
    if (typeof window !== "undefined") {
      localStorage.setItem("authToken", token);
    }
  }

  // Remove auth token
  removeToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("authToken");
    }
  }

  // Register new user
  async register(userData) {
    const response = await fetch(`${this.baseUrl}/api/user/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (data.success) {
      this.setToken(data.access_token);
    }

    return data;
  }

  // Login user
  async login(credentials) {
    const response = await fetch(`${this.baseUrl}/api/user/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });

    const data = await response.json();

    if (data.success) {
      this.setToken(data.access_token);
    }

    return data;
  }

  // Get user profile
  async getProfile() {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(`${this.baseUrl}/api/user/profile`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    return await response.json();
  }

  // Update user profile
  async updateProfile(updates) {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(`${this.baseUrl}/api/user/update-profile`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updates),
    });

    return await response.json();
  }

  // Get Facebook connection status
  async getFacebookStatus() {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(
      `${this.baseUrl}/api/user/facebook-connection-status`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    return await response.json();
  }

  // Get Facebook login URL
  async getFacebookLoginUrl() {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(
      `${this.baseUrl}/api/facebook-auth/facebook/login-url`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    return await response.json();
  }

  // Get user's Facebook pages
  async getFacebookPages() {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(`${this.baseUrl}/api/facebook-auth/pages`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    return await response.json();
  }

  // Select Facebook page
  async selectFacebookPage(pageId) {
    const token = this.getToken();
    if (!token) throw new Error("No auth token");

    const response = await fetch(
      `${this.baseUrl}/api/facebook-auth/select-page`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ page_id: pageId }),
      }
    );

    return await response.json();
  }

  // Logout
  logout() {
    this.removeToken();
  }
}

// React component for registration
export function RegisterForm({ onSuccessfulRegister }) {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    connect_facebook: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [authService] = useState(new AuthService());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await authService.register(formData);

      if (result.success) {
        console.log("Registration successful:", result);
        if (onSuccessfulRegister) {
          onSuccessfulRegister(result);
        }
      } else {
        setError(result.error || "Registration failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-md mx-auto p-6 bg-white shadow-md rounded-lg"
    >
      <h2 className="text-2xl font-bold mb-6 text-center">Create Account</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Username
        </label>
        <input
          type="text"
          value={formData.username}
          onChange={(e) =>
            setFormData({ ...formData, username: e.target.value })
          }
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Email
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Password
        </label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          required
          minLength="6"
        />
        <p className="text-xs text-gray-600 mt-1">Minimum 6 characters</p>
      </div>

      <div className="mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.connect_facebook}
            onChange={(e) =>
              setFormData({ ...formData, connect_facebook: e.target.checked })
            }
            className="mr-2"
          />
          <span className="text-sm text-gray-700">
            Connect Facebook after registration
          </span>
        </label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? "Creating Account..." : "Create Account"}
      </button>
    </form>
  );
}

// React component for login
export function LoginForm({ onSuccessfulLogin }) {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [authService] = useState(new AuthService());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await authService.login(formData);

      if (result.success) {
        console.log("Login successful:", result);
        if (onSuccessfulLogin) {
          onSuccessfulLogin(result);
        }
      } else {
        setError(result.error || "Login failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-md mx-auto p-6 bg-white shadow-md rounded-lg"
    >
      <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Username or Email
        </label>
        <input
          type="text"
          value={formData.username}
          onChange={(e) =>
            setFormData({ ...formData, username: e.target.value })
          }
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Password
        </label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}

// React component for Facebook connection
export function FacebookConnectComponent({ user, onFacebookConnected }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pages, setPages] = useState([]);
  const [authService] = useState(new AuthService());

  // Check Facebook status on component mount
  useEffect(() => {
    checkFacebookStatus();
  }, []);

  const checkFacebookStatus = async () => {
    try {
      const status = await authService.getFacebookStatus();
      if (status.success && status.facebook_pages) {
        setPages(status.facebook_pages);
      }
    } catch (err) {
      console.error("Error checking Facebook status:", err);
    }
  };

  const connectFacebook = async () => {
    setLoading(true);
    setError("");

    try {
      const result = await authService.getFacebookLoginUrl();

      if (result.success) {
        // Redirect to Facebook login
        window.location.href = result.login_url;
      } else {
        setError(result.error || "Failed to get Facebook login URL");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Facebook connect error:", err);
    } finally {
      setLoading(false);
    }
  };

  const selectPage = async (pageId) => {
    try {
      const result = await authService.selectFacebookPage(pageId);

      if (result.success) {
        if (onFacebookConnected) {
          onFacebookConnected(result);
        }
        // Refresh status
        checkFacebookStatus();
      } else {
        setError(result.error || "Failed to select page");
      }
    } catch (err) {
      setError("Failed to select page");
      console.error("Page selection error:", err);
    }
  };

  if (user?.facebook_connected && pages.length > 0) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white shadow-md rounded-lg">
        <h3 className="text-xl font-bold mb-4">Facebook Pages</h3>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="space-y-2">
          {pages.map((page) => (
            <div
              key={page.id}
              className="flex items-center justify-between p-3 border rounded"
            >
              <div>
                <p className="font-medium">{page.name}</p>
                <p className="text-sm text-gray-600">{page.category}</p>
              </div>
              <button
                onClick={() => selectPage(page.id)}
                className={`px-3 py-1 rounded text-sm ${
                  user.selected_page_id === page.id
                    ? "bg-green-500 text-white"
                    : "bg-blue-500 text-white hover:bg-blue-600"
                }`}
              >
                {user.selected_page_id === page.id ? "Selected" : "Select"}
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white shadow-md rounded-lg">
      <h3 className="text-xl font-bold mb-4">Connect Facebook</h3>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <p className="text-gray-600 mb-4">
        Connect your Facebook account to manage and post to your Facebook pages.
      </p>

      <button
        onClick={connectFacebook}
        disabled={loading}
        className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Connecting..." : "Connect with Facebook"}
      </button>
    </div>
  );
}

// Main authentication component
export default function AuthComponent() {
  const [currentView, setCurrentView] = useState("login"); // 'login', 'register', 'dashboard'
  const [user, setUser] = useState(null);
  const [authService] = useState(new AuthService());

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const token = authService.getToken();
      if (token) {
        try {
          const profile = await authService.getProfile();
          if (profile.success) {
            setUser(profile.user);
            setCurrentView("dashboard");
          }
        } catch (err) {
          // Token might be invalid
          authService.removeToken();
        }
      }
    };

    checkAuth();
  }, []);

  const handleSuccessfulAuth = (result) => {
    setUser(result.user);
    setCurrentView("dashboard");
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    setCurrentView("login");
  };

  if (currentView === "dashboard" && user) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Welcome, {user.username}!</h1>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4">Profile Information</h2>
              <p>
                <strong>Username:</strong> {user.username}
              </p>
              <p>
                <strong>Email:</strong> {user.email}
              </p>
              <p>
                <strong>Facebook Connected:</strong>{" "}
                {user.facebook_connected ? "✅ Yes" : "❌ No"}
              </p>
              {user.selected_page_id && (
                <p>
                  <strong>Selected Page:</strong> {user.selected_page_id}
                </p>
              )}
            </div>

            <FacebookConnectComponent
              user={user}
              onFacebookConnected={(result) => {
                console.log("Facebook connected:", result);
                // Refresh user profile
                authService.getProfile().then((profile) => {
                  if (profile.success) {
                    setUser(profile.user);
                  }
                });
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">FB Daily Posts</h1>
          <p className="text-gray-600">Social Media Management Platform</p>
        </div>

        <div className="mb-4 flex justify-center space-x-4">
          <button
            onClick={() => setCurrentView("login")}
            className={`px-4 py-2 rounded ${
              currentView === "login"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setCurrentView("register")}
            className={`px-4 py-2 rounded ${
              currentView === "register"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            Register
          </button>
        </div>

        {currentView === "login" && (
          <LoginForm onSuccessfulLogin={handleSuccessfulAuth} />
        )}

        {currentView === "register" && (
          <RegisterForm onSuccessfulRegister={handleSuccessfulAuth} />
        )}
      </div>
    </div>
  );
}
