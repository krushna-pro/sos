// src/pages/DashboardPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";
import { authFetch, getToken } from "../api";
import {
  Users,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  Loader2,
  Download,
  UserPlus,
} from "lucide-react";
import { motion } from "framer-motion";

import StatsCard from "../components/StatsCard";
import RiskPieChart from "../components/RiskPieChart";
import RiskBarChart from "../components/RiskBarChart";
import StudentsTable from "../components/StudentsTable";

export default function DashboardPage() {
  const [user, setUser] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  // admin tools state
  const [exporting, setExporting] = useState(false);
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState("");
  const [regSuccess, setRegSuccess] = useState("");
  const [counselorForm, setCounselorForm] = useState({
    username: "",
    email: "",
    full_name: "",
    password: "",
    specialization: "academic", // default
  });

  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    try {
      const token = getToken();
      let currentUser = null;

      if (token) {
        const userRes = await authFetch("/auth/me");
        if (userRes.ok) {
          currentUser = await userRes.json();
          setUser(currentUser);
        }
      }

      let studentsData = [];

      if (currentUser && currentUser.role === "counselor") {
        // Counselor sees only their assigned students
        const res = await authFetch("/counselor/assigned");
        if (res.ok) {
          studentsData = await res.json();
        }
      } else {
        // Admin / others: brief list of all students
        const studentsRes = await fetch(
          `${API_BASE_URL}/students/brief/list`
        );
        if (studentsRes.ok) {
          studentsData = await studentsRes.json();
        }
      }

      setStudents(studentsData);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }

  const totalStudents = students.length;
  const greenCount = students.filter((s) => s.final_risk === "green").length;
  const yellowCount = students.filter((s) => s.final_risk === "yellow").length;
  const redCount = students.filter((s) => s.final_risk === "red").length;

  const riskData = {
    green: greenCount,
    yellow: yellowCount,
    red: redCount,
  };

  const isAdmin = user?.role === "admin";
  const isCounselor = user?.role === "counselor";

  async function handleExportStudentsCsv() {
    try {
      setExporting(true);
      const res = await authFetch("/students");
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Export failed (HTTP ${res.status})`);
      }
      const data = await res.json(); // array of students

      const header = [
        "student_id",
        "name",
        "email",
        "department",
        "semester",
        "attendance_percentage",
        "cgpa",
        "backlogs",
        "fees_pending",
        "fees_amount_due",
        "quiz_score_avg",
        "bot_engagement_score",
        "counselling_sessions",
        "baseline_risk",
        "final_risk",
        "dropout_probability",
      ];

      const rows = data.map((s) =>
        [
          s.student_id,
          s.name,
          s.email,
          s.department,
          s.semester,
          s.attendance_percentage,
          s.cgpa,
          s.backlogs,
          s.fees_pending,
          s.fees_amount_due,
          s.quiz_score_avg,
          s.bot_engagement_score,
          s.counselling_sessions,
          s.baseline_risk,
          s.final_risk,
          s.dropout_probability,
        ]
          .map((v) => (v != null ? String(v) : ""))
          .join(",")
      );

      const csv = [header.join(","), ...rows].join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "students_export.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Export error: " + e.message);
    } finally {
      setExporting(false);
    }
  }

  function handleCounselorFormChange(e) {
    const { name, value } = e.target;
    setCounselorForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleRegisterCounselor(e) {
    e.preventDefault();
    setRegLoading(true);
    setRegError("");
    setRegSuccess("");

    try {
      const body = {
        ...counselorForm,
        role: "counselor",
      };

      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Register failed (HTTP ${res.status})`);
      }

      setRegSuccess("Counselor registered successfully.");
      setCounselorForm({
        username: "",
        email: "",
        full_name: "",
        password: "",
        specialization: "academic",
      });
    } catch (e) {
      setRegError(e.message);
    } finally {
      setRegLoading(false);
      setTimeout(() => {
        setRegError("");
        setRegSuccess("");
      }, 4000);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-xs text-gray-500">
            {isAdmin && "Institution-wide overview and admin tools"}
            {isCounselor &&
              "Overview of your assigned students and their risk"}
            {!user && "Overview of student risk and engagement"}
          </p>
        </div>
        {user && (
          <div className="text-xs text-gray-600">
            Logged in as <strong>{user.username}</strong> ({user.role})
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-2">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <StatsCard
            title={isCounselor ? "My Students" : "Total Students"}
            value={totalStudents}
            icon={Users}
            color="blue"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <StatsCard
            title="Low Risk"
            value={greenCount}
            icon={ShieldCheck}
            color="green"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <StatsCard
            title="Medium Risk"
            value={yellowCount}
            icon={AlertTriangle}
            color="yellow"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <StatsCard
            title="High Risk"
            value={redCount}
            icon={AlertOctagon}
            color="red"
          />
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4"
        >
          <h3 className="font-semibold mb-2 text-sm">Risk Distribution</h3>
          <RiskPieChart data={riskData} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4"
        >
          <h3 className="font-semibold mb-2 text-sm">
            {isCounselor ? "My At‑Risk Students" : "Top At‑Risk Students"}
          </h3>
          <RiskBarChart
            students={students}
            onStudentClick={(id) => navigate(`/students/${id}`)}
          />
        </motion.div>
      </div>

      {/* Students overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4"
      >
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-sm">
            {isCounselor ? "My Students (preview)" : "Students Overview"}
          </h3>
          <span className="text-xs text-gray-500">
            Showing first 10 students
          </span>
        </div>
        <StudentsTable students={students.slice(0, 10)} />
      </motion.div>

      {/* Admin Tools */}
      {isAdmin && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4 space-y-4"
        >
          <h3 className="text-sm font-black flex items-center gap-2">
            <div className="w-2 h-6 bg-blue-600" />
            Admin Tools
          </h3>

          {/* Export students */}
          <div className="flex items-center justify-between border border-dashed border-gray-300 p-3 rounded-md">
            <div className="text-xs text-gray-700">
              <div className="font-semibold">Export Students CSV</div>
              <div className="text-[11px] text-gray-500">
                Download all students with current risk and academic fields.
              </div>
            </div>
            <button
              onClick={handleExportStudentsCsv}
              disabled={exporting}
              className="inline-flex items-center px-3 py-2 text-xs font-semibold border-2 border-black rounded-md bg-white hover:bg-gray-100 disabled:opacity-60"
            >
              <Download className="w-4 h-4 mr-1" />
              {exporting ? "Exporting..." : "Export CSV"}
            </button>
          </div>

          {/* Register counselor */}
          <form
            onSubmit={handleRegisterCounselor}
            className="border border-dashed border-gray-300 p-3 rounded-md text-xs space-y-2"
          >
            <div className="flex items-center gap-2 mb-1">
              <UserPlus className="w-4 h-4 text-blue-600" />
              <span className="font-semibold">
                Register New Counselor
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <AdminInputField
                label="Username"
                name="username"
                value={counselorForm.username}
                onChange={handleCounselorFormChange}
                required
              />
              <AdminInputField
                label="Full Name"
                name="full_name"
                value={counselorForm.full_name}
                onChange={handleCounselorFormChange}
                required
              />
              <AdminInputField
                label="Email"
                name="email"
                type="email"
                value={counselorForm.email}
                onChange={handleCounselorFormChange}
                required
              />
              <AdminInputField
                label="Password"
                name="password"
                type="password"
                value={counselorForm.password}
                onChange={handleCounselorFormChange}
                required
              />

              {/* Specialization select */}
              <label className="flex flex-col gap-1 text-[11px] text-gray-700">
                Specialization
                <select
                  name="specialization"
                  value={counselorForm.specialization}
                  onChange={handleCounselorFormChange}
                  className="h-8 px-2 border border-gray-300 rounded-md text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="academic">Academic Performance</option>
                  <option value="attendance">Attendance & Engagement</option>
                  <option value="financial">Financial / Fees Issues</option>
                  <option value="mental">Mental Health & Wellbeing</option>
                  <option value="behavioural">Behaviour & Discipline</option>
                </select>
              </label>
            </div>

            <button
              type="submit"
              disabled={regLoading}
              className="mt-1 inline-flex items-center px-3 py-2 text-xs font-semibold border-2 border-black rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
            >
              {regLoading ? "Registering..." : "Register Counselor"}
            </button>

            {regError && (
              <p className="text-[11px] text-red-600 mt-1">{regError}</p>
            )}
            {regSuccess && (
              <p className="text-[11px] text-green-600 mt-1">
                {regSuccess}
              </p>
            )}
          </form>
        </motion.div>
      )}
    </div>
  );
}

function AdminInputField({
  label,
  name,
  value,
  onChange,
  type = "text",
  required,
}) {
  return (
    <label className="flex flex-col gap-1 text-[11px] text-gray-700">
      {label}
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        className="h-8 px-2 border border-gray-300 rounded-md text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </label>
  );
}