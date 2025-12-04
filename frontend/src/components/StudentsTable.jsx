// src/components/StudentsTable.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

/**
 * Simple Students table used on the dashboard.
 * Rows are clickable and navigate to /students/:studentId.
 */
export default function StudentsTable({ students }) {
  const navigate = useNavigate();

  if (!students || students.length === 0) {
    return <p className="text-xs text-gray-500">No students found.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-gray-50">
            <th className="border-b border-gray-300 p-2 text-left">ID</th>
            <th className="border-b border-gray-300 p-2 text-left">Name</th>
            <th className="border-b border-gray-300 p-2 text-left">Final Risk</th>
            <th className="border-b border-gray-300 p-2 text-left">Dropout %</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr
              key={s.student_id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => navigate(`/students/${s.student_id}`)}
            >
              <td className="border-b border-gray-200 p-2">{s.student_id}</td>
              <td className="border-b border-gray-200 p-2">{s.name}</td>
              <td className="border-b border-gray-200 p-2">{s.final_risk}</td>
              <td className="border-b border-gray-200 p-2">
                {s.dropout_probability != null
                  ? (s.dropout_probability * 100).toFixed(1)
                  : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}