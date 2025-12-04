// src/pages/AdminCounselorsPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch, getToken, getCurrentUser } from "../api";
import {
  Users,
  AlertTriangle,
  CheckCircle2,
  Activity,
  BarChart3,
} from "lucide-react";

export default function AdminCounselorsPage() {
  const [counselors, setCounselors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    const user = getCurrentUser();

    if (!token || !user) {
      navigate("/login", { replace: true });
      return;
    }
    if (user.role !== "admin") {
      navigate("/dashboard", { replace: true });
      return;
    }

    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadSummary() {
    setLoading(true);
    setError("");
    try {
      const res = await authFetch("/admin/counselors/summary");
      const data = await res.json();
      setCounselors(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">
            Loading counselor overview...
          </p>
        </div>
      </div>
    );
  }

  const totalCounselors = counselors.length;
  const totalStudents = counselors.reduce(
    (sum, c) => sum + c.total_students,
    0
  );
  const totalUnresolved = counselors.reduce(
    (sum, c) => sum + c.unresolved_cases,
    0
  );
  const totalResolved = counselors.reduce(
    (sum, c) => sum + c.resolved_cases,
    0
  );
  const totalSessions = counselors.reduce(
    (sum, c) => sum + c.total_counselling_sessions,
    0
  );

  const sorted = [...counselors].sort(
    (a, b) => b.unresolved_cases - a.unresolved_cases
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-black text-black flex items-center gap-2">
          <div className="w-2 h-8 bg-blue-600" />
          Counselor Performance Overview
        </h2>
      </div>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-md px-2 py-1">
          {error}
        </p>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          icon={Users}
          label="Total Counselors"
          value={totalCounselors}
          bg="bg-blue-50"
        />
        <SummaryCard
          icon={Activity}
          label="Total Assigned Students"
          value={totalStudents}
          bg="bg-emerald-50"
        />
        <SummaryCard
          icon={AlertTriangle}
          label="Open (Unresolved) Cases"
          value={totalUnresolved}
          bg="bg-amber-50"
        />
        <SummaryCard
          icon={CheckCircle2}
          label="Resolved (Low-Risk) Cases"
          value={totalResolved}
          bg="bg-green-50"
        />
      </div>

      {/* Detail table */}
      <div className="bg-white border-2 border-black rounded-xl shadow-[6px_6px_0_0_rgba(0,0,0,1)] p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold">
            Counselors (sorted by open/unresolved cases)
          </h3>
          <span className="text-[11px] text-gray-500">
            Total sessions: {totalSessions}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-stone-100 border-b-2 border-black">
                <th className="text-left p-2 font-black text-black">
                  Counselor
                </th>
                <th className="text-left p-2 font-black text-black">
                  Specialization
                </th>
                <th className="text-left p-2 font-black text-black">
                  Students
                </th>
                <th className="text-left p-2 font-black text-black">
                  High
                </th>
                <th className="text-left p-2 font-black text-black">
                  Medium
                </th>
                <th className="text-left p-2 font-black text-black">
                  Low
                </th>
                <th className="text-left p-2 font-black text-black">
                  Open
                </th>
                <th className="text-left p-2 font-black text-black">
                  Resolved
                </th>
                <th className="text-left p-2 font-black text-black">
                  Sessions
                </th>
                <th className="text-left p-2 font-black text-black">
                  Avg Dropout %
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((c) => {
                const avgPct = (c.avg_dropout_probability || 0) * 100;
                const open = c.unresolved_cases;
                const openBg =
                  open > 10
                    ? "bg-red-50 text-red-700"
                    : open > 3
                    ? "bg-amber-50 text-amber-700"
                    : "bg-emerald-50 text-emerald-700";

                return (
                  <tr
                    key={c.id}
                    className="border-b border-gray-200 hover:bg-stone-50"
                  >
                    <td className="p-2">
                      <div className="font-semibold text-gray-900">
                        {c.full_name || c.username}
                      </div>
                      <div className="text-[11px] text-gray-500">
                        {c.email}
                      </div>
                    </td>
                    <td className="p-2 text-gray-700">
                      {c.specialization || "-"}
                    </td>
                    <td className="p-2 font-semibold text-gray-800">
                      {c.total_students}
                    </td>
                    <td className="p-2 text-red-600 font-semibold">
                      {c.high_risk}
                    </td>
                    <td className="p-2 text-amber-600 font-semibold">
                      {c.medium_risk}
                    </td>
                    <td className="p-2 text-emerald-600 font-semibold">
                      {c.low_risk}
                    </td>
                    <td className="p-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[11px] font-semibold ${openBg}`}
                      >
                        {open}
                      </span>
                    </td>
                    <td className="p-2 text-emerald-700 font-semibold">
                      {c.resolved_cases}
                    </td>
                    <td className="p-2 text-gray-800 font-semibold">
                      {c.total_counselling_sessions}
                    </td>
                    <td className="p-2 font-semibold">
                      {avgPct.toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
              {sorted.length === 0 && (
                <tr>
                  <td
                    colSpan={10}
                    className="p-6 text-center text-gray-500"
                  >
                    No counselors found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ icon: Icon, label, value, bg }) {
  return (
    <div
      className={`flex items-center gap-3 border-2 border-black rounded-xl px-4 py-3 shadow-[3px_3px_0_0_rgba(0,0,0,1)] ${bg}`}
    >
      <div className="w-9 h-9 rounded-full bg-white border border-gray-300 flex items-center justify-center">
        <Icon className="w-5 h-5 text-gray-800" />
      </div>
      <div>
        <p className="text-[11px] text-gray-600">{label}</p>
        <p className="text-lg font-black text-gray-900">{value}</p>
      </div>
    </div>
  );
}