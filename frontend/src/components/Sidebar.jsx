// src/components/Sidebar.jsx
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { getToken, getCurrentUser } from "../api";

export default function Sidebar() {
  const location = useLocation();
  const [user, setUser] = useState(null);

  // Load user from localStorage / token whenever route changes
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setUser(null);
      return;
    }
    const u = getCurrentUser();
    setUser(u || null);
  }, [location.pathname]);

  const linkClass = (path) =>
    `block px-4 py-2 rounded-md text-sm font-medium ${
      location.pathname === path
        ? "bg-blue-600 text-white"
        : "text-gray-700 hover:bg-gray-100"
    }`;

  const role = user?.role;
  const isAdmin = role === "admin";
  const isCounselor = role === "counselor";

  return (
    <aside className="w-56 bg-white border-r border-gray-200 p-4 flex flex-col">
      <h1 className="text-lg font-bold mb-6">Syntax of Success</h1>

      <nav className="flex-1 space-y-1">
        {/* Home is always visible */}
        <Link to="/" className={linkClass("/")}>
          Home
        </Link>

        {/* Admin + Counselor: Dashboard & Students */}
        {(isAdmin || isCounselor) && (
          <>
            <Link to="/dashboard" className={linkClass("/dashboard")}>
              Dashboard
            </Link>
            <Link to="/students" className={linkClass("/students")}>
              Students
            </Link>
          </>
        )}

        {/* Admin-only: Counselors overview */}
        {isAdmin && (
          <Link
            to="/admin/counselors"
            className={linkClass("/admin/counselors")}
          >
            Counselors
          </Link>
        )}

        {/* Counselor-only: Clusters */}
        {isCounselor && (
          <Link to="/clusters" className={linkClass("/clusters")}>
            Clusters
          </Link>
        )}
      </nav>
    </aside>
  );
}