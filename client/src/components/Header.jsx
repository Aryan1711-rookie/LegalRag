import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale, Sun, Moon, LogOut, ChevronDown } from "lucide-react";

import { useAuth } from "../context/AuthContext";

function Header({ darkMode, onToggleDarkMode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const isAuthenticated = Boolean(user);

  // Generate user initials
  const initials = user?.full_name
    ? user.full_name
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((name) => name[0])
        .join("")
        .toUpperCase()
    : user?.email?.[0]?.toUpperCase() || "U";

  // Close the profile menu on outside click or Escape
  useEffect(() => {
    if (!menuOpen) return;

    function handleClick(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    }

    function handleKey(event) {
      if (event.key === "Escape") setMenuOpen(false);
    }

    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKey);

    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, [menuOpen]);

  // Handle logout
  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate("/login", { replace: true });
  };

  const navLink =
    "hidden text-sm text-slate-600 transition hover:text-[#192957] md:block dark:text-[#b8b6ad] dark:hover:text-white";

  return (
    <header
      className="fixed top-0 z-50 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md transition-colors dark:border-[#3d3d3a] dark:bg-[#262624]/90"
      style={{
        height: 74,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
        boxSizing: "border-box",
      }}
    >
      {/* Brand */}
      <Link
        to="/"
        style={{ display: "flex", alignItems: "center", gap: 12 }}
      >
        <div
          className="rounded-xl bg-[#192957] text-white"
          style={{
            width: 38,
            height: 38,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Scale size={21} />
        </div>

        <div>
          <h1 className="text-lg font-semibold leading-tight text-[#192957] dark:text-[#faf9f5]">
            LegalMind
          </h1>
          <p
            className="text-[11px] text-slate-500 dark:text-[#b8b6ad]"
            style={{ letterSpacing: "0.1em" }}
          >
            LEGAL INTELLIGENCE
          </p>
        </div>
      </Link>

      {/* Right side */}
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {/* Public navigation (signed out) */}
        {!isAuthenticated && (
          <>
            <a href="/#features" className={navLink}>
              Features
            </a>

            <a href="/#how-it-works" className={navLink}>
              How it works
            </a>
          </>
        )}

        {/* Dark mode toggle (only where the page supports it) */}
        {onToggleDarkMode && (
          <button
            onClick={onToggleDarkMode}
            className="rounded-full text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-[#30302e]"
            style={{ padding: 8, display: "flex" }}
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            aria-label="Toggle dark mode"
          >
            {darkMode ? <Sun size={19} /> : <Moon size={19} />}
          </button>
        )}

        {isAuthenticated ? (
          <div ref={menuRef} style={{ position: "relative" }}>
            {/* Profile trigger */}
            <button
              type="button"
              onClick={() => setMenuOpen((open) => !open)}
              aria-haspopup="menu"
              aria-expanded={menuOpen}
              aria-label="Open profile menu"
              className="rounded-full border border-transparent transition hover:border-slate-200 hover:bg-slate-50 dark:hover:border-[#3d3d3a] dark:hover:bg-[#30302e]"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "4px 8px 4px 4px",
              }}
            >
              <span
                className="rounded-full bg-[#192957] text-xs font-semibold text-white dark:bg-[#a9b8f0] dark:text-[#192957]"
                style={{
                  width: 34,
                  height: 34,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {initials}
              </span>

              <ChevronDown
                size={15}
                className={`text-slate-500 transition-transform dark:text-[#b8b6ad] ${
                  menuOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* Profile menu */}
            {menuOpen && (
              <div
                role="menu"
                className="rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10 dark:border-[#3d3d3a] dark:bg-[#30302e] dark:shadow-black/30"
                style={{
                  position: "absolute",
                  right: 0,
                  top: "calc(100% + 10px)",
                  width: 248,
                  padding: 8,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: "10px 10px 14px",
                  }}
                >
                  <span
                    className="rounded-full bg-[#192957]/10 text-sm font-semibold text-[#192957] dark:bg-[#a9b8f0]/15 dark:text-[#a9b8f0]"
                    style={{
                      width: 40,
                      height: 40,
                      flexShrink: 0,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {initials}
                  </span>

                  <div style={{ minWidth: 0 }}>
                    <p className="truncate text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]">
                      {user?.full_name || "Account"}
                    </p>

                    {user?.email && (
                      <p className="truncate text-xs text-slate-500 dark:text-[#b8b6ad]">
                        {user.email}
                      </p>
                    )}
                  </div>
                </div>

                <div
                  className="bg-slate-100 dark:bg-[#3d3d3a]"
                  style={{ height: 1, margin: "0 4px 6px" }}
                />

                <button
                  type="button"
                  role="menuitem"
                  onClick={handleLogout}
                  className="w-full rounded-xl text-sm text-slate-600 transition hover:bg-red-50 hover:text-red-600 dark:text-[#b8b6ad] dark:hover:bg-red-950/30 dark:hover:text-red-400"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px",
                    textAlign: "left",
                  }}
                >
                  <LogOut size={16} />
                  Sign out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/login"
            className="rounded-full bg-[#192957] text-sm font-medium text-white transition hover:bg-[#223675] dark:bg-[#a9b8f0] dark:text-[#192957] dark:hover:bg-[#c4cff5]"
            style={{ padding: "9px 20px" }}
          >
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}

export default Header;