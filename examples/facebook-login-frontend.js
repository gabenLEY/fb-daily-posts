// Facebook Login Integration Example
// This shows how your frontend can handle Facebook authentication

class FacebookAuth {
  constructor(apiBaseUrl = "http://127.0.0.1:8000") {
    this.apiBaseUrl = apiBaseUrl;
    this.authToken = localStorage.getItem("authToken");
  }

  // Step 1: Get Facebook login URL
  async getFacebookLoginUrl() {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/facebook-auth/facebook/login-url`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${this.authToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (data.success) {
        return data.login_url;
      } else {
        throw new Error(data.error || "Failed to get login URL");
      }
    } catch (error) {
      console.error("Error getting Facebook login URL:", error);
      throw error;
    }
  }

  // Step 2: Redirect user to Facebook login
  async redirectToFacebookLogin() {
    try {
      const loginUrl = await this.getFacebookLoginUrl();
      window.location.href = loginUrl;
    } catch (error) {
      console.error("Error redirecting to Facebook:", error);
      alert("Failed to connect to Facebook");
    }
  }

  // Step 3: Get user's Facebook pages after successful login
  async getUserPages() {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/facebook-auth/pages`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${this.authToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (data.success) {
        return data.pages;
      } else {
        throw new Error(data.error || "Failed to get pages");
      }
    } catch (error) {
      console.error("Error getting Facebook pages:", error);
      throw error;
    }
  }

  // Step 4: Select a Facebook page for posting
  async selectPage(pageId) {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/facebook-auth/select-page`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.authToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ page_id: pageId }),
        }
      );

      const data = await response.json();

      if (data.success) {
        return data;
      } else {
        throw new Error(data.error || "Failed to select page");
      }
    } catch (error) {
      console.error("Error selecting Facebook page:", error);
      throw error;
    }
  }

  // Step 5: Disconnect Facebook
  async disconnectFacebook() {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/facebook-auth/disconnect`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.authToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (data.success) {
        return data;
      } else {
        throw new Error(data.error || "Failed to disconnect");
      }
    } catch (error) {
      console.error("Error disconnecting Facebook:", error);
      throw error;
    }
  }
}

// React Component Example
function FacebookConnectComponent() {
  const [facebookAuth] = useState(new FacebookAuth());
  const [pages, setPages] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Check if Facebook is connected when component mounts
  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const pages = await facebookAuth.getUserPages();
      setPages(pages);
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const handleConnectFacebook = async () => {
    try {
      await facebookAuth.redirectToFacebookLogin();
    } catch (error) {
      alert("Failed to connect to Facebook");
    }
  };

  const handleSelectPage = async (pageId) => {
    try {
      await facebookAuth.selectPage(pageId);
      setSelectedPage(pageId);
      alert("Page selected successfully!");
    } catch (error) {
      alert("Failed to select page");
    }
  };

  const handleDisconnect = async () => {
    try {
      await facebookAuth.disconnectFacebook();
      setPages([]);
      setSelectedPage(null);
      setIsConnected(false);
      alert("Facebook disconnected successfully!");
    } catch (error) {
      alert("Failed to disconnect Facebook");
    }
  };

  return (
    <div className="facebook-connect">
      <h3>Facebook Integration</h3>

      {!isConnected ? (
        <div>
          <p>Connect your Facebook account to post to your pages</p>
          <button onClick={handleConnectFacebook} className="btn btn-primary">
            Connect Facebook
          </button>
        </div>
      ) : (
        <div>
          <p>✅ Facebook connected!</p>

          <h4>Select a Page:</h4>
          <div className="pages-list">
            {pages.map((page) => (
              <div key={page.id} className="page-item">
                <div>
                  <strong>{page.name}</strong>
                  <span className="category">({page.category})</span>
                </div>
                <button
                  onClick={() => handleSelectPage(page.id)}
                  className={`btn ${
                    selectedPage === page.id
                      ? "btn-success"
                      : "btn-outline-primary"
                  }`}
                >
                  {selectedPage === page.id ? "Selected" : "Select"}
                </button>
              </div>
            ))}
          </div>

          <button onClick={handleDisconnect} className="btn btn-outline-danger">
            Disconnect Facebook
          </button>
        </div>
      )}
    </div>
  );
}

// Usage in your main app:
// 1. User logs into your app
// 2. User clicks "Connect Facebook"
// 3. User is redirected to Facebook for authorization
// 4. Facebook redirects back to your callback URL
// 5. Backend exchanges code for tokens and gets user's pages
// 6. User selects which page to post to
// 7. Now when user creates posts, they use their own page credentials

export { FacebookAuth, FacebookConnectComponent };
