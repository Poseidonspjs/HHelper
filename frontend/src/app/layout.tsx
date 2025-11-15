import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { BookOpen, Calendar, MessageSquare, Users } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HoosHelper - Your UVA Academic Assistant",
  description: "AI-powered student success platform for UVA students",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          {/* Navigation */}
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
                      href="/"
                      className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors"
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
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

