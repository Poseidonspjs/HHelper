"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Mail, Globe, Instagram, Users as UsersIcon } from "lucide-react";
import ProtectedRoute from "@/components/ProtectedRoute";

interface Club {
  id?: string;
  name: string;
  description?: string;
  category?: string;
  tags?: string[];
  email?: string;
  website?: string;
  instagramHandle?: string;
}

export default function ClubsPage() {
  return (
    <ProtectedRoute pageName="the clubs directory">
      <ClubsContent />
    </ProtectedRoute>
  );
}

function ClubsContent() {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [filteredClubs, setFilteredClubs] = useState<Club[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const categories = ["All", "Academic", "Tech", "Service", "Arts", "Business", "Recreation", "Social"];

  // Fetch clubs
  useEffect(() => {
    const fetchClubs = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/clubs`
        );
        const data = await response.json();
        setClubs(data.clubs || []);
        setFilteredClubs(data.clubs || []);
      } catch (err) {
        console.error("Failed to fetch clubs:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchClubs();
  }, []);

  // Filter clubs
  useEffect(() => {
    let filtered = clubs;

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (club) =>
          club.name.toLowerCase().includes(query) ||
          club.description?.toLowerCase().includes(query) ||
          club.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    // Filter by category
    if (selectedCategory && selectedCategory !== "All") {
      filtered = filtered.filter((club) => club.category === selectedCategory);
    }

    setFilteredClubs(filtered);
  }, [searchQuery, selectedCategory, clubs]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading clubs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-full mb-4">
          <UsersIcon className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Discover Clubs</h1>
        <p className="text-gray-600 mt-2">
          Explore 100+ student organizations at UVA
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search clubs by name, description, or tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 text-lg h-12"
              />
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category || (category === "All" && !selectedCategory) ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category === "All" ? null : category)}
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-gray-600">
          Showing <span className="font-semibold">{filteredClubs.length}</span> clubs
        </p>
      </div>

      {/* Clubs Grid */}
      {filteredClubs.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <UsersIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No clubs found</h3>
            <p className="text-gray-600">
              Try adjusting your search or filters
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredClubs.map((club, index) => (
            <Card key={club.id || index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <Badge className="mb-2">{club.category || "General"}</Badge>
                </div>
                <CardTitle className="text-lg">{club.name}</CardTitle>
                <CardDescription className="line-clamp-3">
                  {club.description || "No description available"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Tags */}
                {club.tags && club.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {club.tags.slice(0, 3).map((tag, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Contact Links */}
                <div className="space-y-2">
                  {club.website && (
                    <a
                      href={club.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Globe className="w-4 h-4" />
                      Website
                    </a>
                  )}
                  {club.email && (
                    <a
                      href={`mailto:${club.email}`}
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Mail className="w-4 h-4" />
                      {club.email}
                    </a>
                  )}
                  {club.instagramHandle && (
                    <a
                      href={`https://instagram.com/${club.instagramHandle}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Instagram className="w-4 h-4" />
                      @{club.instagramHandle}
                    </a>
                  )}
                </div>

                {/* Join Button */}
                <Button className="w-full mt-4" variant="outline">
                  Learn More
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Stats Footer */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-600">{clubs.length}+</p>
              <p className="text-gray-600 mt-1">Student Organizations</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600">
                {new Set(clubs.map((c) => c.category)).size}
              </p>
              <p className="text-gray-600 mt-1">Categories</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600">100%</p>
              <p className="text-gray-600 mt-1">Student-Led</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

