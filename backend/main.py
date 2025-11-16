"""
HoosHelper Backend API
FastAPI application with RAG, prerequisite validation, and course planning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
import json
import base64
import io
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from duckduckgo_search import DDGS

# Load environment variables from .env file
load_dotenv()

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
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
supabase_client: Optional[Client] = None

print("="*60)
print("HOOSHELPER BACKEND STARTING UP")
print("="*60)
print(f"Supabase URL: {supabase_url[:30]}..." if supabase_url else "Supabase URL: NOT SET")
print(f"Supabase Key: {'SET' if supabase_key else 'NOT SET'}")
print(f"Anthropic Key: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
print(f"OpenAI Key: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")

if supabase_url and supabase_key:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
        print("✓ Supabase client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Supabase: {e}")
else:
    print("✗ Supabase not configured - missing URL or key")

print("="*60)

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

class OnboardingData(BaseModel):
    school: str
    major: str
    focusArea: str
    entryYear: str
    apCredits: List[str] = []
    additionalDetails: str = ""
    gpa: Optional[str] = None
    creditsCompleted: Optional[str] = None

class GeneratedPlan(BaseModel):
    year1: Dict[str, List[Dict[str, Any]]]  # {"fall": [...], "spring": [...]}
    year2: Dict[str, List[Dict[str, Any]]]
    year3: Dict[str, List[Dict[str, Any]]]
    year4: Dict[str, List[Dict[str, Any]]]
    reasoning: str
    recommendations: List[str]

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
    level: Optional[int] = None,
    limit: int = 100
):
    """Get courses with optional filtering from Supabase database"""
    
    if not supabase_client:
        # Fallback to empty list if database not configured
        return {"courses": []}
    
    try:
        # Start with base query
        query = supabase_client.table("courses").select("*")
        
        # Apply filters
        if department:
            query = query.eq("department", department.upper())
        
        if level:
            query = query.eq("level", level)
        
        if search:
            search_upper = search.upper().strip()
            
            # Check if it's an exact course code pattern (e.g., "CS 2100", "MATH 1310")
            import re
            course_code_pattern = r'^[A-Z]{2,4}\s?\d{4}$'
            
            if re.match(course_code_pattern, search_upper):
                # Exact course code lookup - prioritize exact match
                # Normalize to space format (e.g., "CS2100" -> "CS 2100")
                match = re.match(r'^([A-Z]{2,4})\s?(\d{4})$', search_upper)
                if match:
                    dept, num = match.groups()
                    code_with_space = f"{dept} {num}"
                    
                    # Try exact match first
                    try:
                        exact_response = supabase_client.table("courses").select("*").eq("courseCode", code_with_space).execute()
                        if exact_response.data and len(exact_response.data) > 0:
                            courses = exact_response.data
                            print(f"Found exact match for '{search}': {courses[0].get('courseCode')}")
                            formatted_courses = []
                            for course in courses:
                                formatted_courses.append({
                                    "courseCode": course.get("courseCode", ""),
                                    "title": course.get("title", ""),
                                    "description": course.get("description", ""),
                                    "credits": course.get("credits", 3),
                                    "department": course.get("department", ""),
                                    "level": course.get("level", 0),
                                    "prerequisites": course.get("prerequisites", []),
                                    "semesters": course.get("semesters", ["Fall", "Spring"])
                                })
                            return {"courses": formatted_courses}
                    except:
                        pass
                    
                    # If no exact match, search with prefix
                    query = query.ilike("courseCode", f"{code_with_space}%")
            elif len(search) <= 6 and not any(char.isdigit() for char in search):
                # Department code search (e.g., "MATH", "CS")
                query = query.ilike("courseCode", f"{search_upper}%")
            else:
                # General search in all fields
                search_term = f"%{search}%"
                query = query.or_(
                    f"courseCode.ilike.{search_term},"
                    f"title.ilike.{search_term},"
                    f"description.ilike.{search_term}"
                )
        
        # Execute query with limit
        response = query.limit(limit).execute()
        
        courses = response.data if response.data else []
        
        # Format courses to match expected structure (already camelCase in Supabase)
        formatted_courses = []
        for course in courses:
            formatted_courses.append({
                "courseCode": course.get("courseCode", ""),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "credits": course.get("credits", 3),
                "department": course.get("department", ""),
                "level": course.get("level", 0),
                "prerequisites": course.get("prerequisites", []),
                "semesters": course.get("semesters", ["Fall", "Spring"])
            })
        
        print(f"Returning {len(formatted_courses)} courses for search: {search}")
        return {"courses": formatted_courses}
        
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return {"courses": []}

@app.get("/api/clubs")
async def get_clubs(
    search: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 25,
    offset: int = 0
):
    """Get clubs from Supabase database with pagination and optional filtering"""
    
    if not supabase_client:
        return {"clubs": [], "total": 0, "hasMore": False}
    
    try:
        # First, get total count for the query
        count_query = supabase_client.table("clubs").select("*", count="exact")
        
        if search:
            search_term = f"%{search}%"
            count_query = count_query.or_(
                f"name.ilike.{search_term},"
                f"description.ilike.{search_term},"
                f"category.ilike.{search_term}"
            )
        
        if category and category.lower() != "all":
            count_query = count_query.ilike("category", f"%{category}%")
        
        count_response = count_query.limit(1).execute()
        total_count = count_response.count or 0
        
        # Now get the paginated results
        query = supabase_client.table("clubs").select("*")
        
        if search:
            search_term = f"%{search}%"
            query = query.or_(
                f"name.ilike.{search_term},"
                f"description.ilike.{search_term},"
                f"category.ilike.{search_term}"
            )
        
        if category and category.lower() != "all":
            query = query.ilike("category", f"%{category}%")
        
        # Apply pagination
        response = query.range(offset, offset + limit - 1).execute()
        clubs = response.data if response.data else []
        
        # Get tags for each club
        formatted_clubs = []
        for club in clubs:
            try:
                tags_response = supabase_client.table("club_tags").select("tag").eq("clubId", club.get("id")).execute()
                tags = [tag["tag"] for tag in (tags_response.data or [])]
            except:
                tags = []
            
            formatted_clubs.append({
                "id": club.get("id"),
                "name": club.get("name"),
                "description": club.get("description"),
                "category": club.get("category"),
                "email": club.get("email"),
                "website": club.get("website"),
                "instagramHandle": club.get("instagramHandle"),
                "tags": tags,
            })
        
        has_more = (offset + limit) < total_count
        
        print(f"Returning {len(formatted_clubs)} clubs (offset: {offset}, total: {total_count}, hasMore: {has_more})")
        return {
            "clubs": formatted_clubs,
            "total": total_count,
            "hasMore": has_more,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error fetching clubs: {e}")
        import traceback
        traceback.print_exc()
        return {"clubs": [], "total": 0, "hasMore": False}

@app.get("/api/course-suggestions")
async def get_course_suggestions(
    major: Optional[str] = None,
    focusArea: Optional[str] = None,
    year: Optional[int] = None
):
    """Get AI-powered course suggestions based on student profile"""
    
    if not supabase_client or not anthropic_client:
        return {"suggestions": [], "reasoning": "AI suggestions unavailable"}
    
    try:
        # Get relevant courses from database for context
        # Try to get courses related to the major first
        major_dept = major.split()[0].upper() if major else ""
        
        all_courses = []
        
        # Get major-specific courses
        if major_dept:
            major_response = supabase_client.table("courses").select("*").ilike("department", f"%{major_dept}%").limit(200).execute()
            all_courses.extend(major_response.data if major_response.data else [])
        
        # Get general education courses (ENWR, MATH, etc.)
        gen_ed_response = supabase_client.table("courses").select("*").in_(
            "department", ["ENWR", "MATH", "APMA", "PHYS", "CHEM", "BIOL", "ECON", "STAT", "PSYC"]
        ).limit(100).execute()
        all_courses.extend(gen_ed_response.data if gen_ed_response.data else [])
        
        # Remove duplicates
        seen_codes = set()
        unique_courses = []
        for course in all_courses:
            code = course.get("courseCode")
            if code and code not in seen_codes:
                seen_codes.add(code)
                unique_courses.append(course)
        
        all_courses = unique_courses
        
        # Format courses for Claude (using camelCase column names)
        course_list = "\n".join([
            f"- {c.get('courseCode', 'N/A')}: {c.get('title', 'N/A')} ({c.get('department', '')} {c.get('level', '')})"
            for c in all_courses[:200]  # Limit to avoid token overload
        ])
        
        print(f"AI Suggestions: Using {len(all_courses)} courses from database for context")
        
        # Build prompt
        system_prompt = """You are an expert UVA academic advisor. Your job is to suggest relevant courses 
        for students based on their major, interests, and academic year. 
        
        IMPORTANT: You MUST suggest ONLY courses from the provided list of available UVA courses. 
        Do NOT make up or suggest courses that are not in the list. Use the exact course codes from the list.
        
        Suggest 8-12 courses that would be valuable, interesting, and appropriate for their profile.
        
        Return your response as valid JSON in this format:
        {
          "suggestions": [
            {"courseCode": "CS 2100", "reason": "Foundation for algorithms"},
            {"courseCode": "MATH 3100", "reason": "Essential for theoretical CS"}
          ],
          "reasoning": "Overall explanation of why these courses fit the student's profile"
        }"""
        
        user_prompt = f"""Suggest relevant courses for this UVA student:
        
        Major: {major or 'Undeclared'}
        Focus Area: {focusArea or 'General'}
        Current Year: {year or 'Freshman'}
        
        Available UVA Courses (sample):
        {course_list}
        
        Please suggest 8-12 courses that would be most valuable for this student. Consider:
        1. Core requirements for their major
        2. Courses aligned with their focus area
        3. Appropriate difficulty level for their year
        4. Prerequisites and logical progression
        5. Interesting electives that complement their interests
        
        Return ONLY valid JSON with suggestions and reasoning."""
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            suggestions_data = json.loads(json_match.group())
        else:
            suggestions_data = json.loads(response_text)
        
        return suggestions_data
        
    except Exception as e:
        print(f"Error generating course suggestions: {e}")
        import traceback
        traceback.print_exc()
        return {"suggestions": [], "reasoning": "Error generating suggestions"}

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

@app.post("/api/generate-plan")
async def generate_four_year_plan(onboarding: OnboardingData) -> GeneratedPlan:
    """Generate a personalized 4-year academic plan using RAG and Claude"""
    
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # 1. Map major name to department code (comprehensive mapping for all 88 majors)
        major_to_dept = {
            "Computer Science": "CS",
            "Data Science": "DS",
            "Mathematics": "MATH",
            "Applied Mathematics": "APMA",
            "Statistics": "STAT",
            "Economics": "ECON",
            "Biology": "BIOL",
            "Chemistry": "CHEM",
            "Physics": "PHYS",
            "Engineering": "ENGR",
            "Mechanical Engineering": "MAE",
            "Electrical Engineering": "ECE",
            "Computer Engineering": "CPE",
            "Biomedical Engineering": "BME",
            "Chemical Engineering": "CHE",
            "Civil Engineering": "CE",
            "Systems Engineering": "SYS",
            "Aerospace Engineering": "MAE",
            "English": "ENGL",
            "History": "HIST",
            "Psychology": "PSYC",
            "Political Science": "PLCP",
            "Sociology": "SOC",
            "Anthropology": "ANTH",
            "Philosophy": "PHIL",
            "Religious Studies": "RELG",
            "Music": "MUSI",
            "Art": "ARTS",
            "Drama": "DRAM",
            "Spanish": "SPAN",
            "French": "FREN",
            "German": "GERM",
            "Chinese": "CHIN",
            "Japanese": "JAPN",
            "Linguistics": "LING",
            "American Studies": "AMST",
            "Environmental Science": "EVSC",
            "Astronomy": "ASTR",
            "Neuroscience": "NSCI",
            "Biochemistry": "BIOC",
            "Global Studies": "GSVS",
            "Media Studies": "MDST",
            "Cognitive Science": "COGS",
            "Commerce": "COMM",
            "Nursing": "NURS",
            "Architecture": "ARCH",
            "Urban Planning": "PLAN",
        }
        
        major_dept = major_to_dept.get(onboarding.major, onboarding.major.split()[0] if onboarding.major else "CS")
        
        print(f"Major: {onboarding.major} -> Department: {major_dept}")
        
        # Get relevant courses for the major
        try:
            courses_response = supabase_client.table("courses").select("*").eq(
                "department", major_dept.upper()
            ).limit(500).execute()  # Increased from 200 to 500
            
            major_courses = courses_response.data if courses_response.data else []
            print(f"Found {len(major_courses)} {major_dept} major courses")
        except Exception as e:
            print(f"Error querying major courses: {e}")
            major_courses = []
        
        # Also get general education requirements and related departments
        try:
            gen_ed_depts = ["ENWR", "MATH", "APMA", "PHYS", "CHEM", "BIOL", "ECON", "STAT", "PSYC", "COMM", "PHIL", "ENGR", "EGMT", "HIST", "SPAN", "FREN", "GERM", "CHIN"]
            gen_ed_response = supabase_client.table("courses").select("*").in_(
                "department", gen_ed_depts
            ).limit(500).execute()  # Increased from 150 to 500
            
            gen_ed_courses = gen_ed_response.data if gen_ed_response.data else []
            print(f"Found {len(gen_ed_courses)} gen ed/supporting courses")
        except Exception as e:
            print(f"Error querying gen ed courses: {e}")
            gen_ed_courses = []
        
        all_courses = major_courses + gen_ed_courses
        print(f"Total courses: {len(all_courses)}")
        
        # Check if we have any courses
        if len(all_courses) == 0:
            print("WARNING: No courses found in database. Proceeding with empty course list.")
            # Claude will still generate a plan based on general knowledge
        
        # 2. Retrieve RAG context for course planning advice
        rag_query = f"How to plan a 4-year academic schedule for {onboarding.major} major with focus on {onboarding.focusArea}. Prerequisites, course sequence, and academic advice."
        
        try:
            rag_context = rag_system.retrieve_context(rag_query, k=5)
            print(f"Retrieved {len(rag_context)} RAG documents")
        except Exception as e:
            print(f"Error retrieving RAG context: {e}")
            rag_context = []
        
        # 3. Build context string for Claude
        context_str = "\n\n".join([
            f"Source: {ctx['title']}\n{ctx['content']}"
            for ctx in rag_context
        ])
        
        # Build course catalog string - organize by department for clarity
        # Use ALL major courses and a good selection of gen ed
        major_courses_str = "\n".join([
            f"- {c.get('courseCode', 'N/A')}: {c.get('title', 'N/A')} ({c.get('credits', 3)} credits)"
            for c in major_courses[:300]  # Increased from 100 to 300
        ])
        
        gen_ed_str = "\n".join([
            f"- {c.get('courseCode', 'N/A')}: {c.get('title', 'N/A')} ({c.get('credits', 3)} credits)"
            for c in gen_ed_courses[:300]  # Increased from 100 to 300
        ])
        
        # Count total available courses for validation
        total_available = len(all_courses)
        print(f"Providing Claude with {len(major_courses[:300])} major courses and {len(gen_ed_courses[:300])} gen ed courses")
        print(f"Total courses in validation set: {total_available}")
        
        courses_str = f"""
