# HoosHelper RAG System Guide

## 🎯 Overview

The HoosHelper RAG (Retrieval-Augmented Generation) system generates personalized 4-year academic plans for UVA students using:
- **Real course data** from Supabase (2,963 courses with descriptions)
- **Student advice content** (11 RAG documents with UVA-specific guidance)
- **Club information** (39 UVA clubs)
- **Claude Sonnet 4** for intelligent reasoning and plan generation

## 🔄 How It Works

### 1. User Fills Onboarding Form
The student provides:
- **Major** (e.g., "Computer Science")
- **Focus Area** (e.g., "Machine Learning", "Software Engineering")
- **Entry Year** (e.g., "2024")
- **AP Credits** (e.g., ["Calculus AB", "English"])
- **GPA** (optional)
- **Additional Details** (optional career goals, interests, etc.)

### 2. Backend RAG Pipeline (`/api/generate-plan`)

#### Step 1: Query Courses from Database
```python
# Get courses relevant to the major
major_dept = "CS"  # Extracted from "Computer Science"
courses_response = supabase_client.table("courses").select("*").ilike(
    "department", f"%{major_dept}%"
).limit(100).execute()

# Also get general education courses
gen_ed_response = supabase_client.table("courses").select("*").in_(
    "department", ["ENWR", "MATH", "APMA", "PHYS", "CHEM", "BIOL"]
).limit(50).execute()
```

**Result**: ~150 relevant courses with full descriptions, prerequisites, and credits

#### Step 2: Retrieve RAG Content
```python
# Query vector store for relevant academic advice
rag_query = "How to plan a 4-year academic schedule for Computer Science major with focus on Machine Learning. Prerequisites, course sequence, and academic advice."

# Uses OpenAI embeddings + Supabase vector search
rag_context = rag_system.retrieve_context(rag_query, k=5)
```

**Result**: Top 5 most relevant RAG documents, e.g.:
- "CS Prerequisites and Path" (prerequisite chains)
- "Essential Academic Success Tips" (study strategies)
- "Course Registration Guide" (planning advice)

#### Step 3: Build Prompt for Claude
```python
system_prompt = """You are an expert academic advisor for UVA students. 
Create personalized, realistic 4-year academic plans that:
- Follow prerequisite chains correctly
- Balance course load (12-18 credits per semester)
- Include major requirements, general education, and electives
- Consider the student's interests and goals
- Provide practical academic advice

Output as JSON:
{
  "year1": {
    "fall": [{"courseCode": "CS 1110", "title": "...", "credits": 3, "reasoning": "..."}],
    "spring": [...]
  },
  "year2": {...},
  "year3": {...},
  "year4": {...},
  "reasoning": "Overall plan explanation",
  "recommendations": ["Tip 1", "Tip 2", ...]
}"""

user_prompt = f"""Create a personalized 4-year academic plan for this UVA student:

STUDENT PROFILE:
- Major: Computer Science
- Focus Area: Machine Learning
- Entry Year: 2024
- AP Credits: Calculus AB, English
- Additional Details: Interested in AI research

AVAILABLE COURSES:
{150 courses with descriptions, prerequisites, credits}

UVA ACADEMIC GUIDANCE:
{5 RAG documents with UVA-specific advice}

Please create a comprehensive 4-year plan..."""
```

#### Step 4: Claude Generates the Plan
```python
message = anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    temperature=0.7,
    system=system_prompt,
    messages=[{"role": "user", "content": user_prompt}]
)
```

**Claude's Reasoning Process**:
1. Analyzes the student's profile (major, interests, AP credits)
2. Reviews available courses and prerequisites
3. Consults RAG content for UVA-specific advice
4. Builds a semester-by-semester plan:
   - **Year 1**: Foundational courses (CS 1110, MATH 1310, Gen Eds)
   - **Year 2**: Core requirements (CS 2100, CS 2120, Prerequisites)
   - **Year 3**: Advanced courses + ML focus (CS 4710 AI, CS 4774 ML)
   - **Year 4**: Electives, capstone, research opportunities

