"""
HoosHelper Backend API
FastAPI application with RAG, prerequisite validation, and course planning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
import json

# AI/ML imports
from anthropic import Anthropic
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client, Client

# Initialize FastAPI
app = FastAPI(
    title="HoosHelper API",
    description="AI-powered student success platform for UVA",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# Initialize Supabase (for vector store)
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase_client: Optional[Client] = None

if supabase_url and supabase_key:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Failed to initialize Supabase: {e}")

# ============ MODELS ============

class Course(BaseModel):
    courseCode: str
    title: str
    description: Optional[str] = None
    credits: int = 3
    department: str
    level: int
    prerequisites: List[str] = []

class PlanCourse(BaseModel):
    courseCode: str
    year: int  # 1-4
    semester: str  # "Fall" or "Spring"

class StudentPlan(BaseModel):
    courses: List[PlanCourse]
    startYear: int = 2024

class ValidationError(BaseModel):
    courseCode: str
    year: int
    semester: str
    error: str
    severity: str = "error"  # "error" or "warning"

class PlanValidationResult(BaseModel):
    isValid: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    sessionId: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    context: Optional[List[Dict[str, Any]]] = None

class ClubFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []

# ============ PREREQUISITE VALIDATOR ============

class PrerequisiteValidator:
    """Graph-based prerequisite validation"""
    
    def __init__(self):
        self.course_graph = self._build_course_graph()
    
    def _build_course_graph(self) -> Dict[str, List[str]]:
        """Build prerequisite graph from course data"""
        # In production, this would query the database
        # For demo, we'll use a sample graph
        return {
            "CS 1110": [],
            "CS 2100": ["CS 1110"],
            "CS 2120": ["CS 2100"],
            "CS 3100": ["CS 2100", "CS 2120"],
            "CS 4750": ["CS 2120"],
            "CS 4710": ["CS 2120"],
            "MATH 1310": [],
            "MATH 1320": ["MATH 1310"],
            "MATH 2310": ["MATH 1320"],
            "APMA 3080": ["MATH 1320"],
        }
    
    def validate_plan(self, plan: StudentPlan) -> PlanValidationResult:
        """Validate entire plan for prerequisite violations"""
        errors = []
        warnings = []
        
        # Build timeline of courses
        timeline = {}
        for course in plan.courses:
            semester_key = f"{course.year}-{'1' if course.semester == 'Fall' else '2'}"
            if semester_key not in timeline:
                timeline[semester_key] = []
            timeline[semester_key].append(course.courseCode)
        
        # Check prerequisites in chronological order
        completed = set()
        for semester_key in sorted(timeline.keys()):
            courses_this_semester = timeline[semester_key]
            
            for course_code in courses_this_semester:
                prereqs = self.course_graph.get(course_code, [])
                
                for prereq in prereqs:
                    if prereq not in completed and prereq not in courses_this_semester:
                        # Find the course details
                        course_info = next(
                            (c for c in plan.courses if c.courseCode == course_code),
                            None
                        )
                        if course_info:
                            errors.append(ValidationError(
                                courseCode=course_code,
                                year=course_info.year,
                                semester=course_info.semester,
                                error=f"Missing prerequisite: {prereq}",
                                severity="error"
                            ))
            
            # Mark these courses as completed
            completed.update(courses_this_semester)
        
        # Check credit load warnings
        for semester_key, courses in timeline.items():
            year, sem = semester_key.split('-')
            sem_name = "Fall" if sem == "1" else "Spring"
            
            # Assume 3 credits per course (would query DB in production)
            total_credits = len(courses) * 3
            
            if total_credits < 12:
                warnings.append(ValidationError(
                    courseCode="",
                    year=int(year),
                    semester=sem_name,
                    error=f"Low credit load: {total_credits} credits (minimum 12 recommended)",
                    severity="warning"
                ))
            elif total_credits > 18:
                warnings.append(ValidationError(
                    courseCode="",
                    year=int(year),
                    semester=sem_name,
                    error=f"High credit load: {total_credits} credits (maximum 18 recommended)",
                    severity="warning"
                ))
        
        return PlanValidationResult(
            isValid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

# Initialize validator
validator = PrerequisiteValidator()

# ============ RAG SYSTEM ============

class RAGSystem:
    """Retrieval-Augmented Generation system for UVA-specific Q&A"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        
        if supabase_client:
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=os.getenv("OPENAI_API_KEY", "")
                )
                self.vector_store = SupabaseVectorStore(
                    client=supabase_client,
                    embedding=self.embeddings,
                    table_name="rag_documents",
                    query_name="match_documents"
                )
            except Exception as e:
                print(f"Failed to initialize RAG system: {e}")
    
    def retrieve_context(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", ""),
                    "title": doc.metadata.get("title", "")
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using Claude with retrieved context"""
        
        # Build context string
        context_str = "\n\n".join([
            f"Source: {ctx['source']}\n{ctx['content']}"
            for ctx in context
        ])
        
        # Build prompt
        system_prompt = """You are HoosHelper, an AI assistant for UVA students. 
You help with course planning, academic questions, club recommendations, and general UVA information.

Be helpful, concise, and specific to UVA. Use the provided context to answer questions accurately.
If you don't know something, say so - don't make up information.

You can also help students modify their 4-year plans by understanding natural language commands like:
- "Add CS 2100 to my spring semester"
- "Remove MATH 1310 from year 2"
- "Move CS 3100 to fall of junior year"
"""
        
        user_prompt = f"""Context from UVA resources:
{context_str}

Student question: {query}

Please provide a helpful response based on the context above."""
        
        try:
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

# Initialize RAG system
rag_system = RAGSystem()

# ============ API ENDPOINTS ============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HoosHelper API",
        "version": "1.0.0"
    }

@app.get("/api/courses")
async def get_courses(
    search: Optional[str] = None,
    department: Optional[str] = None,
    level: Optional[int] = None
):
    """Get courses with optional filtering"""
    
    # Sample course data (in production, query from database)
    courses = [
        {
            "courseCode": "CS 1110",
            "title": "Introduction to Programming",
            "description": "Introduction to computer science and programming using Python",
            "credits": 3,
            "department": "CS",
            "level": 1000,
            "prerequisites": [],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 2100",
            "title": "Data Structures and Algorithms I",
            "description": "Introduction to data structures and algorithms",
            "credits": 3,
            "department": "CS",
            "level": 2000,
            "prerequisites": ["CS 1110"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 2120",
            "title": "Discrete Mathematics",
            "description": "Mathematical foundations for computer science",
            "credits": 3,
            "department": "CS",
            "level": 2000,
            "prerequisites": ["CS 2100"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 3100",
            "title": "Data Structures and Algorithms II",
            "description": "Advanced data structures and algorithm analysis",
            "credits": 3,
            "department": "CS",
            "level": 3000,
            "prerequisites": ["CS 2100", "CS 2120"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 4750",
            "title": "Database Systems",
            "description": "Database design, SQL, and database management systems",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2120"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 4710",
            "title": "Artificial Intelligence",
            "description": "Introduction to artificial intelligence and machine learning",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2120"],
            "semesters": ["Fall"]
        },
        {
            "courseCode": "MATH 1310",
            "title": "Calculus I",
            "description": "Differential calculus and applications",
            "credits": 4,
            "department": "MATH",
            "level": 1000,
            "prerequisites": [],
            "semesters": ["Fall", "Spring", "Summer"]
        },
        {
            "courseCode": "MATH 1320",
            "title": "Calculus II",
            "description": "Integral calculus and applications",
            "credits": 4,
            "department": "MATH",
            "level": 1000,
            "prerequisites": ["MATH 1310"],
            "semesters": ["Fall", "Spring", "Summer"]
        },
    ]
    
    # Apply filters
    filtered = courses
    
    if search:
        search_lower = search.lower()
        filtered = [
            c for c in filtered
            if search_lower in c["courseCode"].lower() 
            or search_lower in c["title"].lower()
        ]
    
    if department:
        filtered = [c for c in filtered if c["department"] == department]
    
    if level:
        filtered = [c for c in filtered if c["level"] == level]
    
    return {"courses": filtered}

@app.post("/api/validate-plan")
async def validate_plan(plan: StudentPlan) -> PlanValidationResult:
    """Validate a student's 4-year plan"""
    return validator.validate_plan(plan)

@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with the AI assistant (RAG-powered)"""
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get the last user message
    last_message = request.messages[-1]
    if last_message.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    query = last_message.content
    
    # Retrieve relevant context
    context = rag_system.retrieve_context(query)
    
    # Generate response
    response = rag_system.generate_response(query, context)
    
    return ChatResponse(
        message=response,
        context=context if context else None
    )

@app.get("/api/clubs")
async def get_clubs(
    search: Optional[str] = None,
    category: Optional[str] = None
):
    """Get student clubs with optional filtering"""
    
    # Sample club data (in production, query from database)
    clubs = [
        {
            "id": "1",
            "name": "UVA Computer Science Society",
            "description": "Community for CS students to network, learn, and build projects",
            "category": "Academic",
            "tags": ["Technology", "Computer Science", "Networking"],
            "email": "css@virginia.edu",
            "website": "https://css.virginia.edu"
        },
        {
            "id": "2",
            "name": "Hoos Hacking",
            "description": "Hackathon organization and coding community",
            "category": "Tech",
            "tags": ["Technology", "Hackathons", "Programming"],
            "website": "https://hooshacking.org"
        },
        {
            "id": "3",
            "name": "Madison House",
            "description": "Community service organization connecting students with volunteer opportunities",
            "category": "Service",
            "tags": ["Service", "Volunteering", "Community"],
            "website": "https://madisonhouse.org"
        },
        {
            "id": "4",
            "name": "UVA Drama",
            "description": "Theater productions and performing arts",
            "category": "Arts",
            "tags": ["Theater", "Performance", "Arts"],
            "website": "https://drama.virginia.edu"
        },
        {
            "id": "5",
            "name": "Data Science Club",
            "description": "Learn data science, machine learning, and analytics",
            "category": "Academic",
            "tags": ["Technology", "Data Science", "Machine Learning"],
            "email": "datascience@virginia.edu"
        },
        {
            "id": "6",
            "name": "Entrepreneurship Club",
            "description": "Support student startups and innovation",
            "category": "Business",
            "tags": ["Business", "Entrepreneurship", "Startups"],
            "website": "https://eclub.virginia.edu"
        },
    ]
    
    # Apply filters
    filtered = clubs
    
    if search:
        search_lower = search.lower()
        filtered = [
            c for c in filtered
            if search_lower in c["name"].lower()
            or search_lower in c["description"].lower()
        ]
    
    if category:
        filtered = [c for c in filtered if c["category"] == category]
    
    return {"clubs": filtered}

@app.get("/api/clubs/recommended")
async def get_recommended_clubs(interests: Optional[str] = None):
    """Get recommended clubs based on user interests"""
    
    # Get all clubs
    clubs_response = await get_clubs()
    clubs = clubs_response["clubs"]
    
    # Simple recommendation: if interests provided, filter by tags
    if interests:
        interest_keywords = interests.lower().split()
        recommended = [
            c for c in clubs
            if any(
                keyword in tag.lower()
                for keyword in interest_keywords
                for tag in c.get("tags", [])
            )
        ]
        return {"clubs": recommended[:6]}  # Return top 6
    
    # Otherwise, return random selection
    return {"clubs": clubs[:6]}

# ============ BACKGROUND TASKS ============

@app.post("/api/scrape/courses")
async def scrape_courses(background_tasks: BackgroundTasks):
    """Trigger course scraping (background task)"""
    
    def scrape_task():
        # Import here to avoid circular dependencies
        try:
            from scrapers.course_scraper import scrape_courses
            scrape_courses()
        except Exception as e:
            print(f"Scraping error: {e}")
    
    background_tasks.add_task(scrape_task)
    
    return {"status": "started", "message": "Course scraping started in background"}

@app.post("/api/scrape/clubs")
async def scrape_clubs(background_tasks: BackgroundTasks):
    """Trigger club scraping (background task)"""
    
    def scrape_task():
        try:
            from scrapers.club_scraper import scrape_clubs
            scrape_clubs()
        except Exception as e:
            print(f"Scraping error: {e}")
    
    background_tasks.add_task(scrape_task)
    
    return {"status": "started", "message": "Club scraping started in background"}

@app.post("/api/scrape/rag-content")
async def scrape_rag_content(background_tasks: BackgroundTasks):
    """Trigger RAG content scraping (background task)"""
    
    def scrape_task():
        try:
            from scrapers.rag_scraper import scrape_rag_content
            scrape_rag_content()
        except Exception as e:
            print(f"Scraping error: {e}")
    
    background_tasks.add_task(scrape_task)
    
    return {"status": "started", "message": "RAG content scraping started in background"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

