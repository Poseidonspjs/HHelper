"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { AlertCircle, CheckCircle, Search, Plus } from "lucide-react";

interface Course {
  courseCode: string;
  title: string;
  credits: number;
  prerequisites: string[];
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

  // Fetch available courses
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/courses`)
      .then((res) => res.json())
      .then((data) => setAvailableCourses(data.courses || []))
      .catch((err) => console.error("Failed to fetch courses:", err));
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

  // Filter courses by search
  const filteredCourses = availableCourses.filter(
    (course) =>
      course.courseCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
                    {filteredCourses.map((course, index) => (
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
                            className={`p-3 border rounded-lg cursor-move hover:border-blue-500 transition-colors ${
                              snapshot.isDragging ? "bg-blue-50 border-blue-500 shadow-lg" : "bg-white"
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="font-semibold text-sm">{course.courseCode}</p>
                                <p className="text-xs text-gray-600 mt-1">{course.title}</p>
                              </div>
                              <Badge variant="secondary">{course.credits}</Badge>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
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
                                              className={`p-3 rounded-lg cursor-move ${
                                                error
                                                  ? "bg-red-100 border-2 border-red-500"
                                                  : snapshot.isDragging
                                                  ? "bg-blue-50 border-2 border-blue-500 shadow-lg"
                                                  : "bg-white border border-gray-200"
                                              }`}
                                            >
                                              <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                  <p className="font-semibold text-sm">
                                                    {course.courseCode}
                                                  </p>
                                                  {courseData && (
                                                    <p className="text-xs text-gray-600 mt-1">
                                                      {courseData.title}
                                                    </p>
                                                  )}
                                                </div>
                                                <button
                                                  onClick={() => removeCourse(semesterKey, index)}
                                                  className="text-red-500 hover:text-red-700 text-xs"
                                                >
                                                  Remove
                                                </button>
                                              </div>
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
    </div>
  );
}

