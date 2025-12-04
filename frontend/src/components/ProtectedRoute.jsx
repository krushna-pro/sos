// src/components/ProtectedRoute.jsx
import { Navigate, useLocation } from "react-router-dom";
import { getToken } from "../api";

export default function ProtectedRoute({ children }) {
  const token = getToken();
  const location = useLocation();

  // If no token, redirect to login and remember where we came from
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}