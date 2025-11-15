# 🎓 HoosHelper

> **AI-powered student success platform for UVA students**

HoosHelper is a production-grade web application that helps UVA students plan their academic journey, discover opportunities, and get instant answers to university-related questions using AI.

---

## ✨ Features

### 📅 4-Year Plan Editor
- **Drag-and-drop interface** for intuitive course planning
- **Real-time prerequisite validation** using graph algorithms
- **Credit load warnings** (12-18 credits recommended)
- **Visual error feedback** with specific prerequisite violations

### 🤖 AI Chat Assistant
- **Claude Sonnet 4** for natural language understanding
- **RAG (Retrieval-Augmented Generation)** with pgvector for UVA-specific knowledge
- **Natural language plan editing** - "Add CS 2100 to spring semester"
- **Contextual responses** with source citations

### 🎯 Club Discovery
- Browse **100+ student organizations**
- **Smart filtering** by category and tags
- **Search** by name, description, or interests
- Contact information and social links

### 📊 Personalized Dashboard
- Current course overview
- GPA tracking
- Upcoming deadlines
- Recommended clubs based on major

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React, TailwindCSS | Modern, responsive UI |
| **Backend** | FastAPI (Python) | High-performance async API |
| **Database** | PostgreSQL + pgvector | Relational data + vector search |
| **ORM** | Prisma | Type-safe database access |
| **AI/LLM** | Claude Sonnet 4 (Anthropic) | Chat and intelligent responses |
| **Embeddings** | OpenAI text-embedding-3-small | 1536-dimensional vectors |
| **RAG** | LangChain | Retrieval pipeline |
| **UI Components** | shadcn/ui | Professional component library |
| **Drag & Drop** | @hello-pangea/dnd | Plan editor interactions |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** 14+ with pgvector extension
- **API Keys**:
  - OpenAI API key (for embeddings)
  - Anthropic API key (for Claude)
  - Supabase account (or PostgreSQL + pgvector)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/hooshelper.git
cd hooshelper
```

2. **Run the automated setup script**

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

3. **Set up the database**

Create a PostgreSQL database with pgvector:

```sql
CREATE DATABASE hooshelper;
\c hooshelper
CREATE EXTENSION vector;
```

4. **Configure environment variables**

Create `.env` in the project root:

```bash
# Database (use your Supabase or PostgreSQL connection string)
DATABASE_URL="postgresql://user:password@host:5432/hooshelper?pgbouncer=true"
DIRECT_URL="postgresql://user:password@host:5432/hooshelper"

# Supabase (if using Supabase)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"

# OpenAI
OPENAI_API_KEY="sk-..."

# Anthropic
ANTHROPIC_API_KEY="sk-ant-..."

# Frontend
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

5. **Install frontend dependencies**

```bash
cd frontend
npm install
npx prisma generate
npx prisma db push
```

6. **Install backend dependencies**

```bash
cd ../backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

7. **Populate the database** (optional but recommended)

```bash
# Still in backend directory with venv activated
python -c "from scrapers import scrape_courses, scrape_clubs, scrape_rag_content; scrape_courses(); scrape_clubs(); scrape_rag_content()"
```

8. **Run the application**

In two separate terminals:

```bash
# Terminal 1: Backend (from backend directory)
source venv/bin/activate
python main.py

# Terminal 2: Frontend (from frontend directory)
npm run dev
```

9. **Open your browser**

Navigate to **http://localhost:3000**

---

## 📁 Project Structure

```
hooshelper/
├── README.md                    # This file
├── HACKATHON_GUIDE.md          # Hour-by-hour execution plan
├── DEPLOYMENT.md               # Production deployment guide
├── setup.sh                    # Automated setup script
│
├── frontend/                   # Next.js application
│   ├── prisma/
│   │   └── schema.prisma       # Database schema (29 models)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Dashboard
│   │   │   ├── plan/page.tsx   # 4-year plan editor
│   │   │   ├── chat/page.tsx   # AI chatbot
│   │   │   └── clubs/page.tsx  # Club discovery
│   │   ├── components/ui/      # shadcn/ui components
│   │   └── lib/utils.ts
│   ├── package.json
│   └── next.config.mjs
│
└── backend/                    # FastAPI application
    ├── main.py                 # Main API with RAG & validation
    ├── scrapers/
    │   ├── course_scraper.py   # Course data scraping
    │   ├── club_scraper.py     # Club data scraping
    │   └── rag_scraper.py      # RAG content scraping
    └── requirements.txt
