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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
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
          message: "Account created successfully. You can now sign in.",
        },
      });
    } catch (err) {
      setError(err.message);
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
      {error && <AuthAlert type="error">{error}</AuthAlert>}

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 20 }}
      >
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
          placeholder="Create a password"
          autoComplete="new-password"
          minLength={8}
          maxLength={128}
          required
          hint="Use at least 8 characters."
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
          <AuthSubmit disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
            {!loading && <ArrowRight size={16} />}
          </AuthSubmit>
        </div>
      </form>
    </AuthLayout>
  );
}

export default Register;