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
  const [successMessage] = useState(location.state?.message || "");

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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await login(formData);
      navigate("/research", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <AuthLayout
      title="Welcome back."
      subtitle="Sign in to continue your legal research."
      footer={
        <>
          Don't have an account?{" "}
          <Link to="/register" className={authLinkClass}>
            Create an account
          </Link>
        </>
      }
    >
      {successMessage && (
        <AuthAlert type="success">{successMessage}</AuthAlert>
      )}

      {error && <AuthAlert type="error">{error}</AuthAlert>}

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 20 }}
      >
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
              onClick={() => setShowPassword(!showPassword)}
              className="text-[#9c9a92] transition hover:text-[#3d3929] dark:hover:text-white"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          }
        />

        <div style={{ marginTop: 8 }}>
          <AuthSubmit disabled={isLoading}>
            {isLoading ? "Signing in…" : "Sign in"}
            {!isLoading && <ArrowRight size={16} />}
          </AuthSubmit>
        </div>
      </form>
    </AuthLayout>
  );
}

export default Login;