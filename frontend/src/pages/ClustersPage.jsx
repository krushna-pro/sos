// frontend/src/pages/ClustersPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch, getToken, getCurrentUser } from "../api";

function riskColor(risk) {
  if (risk === "red") return "#fee2e2";      // light red
  if (risk === "yellow") return "#fef9c3";  // light yellow
  if (risk === "green") return "#dcfce7";   // light green
  return "white";
}

function riskBadgeStyle(risk) {
  const base = {
    borderRadius: "999px",
    padding: "0.15rem 0.5rem",
    fontSize: "0.75rem",
    fontWeight: 600,
    textTransform: "uppercase",
  };
  if (risk === "red") {
    return { ...base, backgroundColor: "#fee2e2", color: "#b91c1c" };
  }
  if (risk === "yellow") {
    return { ...base, backgroundColor: "#fef9c3", color: "#854d0e" };
  }
  if (risk === "green") {
    return { ...base, backgroundColor: "#dcfce7", color: "#166534" };
  }
  return { ...base, backgroundColor: "#e5e7eb", color: "#374151" };
}

function stageBadgeStyle(stage) {
  const base = {
    borderRadius: "999px",
    padding: "0.15rem 0.5rem",
    fontSize: "0.75rem",
    fontWeight: 600,
  };
  if (stage === 3) {
    return { ...base, backgroundColor: "#fee2e2", color: "#b91c1c" }; // red
  }
  if (stage === 2) {
    return { ...base, backgroundColor: "#fef3c7", color: "#92400e" }; // amber
  }
  return { ...base, backgroundColor: "#ecfdf5", color: "#166534" };   // green
}

