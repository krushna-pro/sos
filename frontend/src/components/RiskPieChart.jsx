// src/components/RiskPieChart.jsx
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const COLORS = {
  green: "#22c55e",  // tailwind green-500
  yellow: "#eab308", // amber-500
  red: "#ef4444",    // red-500
};

export default function RiskPieChart({ data }) {
  const chartData = [
    { name: "Low (Green)", value: data?.green || 0, color: COLORS.green },
    { name: "Medium (Yellow)", value: data?.yellow || 0, color: COLORS.yellow },
    { name: "High (Red)", value: data?.red || 0, color: COLORS.red },
  ];

  const total = chartData.reduce((sum, d) => sum + d.value, 0);
  if (!total) {
    return (
      <p className="text-xs text-gray-500">
        No students yet. Add students to see risk distribution.
      </p>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label={(entry) =>
              entry.value > 0
                ? `${entry.name.split(" ")[0]} (${entry.value})`
                : ""
            }
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [`${value} students`, "Count"]}
            cursor={{ fill: "rgba(148, 163, 184, 0.1)" }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}