#### Step 5: Return Structured Plan
```json
{
  "year1": {
    "fall": [
      {"courseCode": "CS 1110", "title": "Intro to Programming", "credits": 3, "reasoning": "Foundation course"},
      {"courseCode": "MATH 1310", "title": "Calculus I", "credits": 4, "reasoning": "Math prerequisite"},
      {"courseCode": "ENWR 1510", "title": "Academic Writing", "credits": 3, "reasoning": "Gen ed requirement"},
      {"courseCode": "PSYC 1010", "title": "Intro to Psychology", "credits": 3, "reasoning": "Social science elective"}
    ],
    "spring": [...]
  },
  "year2": {...},
  "year3": {...},
  "year4": {...},
  "reasoning": "This plan builds a strong foundation in CS fundamentals while progressively introducing ML-focused courses. AP Calculus credit allows you to start with Calc II or skip to discrete math earlier.",
  "recommendations": [
    "Join CS Society (CSS) for networking and projects",
    "Consider undergraduate research in AI lab by sophomore year",
    "Take CS 4710 (AI) before CS 4774 (ML) for better preparation"
  ]
}
```

### 3. Frontend Displays the Plan
```typescript
// Load generated plan from localStorage
const generatedPlan = JSON.parse(localStorage.getItem('generatedPlan'));

// Convert to frontend format and display in drag-and-drop interface
setPlan({
  "1-Fall": [CS 1110, MATH 1310, ENWR 1510, PSYC 1010],
  "1-Spring": [...],
  // ... 8 semesters total
});
```

Students can then:
- ✅ View the AI-generated plan
- ✅ Drag and drop courses between semesters
- ✅ Add/remove courses
- ✅ Validate prerequisites
- ✅ See reasoning and recommendations

## 🔑 Key Features

### 1. **Smart Prerequisite Handling**
- Claude understands prerequisite chains (e.g., CS 1110 → CS 2100 → CS 2120 → CS 3100)
- Won't schedule advanced courses before prerequisites
- Considers AP credits to skip intro courses

### 2. **Credit Load Balancing**
- Targets 15-16 credits per semester (4-5 courses)
- Balances hard courses with lighter electives
- Warns about overload (>18 credits) or underload (<12 credits)

### 3. **Major-Specific Planning**
- Queries courses from student's department
- Follows UVA degree requirements
- Aligns with chosen focus area

### 4. **RAG-Enhanced Advice**
- Uses real UVA student advice from RAG documents
- Considers course registration tips
- Includes club recommendations
- Provides career development timeline

### 5. **Personalization**
- Considers student's interests and goals
- Adapts to GPA and credits completed
- Factors in additional details (study abroad, research, etc.)

## 🚀 How to Test

### 1. Start the Backend
```bash
cd /Users/mk/hackathon/CFGHHelper/HHelper/backend
python3 main.py
```

Backend runs on `http://localhost:8000`

### 2. Start the Frontend
```bash
cd /Users/mk/hackathon/CFGHHelper/HHelper/frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Fill Out the Onboarding Form
1. Go to `http://localhost:3000`
2. Fill out the form:
   - **Major**: "Computer Science"
   - **Focus Area**: "Machine Learning"
   - **Entry Year**: "2024"
   - **AP Credits**: Select some credits
   - **Additional Details**: "Interested in AI research and want to work at a tech company"
3. Click "Submit"

### 4. Watch the Magic!
- Loading message: "Generating your personalized 4-year plan..."
- Backend queries database for CS courses
- RAG system retrieves UVA academic advice
- Claude generates a complete 4-year plan
- Success message: "✓ Plan generated! Redirecting..."
- Redirects to `/plan` page with your AI-generated plan

### 5. Interact with Your Plan
- View all 8 semesters (4 years × 2 semesters)
- Each course shows: code, title, credits
- Drag and drop courses between semesters
- Add/remove courses
- Validate prerequisites
- See AI's reasoning and recommendations

## 📊 Data Sources

### Courses (2,963 total)
- **Source**: Lou's List (UVA's official course catalog)
- **Format**: `uva_courses.json` → Supabase `courses` table
- **Fields**: courseCode, title, description, credits, department, prerequisites
- **Departments**: 198 (CS, MATH, ENWR, PHYS, LAW, GBUS, etc.)

### RAG Documents (11 total)
- **Source**: UVA Reddit, student experiences, UVA websites
- **Format**: `uva_rag_content.json` → Supabase `rag_documents` table (with embeddings)
- **Types**:
  - Student advice (2 docs): Academic tips, first-year guide
  - Course planning (1 doc): CS prerequisites and paths
  - Resources (6 docs): Registration, clubs, career, housing, mental health, research
  - Culture (1 doc): UVA traditions and culture
  - Policy (1 doc): Registration policies

