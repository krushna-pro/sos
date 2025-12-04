// src/pages/LoginPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";
import { setCurrentUser, getToken, getCurrentUser } from "../api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // If already logged in, redirect based on role
  useEffect(() => {
    const token = getToken();
    if (!token) return;
    const user = getCurrentUser();
    if (!user) return;

    if (user.role === "admin" || user.role === "counselor") {
      navigate("/dashboard", { replace: true });
    } else {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const body = new URLSearchParams({
        username,
        password,
      });

      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Login failed (HTTP ${res.status})`);
      }

      const data = await res.json(); // { access_token, token_type }
      localStorage.setItem("token", data.access_token);

      // Fetch current user info once and store it
      const meRes = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      let user = null;
      if (meRes.ok) {
        user = await meRes.json();
        setCurrentUser(user);
      } else {
        setCurrentUser(null);
      }

      // Redirect after login based on role
      if (user && (user.role === "admin" || user.role === "counselor")) {
        navigate("/dashboard", { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100 flex items-center justify-center px-4">
      <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-6 bg-white/80 border border-slate-200 rounded-2xl shadow-xl overflow-hidden">
        {/* Left side: branding / description */}
        <div className="hidden md:flex flex-col justify-between p-6 bg-gradient-to-br from-blue-600 via-indigo-600 to-slate-900 text-white">
          <div>
            <h1 className="text-2xl font-black mb-2">Syntax of Success</h1>
            <p className="text-sm text-blue-100 mb-4">
              Smart dropout risk monitoring for colleges – combining academic
              data, daily wellbeing check‑ins and counselor interventions.
            </p>
          </div>
          <div className="space-y-3 text-xs text-blue-100">
            <p className="font-semibold uppercase tracking-wide text-[11px]">
              What you get:
            </p>
            <ul className="space-y-1">
              <li>• Real‑time dropout risk prediction and clustering</li>
              <li>• Daily insights from Telegram wellbeing bot</li>
              <li>• Color‑coded risk dashboard for admins & counselors</li>
              <li>• Clear intervention stages for each student</li>
            </ul>
          </div>
          <p className="text-[11px] text-blue-200 mt-4">
            Use the credentials provided by your admin to log in.
          </p>
        </div>

        {/* Right side: login form */}
        <div className="p-6 md:p-8 flex flex-col justify-center">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Login</h2>
          <p className="text-xs text-gray-500 mb-4">
            Sign in to access the student risk dashboard.
          </p>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="space-y-1 text-xs">
              <label className="font-medium text-gray-700">
                Username
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="mt-1 block w-full h-9 rounded-md border border-gray-300 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </label>
            </div>

            <div className="space-y-1 text-xs">
              <label className="font-medium text-gray-700">
                Password
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 block w-full h-9 rounded-md border border-gray-300 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </label>
            </div>

            {error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-md px-2 py-1">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 inline-flex items-center justify-center px-4 py-2 text-xs font-semibold border-2 border-black rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
            >
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>

          <p className="mt-4 text-[11px] text-gray-500">
            Admins and counselors will be redirected to the{" "}
            <span className="font-semibold">Dashboard</span> after login.
          </p>
        </div>
      </div>
    </div>
  );
}