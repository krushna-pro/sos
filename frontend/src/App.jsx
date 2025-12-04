// src/App.jsx
import { Routes, Route } from "react-router-dom";
import Layout from "./Layout";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import StudentsPage from "./pages/StudentsPage";
import StudentDetailPage from "./pages/StudentDetailPage";
import ClustersPage from "./pages/ClustersPage";       // NEW
import ProtectedRoute from "./components/ProtectedRoute";
import AdminCounselorsPage from "./pages/AdminCounselorsPage";

export default function App() {
  return (
    <Routes>
      {/* Public login page (no layout wrapper) */}
      <Route path="/login" element={<LoginPage />} />

      {/* All other routes use the main Layout */}
      <Route element={<Layout />}>
        {/* Home is public */}
        <Route path="/" element={<HomePage />} />

        {/* These routes require login */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/students"
          element={
            <ProtectedRoute>
              <StudentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/students/:studentId"
          element={
            <ProtectedRoute>
              <StudentDetailPage />
            </ProtectedRoute>
          }
        />

        {/* NEW: Clusters page with same layout + auth */}
        <Route
          path="/clusters"
          element={
            <ProtectedRoute>
              <ClustersPage />
            </ProtectedRoute>
          }
        />
        {/* Admin Counselors Overview */}
        <Route
  path="/admin/counselors"
  element={
    <ProtectedRoute>
      <AdminCounselorsPage />
    </ProtectedRoute>
  }
/>
      </Route>
    </Routes>
  );
}