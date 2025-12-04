// src/pages/StudentsPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch, getToken } from "../api";
import {
  Users,
  Calendar,
  GraduationCap,
  DollarSign,
  Eye,
  Brain,
  Search,
  Filter,
  Loader2,
  RefreshCw,
  MessageCircle,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function StudentsPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingStudent, setAddingStudent] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");
  const [stageFilter, setStageFilter] = useState("all");
  const [onlyBotLinked, setOnlyBotLinked] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    try {
      const token = getToken();
      if (!token) {
        setUser(null);
        setStudents([]);
        return;
      }

      // Fetch user info
      const userRes = await authFetch("/auth/me");
      if (userRes.ok) {
        const userData = await userRes.json();
        setUser(userData);
      } else {
        setUser(null);
      }

      // Fetch students list (full data)
      const studentsRes = await authFetch("/students");
      if (studentsRes.ok) {
        const studentsData = await studentsRes.json();
        setStudents(studentsData);
      } else {
        setStudents([]);
      }
    } catch (error) {
      console.error("Error fetching students:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAddStudent(formData) {
    setAddingStudent(true);
    try {
      const response = await authFetch("/students", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to add student");
      }

      setMessage({ type: "success", text: "Student added successfully!" });
      await fetchData();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setAddingStudent(false);
      setTimeout(() => setMessage(null), 3000);
    }
  }

  async function handleCSVUpload(endpoint, file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await authFetch(endpoint, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    await fetchData();
    return await response.json();
  }

  function handleAnalyze(studentId) {
    navigate(`/students/${studentId}`);
  }

  const isAdmin = user?.role === "admin" || user?.role === "counselor";

  // Filter + sort high → low risk
  const filteredStudents = students
    .filter((student) => {
      const q = searchTerm.toLowerCase();
      const matchesSearch =
        student.name?.toLowerCase().includes(q) ||
        student.student_id?.toLowerCase().includes(q) ||
        student.email?.toLowerCase().includes(q);

      const matchesRisk =
        riskFilter === "all" || student.final_risk === riskFilter;

      const matchesStage =
        stageFilter === "all" ||
        (student.stage != null &&
          Number(stageFilter) === Number(student.stage));

      const matchesBotLinked =
        !onlyBotLinked || Boolean(student.telegram_chat_id);

      return matchesSearch && matchesRisk && matchesStage && matchesBotLinked;
    })
    .sort(
      (a, b) =>
        (b.dropout_probability ?? 0) - (a.dropout_probability ?? 0)
    );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">
            Loading students...
          </p>
        </div>
      </div>
    );
  }

  if (!user && !getToken()) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="text-center space-y-3">
          <p className="text-gray-700 font-medium">
            You are not logged in.
          </p>
          <button
            onClick={() => navigate("/login")}
            className="inline-flex items-center px-4 py-2 text-xs font-semibold border-2 border-black rounded-md bg-blue-600 text-white hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Global message */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`p-4 border-2 ${
              message.type === "success"
                ? "bg-green-50 border-green-500 text-green-700"
                : "bg-red-50 border-red-500 text-red-700"
            } font-medium rounded-md`}
          >
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-2xl font-black text-black flex items-center gap-2">
          <div className="w-2 h-8 bg-blue-600" />
          Student Risk Overview ({filteredStudents.length})
        </h2>

        <button
          onClick={fetchData}
          className="inline-flex items-center px-3 py-2 text-xs font-semibold border-2 border-black rounded-md bg-white hover:bg-gray-100"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Admin Panel */}
      {isAdmin && (
        <section className="space-y-6">
          <h3 className="text-lg font-black text-black flex items-center gap-2">
            <div className="w-2 h-6 bg-blue-600" />
            Admin Panel
          </h3>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AddStudentForm
              onSubmit={handleAddStudent}
              loading={addingStudent}
            />

            <div className="space-y-4">
              <CSVUploadCard
                title="Import Base Students"
                description="Upload CSV with student basic info"
                endpoint="/students/import-base-csv"
                icon={Users}
                color="blue"
                onUpload={handleCSVUpload}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CSVUploadCard
              title="Attendance Data"
              description="Import attendance percentages"
              endpoint="/students/import-attendance-csv"
              icon={Calendar}
              color="green"
              onUpload={handleCSVUpload}
            />
            <CSVUploadCard
              title="Academic Data"
              description="Import CGPA, backlogs & scores"
              endpoint="/students/import-academics-csv"
              icon={GraduationCap}
              color="purple"
              onUpload={handleCSVUpload}
            />
            <CSVUploadCard
              title="Fees Data"
              description="Import fee payment status"
              endpoint="/students/import-fees-csv"
              icon={DollarSign}
              color="orange"
              onUpload={handleCSVUpload}
            />
          </div>
        </section>
      )}

      {/* Filters */}
      <section className="space-y-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              placeholder="Search by name, ID, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full h-11 pl-12 pr-3 border-2 border-black rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="h-11 border-2 border-black rounded-md px-3 text-sm bg-white"
              >
                <option value="all">All Risks</option>
                <option value="green">Low Risk</option>
                <option value="yellow">Medium Risk</option>
                <option value="red">High Risk</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-600">Stage</span>
              <select
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                className="h-11 border-2 border-black rounded-md px-3 text-sm bg-white"
              >
                <option value="all">All</option>
                <option value="1">Stage 1</option>
                <option value="2">Stage 2</option>
                <option value="3">Stage 3</option>
              </select>
            </div>

            <label className="inline-flex items-center gap-2 text-xs text-gray-700">
              <input
                type="checkbox"
                checked={onlyBotLinked}
                onChange={(e) => setOnlyBotLinked(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="flex items-center gap-1">
                <MessageCircle className="w-3 h-3" />
                Only Telegram‑linked
              </span>
            </label>
          </div>
        </div>
      </section>

      {/* Students Table (scrollable) */}
      <section className="bg-white border-2 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
        <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-stone-100 border-b-2 border-black">
                <th className="text-left p-3 font-black text-black">
                  Student ID
                </th>
                <th className="text-left p-3 font-black text-black">Name</th>
                <th className="text-left p-3 font-black text-black hidden md:table-cell">
                  Email
                </th>
                <th className="text-left p-3 font-black text-black hidden lg:table-cell">
                  Department
                </th>
                <th className="text-left p-3 font-black text-black">
                  Risk Level
                </th>
                <th className="text-left p-3 font-black text-black">
                  Stage
                </th>
                <th className="text-left p-3 font-black text-black">
                  Dropout %
                </th>
                <th className="text-left p-3 font-black text-black hidden md:table-cell">
                  Bot Linked
                </th>
                <th className="text-left p-3 font-black text-black">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student, index) => {
                const rowBg =
                  student.final_risk === "red"
                    ? "bg-red-50"
                    : student.final_risk === "yellow"
                    ? "bg-amber-50"
                    : student.final_risk === "green"
                    ? "bg-emerald-50"
                    : "bg-white";

                return (
                  <motion.tr
                    key={student.student_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.02 }}
                    className={`border-b border-gray-200 hover:bg-stone-100 transition-colors ${rowBg}`}
                  >
                    <td className="p-3 font-mono font-bold text-gray-700">
                      {student.student_id}
                    </td>
                    <td className="p-3 font-semibold text-black">
                      {student.name}
                    </td>
                    <td className="p-3 hidden md:table-cell text-gray-600">
                      {student.email}
                    </td>
                    <td className="p-3 hidden lg:table-cell text-gray-600">
                      {student.department}
                    </td>
                    <td className="p-3">
                      <RiskBadge risk={student.final_risk} />
                    </td>
                    <td className="p-3">
                      <StageChip stage={student.stage} />
                    </td>
                    <td className="p-3">
                      <span
                        className={`font-bold ${
                          (student.dropout_probability || 0) > 0.7
                            ? "text-red-600"
                            : (student.dropout_probability || 0) > 0.4
                            ? "text-yellow-600"
                            : "text-green-600"
                        }`}
                      >
                        {student.dropout_probability != null
                          ? `${Math.round(
                              student.dropout_probability * 100
                            )}%`
                          : "N/A"}
                      </span>
                    </td>
                    <td className="p-3 hidden md:table-cell">
                      {student.telegram_chat_id ? (
                        <span className="inline-flex items-center gap-1 text-xs text-green-700">
                          <span className="w-2 h-2 rounded-full bg-green-500" />
                          Linked
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-gray-400">
                          <span className="w-2 h-2 rounded-full bg-gray-300" />
                          Not linked
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() =>
                            navigate(`/students/${student.student_id}`)
                          }
                          className="p-2 bg-blue-50 text-blue-600 border-2 border-blue-500 hover:bg-blue-100 transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleAnalyze(student.student_id)}
                          className="p-2 bg-purple-50 text-purple-600 border-2 border-purple-500 hover:bg-purple-100 transition-colors"
                          title="Go to Analysis"
                        >
                          <Brain className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredStudents.length === 0 && (
          <div className="p-12 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">No students found</p>
            <p className="text-sm text-gray-400">
              Try adjusting your search or filters.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

/* --------- Small helper components inside this file --------- */

function RiskBadge({ risk }) {
  const r = (risk || "").toLowerCase();
  let text = "Unknown";
  let bg = "bg-gray-100 text-gray-700 border-gray-300";

  if (r === "green") {
    text = "Low";
    bg = "bg-green-50 text-green-700 border-green-500";
  } else if (r === "yellow") {
    text = "Medium";
    bg = "bg-yellow-50 text-yellow-700 border-yellow-500";
  } else if (r === "red") {
    text = "High";
    bg = "bg-red-50 text-red-700 border-red-500";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${bg}`}
    >
      {text}
    </span>
  );
}

