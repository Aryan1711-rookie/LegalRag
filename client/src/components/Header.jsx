import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale, Sun, Moon, LogOut, ChevronDown, Settings } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Header({ darkMode, onToggleDarkMode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const isAuthenticated = Boolean(user);

  const initials = user?.full_name
    ? user.full_name.trim().split(/\s+/).slice(0, 2).map((name) => name[0]).join("").toUpperCase()
    : user?.email?.[0]?.toUpperCase() || "U";

  useEffect(() => {
    if (!menuOpen) return;
    function onPointerDown(event) {
      if (!menuRef.current?.contains(event.target)) setMenuOpen(false);
    }
    function onKeyDown(event) {
      if (event.key === "Escape") setMenuOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [menuOpen]);

  function handleLogout() {
    setMenuOpen(false);
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex h-[74px] items-center justify-between gap-3 border-b border-slate-200 bg-white/95 px-3 backdrop-blur-md transition-colors sm:px-6 dark:border-[#3d3d3a] dark:bg-[#262624]/95">
      <Link to="/" className="flex min-w-0 items-center gap-2.5 sm:gap-3" aria-label="LegalMind home">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#192957] text-white sm:h-[38px] sm:w-[38px]">
          <Scale size={21} />
        </span>
        <span className="min-w-0">
          <span className="block truncate text-base font-semibold leading-tight text-[#192957] sm:text-lg dark:text-[#faf9f5]">LegalMind</span>
          <span className="hidden text-[10px] tracking-[0.1em] text-slate-500 min-[375px]:block sm:text-[11px] dark:text-[#b8b6ad]">LEGAL INTELLIGENCE</span>
        </span>
      </Link>

      <div className="flex shrink-0 items-center gap-1 sm:gap-3">
        {!isAuthenticated && (
          <nav className="mr-1 hidden items-center gap-5 md:flex" aria-label="Public navigation">
            <a href="/#features" className="text-sm text-slate-600 hover:text-[#192957] dark:text-[#b8b6ad] dark:hover:text-white">Features</a>
            <a href="/#how-it-works" className="text-sm text-slate-600 hover:text-[#192957] dark:text-[#b8b6ad] dark:hover:text-white">How it works</a>
          </nav>
        )}

        {onToggleDarkMode && (
          <button type="button" onClick={onToggleDarkMode} title={darkMode ? "Switch to light mode" : "Switch to dark mode"} aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"} className="flex h-11 w-11 items-center justify-center rounded-full text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-[#30302e]">
            {darkMode ? <Sun size={19} /> : <Moon size={19} />}
          </button>
        )}

        {isAuthenticated ? (
          <div ref={menuRef} className="relative">
            <button type="button" onClick={() => setMenuOpen((open) => !open)} aria-haspopup="menu" aria-expanded={menuOpen} aria-label="Account menu" className="flex h-11 items-center gap-1 rounded-full border border-transparent pl-1 pr-2 transition hover:border-slate-200 hover:bg-slate-50 dark:hover:border-[#3d3d3a] dark:hover:bg-[#30302e]">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#192957] text-xs font-semibold text-white dark:bg-[#a9b8f0] dark:text-[#192957]">{initials}</span>
              <ChevronDown size={14} className={`hidden text-slate-500 transition-transform sm:block dark:text-[#b8b6ad] ${menuOpen ? "rotate-180" : ""}`} />
            </button>

            {menuOpen && (
              <div role="menu" className="absolute right-0 top-[calc(100%+8px)] w-[min(280px,calc(100vw-24px))] rounded-2xl border border-slate-200 bg-white p-2 shadow-xl shadow-slate-900/10 dark:border-[#3d3d3a] dark:bg-[#30302e] dark:shadow-black/30">
                <div className="flex items-center gap-3 px-2 py-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#192957]/10 text-sm font-semibold text-[#192957] dark:bg-[#a9b8f0]/15 dark:text-[#a9b8f0]">{initials}</span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]">{user?.full_name || "Account"}</p>
                    {user?.email && <p className="truncate text-xs text-slate-500 dark:text-[#b8b6ad]">{user.email}</p>}
                  </div>
                </div>
                <div className="mx-1 mb-1 h-px bg-slate-100 dark:bg-[#3d3d3a]" />
                <Link to="/settings" role="menuitem" onClick={() => setMenuOpen(false)} className="flex min-h-11 items-center gap-2.5 rounded-xl px-3 text-sm text-slate-600 hover:bg-slate-50 dark:text-[#b8b6ad] dark:hover:bg-[#3a3a37]">
                  <Settings size={16} /> Settings
                </Link>
                <button type="button" role="menuitem" onClick={handleLogout} className="flex min-h-11 w-full items-center gap-2.5 rounded-xl px-3 text-left text-sm text-slate-600 hover:bg-red-50 hover:text-red-600 dark:text-[#b8b6ad] dark:hover:bg-red-950/30 dark:hover:text-red-400">
                  <LogOut size={16} /> Sign out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link to="/login" className="rounded-full bg-[#192957] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#223675] sm:px-5 dark:bg-[#a9b8f0] dark:text-[#192957] dark:hover:bg-[#c4cff5]">Sign in</Link>
        )}
      </div>
    </header>
  );
}

export default Header;
