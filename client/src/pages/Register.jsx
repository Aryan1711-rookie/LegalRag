
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  UserRound,
  ArrowRight,
} from "lucide-react";

import AuthLayout, {
  AuthField,
  AuthAlert,
  AuthSubmit,
  authLinkClass,
} from "../components/AuthLayout";

import { registerUser } from "../services/auth";

function Register() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
  });

  // Handle form input changes
  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  // Handle account registration
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (loading) return;

    setError("");
    setLoading(true);

    try {
      await registerUser({
        ...formData,
        full_name: formData.full_name.trim(),
      });

      navigate("/login", {
        replace: true,
        state: {
          message:
            "Account created successfully. You can now sign in.",
        },
      });
    } catch (err) {
      setError(
        err.message || "Unable to create account. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account."
      subtitle="Set up your LegalMind workspace in a few steps."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className={authLinkClass}>
            Sign in
          </Link>
        </>
      }
    >
      <div className="w-full min-w-0">
        {/* Registration error */}
        {error && (
          <div className="mb-4 sm:mb-5">
            <AuthAlert type="error">
              {error}
            </AuthAlert>
          </div>
        )}

        {/* Registration form */}
        <form
          onSubmit={handleSubmit}
          className="
            flex w-full min-w-0 flex-col
            gap-4 sm:gap-5
          "
        >
          {/* Full name */}
          <div className="w-full min-w-0">
            <AuthField
              label="Full name"
              icon={UserRound}
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Your full name"
              autoComplete="name"
              minLength={2}
              maxLength={100}
              required
            />
          </div>

          {/* Email */}
          <div className="w-full min-w-0">
            <AuthField
              label="Email address"
              icon={Mail}
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </div>

          {/* Password */}
          <div className="w-full min-w-0">
            <AuthField
              label="Password"
              icon={Lock}
              type={showPassword ? "text" : "password"}
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password"
              autoComplete="new-password"
              minLength={8}
              maxLength={128}
              required
              hint="Use at least 8 characters."
              rightSlot={
                <button
                  type="button"
                  onClick={() =>
                    setShowPassword((prev) => !prev)
                  }
                  className="
                    flex h-10 w-10 shrink-0
                    items-center justify-center
                    rounded-lg
                    text-[#9c9a92]
                    transition-colors
                    hover:bg-[#f0eee6]
                    hover:text-[#3d3929]
                    focus-visible:outline-2
                    focus-visible:outline-offset-2
                    focus-visible:outline-[#192957]

                    dark:hover:bg-[#3d3d3a]
                    dark:hover:text-white
                    dark:focus-visible:outline-[#a9b8f0]
                  "
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  aria-pressed={showPassword}
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              }
            />
          </div>

          {/* Submit */}
          <div className="mt-2 w-full sm:mt-3">
            <AuthSubmit disabled={loading}>
              {loading
                ? "Creating account…"
                : "Create account"}

              {!loading && (
                <ArrowRight
                  size={16}
                  className="shrink-0"
                />
              )}
            </AuthSubmit>
          </div>
        </form>
      </div>
    </AuthLayout>
  );
}

export default Register;
