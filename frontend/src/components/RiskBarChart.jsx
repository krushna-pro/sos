// src/components/RiskBarChart.jsx
import React from "react";

/**
 * students: array with
 *  - student_id
 *  - name
 *  - final_risk: "green" | "yellow" | "red"
 *  - dropout_probability: 0..1
 *  - stage (optional)
 * onStudentClick?: function(student_id)  // optional callback
 */
export default function RiskBarChart({ students, onStudentClick }) {
  const sorted = [...students]
    .filter((s) => typeof s.dropout_probability === "number")
    .sort((a, b) => b.dropout_probability - a.dropout_probability);

  const top = sorted
    .filter((s) => s.final_risk === "red" || s.final_risk === "yellow")
    .slice(0, 5);

  if (!top.length) {
    return (
      <p className="text-xs text-gray-500">
        No at‑risk students yet. Add students and run analysis.
      </p>
    );
  }

  const maxProb = top[0].dropout_probability || 1;

  return (
    <div className="space-y-2">
      {top.map((s) => {
        const prob = s.dropout_probability || 0;
        const pct = prob * 100;
        const barWidth = (prob / maxProb) * 100;

        const isRed = s.final_risk === "red";
        const barColor = isRed ? "bg-red-500" : "bg-amber-400";
        const bgStrip = isRed ? "bg-red-50" : "bg-amber-50";
        const textColor = isRed ? "text-red-700" : "text-amber-700";

        return (
          <div
            key={s.student_id}
            className={`rounded-md px-2 py-1 ${bgStrip} flex flex-col gap-1 cursor-pointer`}
            onClick={() => onStudentClick && onStudentClick(s.student_id)}
          >
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-gray-800">
                {s.name || s.student_id}
              </span>
              <span className={`font-semibold ${textColor}`}>
                {pct.toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-2 bg-white rounded-full overflow-hidden border border-gray-200">
              <div
                className={`h-full ${barColor}`}
                style={{ width: `${barWidth}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[10px] text-gray-500">
              <span>
                {s.final_risk === "red"
                  ? "High risk"
                  : s.final_risk === "yellow"
                  ? "Medium risk"
                  : "Low risk"}
              </span>
              {s.stage != null && <span>Stage {s.stage}</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}