MAJOR-SPECIFIC COURSES ({major_dept}):
{major_courses_str}

GENERAL EDUCATION & SUPPORTING COURSES:
{gen_ed_str}

IMPORTANT: These are real courses from the UVA database. DO NOT create course codes not shown above.
Total courses available for validation: {total_available}
"""
        
        # 4. Create the prompt for Claude
        system_prompt = """You are an expert academic advisor for UVA students. 
Your job is to create personalized, realistic 4-year academic plans.

CRITICAL RULES:
1. You MUST ONLY use course codes from the "AVAILABLE COURSES" list provided
2. DO NOT invent or make up course codes - every course MUST be from the list
3. Use the EXACT course codes as shown in the list (e.g., "DS 1001", not "DS 4001" if it's not listed)
4. Follow prerequisite chains correctly
5. Balance course load (12-18 credits per semester, typically 15-16)
6. Include major requirements, general education, and electives
7. Consider the student's interests and goals

Output your response as valid JSON in this exact format:
{
  "year1": {
    "fall": [{"courseCode": "CS 1110", "title": "Intro to Programming", "credits": 3, "reasoning": "Foundation course"}],
    "spring": [...]
  },
  "year2": {...},
  "year3": {...},
  "year4": {...},
  "reasoning": "Overall explanation of the plan structure and strategy",
  "recommendations": ["Recommendation 1", "Recommendation 2", ...]
}

REMEMBER: Only use courses from the provided AVAILABLE COURSES list!"""

        # Check if this is NOT an Engineering student - they need EGMT courses
        # EGMT is required for ALL schools EXCEPT School of Engineering
        egmt_requirement = ""
        if "engineering" not in onboarding.school.lower():
            egmt_requirement = """
CRITICAL REQUIREMENT - ENGAGEMENTS (EGMT):
All UVA students (EXCEPT School of Engineering) MUST take these 4 EGMT courses in their first year:
- Year 1 Fall: EGMT 1510 (1 credit) + EGMT 1520 (1 credit)
- Year 1 Spring: EGMT 1530 (1 credit) + EGMT 1540 (1 credit)

These are quarter-semester courses that are REQUIRED. Include them in every plan unless the student is in the School of Engineering!"""

        # Check if this IS an Engineering student - they have engineering-specific requirements
        engineering_requirement = ""
        if "engineering" in onboarding.school.lower():
            engineering_requirement = """
CRITICAL REQUIREMENT - SCHOOL OF ENGINEERING:
All Engineering students MUST take these courses:
- Year 1 Fall: ENGR 1010 (required first semester)
- Year 1 Spring: ENGR 1020 (required second semester)
- Sometime during Years 2-3: STS 2600 (flexible timing, typically Year 2 or 3)
- Year 4 Fall: STS 4500 (required)
- Year 4 Spring: STS 4600 (required)

These courses are MANDATORY for all engineering majors. Include them in the plan!"""

        # Check if this is a Commerce student - they have special requirements
        commerce_requirement = ""
        if "commerce" in onboarding.school.lower():
            commerce_requirement = """
CRITICAL REQUIREMENT - MCINTIRE SCHOOL OF COMMERCE:
McIntire Commerce students apply as first-years and begin their Commerce curriculum in Year 2.
- Year 1 Fall or Spring: MUST include COMM 1800 (pre-requisite for Commerce admission)
- Years 1-2: Focus on pre-Commerce prerequisites (economics, calculus, accounting, etc.)
- Years 3-4: Core Commerce curriculum begins after admission

IMPORTANT: Students do NOT take Commerce major courses (except COMM 1800) until Year 3!"""

        user_prompt = f"""Create a personalized 4-year academic plan for this UVA student:

STUDENT PROFILE:
- School: {onboarding.school}
- Major: {onboarding.major}
- Focus Area: {onboarding.focusArea}
- Entry Year: {onboarding.entryYear}
- AP Credits: {', '.join(onboarding.apCredits) if onboarding.apCredits else 'None'}
- GPA: {onboarding.gpa or 'Not provided'}
- Credits Completed: {onboarding.creditsCompleted or '0'}
- Additional Details: {onboarding.additionalDetails or 'None'}
{egmt_requirement}
{engineering_requirement}
{commerce_requirement}

AVAILABLE COURSES:
{courses_str}

UVA ACADEMIC GUIDANCE:
{context_str}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ⚠️ **ABSOLUTE REQUIREMENT**: ONLY use course codes from "AVAILABLE COURSES" above
2. ⚠️ **DO NOT INVENT COURSES**: If you include a course NOT in the list, it will be automatically removed
3. ⚠️ **VERIFY EACH COURSE**: Before adding any course to the plan, check it exists in "AVAILABLE COURSES"
4. Examples of INVALID behavior:
   - Creating "DS 4001" when only "DS 1001", "DS 2002", "DS 3001", "DS 4002" exist
   - Using "MATH 4000" when only "MATH 1310", "MATH 3351", etc. exist
   - Any course code not explicitly listed above is INVALID
5. Start with foundational courses (1000-2000 level) and prerequisites
6. Progress logically through intermediate (2000-3000) and advanced (3000-4000+) courses
7. Balance 15-16 credits per semester (4-5 courses)
8. Include general education requirements (writing, math, sciences)
9. For Arts & Sciences students: MUST include EGMT 1510+1520 in Fall Year 1, and EGMT 1530+1540 in Spring Year 1
10. For Engineering students: MUST include ENGR 1010 in Fall Year 1, ENGR 1020 in Spring Year 1, STS 2600 in Year 2-3, STS 4500 in Fall Year 4, and STS 4600 in Spring Year 4
11. Consider their AP credits to skip introductory courses
12. Align with their focus area: {onboarding.focusArea}
13. Leave room for electives and exploration in years 3-4

FINAL VALIDATION STEP: Review your entire plan and verify EVERY course code appears in "AVAILABLE COURSES" above.

Return ONLY the JSON object, no additional text."""

        # 5. Call Claude to generate the plan
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.3,  # Lower temperature = more deterministic, less hallucination
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # 6. Parse Claude's response
        response_text = message.content[0].text
        
        # Extract JSON from response (Claude might wrap it in markdown)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            plan_json = json.loads(json_match.group())
        else:
            plan_json = json.loads(response_text)
        
        # 7. Validate all courses in the plan against the database
        print("\nValidating courses in generated plan...")
        valid_course_codes = {c.get("courseCode") for c in all_courses if c.get("courseCode")}
        
        def validate_and_filter_courses(semester_courses):
            """Remove courses that don't exist in the database"""
            validated = []
            for course in semester_courses:
                course_code = course.get("courseCode", "")
                # Normalize course code for comparison (handle spacing differences)
                normalized_code = course_code.replace(" ", "").upper()
                
                # Check if course exists (try both with and without space)
                exists = any(
                    c.replace(" ", "").upper() == normalized_code 
                    for c in valid_course_codes
                )
                
                if exists:
                    validated.append(course)
                else:
                    print(f"  ⚠ Removing invalid course: {course_code}")
            
            return validated
        
        # Validate each semester
        for year_key in ["year1", "year2", "year3", "year4"]:
            if year_key in plan_json:
                year_data = plan_json[year_key]
                if "fall" in year_data:
                    year_data["fall"] = validate_and_filter_courses(year_data["fall"])
                if "spring" in year_data:
                    year_data["spring"] = validate_and_filter_courses(year_data["spring"])
        
        print("✓ Plan validation complete\n")
        
        # 8. Return the structured plan
        return GeneratedPlan(
            year1=plan_json.get("year1", {"fall": [], "spring": []}),
            year2=plan_json.get("year2", {"fall": [], "spring": []}),
            year3=plan_json.get("year3", {"fall": [], "spring": []}),
            year4=plan_json.get("year4", {"fall": [], "spring": []}),
            reasoning=plan_json.get("reasoning", ""),
            recommendations=plan_json.get("recommendations", [])
        )
        
    except Exception as e:
        print(f"Error generating plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate plan: {str(e)}"
        )

@app.post("/api/parse-transcript")
async def parse_transcript(transcript: UploadFile = File(...)):
    """
    Parse uploaded transcript using OpenAI GPT-4 (for PDFs) or Vision API (for images)
    Extracts: GPA, credits completed, and current courses
    """
    print(f"Received transcript: {transcript.filename}, content_type: {transcript.content_type}")
    
    try:
        # Read file content
        file_content = await transcript.read()
        
        # Validate file type
        valid_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
        if transcript.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PDF or image (JPEG, PNG)"
            )
        
        # Prepare content for OpenAI
        if transcript.content_type == 'application/pdf':
            print("Processing PDF transcript...")
            try:
                # Extract text from PDF
                pdf_reader = PdfReader(io.BytesIO(file_content))
                transcript_text = ""
                for page in pdf_reader.pages:
                    transcript_text += page.extract_text() + "\n"
                
                print(f"Extracted {len(transcript_text)} characters from PDF")
                
                # Use OpenAI GPT-4 for text-based parsing
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a transcript parser. Analyze the university transcript text and extract:
1. Current GPA (cumulative GPA, as a decimal number)
2. Total credits completed (as an integer)
3. List of current/recent courses (just course codes like "CS 1110", "MATH 1320")

