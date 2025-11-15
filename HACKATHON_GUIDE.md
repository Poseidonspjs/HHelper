# 🏆 HoosHelper: Hackathon Execution Guide

**Win your hackathon with this hour-by-hour plan**

---

## 📋 Pre-Hackathon Checklist (Do This Week Before!)

### Account Setup
- [ ] Create Supabase account (free tier)
- [ ] Get OpenAI API key ($5 credit is enough)
- [ ] Get Anthropic API key (free tier available)
- [ ] Create GitHub repository (public)
- [ ] Join hackathon Discord/Slack

### Local Setup
- [ ] Install Node.js 18+
- [ ] Install Python 3.10+
- [ ] Install PostgreSQL (or plan to use Supabase)
- [ ] Clone your repo locally
- [ ] Run `setup.sh` to verify everything works
- [ ] Test that frontend and backend start

### Practice
- [ ] Run through demo script 3 times
- [ ] Time your demo (keep under 5 minutes)
- [ ] Test on different networks (WiFi, hotspot backup)
- [ ] Prepare 1-slide architecture diagram

---

## ⏰ Hour-by-Hour Timeline (48 Hours)

### **Hour 0-2: Setup & Foundation**

**Goal**: Environment ready, database initialized

```bash
# Immediate actions
git pull
./setup.sh
cd frontend && npm install && npx prisma db push
cd ../backend && pip install -r requirements.txt
```

**What to build**:
- ✅ Verify all dependencies install
- ✅ Create Supabase database with pgvector
- ✅ Set up .env files with API keys
- ✅ Run migrations
- ✅ Test backend starts (port 8000)
- ✅ Test frontend starts (port 3000)

**Output**: Green "Hello World" on both servers

---

### **Hour 2-6: Backend Foundation**

**Goal**: Working API with sample data

**Priority 1: Prerequisite Validator** (CORE FEATURE)
```python
# backend/main.py - Already implemented!
# Test it works:
curl -X POST http://localhost:8000/api/validate-plan \
  -H "Content-Type: application/json" \
  -d '{"courses":[{"courseCode":"CS 4750","year":1,"semester":"Fall"}],"startYear":2024}'
```

**Priority 2: Sample Data**
```bash
cd backend
python -c "from scrapers import scrape_courses; scrape_courses()"
# Uses fallback data if scraping fails - that's fine!
```

**Output**: 
- `/api/courses` returns 10+ courses
- `/api/validate-plan` returns validation result
- Prerequisite graph built correctly

---

### **Hour 6-12: Frontend Foundation**

**Goal**: Working plan editor UI

**Priority 1: Plan Editor Page** ✅ Already built!
- Test drag-and-drop works
- Verify courses render
- Test semester grid

**Priority 2: Connect to Backend**
- Add courses to plan
- Click "Validate Plan"
- See errors displayed (red highlighting)

**Demo Checkpoint**: Show working prerequisite validation!

---

### **Hour 12-18: Break + RAG System**

**Take a 2-hour break!** Seriously. Sleep, eat, shower.

**Priority 1: RAG Content Scraping**
```bash
cd backend
python -c "from scrapers import scrape_rag_content; scrape_rag_content()"
```

