"use client";

import Link from "next/link";
import { BookOpen, Calendar, MessageSquare, Users, LogOut } from "lucide-react";
import { useSession, signOut } from "next-auth/react";
import { useState } from "react";
import AuthModal from "./AuthModal";

export default function Header() {
  const { data: session } = useSession();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  return (
    <>
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link href="/" className="flex items-center">
                <span className="text-2xl font-bold text-blue-600">
                  HoosHelper
                </span>
              </Link>

              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
                >
                  <BookOpen className="w-4 h-4 mr-2" />
                  Dashboard
                </Link>
                <Link
                  href="/plan"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  4-Year Plan
                </Link>
                <Link
                  href="/chat"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Chat
                </Link>
                <Link
                  href="/clubs"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Clubs
                </Link>
              </div>
            </div>

            {/* Auth Section */}
            <div className="flex items-center space-x-4">
              {session ? (
                <>
                  <span className="text-sm text-gray-700">
                    {session.user?.email}
                  </span>
                  <button
                    onClick={() => signOut()}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Log Out
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  Log In / Sign Up
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </>
  );
}