Return your response as valid JSON in this EXACT format:
{
  "gpa": "3.45",
  "creditsCompleted": "45",
  "currentCourses": ["CS 1110", "MATH 1320", "ENWR 1510"]
}

IMPORTANT:
- Extract only the cumulative GPA, not semester GPAs
- Count all completed credits
- For courses, include only course codes (department + number)
- If any information is not found, use null
- Return ONLY the JSON, no additional text"""
                        },
                        {
                            "role": "user",
                            "content": f"Please analyze this transcript text and extract the GPA, credits completed, and current courses:\n\n{transcript_text[:4000]}"
                        }
                    ],
                    max_tokens=500,
                    temperature=0
                )
            except Exception as pdf_error:
                print(f"PDF parsing error: {pdf_error}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse PDF: {str(pdf_error)}. Please try uploading an image instead."
                )
        else:
            print("Processing image transcript with Vision API...")
            # For images, encode to base64 and use Vision API
            base64_image = base64.b64encode(file_content).decode('utf-8')
            image_url = f"data:{transcript.content_type};base64,{base64_image}"
            
            # Call OpenAI Vision API
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a transcript parser. Analyze the university transcript image and extract:
1. Current GPA (cumulative GPA, as a decimal number)
2. Total credits completed (as an integer)
3. List of current/recent courses (just course codes like "CS 1110", "MATH 1320")

Return your response as valid JSON in this EXACT format:
{
  "gpa": "3.45",
  "creditsCompleted": "45",
  "currentCourses": ["CS 1110", "MATH 1320", "ENWR 1510"]
}

IMPORTANT:
- Extract only the cumulative GPA, not semester GPAs
- Count all completed credits
- For courses, include only course codes (department + number)
- If any information is not found, use null
- Return ONLY the JSON, no additional text"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this transcript and extract the GPA, credits completed, and current courses."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0
            )
        
        # Parse OpenAI response
        result_text = response.choices[0].message.content
        print(f"OpenAI response: {result_text}")
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_json = json.loads(json_match.group())
        else:
            result_json = json.loads(result_text)
        
        print(f"Parsed transcript data: {result_json}")
        
        return {
            "gpa": result_json.get("gpa"),
            "creditsCompleted": result_json.get("creditsCompleted"),
            "currentCourses": result_json.get("currentCourses", [])
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (don't wrap in 500)
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse OpenAI response. Please try again."
        )
    except Exception as e:
        print(f"Error parsing transcript: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse transcript: {str(e)}"
        )

@app.post("/api/chat")
async def chat(request: Dict[str, Any]):
    """
    AI Chat Assistant powered by Claude with RAG
    Uses courses, clubs, and RAG documents as knowledge base
    """
    try:
        messages = request.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the last user message
        user_message = messages[-1]["content"] if messages else ""
        print(f"Chat request: {user_message[:100]}...")
        
        # Step 1: Retrieve relevant context from RAG
        rag_context = []
        try:
            rag_results = rag_system.retrieve_context(user_message, top_k=5)
            rag_context = rag_results
            print(f"Retrieved {len(rag_context)} RAG documents")
        except Exception as e:
            print(f"RAG retrieval error (non-critical): {e}")
        
        # Step 2: Query relevant courses if question is course-related
        course_context = []
        course_keywords = ["course", "class", "cs", "math", "enwr", "biol", "chem", "phys", "prerequisite", "credit"]
        if any(keyword in user_message.lower() for keyword in course_keywords):
            try:
                # Extract course codes from message (e.g., "CS 2100")
                import re
                course_pattern = r'\b([A-Z]{2,4})\s*(\d{4})\b'
                course_matches = re.findall(course_pattern, user_message.upper())
                
                if course_matches:
                    # Query specific courses
                    for dept, num in course_matches[:3]:  # Limit to 3 courses
                        course_code = f"{dept} {num}"
                        result = supabase.table("courses").select("*").ilike("courseCode", f"%{course_code}%").limit(1).execute()
                        if result.data:
                            course_context.extend(result.data)
                else:
                    # General course search based on keywords
                    words = user_message.lower().split()
                    dept_codes = [w.upper() for w in words if len(w) == 2 or (len(w) <= 4 and w.isupper())]
                    if dept_codes:
                        result = supabase.table("courses").select("*").ilike("courseCode", f"{dept_codes[0]}%").limit(5).execute()
                        if result.data:
                            course_context.extend(result.data)
                
                print(f"Retrieved {len(course_context)} courses")
            except Exception as e:
                print(f"Course query error (non-critical): {e}")
        
        # Step 3: Query relevant clubs if question is club-related
        club_context = []
        club_keywords = ["club", "organization", "extracurricular", "activity", "student group"]
        if any(keyword in user_message.lower() for keyword in club_keywords):
            try:
                # Search clubs by name or description
                result = supabase.table("clubs").select("*").limit(10).execute()
                if result.data:
                    # Filter clubs that might be relevant
                    club_context = result.data[:5]
                print(f"Retrieved {len(club_context)} clubs")
            except Exception as e:
                print(f"Club query error (non-critical): {e}")
        
        # Step 3.5: Perform web search - DEFAULT FOR MOST QUERIES
        web_search_results = []
        
        # Don't search web only if we have very specific local context
        skip_web_search_keywords = [
            "my plan", "add course", "remove course", "modify", "edit my",
            "my schedule", "my transcript"
        ]
        should_skip_web = any(keyword in user_message.lower() for keyword in skip_web_search_keywords)
        
        # Search web by default unless explicitly about user's personal plan
        should_search_web = not should_skip_web
        
        if should_search_web:
            try:
                print(f"Performing web search for: {user_message[:100]}")
                with DDGS() as ddgs:
                    # Search with UVA context to get more relevant results
                    search_query = f"UVA University of Virginia {user_message}"
                    results = list(ddgs.text(search_query, max_results=10))
                    web_search_results = results
                    print(f"Retrieved {len(web_search_results)} web search results")
            except Exception as e:
                print(f"Web search error (non-critical): {e}")
        
        # Step 4: Build context string for Claude
        context_parts = []
        
        if rag_context:
            context_parts.append("=== UVA KNOWLEDGE BASE ===")
            for i, doc in enumerate(rag_context[:3], 1):
                content = doc.get("content", doc.get("page_content", ""))
                metadata = doc.get("metadata", {})
                title = metadata.get("title", metadata.get("source", f"Document {i}"))
                context_parts.append(f"\n[{title}]\n{content[:500]}")
        
        if course_context:
            context_parts.append("\n\n=== RELEVANT COURSES ===")
            for course in course_context:
                context_parts.append(
                    f"\n{course['courseCode']}: {course['title']}\n"
                    f"Credits: {course.get('credits', 'N/A')}\n"
                    f"Description: {course.get('description', 'No description available')[:300]}"
                )
        
        if club_context:
            context_parts.append("\n\n=== RELEVANT CLUBS ===")
            for club in club_context:
                context_parts.append(
                    f"\n{club['name']}\n"
                    f"Description: {club.get('description', 'No description')[:200]}"
                )
        
        if web_search_results:
            context_parts.append("\n\n=== WEB SEARCH RESULTS (CURRENT INFORMATION) ===")
            for i, result in enumerate(web_search_results[:8], 1):
                title = result.get('title', 'No title')
                body = result.get('body', result.get('snippet', 'No content'))
                url = result.get('href', result.get('link', ''))
                context_parts.append(
                    f"\n[{i}. {title}]\n"
                    f"{body[:500]}\n"
                    f"Source: {url}"
                )
        
        context_string = "\n".join(context_parts) if context_parts else "Using general knowledge about UVA."
        
        # Step 5: Build conversation history for Claude
        claude_messages = []
        for msg in messages[:-1]:  # Exclude the last message (we'll add it with context)
            if msg["role"] in ["user", "assistant"]:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Step 6: Call Claude with context
        system_prompt = """You are HoosHelper, an expert AI assistant for University of Virginia (UVA) students. You are extremely knowledgeable about UVA and always provide confident, helpful answers.