### Clubs (39 total)
- **Source**: UVA club directories
- **Format**: `uva_clubs.json` → Supabase `clubs` table
- **Categories**: Technology (10), Academic (5), Service (4), Engineering (5), etc.

## 🛠️ Technical Architecture

### Backend Stack
- **Framework**: FastAPI
- **AI**: Anthropic Claude Sonnet 4
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Supabase (PostgreSQL + pgvector)
- **RAG**: LangChain with SupabaseVectorStore

### Frontend Stack
- **Framework**: Next.js 14 (App Router)
- **UI**: TailwindCSS + shadcn/ui
- **Drag & Drop**: @hello-pangea/dnd
- **ORM**: Prisma

### Environment Variables

#### Backend `.env`
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
SUPABASE_URL=https://...supabase.co
SUPABASE_ANON_KEY=eyJ...
BACKEND_PORT=8000
```

#### Frontend `.env.local`
```bash
DATABASE_URL=postgresql://...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 API Endpoints

### `POST /api/generate-plan`
**Request**:
```json
{
  "school": "College of Arts & Sciences",
  "major": "Computer Science",
  "focusArea": "Machine Learning",
  "entryYear": "2024",
  "apCredits": ["Calculus AB", "English"],
  "additionalDetails": "Interested in AI research",
  "gpa": "3.8",
  "creditsCompleted": "0"
}
```

**Response**:
```json
{
  "year1": {
    "fall": [...],
    "spring": [...]
  },
  "year2": {...},
  "year3": {...},
  "year4": {...},
  "reasoning": "This plan...",
  "recommendations": [...]
}
```

### `POST /api/chat`
RAG-powered chatbot for academic questions

### `GET /api/courses`
Query courses with filtering

### `POST /api/validate-plan`
Validate prerequisite chain

## 🎓 Example Generated Plan

### Year 1 - Fall
- **CS 1110**: Intro to Programming (3 credits)
- **MATH 1310**: Calculus I (4 credits) *[Skipped with AP credit]*
- **ENWR 1510**: Academic Writing (3 credits)
- **PSYC 1010**: Intro to Psychology (3 credits)
- **Total**: 13 credits

### Year 1 - Spring
- **CS 2100**: Data Structures & Algorithms I (3 credits)
- **MATH 1320**: Calculus II (4 credits)
- **PHYS 1425**: Physics I (4 credits)
- **Elective**: Gen ed (3 credits)
- **Total**: 14 credits

### Year 2 - Fall
- **CS 2120**: Discrete Math (3 credits)
- **CS 2130**: Computer Systems (3 credits)
- **MATH 2310**: Multivariable Calculus (4 credits)
- **Elective**: Social science (3 credits)
- **Total**: 13 credits

... and so on through Year 4!

## 🔮 Future Enhancements

1. **Real-time prerequisite validation** during drag-and-drop
2. **Study abroad integration** - block out semesters for travel
3. **Internship planning** - account for summer internships
4. **Minor/certificate tracking** - plan secondary programs
5. **Course availability** - warn if courses aren't offered certain semesters
6. **Graduation requirements** - track degree progress
7. **Export to PDF** - printable 4-year plan

## 🐛 Troubleshooting

### Backend won't start
- Check `.env` file has all required keys
- Verify Supabase connection: `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Ensure Claude API key is valid: `ANTHROPIC_API_KEY`

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`

### Plan generation fails
- Check Claude API key has credits
- Verify database has courses: `SELECT COUNT(*) FROM courses;`
- Check RAG documents exist: `SELECT COUNT(*) FROM rag_documents;`
- Review backend logs for errors

### Plan looks wrong
- Claude may hallucinate courses not in database
- Increase course limit in query (currently 150)
- Adjust Claude's temperature (lower = more conservative)
- Provide more context in "Additional Details"

## ✅ Success Checklist

- [x] Backend API running on port 8000
- [x] Frontend running on port 3000
- [x] Database populated with 2,963 courses
- [x] RAG documents embedded in vector store
- [x] Claude API key configured
- [x] OpenAI API key configured (for embeddings)
- [x] Onboarding form submits successfully
- [x] Plan generation completes in ~10-30 seconds
- [x] Plan displays on `/plan` page
- [x] Drag-and-drop works
- [x] Courses show correct information

## 🎉 You're All Set!

Your RAG-powered 4-year plan generator is ready to help UVA students plan their academic journey!

