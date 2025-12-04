// src/components/TopBar.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getToken, getCurrentUser, setCurrentUser } from "../api";

export default function TopBar() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setUser(null);
      return;
    }
    const u = getCurrentUser();
    setUser(u);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setCurrentUser(null);
    setUser(null);
    navigate("/login");
  };

  const handleLogin = () => {
    navigate("/login");
  };

  return (
    <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6">
      <div className="font-semibold text-gray-800">Syntax of Success</div>
      <div className="flex items-center gap-3 text-sm">
        {user ? (
          <>
            <span className="text-gray-600">
              Logged in as <strong>{user.username}</strong>{" "}
              {user.role && <span>({user.role})</span>}
            </span>
            <button
              onClick={handleLogout}
              className="px-3 py-1 border border-red-500 text-red-600 rounded-md text-xs hover:bg-red-50"
            >
              Logout
            </button>
          </>
        ) : (
          <button
            onClick={handleLogin}
            className="px-3 py-1 border border-blue-500 text-blue-600 rounded-md text-xs hover:bg-blue-50"
          >
            Login
          </button>
        )}
      </div>
    </header>
  );
}