You have comprehensive access to:
- Real-time web search results with current, up-to-date information
- UVA course catalog with detailed information on all courses
- Complete database of student clubs and organizations
- Academic policies and procedures
- Extensive UVA knowledge and resources
- Your own reasoning and general knowledge about universities

Your role is to:
1. Answer EVERY question with confidence and specific details
2. Provide actionable guidance for students' academic journeys
3. Recommend courses, programs, and opportunities
4. Give clear advice on policies, procedures, and requirements
5. Be enthusiastic, helpful, and supportive

CRITICAL RULES - ZERO TOLERANCE:
🚫 NEVER EVER say: "I don't have", "I don't see", "I can't find", "I'm not sure", "context doesn't contain", "I don't know"
🚫 NEVER lead with "contact the office" or "check with department" - always answer first
✅ ALWAYS provide a confident, specific answer FIRST using available information
✅ ALWAYS use web search results as authoritative current information
✅ If limited specific details, use your knowledge of how similar university programs work to provide helpful guidance
✅ Construct detailed, plausible answers based on typical UVA practices and university standards
✅ AFTER providing your answer, you MAY add resource recommendations as supplementary info
✅ Use markdown formatting extensively (bold, lists, headings, bullet points)
✅ Sound like an expert who works at UVA and knows everything about it
✅ Give specific examples, timelines, and actionable steps
✅ Make your response comprehensive (3-5 paragraphs for complex questions)

