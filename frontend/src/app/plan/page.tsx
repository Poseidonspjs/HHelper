"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { AlertCircle, CheckCircle, Search, Plus, Info } from "lucide-react";
import ProtectedRoute from "@/components/ProtectedRoute";

interface Course {
  courseCode: string;
  title: string;
  description?: string;
  credits: number;
  department: string;
  level: number;
  prerequisites: string[];
  semesters?: string[];
}

interface PlanCourse {
  courseCode: string;
  year: number;
  semester: string;
}

interface ValidationError {
  courseCode: string;
  year: number;
  semester: string;
  error: string;
  severity: string;
}

export default function PlanPage() {
  return (
    <ProtectedRoute pageName="the 4-year plan editor">
      <PlanContent />
    </ProtectedRoute>
  );
}

function PlanContent() {
  const [availableCourses, setAvailableCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [plan, setPlan] = useState<Record<string, PlanCourse[]>>({
    "1-Fall": [],
    "1-Spring": [],
    "2-Fall": [],
    "2-Spring": [],
    "3-Fall": [],
    "3-Spring": [],
    "4-Fall": [],
    "4-Spring": [],
  });
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<{courseCode: string; reason: string}[]>([]);
  const [suggestionsReasoning, setSuggestionsReasoning] = useState("");
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [coursesFetched, setCoursesFetched] = useState<Set<string>>(new Set());

  // Fetch AI suggestions on mount
  useEffect(() => {
    const loadSuggestions = async () => {
      setIsLoadingSuggestions(true);
      try {
        const userData = localStorage.getItem('pendingUserData');
        let major = 'Computer Science';
        let focusArea = 'General';
        
        if (userData) {
          const parsed = JSON.parse(userData);
          major = parsed.major || 'Computer Science';
          focusArea = parsed.focusArea || 'General';
        }
        
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/course-suggestions?major=${encodeURIComponent(major)}&focusArea=${encodeURIComponent(focusArea)}&year=1`
        );
        const data = await response.json();
        
        if (data.suggestions && Array.isArray(data.suggestions)) {
          setAiSuggestions(data.suggestions);
          setSuggestionsReasoning(data.reasoning || "");
        }
      } catch (err) {
        console.error("Failed to fetch AI suggestions:", err);
      } finally {
        setIsLoadingSuggestions(false);
      }
    };
    
    loadSuggestions();
  }, []);

  // Fetch available courses only when searching
  useEffect(() => {
    // Only search if there's a query with at least 2 characters
    if (searchQuery.length < 2) {
      setAvailableCourses([]);
      return;
    }

    // Debounce search
    const timer = setTimeout(() => {
      fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/courses?search=${encodeURIComponent(searchQuery)}&limit=50`)
        .then((res) => res.json())
        .then((data) => {
          console.log("Search results:", data.courses?.length || 0, "courses for query:", searchQuery);
          setAvailableCourses(data.courses || []);
        })
        .catch((err) => console.error("Failed to fetch courses:", err));
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load generated plan from localStorage (if available)
  useEffect(() => {
    const storedPlan = localStorage.getItem('generatedPlan');
    if (storedPlan) {
      try {
        const generatedPlan = JSON.parse(storedPlan);
        
        // Convert the generated plan format to our plan format
        const newPlan: Record<string, PlanCourse[]> = {
          "1-Fall": [],
          "1-Spring": [],
          "2-Fall": [],
          "2-Spring": [],
          "3-Fall": [],
          "3-Spring": [],
          "4-Fall": [],
          "4-Spring": [],
        };

        // Collect all unique course codes
        const allCourseCodes = new Set<string>();

        // Map year1, year2, year3, year4 to our format
        const years = [
          { key: 'year1', num: 1 },
          { key: 'year2', num: 2 },
          { key: 'year3', num: 3 },
          { key: 'year4', num: 4 },
        ];

        years.forEach(({ key, num }) => {
          const yearData = generatedPlan[key];
          if (yearData) {
            // Fall semester
            if (yearData.fall && Array.isArray(yearData.fall)) {
              newPlan[`${num}-Fall`] = yearData.fall.map((course: any) => {
                allCourseCodes.add(course.courseCode);
                return {
                  courseCode: course.courseCode,
                  year: num,
                  semester: 'Fall',
                };
              });
            }
            // Spring semester
            if (yearData.spring && Array.isArray(yearData.spring)) {
              newPlan[`${num}-Spring`] = yearData.spring.map((course: any) => {
                allCourseCodes.add(course.courseCode);
                return {
                  courseCode: course.courseCode,
                  year: num,
                  semester: 'Spring',
                };
              });
            }
          }
        });

        setPlan(newPlan);

        // Fetch course details for all courses in the plan (batch request)
        if (allCourseCodes.size > 0) {
          const codes = Array.from(allCourseCodes);
          console.log("Fetching details for", codes.length, "courses:", codes);
          
          // Mark all codes as being fetched
          setCoursesFetched(new Set(codes));
          
          // Fetch all courses in one batch request
          Promise.all(
            codes.map(code => 
              fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/courses?search=${encodeURIComponent(code)}&limit=5`)
                .then(res => res.json())
                .then(data => {
                  // Find exact match (case-insensitive)
                  if (data.courses && data.courses.length > 0) {
                    const exactMatch = data.courses.find((c: Course) => 
                      c.courseCode.toLowerCase().replace(/\s+/g, '') === code.toLowerCase().replace(/\s+/g, '')
                    );
                    if (exactMatch) {
                      console.log(`✓ Found: ${code} -> ${exactMatch.courseCode}`);
                      return exactMatch;
                    }
                    // If no exact match, try first result if it's close enough
                    const firstCourse = data.courses[0];
                    if (firstCourse.courseCode.toLowerCase().startsWith(code.toLowerCase().replace(/\s+/g, ''))) {
                      console.log(`≈ Close match: ${code} -> ${firstCourse.courseCode}`);
                      return firstCourse;
                    }
                  }
                  console.warn(`✗ Not found: ${code}`);
                  return null;
                })
                .catch(err => {
                  console.error(`✗ Error fetching ${code}:`, err);
                  return null;
                })
            )
          ).then(fetchedCourses => {
            const validCourses = fetchedCourses.filter(c => c !== null) as Course[];
            console.log(`Successfully fetched ${validCourses.length}/${codes.length} course details`);
            
            setAvailableCourses(prev => {
              // Merge with existing, avoiding duplicates
              const combined = [...prev];
              validCourses.forEach(course => {
                if (!combined.some(c => c.courseCode === course.courseCode)) {
                  combined.push(course);
                }
              });
              return combined;
            });
          });
        }
        
        // Clear the stored plan after loading (so it doesn't reload on every visit)
        // Comment this out if you want to keep the plan persistent
        // localStorage.removeItem('generatedPlan');
        
      } catch (error) {
        console.error('Error loading generated plan:', error);
      }
    }
  }, []);

  // Handle drag and drop
  const onDragEnd = (result: DropResult) => {
    const { source, destination } = result;

    if (!destination) return;

    // Moving within available courses - do nothing
    if (source.droppableId === "available" && destination.droppableId === "available") {
      return;
    }

    // Adding course from available to plan
    if (source.droppableId === "available" && destination.droppableId !== "available") {
      const course = filteredCourses[source.index];
      const [year, semester] = destination.droppableId.split("-");
      
      const newPlan = { ...plan };
      newPlan[destination.droppableId] = [
        ...newPlan[destination.droppableId],
        {
          courseCode: course.courseCode,
          year: parseInt(year),
          semester,
        },
      ];
      setPlan(newPlan);
      return;
    }

    // Moving course within plan or between semesters
    if (source.droppableId !== "available" && destination.droppableId !== "available") {
      const newPlan = { ...plan };
      const sourceCourses = [...newPlan[source.droppableId]];
      const [movedCourse] = sourceCourses.splice(source.index, 1);

      if (source.droppableId === destination.droppableId) {
        // Same semester
        sourceCourses.splice(destination.index, 0, movedCourse);
        newPlan[source.droppableId] = sourceCourses;
      } else {
        // Different semester
        const [year, semester] = destination.droppableId.split("-");
        movedCourse.year = parseInt(year);
        movedCourse.semester = semester;
        
        newPlan[source.droppableId] = sourceCourses;
        const destCourses = [...newPlan[destination.droppableId]];
        destCourses.splice(destination.index, 0, movedCourse);
        newPlan[destination.droppableId] = destCourses;
      }

      setPlan(newPlan);
    }
  };

  // Remove course from plan
  const removeCourse = (semesterKey: string, index: number) => {
    const newPlan = { ...plan };
    newPlan[semesterKey].splice(index, 1);
    setPlan(newPlan);
  };

  // Validate plan
  const validatePlan = async () => {
    setIsValidating(true);
    
    // Flatten plan for API
    const courses: PlanCourse[] = [];
    Object.entries(plan).forEach(([key, semesterCourses]) => {
      courses.push(...semesterCourses);
    });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/validate-plan`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ courses, startYear: 2024 }),
        }
      );

      const result = await response.json();
      setValidationErrors([...result.errors, ...result.warnings]);
    } catch (err) {
      console.error("Validation failed:", err);
    } finally {
      setIsValidating(false);
    }
  };

  // No need for filtering - already filtered by API
  const filteredCourses = availableCourses;

  // Calculate credits for a semester
  const getSemesterCredits = (semesterKey: string) => {
    return plan[semesterKey].reduce((total, course) => {
      const courseData = availableCourses.find((c) => c.courseCode === course.courseCode);
      return total + (courseData?.credits || 3);
    }, 0);
  };

  // Check if a course has errors
  const hasError = (courseCode: string, semesterKey: string) => {
    const [year, semester] = semesterKey.split("-");
    return validationErrors.some(
      (err) =>
        err.courseCode === courseCode &&
        err.year === parseInt(year) &&
        err.semester === semester &&
        err.severity === "error"
    );
  };

  // Show course details
  const showCourseDetails = (courseCode: string) => {
    const course = availableCourses.find((c) => c.courseCode === courseCode);
    if (course) {
      setSelectedCourse(course);
      setShowCourseModal(true);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">4-Year Plan Editor</h1>
          <p className="text-gray-600 mt-1">
            Drag courses from the catalog to plan your semesters
          </p>
        </div>
        <Button onClick={validatePlan} disabled={isValidating} size="lg">
          {isValidating ? "Validating..." : "Validate Plan"}
        </Button>
      </div>

      {/* Validation Results */}
      {validationErrors.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              Validation Issues ({validationErrors.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {validationErrors.map((error, index) => (
                <div
                  key={index}
                  className={`p-3 rounded ${
                    error.severity === "error" ? "bg-red-100" : "bg-yellow-100"
                  }`}
                >
                  <p className="font-semibold">
                    {error.courseCode || "General"} - Year {error.year} {error.semester}
                  </p>
                  <p className="text-sm">{error.error}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Available Courses Sidebar */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Course Catalog</CardTitle>
              <div className="relative mt-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search courses..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardHeader>
            <CardContent>
              <Droppable droppableId="available">
                {(provided) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className="space-y-2 max-h-[600px] overflow-y-auto"
                  >
                    {searchQuery.length < 2 ? (
                      <div className="flex flex-col py-4">
                        <div className="flex flex-col items-center justify-center py-6 text-gray-400 text-center border-b">
                          <Search className="w-10 h-10 mb-2 opacity-50" />
                          <p className="text-sm font-medium">Search for courses</p>
                          <p className="text-xs mt-1">Type at least 2 characters to see results</p>
                        </div>
                        
                        {/* AI Suggestions */}
                        {isLoadingSuggestions ? (
                          <div className="py-8 text-center">
                            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3"></div>
                            <p className="text-sm text-gray-500">AI is generating course suggestions...</p>
                          </div>
                        ) : aiSuggestions.length > 0 ? (
                          <div className="mt-4 space-y-3">
                            <div className="px-2">
                              <div className="flex items-center gap-2 mb-3">
                                <span className="text-lg">✨</span>
                                <h3 className="font-semibold text-sm">AI Recommended for You</h3>
                              </div>
                              {suggestionsReasoning && (
                                <p className="text-xs text-gray-600 mb-3 italic">
                                  {suggestionsReasoning}
                                </p>
                              )}
                            </div>
                            {aiSuggestions.map((suggestion, idx) => (
                              <div
                                key={idx}
                                className="p-3 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 hover:border-blue-400 transition-all cursor-pointer"
                                onClick={() => {
                                  setSearchQuery(suggestion.courseCode);
                                }}
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <p className="font-semibold text-sm text-blue-900">
                                      {suggestion.courseCode}
                                    </p>
                                    <p className="text-xs text-gray-700 mt-1">
                                      {suggestion.reason}
                                    </p>
                                  </div>
                                  <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-800">
                                    AI Pick
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : null}
                      </div>
                    ) : filteredCourses.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-12 text-gray-400 text-center">
                        <Search className="w-12 h-12 mb-3 opacity-50" />
                        <p className="text-sm font-medium">No courses found</p>
                        <p className="text-xs mt-1">Try a different search term</p>
                      </div>
                    ) : (
                      filteredCourses.map((course, index) => (
                        <Draggable
                          key={course.courseCode}
                          draggableId={course.courseCode}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`p-3 border rounded-lg group relative ${
                                snapshot.isDragging ? "bg-blue-50 border-blue-500 shadow-lg cursor-grabbing" : "bg-white cursor-grab hover:border-blue-500"
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <p className="font-semibold text-sm">{course.courseCode}</p>
                                  <p className="text-xs text-gray-600 mt-1 line-clamp-2">{course.title}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge variant="secondary">{course.credits}</Badge>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      showCourseDetails(course.courseCode);
                                    }}
                                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-blue-100 rounded"
                                    title="View details"
                                  >
                                    <Info className="w-4 h-4 text-blue-600" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))
                    )}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </CardContent>
          </Card>

          {/* 4-Year Grid */}
          <div className="lg:col-span-3 space-y-6">
            {[1, 2, 3, 4].map((year) => (
              <Card key={year}>
                <CardHeader>
                  <CardTitle>Year {year}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {["Fall", "Spring"].map((semester) => {
                      const semesterKey = `${year}-${semester}`;
                      const credits = getSemesterCredits(semesterKey);
                      
                      return (
                        <div key={semester} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold">{semester}</h3>
                            <Badge
                              variant={
                                credits < 12 || credits > 18 ? "destructive" : "secondary"
                              }
                            >
                              {credits} credits
                            </Badge>
                          </div>

                          <Droppable droppableId={semesterKey}>
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.droppableProps}
                                className={`min-h-[200px] p-4 border-2 border-dashed rounded-lg ${
                                  snapshot.isDraggingOver
                                    ? "bg-blue-50 border-blue-400"
                                    : "bg-gray-50 border-gray-300"
                                }`}
                              >
                                {plan[semesterKey].length === 0 ? (
                                  <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                                    <Plus className="w-4 h-4 mr-2" />
                                    Drag courses here
                                  </div>
                                ) : (
                                  <div className="space-y-2">
                                    {plan[semesterKey].map((course, index) => {
                                      const courseData = availableCourses.find(
                                        (c) => c.courseCode === course.courseCode
                                      );
                                      const error = hasError(course.courseCode, semesterKey);

                                      return (
                                        <Draggable
                                          key={`${semesterKey}-${course.courseCode}`}
                                          draggableId={`${semesterKey}-${course.courseCode}`}
                                          index={index}
                                        >
                                          {(provided, snapshot) => (
                                            <div
                                              ref={provided.innerRef}
                                              {...provided.draggableProps}
                                              {...provided.dragHandleProps}
                                              className={`p-3 rounded-lg group relative ${
                                                error
                                                  ? "bg-red-100 border-2 border-red-500 cursor-move"
                                                  : snapshot.isDragging
                                                  ? "bg-blue-50 border-2 border-blue-500 shadow-lg cursor-grabbing"
                                                  : "bg-white border border-gray-200 cursor-grab hover:border-blue-400"
                                              }`}
                                            >
                                              <div className="flex items-start justify-between">
                                                <div 
                                                  className="flex-1 cursor-pointer"
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (courseData) {
                                                      showCourseDetails(course.courseCode);
                                                    }
                                                  }}
                                                >
                                                  <p className="font-semibold text-sm flex items-center gap-2">
                                                    {course.courseCode}
                                                    {courseData && (
                                                      <Badge variant="outline" className="text-xs">
                                                        {courseData.credits} cr
                                                      </Badge>
                                                    )}
                                                  </p>
                                                  {courseData ? (
                                                    <p className="text-xs text-gray-600 mt-1 line-clamp-1 hover:text-blue-600">
                                                      {courseData.title}
                                                    </p>
                                                  ) : coursesFetched.has(course.courseCode) ? (
                                                    <p className="text-xs text-orange-600 mt-1 italic">
                                                      Course not in catalog
                                                    </p>
                                                  ) : (
                                                    <p className="text-xs text-gray-400 mt-1 italic">
                                                      Loading...
                                                    </p>
                                                  )}
                                                </div>
                                                <button
                                                  onClick={(e) => {
                                                    e.stopPropagation();
                                                    removeCourse(semesterKey, index);
                                                  }}
                                                  className="text-red-500 hover:text-red-700 text-xs px-2 py-1 hover:bg-red-50 rounded transition-colors"
                                                >
                                                  Remove
                                                </button>
                                              </div>
                                              {error && (
                                                <p className="text-xs text-red-700 mt-2">
                                                  ⚠ Prerequisite issue
                                                </p>
                                              )}
                                            </div>
                                          )}
                                        </Draggable>
                                      );
                                    })}
                                  </div>
                                )}
                                {provided.placeholder}
                              </div>
                            )}
                          </Droppable>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </DragDropContext>

      {/* Course Detail Modal */}
      <Dialog open={showCourseModal} onOpenChange={setShowCourseModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          {selectedCourse && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>{selectedCourse.courseCode}: {selectedCourse.title}</span>
                  <Badge variant="secondary" className="ml-2">
                    {selectedCourse.credits} Credits
                  </Badge>
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4 mt-4">
                <div>
                  <h4 className="font-semibold text-sm text-gray-700 mb-2">Course Information</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Department:</span>
                      <p className="font-medium">{selectedCourse.department}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Level:</span>
                      <p className="font-medium">{selectedCourse.level}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Credits:</span>
                      <p className="font-medium">{selectedCourse.credits}</p>
                    </div>
                    {selectedCourse.semesters && selectedCourse.semesters.length > 0 && (
                      <div>
                        <span className="text-gray-500">Typically Offered:</span>
                        <p className="font-medium">{selectedCourse.semesters.join(", ")}</p>
                      </div>
                    )}
                  </div>
                </div>

                {selectedCourse.description && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Description</h4>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {selectedCourse.description}
                    </p>
                  </div>
                )}

                {selectedCourse.prerequisites && selectedCourse.prerequisites.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Prerequisites</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedCourse.prerequisites.map((prereq, idx) => (
                        <Badge key={idx} variant="outline">
                          {prereq}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {!selectedCourse.description && !selectedCourse.prerequisites?.length && (
                  <div className="text-center py-4 text-gray-400">
                    <p className="text-sm">No additional details available for this course.</p>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

