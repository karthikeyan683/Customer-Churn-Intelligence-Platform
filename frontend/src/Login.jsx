
import { useState } from "react";
import api from "./api/axios";
import { ShieldCheck, Eye, EyeOff, CheckCircle } from "lucide-react";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      if (!token) {
        throw new Error("Login succeeded, but no access token was returned.");
      }

      // Save the authentication token
      localStorage.setItem("access_token", token);

      // Show successful login message
      setSuccess("Login successful! Redirecting to dashboard...");

      // Open dashboard after showing the message
      setTimeout(() => {
        onLogin();
      }, 1200);
    } catch (err) {
  const status = err.response?.status;
  const detail = err.response?.data?.detail;

  if (status === 401 || status === 400) {
    setError("Incorrect email or password. Please try again.");
  } else {
    setError(
      typeof detail === "string"
        ? detail
        : err.message || "Login failed. Please try again."
    );
  }
} finally {
  setLoading(false);
}
  };

  return (
    <main className="min-h-screen bg-[#080d18] text-white flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo and heading */}
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 shadow-lg shadow-blue-600/20">
            <ShieldCheck size={34} />
          </div>

          <h1 className="text-3xl font-bold tracking-tight">
            Churn Intelligence
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Sign in to your analytics platform
          </p>
        </div>

        {/* Login form */}
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-2xl border border-slate-700/70 bg-[#111827] p-7 shadow-2xl"
        >
          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Email address
            </label>

            <input
              id="email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#080d18] px-4 py-3 text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              placeholder="Enter your email"
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Password
            </label>

            <div className="flex items-center rounded-lg border border-slate-700 bg-[#080d18] transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-lg bg-transparent px-4 py-3 text-white outline-none"
                placeholder="Enter your password"
              />

              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                className="px-3 text-slate-400 transition hover:text-white"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff size={19} />
                ) : (
                  <Eye size={19} />
                )}
              </button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <p
              role="alert"
              className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400"
            >
              {error}
            </p>
          )}

          {/* Success message */}
          {success && (
            <div
              role="status"
              className="flex items-center gap-2 rounded-lg border border-green-500/20 bg-green-500/10 p-3 text-sm text-green-400"
            >
              <CheckCircle size={19} className="shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={loading || Boolean(success)}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Signing in..."
              : success
                ? "Login successful"
                : "Sign in"}
          </button>

          <p className="text-center text-xs text-slate-500">
            Secure access to your customer analytics
          </p>
        </form>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-slate-600">
          Customer Churn Intelligence & Prediction Platform
        </p>
      </div>
    </main>
  );
}