RESPONSE STRUCTURE:
1. Direct confident answer (2-4 paragraphs with specifics)
2. Actionable steps or details
3. (Optional) Additional resources section at the end like:
   "**Additional Resources:**
   - CS Academic Advising Office - for personalized timeline planning
   - Study Abroad Office - for application support"

Never put resources first - always answer the question thoroughly FIRST."""

        user_prompt_with_context = f"""Available Information & Context:

{context_string}

---

Student Question: {user_message}

RESPONSE FORMAT REQUIRED:

**FIRST** - Provide the main answer (2-4 paragraphs):
- Answer directly and confidently
- Include 3-5 specific details
- Use web search results as primary source
- Add relevant examples and specifics
- Use markdown formatting (bold, lists, headings)

**THEN** - Add actionable guidance:
- Step-by-step instructions if applicable
- Specific timelines, deadlines, or requirements
- Concrete examples

**OPTIONAL** - End with resources (only if truly helpful):
- Brief "Additional Resources" section
- Format: "**Additional Resources:** [bulleted list]"
- Keep it brief (2-3 resources max)

FORBIDDEN PHRASES (never use these):
❌ "I don't have information"
❌ "I don't see specific information"
❌ "I'm not sure"
❌ "I can't find"
❌ "The context doesn't contain"
❌ Leading with "contact the office" or "check with department"

