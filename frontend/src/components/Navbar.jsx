// frontend/src/components/Navbar.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { authFetch, getToken } from "../api";

export default function Navbar() {
  const [user, setUser] = useState(null); // { username, role, ... }
  const [loadingUser, setLoadingUser] = useState(true);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoadingUser(false);
      setUser(null);
      return;
    }

    loadCurrentUser();
  }, []);

  async function loadCurrentUser() {
    setLoadingUser(true);
    try {
      const me = await authFetch("/auth/me");
      setUser(me);
    } catch (err) {
      console.error("Failed to load current user:", err);
      // If token invalid, clear it
      localStorage.removeItem("token");
      setUser(null);
    } finally {
      setLoadingUser(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login");
  }

  const isActive = (path) => location.pathname === path;

  return (
    <nav
      style={{
        padding: "0.75rem 1.5rem",
        borderBottom: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        fontFamily: "sans-serif",
        background: "#f9fafb",
      }}
    >
      {/* Left: brand + links */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <Link
          to="/"
          style={{
            fontWeight: "bold",
            fontSize: "1.1rem",
            textDecoration: "none",
            color: "#111827",
          }}
        >
          Syntax of Success
        </Link>

        <Link
          to="/"
          style={linkStyle(isActive("/"))}
        >
          Home
        </Link>
        <Link
          to="/dashboard"
          style={linkStyle(isActive("/dashboard"))}
        >
          Dashboard
        </Link>
        <Link
          to="/students"
          style={linkStyle(isActive("/students"))}
        >
          Students
        </Link>
      </div>

      {/* Right: user info + login/logout */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        {!loadingUser && user && (
          <span style={{ fontSize: "0.9rem", color: "#4b5563" }}>
            Logged in as{" "}
            <strong>{user.username || user.full_name || "user"}</strong>{" "}
            {user.role && (
              <>
                {" "}
                (<span>{user.role}</span>)
              </>
            )}
          </span>
        )}

        {!loadingUser && !user && (
          <span style={{ fontSize: "0.9rem", color: "#4b5563" }}>
            Not logged in
          </span>
        )}

        {user ? (
          <button
            onClick={handleLogout}
            style={{
              padding: "0.35rem 0.75rem",
              borderRadius: "4px",
              border: "1px solid #ef4444",
              background: "#fef2f2",
              color: "#b91c1c",
              cursor: "pointer",
              fontSize: "0.9rem",
            }}
          >
            Logout
          </button>
        ) : (
          <Link
            to="/login"
            style={{
              padding: "0.35rem 0.75rem",
              borderRadius: "4px",
              border: "1px solid #3b82f6",
              background: "#eff6ff",
              color: "#1d4ed8",
              textDecoration: "none",
              fontSize: "0.9rem",
            }}
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}

function linkStyle(active) {
  return {
    textDecoration: "none",
    fontSize: "0.95rem",
    color: active ? "#111827" : "#4b5563",
    fontWeight: active ? "600" : "400",
  };
}