**Priority 2: Test RAG System**
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is HGR?"}]}'
```

**Priority 3: Vector Embeddings**
- Verify OpenAI API key works
- Run embedding generation
- Store in pgvector

**Output**: Chat returns intelligent UVA-specific answers

---

### **Hour 18-24: Chat UI + Club Features**

**Goal**: Full chat experience

**Priority 1: Chat Page** ✅ Already built!
- Test message sending
- Verify responses appear
- Check loading states

**Priority 2: Club Scraper**
```bash
python -c "from scrapers import scrape_clubs; scrape_clubs()"
```

**Priority 3: Club Discovery Page** ✅ Already built!
- Test search
- Test filters
- Verify data displays

**Demo Checkpoint**: Show chat answering UVA questions!

---

### **Hour 24-30: Sleep!**

**Seriously, sleep 6 hours.** You need energy for demos.

Set alarm for Hour 30. Your code is already working.

---

### **Hour 30-36: Polish & Testing**

**Goal**: Production-ready experience

**Polish Checklist**:
- [ ] Loading states on all API calls
- [ ] Error messages are user-friendly
- [ ] Empty states have helpful text
- [ ] Mobile responsive (test on phone)
- [ ] No console errors
- [ ] All buttons work

**Test Scenarios**:
1. **Happy Path**: Add courses, validate, chat, browse clubs
2. **Validation Error**: Add CS 4750 to Year 1 → see error
3. **Chat**: Ask about HGR → see sources
4. **Clubs**: Search "tech" → see results

**Dashboard Polish**:
- Add sample current courses
- Add GPA widget
- Add upcoming tasks
- Make it look lived-in

---

### **Hour 36-42: Demo Prep**

**Goal**: Perfect 5-minute demo

**Demo Script** (Practice 10x):

```
[0:00-0:30] HOOK
"Every UVA student struggles with course planning.
Prerequisite errors. Missed requirements. Overwhelming choices.
HoosHelper solves this with AI."

[0:30-1:00] OVERVIEW
"Here's your dashboard - current courses, GPA, upcoming deadlines."
[Show dashboard quickly]

[1:00-3:00] MONEY SHOT: Plan Validation
"Let me show you the real power. 4-year plan editor."
[Open plan page]

"I'll add CS 1110 to first year fall..."
[Drag course]

"Now let me add CS 4750 - an advanced database course."
[Drag to Year 1]

"Watch what happens when I validate..."
[Click validate button]

"ERROR! The system knows CS 4750 requires CS 2120.
This uses graph algorithms to check prerequisites."

"Let me fix that by adding CS 2120 to Year 2..."
[Drag CS 2120, move CS 4750 to Year 3]

"Validate again... Perfect! Plan is valid."

[3:00-4:00] Chat Demo
"Now for the AI assistant..."
[Open chat]

[Type: "What is the Hoos Getting Ready program?"]
[Show response with sources]

"It uses RAG - retrieval-augmented generation.
We scraped UVA content, embedded it with OpenAI,
stored in pgvector, and retrieve with Claude."

[Type: "Add CS 2100 to my spring semester"]
"And the coolest part - natural language plan editing!"

[4:00-4:30] Clubs
"Discover 100+ clubs with smart filtering."
[Quick browse]

[4:30-5:00] CLOSE
"HoosHelper isn't a prototype. It's production-ready:
- Graph algorithms for validation
- pgvector for semantic search  
- Microservice architecture
- Real UVA data

