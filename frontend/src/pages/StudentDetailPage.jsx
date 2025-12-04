// src/pages/StudentDetailPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { authFetch, getToken } from "../api";
import {
  ArrowLeft,
  User,
  GraduationCap,
  AlertTriangle,
  Shield,
  BarChart3,
  Wallet,
  Activity,
} from "lucide-react";

export default function StudentDetailPage() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const token = getToken();

  const [student, setStudent] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    loadStudent();
    // auto-run analysis in background
    runAnalysis(true);
  }, [studentId, token]);

  async function loadStudent() {
    setLoading(true);
    setError("");
    try {
      const res = await authFetch(
        `/students/${encodeURIComponent(studentId)}`
      );
      const data = await res.json();
      setStudent(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  async function runAnalysis(auto = false) {
    setAnalyzing(!auto);
    setError("");
    try {
      const res = await authFetch(
        `/students/${encodeURIComponent(studentId)}/analyze`
      );
      const data = await res.json();
      setAnalysis(data);
      if (!auto) {
        await loadStudent(); // refresh risk fields if user manually re-runs
      }
    } catch (err) {
      // don’t blow up page if analysis fails
      if (!auto) {
        setError(err.message || String(err));
      }
    } finally {
      setAnalyzing(false);
    }
  }

  const formatPercent = (val) => {
    const num = typeof val === "number" ? val : Number(val);
    return Number.isFinite(num) ? (num * 100).toFixed(1) + "%" : "0.0%";
  };

  const formatScore = (val) => {
    const num = typeof val === "number" ? val : Number(val);
    return Number.isFinite(num) ? num.toFixed(1) : "-";
  };

  if (!token) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-bold mb-2">Student Details</h1>
        <p className="text-sm text-gray-600">
          You are not logged in. Please log in first.
        </p>
        <p className="mt-2">
          <Link to="/login" className="text-blue-600 underline text-sm">
            Go to Login
          </Link>
        </p>
      </div>
    );
  }

  if (loading && !student) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">
            Loading student {studentId}...
          </p>
        </div>
      </div>
    );
  }

  if (!student && error) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-bold mb-2">Student Details</h1>
        <p className="text-sm text-red-600">Error: {error}</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-3 inline-flex items-center px-3 py-1.5 text-xs font-semibold border-2 border-black rounded-md bg-white hover:bg-gray-100"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Go Back
        </button>
      </div>
    );
  }

  const risk = (student?.final_risk || "").toLowerCase();
  const stage = Number(student?.stage || 0);

  const riskText =
    risk === "red" ? "High Risk" : risk === "yellow" ? "Medium Risk" : "Low Risk";

  const riskBg =
    risk === "red"
      ? "bg-red-50 border-red-500 text-red-700"
      : risk === "yellow"
      ? "bg-amber-50 border-amber-500 text-amber-700"
      : "bg-emerald-50 border-emerald-500 text-emerald-700";

  let stageLabel = "Stage 1 – Normal Monitoring";
  let stageBg = "bg-emerald-50 border-emerald-500 text-emerald-700";
  if (stage === 2) {
    stageLabel = "Stage 2 – At‑Risk (Automated Support)";
    stageBg = "bg-amber-50 border-amber-500 text-amber-700";
  } else if (stage === 3) {
    stageLabel = "Stage 3 – High‑Risk (Counselor Intervention)";
    stageBg = "bg-red-50 border-red-500 text-red-700";
  }

  const dropoutPercent = formatPercent(student?.dropout_probability ?? 0);

  return (
    <div className="space-y-6">
      {/* Header + Back */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold border-2 border-black rounded-md bg-white hover:bg-gray-100"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </button>
          <span className="text-xs text-gray-500">
            Student ID: <span className="font-mono">{student.student_id}</span>
          </span>
        </div>
      </div>

      {/* Hero summary */}
      <div className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-blue-50 border-2 border-blue-500 flex items-center justify-center">
            <User className="w-7 h-7 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {student.name}
            </h1>
            <p className="text-xs text-gray-600">
              {student.department || "Department N/A"} • Semester{" "}
              {student.semester || "-"}
            </p>
            {student.parent_name && (
              <p className="text-[11px] text-gray-500 mt-0.5">
                Parent: {student.parent_name}{" "}
                {student.parent_phone && `(${student.parent_phone})`}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          <div
            className={`px-3 py-1.5 rounded-full border-2 text-xs font-semibold inline-flex items-center gap-1 ${riskBg}`}
          >
            <AlertTriangle className="w-3 h-3" />
            {riskText}
          </div>
          <div
            className={`px-3 py-1.5 rounded-full border-2 text-xs font-semibold inline-flex items-center gap-1 ${stageBg}`}
          >
            <Shield className="w-3 h-3" />
            {stageLabel}
          </div>
          <div className="px-3 py-1.5 rounded-full border-2 border-slate-900 bg-slate-900 text-white text-xs font-semibold inline-flex items-center gap-1">
            <BarChart3 className="w-3 h-3" />
            Dropout: {dropoutPercent}
          </div>
        </div>
      </div>

      {/* Quick metrics cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          label="Attendance"
          value={`${formatScore(student.attendance_percentage)}%`}
          icon={CalendarIcon}
        />
        <MetricCard
          label="CGPA"
          value={formatScore(student.cgpa)}
          icon={GraduationCap}
        />
        <MetricCard
          label="Backlogs"
          value={student.backlogs ?? 0}
          icon={AlertTriangle}
        />
        <MetricCard
          label="Fees Due"
          value={
            student.fees_pending
              ? `₹${student.fees_amount_due?.toLocaleString() || 0}`
              : "Cleared"
          }
          icon={Wallet}
        />
        <MetricCard
          label="Bot Engagement"
          value={formatScore(student.bot_engagement_score)}
          icon={Activity}
        />
        <MetricCard
          label="Counselling Sessions"
          value={student.counselling_sessions ?? 0}
          icon={Shield}
        />
      </div>

      {/* Two-column: Profile + Academic & Risk details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile card */}
        <div className="bg-white border-2 border-gray-200 rounded-xl p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <div className="w-1.5 h-5 bg-blue-600" />
            Profile
          </h2>
          <InfoRow label="Student ID" value={student.student_id} />
          <InfoRow label="Name" value={student.name} />
          <InfoRow label="Email" value={student.email} />
          <InfoRow label="Phone" value={student.phone} />
          <InfoRow label="Department" value={student.department} />
          <InfoRow label="Semester" value={student.semester} />
          <InfoRow
            label="Created At"
            value={
              student.created_at
                ? new Date(student.created_at).toLocaleString()
                : "-"
            }
          />
        </div>

        {/* Academics & risk detail card */}
        <div className="bg-white border-2 border-gray-200 rounded-xl p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <div className="w-1.5 h-5 bg-emerald-600" />
            Academic & Risk
          </h2>
          <InfoRow
            label="Attendance %"
            value={formatScore(student.attendance_percentage)}
          />
          <InfoRow label="CGPA" value={formatScore(student.cgpa)} />
          <InfoRow label="Backlogs" value={student.backlogs} />
          <InfoRow
            label="Fees Pending"
            value={student.fees_pending ? "Yes" : "No"}
          />
          <InfoRow
            label="Fees Amount Due"
            value={
              student.fees_pending
                ? `₹${student.fees_amount_due?.toLocaleString() || 0}`
                : "-"
            }
          />
          <InfoRow
            label="Quiz Score Avg"
            value={formatScore(student.quiz_score_avg)}
          />
          <InfoRow
            label="Bot Engagement Score"
            value={formatScore(student.bot_engagement_score)}
          />
          <InfoRow
            label="Counselling Sessions"
            value={student.counselling_sessions}
          />
          <InfoRow label="Cluster ID" value={student.cluster_id ?? "-"} />
        </div>
      </div>

      {/* Risk analysis & recommendations */}
      <div className="bg-white border-2 border-gray-900 rounded-xl shadow-[3px_3px_0_0_rgba(15,23,42,1)] p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <div className="w-1.5 h-5 bg-purple-600" />
            Risk Analysis & Recommendations
          </h2>
          <button
            onClick={() => runAnalysis(false)}
            disabled={analyzing}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold border-2 border-black rounded-md bg-white hover:bg-gray-100 disabled:opacity-60"
          >
            {analyzing ? "Analyzing..." : "Re‑run Analysis"}
          </button>
        </div>

        {!analysis && (
          <p className="text-xs text-gray-500">
            Analysis runs automatically when you open this page. If you
            recently changed data, click “Re‑run Analysis”.
          </p>
        )}

        {analysis && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-1">
                <p>
                  <strong>Baseline Risk:</strong> {analysis.baseline_risk}
                </p>
                <p>
                  <strong>Final Risk:</strong> {analysis.final_risk}
                </p>
                <p>
                  <strong>Dropout Probability:</strong>{" "}
                  {formatPercent(analysis.dropout_probability)}
                </p>
                <p>
                  <strong>ML Risk Score:</strong>{" "}
                  {formatScore(analysis.ml_risk_score)}
                </p>
                <p>
                  <strong>Stage:</strong> {analysis.stage}
                </p>
              </div>
              <div className="space-y-1">
                <p>
                  <strong>Cluster:</strong> {analysis.cluster_name}
                </p>
                <p className="text-xs text-gray-600">
                  {analysis.cluster_description}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
              <div>
                <h3 className="font-semibold text-sm mb-1">Risk Factors</h3>
                <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5">
                  {Array.isArray(analysis.risk_factors) &&
                  analysis.risk_factors.length > 0 ? (
                    analysis.risk_factors.map((f, idx) => (
                      <li key={idx}>{f}</li>
                    ))
                  ) : (
                    <li>No specific factors listed.</li>
                  )}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-1">Recommendations</h3>
                <p
                  className="text-xs text-gray-700 whitespace-pre-line"
                >
                  {Array.isArray(analysis.recommendations)
                    ? analysis.recommendations.join("\n")
                    : analysis.recommendations || "No recommendations available."}
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ------------- Small subcomponents ---------------- */

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-1 text-xs">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800">
        {value !== undefined && value !== null && value !== "" ? value : "-"}
      </span>
    </div>
  );
}

function MetricCard({ label, value, icon: Icon }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 flex items-center gap-2">
      <div className="w-7 h-7 rounded-md bg-slate-50 border border-slate-200 flex items-center justify-center">
        {Icon ? (
          <Icon className="w-4 h-4 text-slate-700" />
        ) : (
          <BarChart3 className="w-4 h-4 text-slate-700" />
        )}
      </div>
      <div>
        <p className="text-[11px] text-gray-500">{label}</p>
        <p className="text-xs font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

// Simple calendar icon substitute so we don't import it separately
function CalendarIcon(props) {
  return <Activity {...props} />;
}