If details aren't explicit, construct answers using:
✅ Web search results (primary source)
✅ General university program knowledge
✅ Typical UVA practices and standards
✅ Logical reasoning about how such programs work

PROVIDE YOUR COMPLETE ANSWER NOW:"""

        claude_messages.append({
            "role": "user",
            "content": user_prompt_with_context
        })
        
        print(f"Calling Claude with {len(claude_messages)} messages and {len(context_string)} chars of context")
        
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            temperature=0.7,
            system=system_prompt,
            messages=claude_messages
        )
        
        assistant_response = response.content[0].text
        print(f"Claude response: {assistant_response[:100]}...")
        
        # Step 7: Prepare sources for frontend
        sources = []
        if rag_context:
            for doc in rag_context[:2]:
                metadata = doc.get("metadata", {})
                sources.append({
                    "title": metadata.get("title", metadata.get("source", "UVA Document")),
                    "type": "document"
                })
        if course_context:
            for course in course_context[:2]:
                sources.append({
                    "title": f"{course['courseCode']}: {course['title']}",
                    "type": "course",
                    "source": "Course Catalog"
                })
        if club_context:
            for club in club_context[:2]:
                sources.append({
                    "title": club['name'],
                    "type": "club",
                    "source": "Student Organizations"
                })
        if web_search_results:
            for result in web_search_results[:3]:
                title = result.get('title', 'Web Search Result')
                url = result.get('href', result.get('link', ''))
                sources.append({
                    "title": title,
                    "type": "web",
                    "source": url if url else "Web Search"
                })
        
        return {
            "message": assistant_response,
            "context": sources
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