This solves a real problem students face TODAY."
```

**Backup Plan**:
- Record video of demo (in case laptop dies)
- Have screenshots of key features
- Print architecture diagram
- Prepare for questions (see below)

---

### **Hour 42-46: Presentation Slides**

**5 Slides Maximum**:

1. **Title Slide**
   - HoosHelper logo/name
   - "AI-Powered Academic Planning for UVA"
   - Your names

2. **Problem Slide**
   - "UVA students struggle with:"
   - ❌ Complex prerequisites
   - ❌ Information overload
   - ❌ Poor planning tools

3. **Solution Slide**
   - Screenshot of plan editor
   - "Real-time validation + AI guidance"

4. **Technical Architecture**
   - Diagram showing:
     - Next.js Frontend
     - FastAPI Backend
     - PostgreSQL + pgvector
     - Claude Sonnet 4
     - OpenAI Embeddings

5. **Impact Slide**
   - "Production-ready features:"
   - ✅ Graph-based prerequisite checking
   - ✅ RAG with vector database
   - ✅ 100+ courses, 20+ clubs
   - ✅ Natural language plan editing

**Design Tips**:
- Use Canva or Google Slides
- UVA colors: Navy (#232D4B) and Orange (#E57200)
- Keep text minimal
- Use screenshots over text

---

### **Hour 46-48: Final Testing & Contingencies**

**Pre-Demo Checklist**:
- [ ] Laptop fully charged
- [ ] Backup charger accessible
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Phone hotspot configured (backup internet)
- [ ] Video recording of demo (just in case)
- [ ] GitHub repo updated
- [ ] .env files NOT committed (check!)

**Database Pre-Load**:
```bash
# Add sample courses to your plan for demo
# This makes demo faster - no dragging needed
# Just show the validation error!
```

**Emergency Protocols**:

**If laptop crashes**:
- Show video recording
- Have screenshots
- Explain architecture from diagram

**If internet dies**:
- Switch to phone hotspot
- Backend/frontend on localhost still works
- Chat might fail (Claude needs internet) - explain it

**If backend crashes mid-demo**:
- "This is the beauty of microservices..."
- Show frontend still renders
- Explain how backend would validate

---

## 🎤 Common Judge Questions & Answers

### "How does the prerequisite validation work?"

**Answer**: 
"We built a directed graph where each course is a node and prerequisites are edges. When validating, we traverse the student's plan chronologically, maintaining a set of completed courses. For each course, we check if its prerequisites are in the completed set. This handles complex AND/OR logic and gives specific error messages."

### "How did you build the RAG system?"

**Answer**:
"Four steps: First, we scraped UVA content - course catalogs, policies, guides. Second, we generated embeddings using OpenAI's text-embedding-3-small model, which produces 1536-dimensional vectors. Third, we stored these in PostgreSQL using the pgvector extension for fast similarity search. Fourth, when a user asks a question, we embed their query, find the top-K similar documents via cosine similarity, and feed that context to Claude Sonnet 4 to generate a grounded response."

### "Is this actually deployed?"

**Answer**:
"It's deployment-ready. We have Docker configs, can deploy the frontend to Vercel in 5 minutes, backend to Railway in 10 minutes, and database is already on Supabase. We focused on building a robust MVP that students can use immediately rather than fighting deployment bugs during the hackathon."

### "How is this different from ChatGPT?"

**Answer**:
"Three key differences: First, ChatGPT doesn't know UVA-specific information - we embedded our own UVA content. Second, we have structured data and algorithms - like the prerequisite graph - that ChatGPT can't do. Third, we built features tailored to academic planning that a general chatbot doesn't have, like the drag-and-drop plan editor with real-time validation."

### "What's your tech stack?"

**Answer**:
"Modern microservice architecture: Next.js 14 frontend with React and TailwindCSS, FastAPI backend in Python for ML/AI workloads, PostgreSQL with pgvector for both relational data and vector search, Claude Sonnet 4 for the LLM, OpenAI for embeddings, and Prisma as our ORM. This gives us type safety on the frontend and high performance for AI on the backend."

### "How did you get the UVA data?"

**Answer**:
"We built async web scrapers using BeautifulSoup and httpx that pull from public UVA sources like the CS advising site, student organization directories, and orientation guides. We also have fallback data so the app works even if scraping fails. For a production version, we'd work with UVA IT to get official API access."

### "What's next for this project?"

**Answer**:
"Three priorities: First, integrate with UVA's SIS system so students can import their actual transcript and enrolled courses. Second, add degree audit checking to automatically verify graduation requirements. Third, expand beyond CS to all majors with their specific requirements. We've built the foundation - now it's about scaling the content."

---

## 🏅 Winning Strategies

### Technical Depth (40% of score)

**Highlight**:
- ✅ Graph algorithms (not just CRUD)
- ✅ Vector database (advanced)
- ✅ RAG system (cutting-edge AI)
- ✅ Microservice architecture (scalable)

**Explain**: Don't just show it works - explain HOW it works.

### Problem Solving (30% of score)

**Emphasize**:
- Real student pain point (everyone relates)
- Immediate value (use it today)
- Production-ready (not a toy)

**User Story**: "As a first-year CS student, I tried to register for CS 4750 and got rejected because I hadn't taken CS 2120. If I had HoosHelper, I would have caught that error months earlier."

### Execution (20% of score)

**Demonstrate**:
- Every feature works smoothly
- Professional UI (not bootstrap default)
- No broken links or errors
- Handles edge cases gracefully

**Polish Matters**: A beautiful, working app beats a buggy app with more features.

### Presentation (10% of score)

**Keys**:
- Confident delivery
- Clear problem statement
- Engaging demo (tell a story)
- Handle questions well

**Practice**: Record yourself, watch it, cringe, improve, repeat.

---

## 🚨 Last-Minute Emergencies

### "It's Hour 40 and I'm behind schedule!"

**Priority Triage**:
1. **Must Have**: Plan editor + validation (CORE FEATURE)
2. **Should Have**: Chat with RAG
3. **Nice to Have**: Clubs, dashboard polish
4. **Skip**: Advanced features, animations

**Action**: 
- Disable chat page if RAG isn't working
- Use fallback data exclusively
- Focus on ONE feature that works perfectly

### "RAG system isn't working!"

**Fallback**: 
- Make chat call Claude WITHOUT vector search
- Hard-code some UVA facts into the prompt
- Still impressive, just not RAG

### "Drag-and-drop is buggy!"

**Fallback**:
- Add buttons instead: "Add to Plan" → "Remove"
- Validation still works (the key feature)
- Less impressive but still functional

---

## 🎉 Day-of Checklist

### Morning Of
- [ ] Good breakfast
- [ ] Shower (seriously)
- [ ] Laptop charged
- [ ] Backup charger
- [ ] Business casual attire
- [ ] Breath mints

### 1 Hour Before Demo
- [ ] Start backend
- [ ] Start frontend
- [ ] Test all features once
- [ ] Clear browser cache
- [ ] Close unnecessary tabs
- [ ] Disable notifications
- [ ] Put phone on silent

### At Demo Station
- [ ] Request table near power outlet
- [ ] Test WiFi connection
- [ ] Have hotspot ready
- [ ] Open browser to localhost:3000
- [ ] Have slides ready (separate tab)
- [ ] Water bottle accessible

---

## 🏆 Judging Criteria Breakdown

Most hackathons judge on:

1. **Technical Complexity (40%)**
   - Your strengths: Graph algorithms, RAG, vector DB
   - Emphasize: Architecture decisions, scalability

2. **Problem & Impact (30%)**
   - Your strengths: Real student problem, immediate use
   - Emphasize: User research, UVA community value

3. **Execution (20%)**
   - Your strengths: Working demo, professional UI
   - Emphasize: Attention to detail, error handling

4. **Presentation (10%)**
   - Your strengths: Clear explanation, confident delivery
   - Emphasize: Practice makes perfect

---

## 💡 Pro Tips

1. **Start with the end**: Know your demo script on Hour 0
2. **One feature perfectly > three features barely**
3. **Talk to judges during build time** (show enthusiasm)
4. **Help other teams** (good karma, networking)
5. **Take photos** (for LinkedIn, resume)
6. **Get business cards** (judges are potential employers)
7. **Have fun** (judges can tell if you're passionate)

---

## 📸 Content for Social Media

**During Hackathon**:
- Photo of your team at station
- Screenshot of working app
- Whiteboard architecture diagram

**After Hackathon**:
- Demo video (1 minute)
- Architecture diagram (share on LinkedIn)
- GitHub link with README
- "What I learned" blog post

**LinkedIn Post Template**:
```
🎓 Just built HoosHelper at [Hackathon Name]!

An AI-powered academic planning platform using:
• Next.js + FastAPI
• PostgreSQL + pgvector
• Claude Sonnet 4
• RAG for semantic search

Features:
✅ Prerequisite validation with graph algorithms
✅ Natural language plan editing
✅ 100+ UVA courses and clubs

Check it out: [GitHub link]

#hackathon #ai #fullstack #uva
```

---

## 🎯 Remember

You've built something genuinely impressive. This isn't a toy project - it's a production-ready application that solves a real problem with sophisticated technology.

**You've got this! Go win!** 🏆

---

**Questions during the hackathon?**
- Check README.md for troubleshooting
- Google the error
- Ask mentors
- Check Discord
- Keep calm and debug on

**Most importantly**: Have fun and learn something new! 🚀