function StageChip({ stage }) {
  const s = Number(stage);
  if (!s) {
    return (
      <span className="inline-flex px-2 py-0.5 rounded-full text-xs border border-gray-300 text-gray-500">
        -
      </span>
    );
  }

  let bg = "bg-emerald-50 text-emerald-700 border-emerald-500";
  let label = "Stage 1";

  if (s === 2) {
    bg = "bg-amber-50 text-amber-700 border-amber-500";
    label = "Stage 2";
  } else if (s === 3) {
    bg = "bg-red-50 text-red-700 border-red-500";
    label = "Stage 3";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${bg}`}
    >
      {label}
    </span>
  );
}

function AddStudentForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    student_id: "",
    name: "",
    email: "",
    phone: "",
    department: "",
    semester: "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      ...form,
      semester: Number(form.semester) || 0,
    };
    onSubmit(payload);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-white border-2 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] space-y-3"
    >
      <h4 className="text-lg font-black mb-2 flex items-center gap-2">
        <div className="w-2 h-6 bg-blue-600" />
        Add New Student
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <InputField
          label="Student ID"
          name="student_id"
          value={form.student_id}
          onChange={handleChange}
          required
        />
        <InputField
          label="Name"
          name="name"
          value={form.name}
          onChange={handleChange}
          required
        />
        <InputField
          label="Email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <InputField
          label="Phone"
          name="phone"
          value={form.phone}
          onChange={handleChange}
        />
        <InputField
          label="Department"
          name="department"
          value={form.department}
          onChange={handleChange}
        />
        <InputField
          label="Semester"
          name="semester"
          type="number"
          value={form.semester}
          onChange={handleChange}
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="mt-2 inline-flex items-center px-4 py-2 text-xs font-semibold border-2 border-black rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {loading ? "Adding..." : "Add Student"}
      </button>
    </form>
  );
}

function InputField({ label, name, value, onChange, type = "text", required }) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium text-gray-700">
      {label}
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        className="h-9 px-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </label>
  );
}

function CSVUploadCard({
  title,
  description,
  endpoint,
  icon: Icon,
  color,
  onUpload,
}) {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const colorBg =
    color === "green"
      ? "bg-green-50 border-green-500"
      : color === "purple"
      ? "bg-purple-50 border-purple-500"
      : color === "orange"
      ? "bg-orange-50 border-orange-500"
      : "bg-blue-50 border-blue-500";

  async function handleChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setResult(null);
    try {
      const res = await onUpload(endpoint, file);
      setResult(res);
    } catch (e) {
      setResult({ error: e.message });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div
      className={`p-4 border-2 shadow-[4px_4px_0_0_rgba(0,0,0,1)] ${colorBg}`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-1">
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-bold mb-1">{title}</h4>
          <p className="text-xs text-gray-700 mb-2">{description}</p>
          <input
            type="file"
            accept=".csv"
            onChange={handleChange}
            disabled={uploading}
            className="block text-xs"
          />
          {uploading && (
            <p className="mt-1 text-[11px] text-gray-600">
              Uploading...
            </p>
          )}
          {result && !result.error && (
            <p className="mt-1 text-[11px] text-green-700">
              Import completed.
            </p>
          )}
          {result && result.error && (
            <p className="mt-1 text-[11px] text-red-700">
              Error: {result.error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}