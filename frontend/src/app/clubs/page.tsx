"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Search, Mail, Globe, Instagram, Users as UsersIcon, X } from "lucide-react";
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
  const [searchInput, setSearchInput] = useState(""); // What user is typing
  const [searchQuery, setSearchQuery] = useState(""); // Actual search query sent to API
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedClub, setSelectedClub] = useState<Club | null>(null);
  const [showClubModal, setShowClubModal] = useState(false);
  const [totalClubs, setTotalClubs] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  
  const CLUBS_PER_PAGE = 25;

  const categories = ["All", "Academic", "Tech", "Service", "Arts", "Business", "Recreation", "Social"];

  // Fetch clubs with pagination
  const fetchClubs = async (loadMore = false) => {
    const currentOffset = loadMore ? offset : 0;
    
    if (loadMore) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
    }
    
    try {
      const params = new URLSearchParams({
        limit: CLUBS_PER_PAGE.toString(),
        offset: currentOffset.toString(),
      });
      
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      if (selectedCategory && selectedCategory !== "All") {
        params.append('category', selectedCategory);
      }
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/clubs?${params.toString()}`
      );
      const data = await response.json();
      
      if (loadMore) {
        setClubs(prev => [...prev, ...(data.clubs || [])]);
      } else {
        setClubs(data.clubs || []);
      }
      
      setTotalClubs(data.total || 0);
      setHasMore(data.hasMore || false);
      setOffset(loadMore ? currentOffset + CLUBS_PER_PAGE : CLUBS_PER_PAGE);
      
    } catch (err) {
      console.error("Failed to fetch clubs:", err);
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  // Initial load and filter changes (only triggers on searchQuery, not searchInput)
  useEffect(() => {
    setOffset(0);
    fetchClubs(false);
  }, [searchQuery, selectedCategory]);

  // Handle search submit (Enter key or button click)
  const handleSearch = () => {
    setSearchQuery(searchInput);
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Load more handler
  const handleLoadMore = () => {
    fetchClubs(true);
  };

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
          Explore {totalClubs || "1,000+"}  student organizations at UVA
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  placeholder="Search clubs by name, description, or tags... (press Enter)"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-10 pr-10 text-lg h-12"
                />
                {searchInput && (
                  <button
                    onClick={() => {
                      setSearchInput("");
                      setSearchQuery("");
                    }}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    type="button"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
              <Button 
                onClick={handleSearch}
                className="h-12 px-6"
                type="button"
              >
                Search
              </Button>
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
          Showing <span className="font-semibold">{clubs.length}</span> of <span className="font-semibold">{totalClubs}</span> clubs
        </p>
      </div>

      {/* Clubs Grid */}
      {clubs.length === 0 ? (
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
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clubs.map((club, index) => (
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

                {/* Learn More Button */}
                <Button 
                  className="w-full mt-4" 
                  variant="outline"
                  onClick={() => {
                    setSelectedClub(club);
                    setShowClubModal(true);
                  }}
                >
                  Learn More
                </Button>
              </CardContent>
            </Card>
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="flex justify-center mt-8">
              <Button 
                onClick={handleLoadMore}
                disabled={isLoadingMore}
                size="lg"
                className="px-8"
              >
                {isLoadingMore ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Loading...
                  </>
                ) : (
                  <>
                    Load More ({totalClubs - clubs.length} remaining)
                  </>
                )}
              </Button>
            </div>
          )}
        </>
      )}

      {/* Stats Footer */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-600">{totalClubs || clubs.length}+</p>
              <p className="text-gray-600 mt-1">Student Organizations</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600">
                {new Set(clubs.map((c) => c.category)).size}+
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

      {/* Club Details Modal */}
      <Dialog open={showClubModal} onOpenChange={setShowClubModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          {selectedClub && (
            <>
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold">{selectedClub.name}</DialogTitle>
                {selectedClub.category && (
                  <div className="flex gap-2 mt-2">
                    <Badge className="text-sm">{selectedClub.category}</Badge>
                  </div>
                )}
              </DialogHeader>

              <div className="space-y-6 mt-4">
                {/* Description */}
                {selectedClub.description && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">About</h4>
                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                      {selectedClub.description}
                    </p>
                  </div>
                )}

                {/* Tags */}
                {selectedClub.tags && selectedClub.tags.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Categories & Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedClub.tags.map((tag, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Contact Information */}
                <div>
                  <h4 className="font-semibold text-sm text-gray-700 mb-3">Connect With Us</h4>
                  <div className="space-y-3">
                    {selectedClub.website && (
                      <a
                        href={selectedClub.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors group"
                      >
                        <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200">
                          <Globe className="w-5 h-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900">Website</p>
                          <p className="text-xs text-gray-500 truncate">{selectedClub.website}</p>
                        </div>
                      </a>
                    )}

                    {selectedClub.email && (
                      <a
                        href={`mailto:${selectedClub.email}`}
                        className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors group"
                      >
                        <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200">
                          <Mail className="w-5 h-5 text-green-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900">Email</p>
                          <p className="text-xs text-gray-500 truncate">{selectedClub.email}</p>
                        </div>
                      </a>
                    )}

                    {selectedClub.instagramHandle && (
                      <a
                        href={`https://instagram.com/${selectedClub.instagramHandle}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors group"
                      >
                        <div className="p-2 bg-pink-100 rounded-lg group-hover:bg-pink-200">
                          <Instagram className="w-5 h-5 text-pink-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900">Instagram</p>
                          <p className="text-xs text-gray-500">@{selectedClub.instagramHandle}</p>
                        </div>
                      </a>
                    )}

                    {!selectedClub.website && !selectedClub.email && !selectedClub.instagramHandle && (
                      <div className="text-center py-4 text-gray-400">
                        <p className="text-sm">No contact information available</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Call to Action */}
                <div className="pt-4 border-t">
                  <p className="text-xs text-gray-500 text-center">
                    Interested? Reach out through the contact methods above to learn more!
                  </p>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

