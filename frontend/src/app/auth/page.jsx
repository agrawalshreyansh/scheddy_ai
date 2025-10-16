'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const Page = () => {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    fullName: '',
    rememberMe: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        // Sign up logic
        const response = await fetch(`${API_BASE_URL}/users/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: formData.username,
            email: formData.email,
            password: formData.password,
            full_name: formData.fullName,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Sign up failed');
        }

        const userData = await response.json();
        localStorage.setItem('user', JSON.stringify(userData));
        router.push('/calendar');
      } else {
        // Login logic
        const response = await fetch(`${API_BASE_URL}/users/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: formData.username,
            password: formData.password,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Login failed');
        }

        const userData = await response.json();
        localStorage.setItem('user', JSON.stringify(userData));
        router.push('/calendar');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setError('');
  };

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden bg-[#101922] text-on-surface-dark">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-10 p-4 sm:px-6 md:px-8">
        <nav className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 text-[#137fec]">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M4 42.4379C4 42.4379 14.0962 36.0744 24 41.1692C35.0664 46.8624 44 42.2078 44 42.2078L44 7.01134C44 7.01134 35.068 11.6577 24.0031 5.96913C14.0971 0.876274 4 7.27094 4 7.27094L4 42.4379Z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white">Scheddy</h2>
          </div>
          <div className="hidden items-center gap-6 md:flex">
            <Link
              className="text-sm font-medium text-gray-400 hover:text-[#137fec] transition-colors"
              href="#"
            >
              Product
            </Link>
            <Link
              className="text-sm font-medium text-gray-400 hover:text-[#137fec] transition-colors"
              href="#"
            >
              Pricing
            </Link>
            <Link
              className="text-sm font-medium text-gray-400 hover:text-[#137fec] transition-colors"
              href="#"
            >
              Resources
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={toggleMode}
              className="rounded-lg bg-[#137fec]/20 px-4 py-2 text-sm font-bold text-[#137fec] hover:bg-[#137fec]/30 transition-colors"
            >
              {isSignUp ? 'Log in' : 'Sign up'}
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 items-center justify-center py-20 px-4">
        <div className="w-full max-w-md space-y-8 rounded-xl bg-[#1a2332] p-8 shadow-2xl shadow-black/20 border border-gray-800">
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight text-white">
              {isSignUp ? 'Create your account' : 'Log in to Scheddy'}
            </h1>
            <p className="mt-2 text-sm text-gray-400">
              {isSignUp
                ? 'Start managing your schedule efficiently'
                : 'Welcome back! Please enter your details.'}
            </p>
          </div>

          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/50 p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="fullName">
                  Full Name
                </label>
                <input
                  autoComplete="name"
                  className="block w-full rounded-lg border border-gray-700 bg-[#101922] py-3 px-4 text-white placeholder-gray-500 focus:border-[#137fec] focus:ring-1 focus:ring-[#137fec] focus:outline-none transition-colors"
                  id="fullName"
                  name="fullName"
                  placeholder="Enter your full name"
                  required
                  type="text"
                  value={formData.fullName}
                  onChange={handleChange}
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="username">
                Username
              </label>
              <input
                autoComplete="username"
                className="block w-full rounded-lg border border-gray-700 bg-[#101922] py-3 px-4 text-white placeholder-gray-500 focus:border-[#137fec] focus:ring-1 focus:ring-[#137fec] focus:outline-none transition-colors"
                id="username"
                name="username"
                placeholder="Enter your username"
                required
                type="text"
                value={formData.username}
                onChange={handleChange}
              />
            </div>

            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="email">
                  Email
                </label>
                <input
                  autoComplete="email"
                  className="block w-full rounded-lg border border-gray-700 bg-[#101922] py-3 px-4 text-white placeholder-gray-500 focus:border-[#137fec] focus:ring-1 focus:ring-[#137fec] focus:outline-none transition-colors"
                  id="email"
                  name="email"
                  placeholder="Enter your email"
                  required
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2" htmlFor="password">
                Password
              </label>
              <input
                autoComplete={isSignUp ? 'new-password' : 'current-password'}
                className="block w-full rounded-lg border border-gray-700 bg-[#101922] py-3 px-4 text-white placeholder-gray-500 focus:border-[#137fec] focus:ring-1 focus:ring-[#137fec] focus:outline-none transition-colors"
                id="password"
                name="password"
                placeholder="Enter your password"
                required
                type="password"
                value={formData.password}
                onChange={handleChange}
              />
              {isSignUp && (
                <p className="mt-1 text-xs text-gray-500">
                  Password must be at least 8 characters long
                </p>
              )}
            </div>

            {!isSignUp && (
              <div className="flex items-center">
                <input
                  className="h-4 w-4 rounded border-gray-600 bg-[#101922] text-[#137fec] focus:ring-[#137fec] focus:ring-offset-[#1a2332]"
                  id="remember-me"
                  name="rememberMe"
                  type="checkbox"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
                <label
                  className="ml-2 block text-sm text-gray-400"
                  htmlFor="remember-me"
                >
                  Remember me
                </label>
              </div>
            )}

            <div>
              <button
                className="flex w-full justify-center rounded-lg bg-[#137fec] py-3 px-4 text-base font-bold text-white shadow-sm hover:bg-[#0d6fd6] focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:ring-offset-2 focus:ring-offset-[#1a2332] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                type="submit"
                disabled={loading}
              >
                {loading ? 'Please wait...' : isSignUp ? 'Sign up' : 'Log in'}
              </button>
            </div>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-[#1a2332] px-2 text-gray-400">
                {isSignUp ? 'Already have an account?' : "Don't have an account?"}
              </span>
            </div>
          </div>

          <button
            onClick={toggleMode}
            className="w-full rounded-lg border-2 border-[#137fec] py-3 px-4 text-base font-bold text-[#137fec] hover:bg-[#137fec]/10 focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:ring-offset-2 focus:ring-offset-[#1a2332] transition-colors"
          >
            {isSignUp ? 'Log in instead' : 'Create new account'}
          </button>
        </div>
      </main>
    </div>
  );
};

export default Page;