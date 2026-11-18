
import { Link, useNavigate } from "react-router-dom";
import {
  Scale,
  Bell,
  Sun,
  Moon,
  LogOut,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

function Header({ darkMode, onToggleDarkMode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="fixed top-0 z-50 flex h-[74px] w-full items-center justify-between border-b border-slate-200 bg-white px-5">
      <Link to="/" className="flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#192957] text-white">
          <Scale size={22} />
        </div>

        <div>
          <h1 className="text-lg font-semibold leading-tight text-[#192957]">
            LegalMind
          </h1>
          <p className="text-[11px] tracking-wide text-slate-500">
            LEGAL INTELLIGENCE
          </p>
        </div>
      </Link>

      <div className="flex items-center gap-5">
        {/* Dark Mode Toggle */}
        <button
          onClick={onToggleDarkMode}
          className="rounded-full p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* Notifications */}
        <button
          className="text-slate-500 transition hover:text-blue-600"
          aria-label="Notifications"
        >
          <Bell size={19} />
        </button>

        {/* User Avatar */}
        <div
          className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700"
          title={user?.full_name || user?.email || "User"}
        >
          {initials}
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="rounded-full p-2 text-slate-500 transition hover:bg-red-50 hover:text-red-600"
          title="Sign out"
          aria-label="Sign out"
        >
          <LogOut size={19} />
        </button>
      </div>
    </header>
  );
}

export default Header;