export default function ClustersPage() {
  const [clusters, setClusters] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [students, setStudents] = useState([]);
  const [stageFilter, setStageFilter] = useState("");
  const [messageTitle, setMessageTitle] = useState("");
  const [messageBody, setMessageBody] = useState("");
  const [info, setInfo] = useState("");
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    const u = getCurrentUser();
    if (!u || u.role !== "counselor") {
      // Only counselors can see this page
      navigate("/dashboard", { replace: true });
      return;
    }
    setUser(u);
    loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  async function loadOverview() {
    setInfo("");
    try {
      const res = await authFetch("/clusters/overview");
      const data = await res.json();
      setClusters(data);
    } catch (err) {
      setInfo(err.message || String(err));
    }
  }

  async function loadClusterStudents(cid) {
    setSelectedCluster(cid);
    setInfo("");
    try {
      const url = stageFilter
        ? `/clusters/${cid}/students?stage=${stageFilter}`
        : `/clusters/${cid}/students`;
      const res = await authFetch(url);
      const data = await res.json();
      setStudents(data);
    } catch (err) {
      setInfo(err.message || String(err));
    }
  }

  async function sendBroadcast() {
    if (selectedCluster === null) return;
    if (!messageBody.trim()) {
      setInfo("Please type a message body first.");
      return;
    }
    setInfo("");
    try {
      const res = await authFetch(
        `/clusters/${selectedCluster}/broadcast`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message_title: messageTitle || "Message from Counselor",
            message_body: messageBody,
            min_stage: 1,
            max_stage: 3,
          }),
        }
      );
      const data = await res.json();
      setInfo(`Sent to ${data.sent} students.`);
    } catch (err) {
      setInfo(err.message || String(err));
    }
  }

  const selectedInfo =
    selectedCluster !== null
      ? clusters.find((c) => c.cluster_id === selectedCluster)
      : null;

  return (
    <div style={{ padding: "1.5rem", fontFamily: "sans-serif" }}>
      <h1 style={{ marginBottom: "1rem", fontSize: "1.5rem", fontWeight: 600 }}>
        Cluster Monitoring & Interventions
      </h1>
      {info && <p style={{ color: "red", marginBottom: "0.5rem" }}>{info}</p>}

      {/* Cluster cards */}
      <h2 style={{ marginBottom: "0.5rem", fontSize: "1.1rem", fontWeight: 600 }}>
        Clusters by similar problems
      </h2>
      <div
        style={{
          display: "flex",
          gap: "1rem",
          flexWrap: "wrap",
          marginBottom: "1.5rem",
        }}
      >
        {clusters.map((c) => {
          const hasRed = c.red > 0;
          const cardBorder =
            selectedCluster === c.cluster_id ? "#4f46e5" : "#e5e7eb";
          const shadow =
            selectedCluster === c.cluster_id
              ? "0 0 0 2px rgba(79,70,229,0.2)"
              : "0 1px 2px rgba(0,0,0,0.05)";

          return (
            <div
              key={c.cluster_id}
              style={{
                border: `1px solid ${cardBorder}`,
                borderRadius: "12px",
                padding: "0.9rem",
                width: "280px",
                cursor: "pointer",
                backgroundColor: hasRed ? "#fef2f2" : "white",
                boxShadow: shadow,
                transition: "box-shadow 0.15s, border-color 0.15s",
              }}
              onClick={() => loadClusterStudents(c.cluster_id)}
            >
              <h3 style={{ marginBottom: "0.3rem", fontWeight: 600 }}>
                {c.name}
              </h3>
              <p style={{ fontSize: "0.85rem", color: "#4b5563", marginBottom: "0.4rem" }}>
                {c.description}
              </p>
              <p style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                <strong>Total:</strong> {c.total_students}
              </p>
              <p style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                <strong>Risk:</strong>{" "}
                <span style={{ color: "#b91c1c" }}>Red {c.red}</span>{" "}
                | <span style={{ color: "#a16207" }}>Yellow {c.yellow}</span>{" "}
                | <span style={{ color: "#15803d" }}>Green {c.green}</span>
              </p>
              <p style={{ fontSize: "0.8rem" }}>
                <strong>Stages:</strong> 1:{c.stage1}  2:{c.stage2}  3:{c.stage3}
              </p>
            </div>
          );
        })}
      </div>

      {/* Selected cluster info + students table */}
      {selectedCluster !== null && (
        <>
          {selectedInfo && (
            <div
              style={{
                marginBottom: "1rem",
                padding: "0.75rem",
                borderRadius: "8px",
                backgroundColor: "#f9fafb",
                border: "1px solid #e5e7eb",
              }}
            >
              <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                {selectedInfo.name} – Group Details
              </h2>
              <p style={{ fontSize: "0.9rem", color: "#4b5563" }}>
                {selectedInfo.description}
              </p>
              {selectedInfo.typical_issues && selectedInfo.typical_issues.length > 0 && (
                <p style={{ fontSize: "0.85rem", marginTop: "0.4rem" }}>
                  <strong>Typical issues:</strong>{" "}
                  {selectedInfo.typical_issues.join("; ")}
                </p>
              )}
              {selectedInfo.recommended_focus && (
                <p style={{ fontSize: "0.85rem", marginTop: "0.3rem" }}>
                  <strong>Recommended focus:</strong> {selectedInfo.recommended_focus}
                </p>
              )}
            </div>
          )}

          <h2 style={{ marginTop: "0.5rem", marginBottom: "0.5rem" }}>
            Students in this cluster
          </h2>
          <div style={{ marginBottom: "0.5rem" }}>
            <label style={{ fontSize: "0.9rem" }}>
              Filter by stage:
              <select
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                style={{ marginLeft: "0.5rem" }}
              >
                <option value="">All</option>
                <option value="1">Stage 1 (Monitoring)</option>
                <option value="2">Stage 2 (At-risk, automated support)</option>
                <option value="3">Stage 3 (High-risk, counselor)</option>
              </select>
            </label>
            <button
              onClick={() => loadClusterStudents(selectedCluster)}
              style={{
                marginLeft: "0.5rem",
                padding: "0.25rem 0.7rem",
                fontSize: "0.85rem",
              }}
            >
              Refresh
            </button>
          </div>

          <div style={{ overflowX: "auto", marginBottom: "1rem" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.9rem",
              }}
            >
              <thead>
                <tr style={{ backgroundColor: "#f3f4f6" }}>
                  <th style={thStyle}>Student ID</th>
                  <th style={thStyle}>Name</th>
                  <th style={thStyle}>Dept</th>
                  <th style={thStyle}>Risk</th>
                  <th style={thStyle}>Stage</th>
                  <th style={thStyle}>Dropout %</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => {
                  const rowBg = riskColor(s.final_risk);
                  const prob =
                    typeof s.dropout_probability === "number"
                      ? (s.dropout_probability * 100).toFixed(1)
                      : "-";

                  return (
                    <tr
                      key={s.student_id}
                      style={{
                        backgroundColor: rowBg,
                        borderBottom: "1px solid #e5e7eb",
                      }}
                    >
                      <td style={tdStyle}>{s.student_id}</td>
                      <td style={tdStyle}>{s.name}</td>
                      <td style={tdStyle}>{s.department}</td>
                      <td style={tdStyle}>
                        <span style={riskBadgeStyle(s.final_risk)}>
                          {s.final_risk}
                        </span>
                      </td>
                      <td style={tdStyle}>
                        <span style={stageBadgeStyle(s.stage)}>
                          Stage {s.stage}
                        </span>
                      </td>
                      <td style={tdStyle}>{prob}</td>
                    </tr>
                  );
                })}
                {students.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ padding: "0.75rem", textAlign: "center" }}>
                      No students found for this cluster / filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <h2 style={{ marginTop: "0.5rem", marginBottom: "0.5rem" }}>
            Send Activity / Message to this Group
          </h2>
          <div style={{ marginBottom: "0.5rem" }}>
            <input
              type="text"
              placeholder="Title (e.g., Remedial Class Info)"
              value={messageTitle}
              onChange={(e) => setMessageTitle(e.target.value)}
              style={{
                width: "100%",
                marginBottom: "0.4rem",
                padding: "0.4rem 0.5rem",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
              }}
            />
            <textarea
              placeholder="Message body to send to all students in this cluster"
              value={messageBody}
              onChange={(e) => setMessageBody(e.target.value)}
              rows={4}
              style={{
                width: "100%",
                padding: "0.4rem 0.5rem",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
              }}
            />
          </div>
          <button
            onClick={sendBroadcast}
            style={{
              padding: "0.4rem 1rem",
              borderRadius: "999px",
              backgroundColor: "#4f46e5",
              color: "white",
              border: "none",
              fontSize: "0.9rem",
              fontWeight: 500,
            }}
          >
            Send to Cluster
          </button>
        </>
      )}
    </div>
  );
}

const thStyle = {
  textAlign: "left",
  padding: "0.4rem 0.5rem",
  fontWeight: 600,
  fontSize: "0.8rem",
  color: "#4b5563",
  borderBottom: "1px solid #e5e7eb",
};

const tdStyle = {
  padding: "0.4rem 0.5rem",
  verticalAlign: "middle",
};