```

---

## 🎯 Core Features Explained

### Prerequisite Validation

The system uses a **graph-based algorithm** to validate course plans:

1. Builds a directed graph of course prerequisites
2. Traverses the plan chronologically
3. Checks that prerequisites are taken before dependent courses
4. Handles complex AND/OR prerequisite logic
5. Returns specific error messages with course and semester

### RAG System Architecture

```
User Question
    ↓
OpenAI Embeddings (1536d)
    ↓
pgvector Similarity Search
    ↓
Retrieve Top-K Documents
    ↓
Claude Sonnet 4 with Context
    ↓
Generated Response
```

The system:
- Stores UVA content (courses, policies, guides) as vector embeddings
- Uses cosine similarity to find relevant context
- Feeds context to Claude for accurate, grounded responses
- Cites sources for transparency

---

## 🧪 Testing the Features

### Test Prerequisite Validation

1. Go to **4-Year Plan** page
2. Drag **CS 4750** (Database Systems) to Year 1, Fall
3. Click **Validate Plan**
4. See error: "Missing prerequisite: CS 2120"
5. Add **CS 2120** to Year 1, Fall (or earlier)
6. Validate again - error resolved!

### Test RAG Chat

1. Go to **Chat** page
2. Ask: "What is the Hoos Getting Ready program?"
3. See AI response with sources from RAG system
4. Try: "What are the prerequisites for CS 4750?"
5. Try plan editing: "Add CS 2100 to my spring semester"

### Test Club Discovery

1. Go to **Clubs** page
2. Search: "technology"
3. Filter by category: "Tech"
4. Browse results with contact information

---

## 🔧 Development

### Database Schema Updates

After modifying `prisma/schema.prisma`:

```bash
cd frontend
npx prisma generate  # Regenerate Prisma client
npx prisma db push   # Push changes to database
```

### Adding New Scrapers

1. Create scraper in `backend/scrapers/`
2. Add fallback data for reliability
3. Import in `backend/main.py`
4. Create endpoint with background task

### Customizing the UI

- Edit `tailwind.config.ts` for theme changes
- Modify `globals.css` for CSS variables
- Components in `src/components/ui/` use shadcn/ui patterns

---

## 📊 Database Schema Highlights

**29 Models Total**, including:

- **User & UserProfile** - User accounts and preferences
- **Course & CoursePrerequisite** - Course catalog with prerequisite graph
- **StudentPlan & StudentPlanCourse** - User's 4-year plans
- **PlanValidation** - Validation results history
- **Club & ClubTag** - Student organizations
- **RagDocument** - Vector embeddings for semantic search (1536d)
- **ChatSession & ChatMessage** - Chat history
- **DegreeRequirement** - Major requirements
- **Resource** - Academic resources and support
- **ResearchOpportunity** - Undergraduate research listings
- **Event** - Campus events

---

## 🐛 Troubleshooting

### "Module not found" errors

```bash
cd frontend
npm install
npx prisma generate
```

### Backend won't start

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Database connection errors

- Verify `DATABASE_URL` in `.env`
- Check PostgreSQL is running
- Ensure pgvector extension is installed: `CREATE EXTENSION vector;`

### Frontend can't reach backend

- Backend must be running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env`
- Verify CORS settings in `backend/main.py`

### Scraping returns no data

- Normal for some sources (network restrictions, structure changes)
- Fallback data automatically loads
- You can use the app with fallback data

---

## 🚢 Deployment

See **DEPLOYMENT.md** for full production deployment guide.

Quick options:
- **Vercel** (frontend) + **Railway** (backend) + **Supabase** (database)
- **VPS with Docker** (all-in-one)
- **Supabase** (all services)

---

## 🎓 For Hackathons

See **HACKATHON_GUIDE.md** for:
- Hour-by-hour execution plan
- Demo script
- Presentation tips
- Common judge questions

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- UVA Computer Science Department
- Hoos Getting Ready Program
- Claude AI by Anthropic
- OpenAI Embeddings
- Supabase for pgvector hosting

---

## 📧 Contact

Questions? Issues? Reach out:
- GitHub Issues: [github.com/yourusername/hooshelper/issues](https://github.com/yourusername/hooshelper/issues)
- Email: your.email@virginia.edu

---

**Built with ❤️ for the UVA community**

*This is a student project and is not officially affiliated with the University of Virginia.*
