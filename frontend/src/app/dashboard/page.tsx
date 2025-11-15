"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { BookOpen, Calendar, MessageSquare, Users, TrendingUp, CheckCircle } from "lucide-react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import { calculateAPCredits, isFirstYear } from "@/lib/apCredits";

export default function DashboardPage() {
  return (
    <ProtectedRoute pageName="your dashboard">
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { data: session } = useSession();
  const userName = session?.user?.name || "Student";
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch user data from database
    const fetchUserData = async () => {
      try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
          const data = await response.json();
          setUserData(data.user);
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (session?.user?.email) {
      fetchUserData();
    }
  }, [session]);

  // Determine if user is a first year
  const userIsFirstYear = userData ? isFirstYear(userData.entryYear) : true;

  // Calculate credits from AP courses
  const apCreditsTotal = userData?.apCredits ? calculateAPCredits(userData.apCredits) : 0;
  const currentCourses = [
    { code: "CS 2100", name: "Data Structures I", credits: 3, grade: "A" },
    { code: "MATH 1320", name: "Calculus II", credits: 4, grade: "B+" },
    { code: "ENWR 1510", name: "Academic Writing", credits: 3, grade: "A-" },
  ];

  const upcomingTasks = [
    { title: "CS 2100 Project Due", date: "Nov 20", priority: "high" },
    { title: "MATH 1320 Midterm", date: "Nov 22", priority: "high" },
    { title: "Register for Spring Classes", date: "Nov 25", priority: "medium" },
  ];

  const recommendedClubs = [
    { name: "UVA Computer Science Society", category: "Academic" },
    { name: "Hoos Hacking", category: "Tech" },
    { name: "Data Science Club", category: "Academic" },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-xl p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">Welcome back, {userName}!</h1>
        <p className="text-blue-100 text-lg">
          Your academic journey at UVA, simplified.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* GPA Card - Only show for non-first years or if uploaded transcript */}
        {(!userIsFirstYear || userData?.gpa) && (
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Current GPA</CardDescription>
              <CardTitle className="text-3xl">{userData?.gpa?.toFixed(2) || "N/A"}</CardTitle>
            </CardHeader>
            <CardContent>
              {userData?.gpa && (
                <div className="flex items-center text-sm text-green-600">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  <span>Track your progress</span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Credits Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Credits {userIsFirstYear ? "From AP" : "Completed"}</CardDescription>
            <CardTitle className="text-3xl">
              {userIsFirstYear ? apCreditsTotal : (userData?.creditsCompleted || apCreditsTotal)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {120 - (userIsFirstYear ? apCreditsTotal : (userData?.creditsCompleted || apCreditsTotal))} remaining
            </p>
          </CardContent>
        </Card>

        {userIsFirstYear && (
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>AP Courses</CardDescription>
              <CardTitle className="text-3xl">{userData?.apCredits?.length || 0}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">courses transferred</p>
            </CardContent>
          </Card>
        )}

        {!userIsFirstYear && (
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Current Load</CardDescription>
              <CardTitle className="text-3xl">15</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">credits this semester</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Plan Status</CardDescription>
            <CardTitle className="text-3xl flex items-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-green-600 font-medium">On Track!</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Courses */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Current Courses</CardTitle>
            <CardDescription>Fall 2024 Semester</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {currentCourses.map((course, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900">{course.code}</span>
                      <Badge variant="secondary">{course.credits} credits</Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{course.name}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-bold text-blue-600">{course.grade}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Link href="/plan">
                <Button className="w-full">View Full Plan</Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Upcoming</CardTitle>
            <CardDescription>Important dates & deadlines</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingTasks.map((task, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div
                    className={`w-2 h-2 rounded-full mt-2 ${
                      task.priority === "high" ? "bg-red-500" : "bg-yellow-500"
                    }`}
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{task.title}</p>
                    <p className="text-xs text-gray-500">{task.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/plan">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <CardTitle className="text-lg">Plan Editor</CardTitle>
              <CardDescription>Build your 4-year plan with validation</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/chat">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
                <MessageSquare className="w-6 h-6 text-purple-600" />
              </div>
              <CardTitle className="text-lg">AI Chat</CardTitle>
              <CardDescription>Get instant answers to UVA questions</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/clubs">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                <Users className="w-6 h-6 text-green-600" />
              </div>
              <CardTitle className="text-lg">Find Clubs</CardTitle>
              <CardDescription>Discover student organizations</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
          <CardHeader>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-2">
              <BookOpen className="w-6 h-6 text-orange-600" />
            </div>
            <CardTitle className="text-lg">Resources</CardTitle>
            <CardDescription>Academic support & career services</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Recommended Clubs */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Clubs</CardTitle>
          <CardDescription>Based on your interests in Computer Science</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recommendedClubs.map((club, index) => (
              <div
                key={index}
                className="p-4 border rounded-lg hover:border-blue-500 transition-colors"
              >
                <Badge className="mb-2">{club.category}</Badge>
                <h3 className="font-semibold text-gray-900">{club.name}</h3>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Link href="/clubs">
              <Button variant="outline" className="w-full">
                Browse All Clubs
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
