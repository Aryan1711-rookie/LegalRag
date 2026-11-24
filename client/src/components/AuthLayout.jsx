
import { useId } from "react";
import { Link } from "react-router-dom";
import {
  Scale,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

/*
  Shared authentication layout for Login and Register.

  Responsive behavior:
  Mobile: 320px–639px
  Tablet: 640px–1023px
  Desktop: 1024px+

  Original palette and functionality preserved.
*/

function AuthLayout({ title, subtitle, footer, children }) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      className="
        flex min-h-screen min-h-[100dvh] w-full
        flex-col overflow-x-hidden
        bg-[#faf9f5] text-[#3d3929]
        transition-colors
        dark:bg-[#262624] dark:text-[#faf9f5]
      "
    >
      {/* Brand header */}
      <header
        className="
          flex w-full shrink-0 items-center
          px-5 py-5
          sm:px-8 sm:py-7
          lg:px-12
        "
      >
        <Link
          to="/"
          className="
            inline-flex min-h-11 items-center gap-2.5
            rounded-lg text-[#192957]
            transition-opacity hover:opacity-80
            focus-visible:outline-2
            focus-visible:outline-offset-4
            focus-visible:outline-[#192957]
            dark:text-[#a9b8f0]
          "
          aria-label="LegalMind home"
        >
          <Scale
            size={20}
            strokeWidth={1.8}
            className="shrink-0"
          />

          <span className="font-serif text-lg font-semibold tracking-tight">
            LegalMind
          </span>
        </Link>
      </header>

      {/* Main authentication content */}
      <main
        className="
          flex w-full min-w-0 flex-1
          items-start justify-center
          px-5 pb-12 pt-8
          sm:items-center
          sm:px-8 sm:pb-20 sm:pt-6
          lg:px-12
        "
      >
        <motion.div
          initial={{
            opacity: 0,
            y: reduceMotion ? 0 : 16,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: reduceMotion ? 0 : 0.6,
            ease: [0.22, 1, 0.36, 1],
          }}
          className="w-full min-w-0 max-w-[400px]"
        >
          {/* Heading */}
          <h1
            className="
              font-serif
              text-[clamp(2rem,5vw,2.75rem)]
              leading-[1.1] tracking-[-0.02em]
              text-[#3d3929]
              dark:text-[#faf9f5]
            "
          >
            {title}
          </h1>

          {/* Subtitle */}
          {subtitle && (
            <p
              className="
                mt-3 text-[14px] leading-7
                text-[#6b6a68]
                sm:mt-3.5 sm:text-[15px]
                dark:text-[#b8b6ad]
              "
            >
              {subtitle}
            </p>
          )}

          {/* Form content */}
          <div className="mt-7 w-full min-w-0 sm:mt-10">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <p
              className="
                mt-7 text-sm leading-6
                text-[#6b6a68]
                sm:mt-8
                dark:text-[#b8b6ad]
              "
            >
              {footer}
            </p>
          )}
        </motion.div>
      </main>
    </div>
  );
}

/*
  Shared form field.

  Preserves all existing props and behavior:
  label, icon, rightSlot, hint, and native input props.
*/
export function AuthField({
  label,
  icon: Icon,
  rightSlot,
  hint,
  id,
  className = "",
  ...inputProps
}) {
  const generatedId = useId();
  const inputId = id || generatedId;
  const hintId = `${inputId}-hint`;

  return (
    <div className="w-full min-w-0">
      <label
        htmlFor={inputId}
        className="
          mb-2 block text-sm font-medium
          text-[#3d3929]
          dark:text-[#faf9f5]
        "
      >
        {label}
      </label>

      <div className="relative w-full min-w-0">
        {/* Leading icon */}
        {Icon && (
          <Icon
            size={17}
            aria-hidden="true"
            className="
              pointer-events-none absolute
              left-4 top-1/2 z-10
              -translate-y-1/2
              text-[#9c9a92]
            "
          />
        )}

        {/* Input */}
        <input
          {...inputProps}
          id={inputId}
          aria-describedby={
            hint
              ? [inputProps["aria-describedby"], hintId]
                  .filter(Boolean)
                  .join(" ")
              : inputProps["aria-describedby"]
          }
          className={`
            block min-h-[50px] w-full min-w-0
            rounded-xl border border-[#e8e6dc]
            bg-white py-3.5
            text-base text-[#3d3929]
            outline-none transition
            placeholder:text-[#9c9a92]
            focus:border-[#192957]/50
            focus:ring-4 focus:ring-[#192957]/10
            sm:text-sm

            dark:border-[#3d3d3a]
            dark:bg-[#30302e]
            dark:text-white
            dark:focus:border-[#a9b8f0]/50
            dark:focus:ring-[#a9b8f0]/10

            ${Icon ? "pl-11" : "pl-4"}
            ${rightSlot ? "pr-14" : "pr-4"}
            ${className}
          `}
        />

        {/* Optional trailing control */}
        {rightSlot && (
          <div
            className="
              absolute right-1.5 top-1/2
              flex -translate-y-1/2
              items-center justify-center
            "
          >
            {rightSlot}
          </div>
        )}
      </div>

      {/* Optional helper text */}
      {hint && (
        <p
          id={hintId}
          className="
            mt-2 break-words text-xs
            leading-5 text-[#9c9a92]
          "
        >
          {hint}
        </p>
      )}
    </div>
  );
}

/*
  Shared error and success alerts.
*/
export function AuthAlert({
  type = "error",
  children,
}) {
  const isError = type === "error";
  const Icon = isError ? AlertCircle : CheckCircle2;

  return (
    <div
      role={isError ? "alert" : "status"}
      className={`
        flex min-w-0 items-start gap-2.5
        rounded-xl px-3.5 py-3
        text-sm leading-6
        sm:px-4

        ${
          isError
            ? `
              bg-red-50 text-red-700
              dark:bg-red-950/30
              dark:text-red-400
            `
            : `
              bg-emerald-50 text-emerald-700
              dark:bg-emerald-950/30
              dark:text-emerald-400
            `
        }
      `}
    >
      <Icon
        size={16}
        aria-hidden="true"
        className="mt-1 shrink-0"
      />

      <span className="min-w-0 flex-1 break-words">
        {children}
      </span>
    </div>
  );
}

/*
  Full-width primary submit button.
*/
export function AuthSubmit({
  disabled,
  children,
}) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="
        flex min-h-[50px] w-full
        items-center justify-center gap-2
        rounded-full bg-[#192957]
        px-6 py-3.5
        text-sm font-medium text-white
        transition-colors duration-200
        hover:bg-[#223675]
        focus-visible:outline-2
        focus-visible:outline-offset-2
        focus-visible:outline-[#192957]
        disabled:cursor-not-allowed
        disabled:opacity-60

        dark:bg-[#a9b8f0]
        dark:text-[#192957]
        dark:hover:bg-[#c4cff5]
        dark:focus-visible:outline-[#a9b8f0]
      "
    >
      {children}
    </button>
  );
}

/*
  Shared footer link styling.
*/
export const authLinkClass = `
  font-medium text-[#192957]
  underline decoration-[#192957]/30
  underline-offset-4 transition
  hover:decoration-[#192957]
  focus-visible:rounded-sm
  focus-visible:outline-2
  focus-visible:outline-offset-2
  focus-visible:outline-[#192957]

  dark:text-[#a9b8f0]
  dark:decoration-[#a9b8f0]/30
  dark:hover:decoration-[#a9b8f0]
  dark:focus-visible:outline-[#a9b8f0]
`;

export default AuthLayout;
