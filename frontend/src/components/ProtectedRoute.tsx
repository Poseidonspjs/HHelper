"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect, ReactNode } from "react";
import AuthModal from "./AuthModal";
import { CheckCircle } from "lucide-react";

interface ProtectedRouteProps {
  children: ReactNode;
  pageName?: string;
}

export default function ProtectedRoute({ children, pageName = "this page" }: ProtectedRouteProps) {
  const { data: session, status } = useSession();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated") {
      setShowAuthModal(true);
    }
  }, [status]);

  if (status === "loading") {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center max-w-md">
            <div className="mb-6">
              <CheckCircle className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Authentication Required
              </h1>
              <p className="text-gray-600">
                Please log in or create an account to access {pageName}.
              </p>
            </div>
            <button
              onClick={() => setShowAuthModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Log In / Sign Up
            </button>
          </div>
        </div>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    );
  }

  return <>{children}</>;
}
