
import { useEffect, useState } from "react";

import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import { AnimatePresence } from "framer-motion";

import Research from "./pages/Research";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Settings from "./pages/Settings";
import Documents from "./pages/Documents";
import Home from "./pages/Home";

import {
  AuthProvider,
  useAuth,
} from "./context/AuthContext";

import ProtectedRoute from "./components/ProtectedRoutes";
import PageTransition from "./components/PageTransition";
import Preloader from "./components/Preloader";

function AppContent() {
  const { isLoading } = useAuth();

  const [minimumTimeElapsed, setMinimumTimeElapsed] =
    useState(false);

  const [startupComplete, setStartupComplete] =
    useState(false);

  // Minimum time for the cinematic animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setMinimumTimeElapsed(true);
    }, 2300);

    return () => clearTimeout(timer);
  }, []);

  // Unlock app only after initial auth and animation
  useEffect(() => {
    if (
      !startupComplete &&
      minimumTimeElapsed &&
      !isLoading
    ) {
      setStartupComplete(true);
    }
  }, [isLoading, minimumTimeElapsed, startupComplete]);

  const showPreloader = !startupComplete;

  return (
    <>
      <AnimatePresence mode="wait">
        {showPreloader && (
          <Preloader key="legalmind-preloader" />
        )}
      </AnimatePresence>

      {!showPreloader && (
        <Routes>
          {/* Public routes */}
          <Route
            path="/"
            element={
              <PageTransition>
                <Home />
              </PageTransition>
            }
          />

          <Route
            path="/login"
            element={
              <PageTransition>
                <Login />
              </PageTransition>
            }
          />

          <Route
            path="/register"
            element={
              <PageTransition>
                <Register />
              </PageTransition>
            }
          />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/research"
              element={
                <PageTransition>
                  <Research />
                </PageTransition>
              }
            />

            <Route
              path="/research/:documentSlug"
              element={
                <PageTransition>
                  <Research />
                </PageTransition>
              }
            />

            <Route
              path="/research/:documentSlug/:chatId"
              element={
                <PageTransition>
                  <Research />
                </PageTransition>
              }
            />

            <Route
              path="/settings"
              element={
                <PageTransition>
                  <Settings />
                </PageTransition>
              }
            />

            <Route
              path="/documents"
              element={
                <PageTransition>
                  <Documents />
                </PageTransition>
              }
            />
          </Route>
        </Routes>
      )}
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}
