
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  ArrowRight,
} from "lucide-react";

import AuthLayout, {
  AuthField,
  AuthAlert,
  AuthSubmit,
  authLinkClass,
} from "../components/AuthLayout";

import { useAuth } from "../context/AuthContext";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const { login, isLoading } = useAuth();

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const [successMessage] = useState(
    location.state?.message || ""
  );

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  // Consume registration success message once
  useEffect(() => {
    if (location.state?.message) {
      navigate(location.pathname, {
        replace: true,
        state: null,
      });
    }
  }, [location.state, location.pathname, navigate]);

  // Handle field changes
  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  // Handle login
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isLoading) return;

    setError("");

    try {
      await login(formData);

      navigate("/research", {
        replace: true,
      });
    } catch (err) {
      setError(
        err.message || "Unable to sign in. Please try again."
      );
    }
  };

  return (
    <AuthLayout
      title="Welcome back."
      subtitle="Sign in to continue your legal research."
      footer={
        <>
          Don't have an account?{" "}
          <Link
            to="/register"
            className={authLinkClass}
          >
            Create an account
          </Link>
        </>
      }
    >
      <div className="w-full min-w-0">
        {/* Registration success message */}
        {successMessage && (
          <div className="mb-4 sm:mb-5">
            <AuthAlert type="success">
              {successMessage}
            </AuthAlert>
          </div>
        )}

        {/* Authentication error */}
        {error && (
          <div className="mb-4 sm:mb-5">
            <AuthAlert type="error">
              {error}
            </AuthAlert>
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="
            flex w-full min-w-0 flex-col
            gap-4
            sm:gap-5
          "
        >
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
              placeholder="Enter your password"
              autoComplete="current-password"
              required
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
            <AuthSubmit disabled={isLoading}>
              {isLoading ? "Signing in…" : "Sign in"}

              {!isLoading && (
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

export default Login;
