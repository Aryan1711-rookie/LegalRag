import { Link } from "react-router-dom";
import { Scale, AlertCircle, CheckCircle2 } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

/*
  Shared shell for the Login and Register pages.
  Palette: navy #192957, paper #faf9f5, rule #e8e6dc.
  Structural spacing is inline so it never depends on generated utilities.
*/

function AuthLayout({ title, subtitle, footer, children }) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      className="min-h-screen bg-[#faf9f5] text-[#3d3929] transition-colors dark:bg-[#262624] dark:text-[#faf9f5]"
      style={{ display: "flex", flexDirection: "column" }}
    >
      <header style={{ padding: "28px 32px" }}>
        <Link
          to="/"
          className="text-[#192957] dark:text-[#a9b8f0]"
          style={{ display: "inline-flex", alignItems: "center", gap: 10 }}
        >
          <Scale size={20} />
          <span className="font-serif text-lg font-semibold">LegalMind</span>
        </Link>
      </header>

      <main
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "24px 24px 96px",
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: reduceMotion ? 0 : 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          style={{ width: "100%", maxWidth: 400 }}
        >
          <h1
            className="font-serif text-[#3d3929] dark:text-[#faf9f5]"
            style={{
              fontSize: "clamp(2rem, 5vw, 2.75rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
            }}
          >
            {title}
          </h1>

          {subtitle && (
            <p
              className="text-[#6b6a68] dark:text-[#b8b6ad]"
              style={{ marginTop: 14, lineHeight: 1.7 }}
            >
              {subtitle}
            </p>
          )}

          <div style={{ marginTop: 40 }}>{children}</div>

          {footer && (
            <p
              className="text-sm text-[#6b6a68] dark:text-[#b8b6ad]"
              style={{ marginTop: 32 }}
            >
              {footer}
            </p>
          )}
        </motion.div>
      </main>
    </div>
  );
}

/* Labeled input with a leading icon and an optional trailing control */
export function AuthField({ label, icon: Icon, rightSlot, hint, ...inputProps }) {
  return (
    <div>
      <label
        className="block text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]"
        style={{ marginBottom: 8 }}
      >
        {label}
      </label>

      <div style={{ position: "relative" }}>
        {Icon && (
          <Icon
            size={17}
            className="text-[#9c9a92]"
            style={{
              position: "absolute",
              left: 16,
              top: "50%",
              transform: "translateY(-50%)",
              pointerEvents: "none",
            }}
          />
        )}

        <input
          {...inputProps}
          className="w-full rounded-xl border border-[#e8e6dc] bg-white text-sm text-[#3d3929] outline-none transition placeholder:text-[#9c9a92] focus:border-[#192957]/50 focus:ring-4 focus:ring-[#192957]/10 dark:border-[#3d3d3a] dark:bg-[#30302e] dark:text-white dark:focus:border-[#a9b8f0]/50 dark:focus:ring-[#a9b8f0]/10"
          style={{
            padding: `14px ${rightSlot ? 48 : 16}px 14px ${Icon ? 44 : 16}px`,
            boxSizing: "border-box",
          }}
        />

        {rightSlot && (
          <div
            style={{
              position: "absolute",
              right: 14,
              top: "50%",
              transform: "translateY(-50%)",
              display: "flex",
            }}
          >
            {rightSlot}
          </div>
        )}
      </div>

      {hint && (
        <p className="text-xs text-[#9c9a92]" style={{ marginTop: 8 }}>
          {hint}
        </p>
      )}
    </div>
  );
}

/* Error / success message */
export function AuthAlert({ type = "error", children }) {
  const isError = type === "error";
  const Icon = isError ? AlertCircle : CheckCircle2;

  return (
    <div
      role={isError ? "alert" : "status"}
      className={`rounded-xl text-sm ${
        isError
          ? "bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400"
          : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400"
      }`}
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 10,
        padding: "12px 14px",
        marginBottom: 24,
      }}
    >
      <Icon size={16} style={{ marginTop: 2, flexShrink: 0 }} />
      <span>{children}</span>
    </div>
  );
}

/* Full-width primary button */
export function AuthSubmit({ disabled, children }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="w-full rounded-full bg-[#192957] text-sm font-medium text-white transition hover:bg-[#223675] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#a9b8f0] dark:text-[#192957] dark:hover:bg-[#c4cff5]"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        padding: "15px 24px",
      }}
    >
      {children}
    </button>
  );
}

/* Shared style for inline links in footers */
export const authLinkClass =
  "font-medium text-[#192957] underline decoration-[#192957]/30 underline-offset-4 transition hover:decoration-[#192957] dark:text-[#a9b8f0] dark:decoration-[#a9b8f0]/30 dark:hover:decoration-[#a9b8f0]";

export default AuthLayout;