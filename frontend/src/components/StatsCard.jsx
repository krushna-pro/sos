// src/components/StatsCard.jsx
import React from "react";

/**
 * Dashboard stats card.
 * color: "blue" | "green" | "yellow" | "red"
 */
export default function StatsCard({ title, value, icon: Icon, color }) {
  const borderColor =
    color === "green"
      ? "border-green-500"
      : color === "yellow"
      ? "border-yellow-500"
      : color === "red"
      ? "border-red-500"
      : "border-blue-500";

  const bgColor =
    color === "green"
      ? "bg-green-50"
      : color === "yellow"
      ? "bg-yellow-50"
      : color === "red"
      ? "bg-red-50"
      : "bg-blue-50";

  const iconBg =
    color === "green"
      ? "bg-green-100 text-green-700"
      : color === "yellow"
      ? "bg-yellow-100 text-yellow-700"
      : color === "red"
      ? "bg-red-100 text-red-700"
      : "bg-blue-100 text-blue-700";

  return (
    <div className="relative">
      <div
        className={`p-4 rounded-xl border-2 shadow-[3px_3px_0_0_rgba(15,23,42,1)] ${bgColor} ${borderColor} flex items-center justify-between gap-3`}
      >
        <div>
          <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
            {title}
          </div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
        </div>
        {Icon && (
          <div
            className={`h-10 w-10 rounded-lg flex items-center justify-center ${iconBg}`}
          >
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
}