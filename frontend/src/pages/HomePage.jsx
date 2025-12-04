// src/pages/HomePage.jsx
import React from "react";
import { Link } from "react-router-dom";
import {
  GraduationCap,
  Brain,
  Shield,
  Users,
  BarChart3,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { motion } from "framer-motion";

export default function HomePage() {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered Predictions",
      description:
        "Advanced machine learning algorithms analyze multiple factors to predict dropout risk with high accuracy.",
    },
    {
      icon: Shield,
      title: "Early Intervention",
      description:
        "Identify at-risk students early and provide timely counselling support before it's too late.",
    },
    {
      icon: BarChart3,
      title: "Comprehensive Analytics",
      description:
        "Visual dashboards and detailed reports help you understand trends and patterns.",
    },
    {
      icon: Users,
      title: "Student-Centric",
      description:
        "Personalized recommendations for each student based on their unique situation.",
    },
  ];

  const stats = [
    { value: "95%", label: "Prediction Accuracy" },
    { value: "500+", label: "Students Analyzed" },
    { value: "40%", label: "Dropout Prevention" },
    { value: "24/7", label: "AI Monitoring" },
  ];

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 py-20 lg:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-stone-50 to-yellow-50" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full blur-3xl opacity-30" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-yellow-200 rounded-full blur-3xl opacity-30" />

        <div className="relative max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-full mb-8">
              <GraduationCap className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-bold">
                AI-Powered Education Analytics
              </span>
            </div>

            <h1 className="text-5xl lg:text-7xl font-black text-black mb-6 leading-tight">
              Syntax of
              <span className="block text-blue-600">Success</span>
            </h1>

            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
              Predict student dropout risk before it happens. Our AI-driven
              system helps educators identify at-risk students and provide
              timely intervention.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 bg-blue-600 text-white font-bold text-lg border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
                >
                  View Dashboard
                  <ChevronRightIcon />
                </motion.button>
              </Link>
              <Link to="/login">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 bg-white text-black font-bold text-lg border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
                >
                  Login to System
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-6 py-16 bg-black">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl lg:text-5xl font-black text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400 font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-black text-black mb-4">
              How It Works
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our system combines multiple data points with advanced AI to
              provide accurate predictions.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="p-8 bg-white border-2 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
              >
                <div className="w-14 h-14 bg-blue-100 border-2 border-black flex items-center justify-center mb-6">
                  <feature.icon className="w-7 h-7 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-black mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Risk Indicators Preview */}
      <section className="px-6 py-20 bg-stone-100">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-black text-black mb-4">
              Risk Classification
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Students are classified into three risk categories based on
              multiple factors.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-8 bg-green-50 border-2 border-black shadow-[6px_6px_0px_0px_rgba(34,197,94,1)]"
            >
              <CheckCircle className="w-12 h-12 text-green-600 mb-4" />
              <h3 className="text-2xl font-bold text-green-700 mb-2">
                Low Risk
              </h3>
              <p className="text-green-600">
                Students performing well with low probability of dropout.
              </p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-8 bg-yellow-50 border-2 border-black shadow-[6px_6px_0px_0px_rgba(234,179,8,1)]"
            >
              <AlertTriangle className="w-12 h-12 text-yellow-600 mb-4" />
              <h3 className="text-2xl font-bold text-yellow-700 mb-2">
                Medium Risk
              </h3>
              <p className="text-yellow-600">
                Students showing warning signs that need monitoring.
              </p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-8 bg-red-50 border-2 border-black shadow-[6px_6px_0px_0px_rgba(239,68,68,1)]"
            >
              <AlertTriangle className="w-12 h-12 text-red-600 mb-4" />
              <h3 className="text-2xl font-bold text-red-700 mb-2">
                High Risk
              </h3>
              <p className="text-red-600">
                Immediate intervention required to prevent dropout.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="p-12 bg-blue-600 border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] text-center"
          >
            <h2 className="text-4xl font-black text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-blue-100 mb-8 text-lg">
              Access the dashboard to view student analytics and predictions.
            </p>
            <Link to="/login">
              <button className="px-8 py-4 bg-white text-blue-600 font-bold text-lg border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all">
                Login Now
              </button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t-2 border-black bg-white">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-blue-600" />
            <span className="font-bold text-lg">Syntax of Success</span>
          </div>
          <p className="text-gray-500 text-sm">
            © 2024 Student Dropout Prediction System. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

// Small inline icon component to avoid extra import
function ChevronRightIcon() {
  return <span className="inline-block ml-2">➜</span>;
}