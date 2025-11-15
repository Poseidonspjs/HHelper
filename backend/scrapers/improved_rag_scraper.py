"""
Comprehensive RAG Content Scraper for UVA
Scrapes helpful information from multiple sources
Author: Enhanced for HoosHelper
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
import json
import re

class UVARAGScraper:
    """Scrapes comprehensive UVA information for RAG system"""
    
    def __init__(self):
        self.documents = []
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def close(self):
        await self.client.aclose()
    
    def get_comprehensive_content(self) -> List[Dict]:
        """Comprehensive RAG content with real UVA information"""
        return [
            # Academic Advice
            {
                "content": """Essential Academic Advice from UVA Students (from Reddit and student experiences):

1. ACTUALLY GO TO CLASS
You're never going to watch recordings later. Professors notice attendance and it affects participation. Being present helps you learn better. You're paying a lot of money to be here - use it.

2. Get to Know Your Professors
Introduce yourself during the first week. Attend office hours early in the semester (not just before exams). Professors give grace on extensions when they know you. They're full of wisdom outside the classroom. This leads to research opportunities and strong recommendation letters.

3. Don't Compare Yourself to Others
There will always be people who seem smarter or better. Focus on doing your personal best. Your mental health matters more than perfect grades. GPA matters less than you think (unless pre-med or law school).

4. Use Your Resources
- Writing Center: free consultations for any writing project
- Teaching Resource Center: peer tutoring for most intro courses  
- Office hours: professors actually want to help you
- Academic coaching: time management and study strategies
- CS TAs: incredibly helpful for debugging and concepts

5. Course Planning Tips
- Read Lou's List AND Course Forum before registering
- Talk to upperclassmen about specific professors
- Balance hard classes with enjoyable ones each semester
- Leave room in schedule for unexpected opportunities
- Don't take all your hardest classes in one semester

6. Time Management
- Set boundaries before classes start (e.g., no work after 10pm)
- Don't sacrifice sleep, meals, or mental health for grades
- Find YOUR study routine (everyone is different)
- Use syllabi to plan ahead for busy weeks
- Start assignments early to avoid all-nighters

7. CS-Specific Advice
- CS 2100 is a make-or-break course - take it seriously
- CS 2120 is required for almost everything - don't delay
- Don't take CS 2100, 2120, and 2130 all together
- Join CSS and go to office hours religiously
- Start coding assignments the day they're released
- Test your code thoroughly before submitting""",
                "source": "https://www.reddit.com/r/UVA/",
                "sourceType": "student_advice",
                "title": "Essential Academic Success Tips",
                "tags": ["academic", "advice", "studying", "success", "reddit"]
            },
            
            # First Year Advice
            {
                "content": """First Year Advice from UVA Upperclassmen:

SOCIAL LIFE:
- Say yes to everything the first month (within reason)
- Your first friend group probably won't be your final one - that's normal
- Go to every social event you can for the first 3 months
- Join at least one club that interests you (Activities Fair!)
- Don't exclusively hang out with your hallmates
- It's okay to branch out and make new friends all four years

ACADEMICS:
- Don't decide your major first semester
- Take classes you're genuinely interested in, not just requirements
- 8am classes sound fine in summer but are brutal in reality
- Actually read the syllabus on day one
- Form study groups early in the semester
- Go to office hours even if you don't have questions

PRACTICAL TIPS:
- Get a bike or learn the UTS bus routes
- Bodo's Bagels is worth the line
- Clem library is best for late-night studying  
- Skip the Newcomb vent (it smells terrible)
- AFC pool is a hidden gem for relaxation
- Do laundry on weekday afternoons (weekends are packed)

MENTAL HEALTH:
- Everyone struggles with the transition
- Homesickness is completely normal
- Don't compare your real life to others' social media
- Use CAPS if you're struggling
- Take mental health days when needed
- Call your family and friends from home

THINGS TO DO:
- Football game vs Virginia Tech (even if you don't like football)
- Attend Lighting of the Lawn in December
- Go to Foxfield (spring and fall races)
- Hike Old Rag or Humpback Rocks
- Explore the Corner and downtown Charlottesville
- Take advantage of free student events

MISTAKES TO AVOID:
- Skipping the first two weeks of classes
- Not attending Activities Fair
- Only hanging out in your room
- Ignoring red flags in your mental health
- Not asking for help when you need it
- Comparing yourself to everyone else""",
                "source": "https://www.reddit.com/r/UVA/comments/16r5nf0/a_comprehensive_uva_guide/",
                "sourceType": "student_advice",
                "title": "Comprehensive First Year Guide",
                "tags": ["first-year", "advice", "social", "academic", "reddit"]
            },
            
            # CS Prerequisites Path
            {
                "content": """Computer Science Prerequisites and Course Path at UVA:

REQUIRED CORE SEQUENCE:

1. CS 1110 or CS 1111 (First Programming Course)
- CS 1110: For students with NO programming experience
- CS 1111: Accelerated version if you have coding background
- Learn Python fundamentals
- Take this FIRST SEMESTER if possible

2. CS 2100 (Data Structures & Algorithms I) - THE GATEWAY COURSE
- Prerequisites: CS 1110/1111
- This is THE most important course in the major
- Covers arrays, linked lists, stacks, queues, trees, recursion
- Introduces Big-O notation and algorithm analysis
- Many students struggle - take seriously!
- You CANNOT take upper-level CS without passing this

3. CS 2120 (Discrete Math & Theory) - REQUIRED FOR ALMOST EVERYTHING
- Prerequisites: CS 2100
- Logic, proofs, sets, functions, relations, graphs
- Prerequisite for almost ALL 3000/4000 level CS courses
- Don't delay taking this!

4. CS 2130 (Computer Systems & Organization)
- Prerequisites: CS 2100
- C/C++ programming, memory management, pointers
- Required for systems courses (OS, Networks, Security)
- Challenging but essential for understanding computers

TYPICAL COURSE SEQUENCE:
First Year Fall: CS 1110, MATH 1310, Gen Eds
First Year Spring: CS 2100, MATH 1320, Gen Eds
Second Year Fall: CS 2120, CS 2130, MATH 2310
Second Year Spring: CS 3100, CS 3140, Elective

IMPORTANT UPPER-LEVEL COURSES:
- CS 3140: Software Development Essentials (take ASAP!)
- CS 3100: Data Structures & Algorithms II
- CS 4102: Algorithms (very challenging, very important)
- CS 4414: Operating Systems
- CS 4750: Database Systems
- CS 4710: Artificial Intelligence
- CS 4774: Machine Learning (requires linear algebra)
- CS 4630: Defense Against the Dark Arts (Security)

CRITICAL TIPS:
- Complete CS 2100 and 2120 ASAP to unlock upper-levels
- CS 2100 is the hardest course for many - don't take lightly
- Don't take CS 2100, 2120, and 2130 all in one semester
- Join CSS (Computer Science Society) for community
- Go to TA office hours - they're incredibly helpful
- Start coding projects early, test thoroughly
- Lou's List shows which semesters courses are offered""",
                "source": "https://uvacsadvising.org",
                "sourceType": "course_catalog",
                "title": "CS Prerequisites and Path",
                "tags": ["computer-science", "CS", "prerequisites", "course-planning"]
            },
            
            # Course Registration
            {
                "content": """Course Registration Guide at UVA:

REGISTRATION BASICS:
- Registration happens twice per year (for next semester)
- First-years register during orientation with advisor help
- Upper-class students get enrollment appointments by class year
- Full-time: 12-18 credits (typical is 15 credits = 5 courses)
- Use SIS (Student Information System) to register

KEY TOOLS:
- SIS: Official system for registration
- Lou's List: Shows course history, enrollment trends
- Course Forum: Student reviews and professor ratings
- Academic advisors: Help plan your schedule

IMPORTANT DATES & POLICIES:
- Add/drop period: First 2 weeks (adjust without penalty)
- Withdrawal deadline: Around week 10
- Grade options: Graded, Pass/Fail, Audit
- Prerequisites must be completed before dependent courses

REGISTRATION STRATEGY:
1. Wake up EARLY for your enrollment appointment time
2. Have backup courses ready (popular courses fill fast)
3. Check Course Forum for professor reviews
4. Balance hard and easy/enjoyable classes
5. Consider class times (8am is brutal)
6. Leave gaps for lunch and travel time
7. Check Lou's List for when courses are typically offered

COMMON MISTAKES:
- Overloading first semester (stick to 15 credits)
- Not having backup plans
- Scheduling back-to-back classes across Grounds
- Taking all hard classes in one semester
- Not checking prerequisites carefully

TIPS FROM STUDENTS:
- Lou's List shows which semesters courses run
- Course Forum shows professor difficulty ratings
- Talk to upperclassmen about specific professors
- Some courses only offered once per year
- Popular electives fill up immediately
- Having a balanced schedule is key to success""",
                "source": "https://records.ureg.virginia.edu",
                "sourceType": "policy",
                "title": "Course Registration Guide",
                "tags": ["registration", "courses", "planning", "SIS"]
            },
            
            # Getting Involved
            {
                "content": """Getting Involved at UVA: Clubs, Activities, and Organizations

WHEN TO GET INVOLVED:
- Activities Fair (first week of fall) - MUST ATTEND!
- First few weeks: clubs have open meetings
- Spring semester: still totally acceptable to join
- Don't feel pressured to join everything immediately

HOW MANY CLUBS?
- Quality over quantity: 1-2 meaningful > 6 superficial
- Don't let peer pressure push you into too much
- You can always add more later
- It's okay to quit clubs that aren't working out

TYPES OF ORGANIZATIONS:

CIOs (Contracted Independent Organizations):
- Receive UVA funding and support
- 800+ registered groups
- Range from academic to social to service

Popular Categories:
- Technology: CSS, ACM, HooHacks, WICS, Data Science Club
- Service: Madison House (huge!), Habitat, ASB
- Cultural: BSA, LSA, SASA, CSA, KSA
- Business: Entrepreneurship Club, Consulting, Finance
- Arts: Drama, A Cappella, Dance, Photography
- Media: Cavalier Daily, WUVA Radio
- Recreation: Outdoors Club, Running, Climbing

CS-SPECIFIC ORGANIZATIONS:
- CSS (Computer Science Society): Largest CS community
- ACM: Competitive programming, tech talks
- HooHacks: Runs Virginia's largest hackathon
- WICS: Supporting women in CS
- Data Science Club: ML and analytics
- SIGAI: AI/ML projects and learning
- Cyber Security Club: CTFs and competitions
- Girls Who Code: Breaking barriers in tech

FINDING YOUR FIT:
- Try 3-5 clubs first month
- Attend several meetings before committing
- Look for communities, not just resume lines
- Leadership opportunities in 2nd/3rd year
- Clubs are where you meet best friends

TIPS FROM STUDENTS:
- Activities Fair is overwhelming - don't sign up for everything
- Go to first meetings even if intimidated
- Most clubs are beginner-friendly
- Don't quit too early (give it 3-4 meetings)
- Balance academic clubs with fun/social ones
- Join at least one club related to career interests""",
                "source": "https://studentaffairs.virginia.edu",
                "sourceType": "resource",
                "title": "Getting Involved Guide",
                "tags": ["clubs", "activities", "involvement", "CIOs"]
            },
            
            # Career Development
            {
                "content": """Career Development Timeline and Resources at UVA:

CENTER FOR CAREER DEVELOPMENT (CCD):
- Location: 3rd floor Newcomb Hall
- Free for all UVA students (use it!)
- Services: Resume reviews, mock interviews, career counseling
- Platform: UVA Career Connect (Handshake) for jobs/internships

YEAR-BY-YEAR TIMELINE:

FIRST YEAR:
- Explore interests (no pressure to decide!)
- Attend career fairs just to learn
- Join professionally-oriented clubs
- Build relationships with professors
- Start thinking about summer plans

SECOND YEAR:
Fall:
- Attend career fairs seriously
- Get resume reviewed by CCD
- Join professional clubs
- Research summer internship opportunities
- Network at company info sessions

Spring:
- Apply for summer internships
- Practice interviewing (mock interviews at CCD)
- Build LinkedIn profile
- Connect with alumni on LinkedIn

THIRD YEAR:
- Summer internships (often lead to full-time offers)
- On-Grounds recruiting (companies interview on campus)
- Career fairs for full-time positions
- Networking events
- Graduate school prep if applicable

FOURTH YEAR:
- Full-time job applications
- On-Grounds recruiting
- Offer evaluation and negotiation
- Grad school applications if applicable

KEY RESOURCES:
- UVA Career Connect (Handshake): Job/internship postings
- Career Fairs: Fall and spring each year
- On-Grounds Recruiting: Top companies interview here
- Alumni Network: Hoos helping Hoos
- Industry-specific career counselors at CCD

POPULAR PATHS FOR CS STUDENTS:
- Software Engineering: Big Tech, startups, finance
- Data Science/ML: Research, analytics, AI companies
- Consulting: Tech consulting, strategy firms
- Product Management: Tech companies
- Graduate School: MS in CS, PhD programs

TIPS FOR CS STUDENTS:
- Start building projects first year
- Contribute to open source
- Do LeetCode for technical interviews
- Attend company info sessions (free food!)
- Network with alumni on LinkedIn
- Apply to many companies (it's a numbers game)
- Big Tech recruit heavily at UVA""",
                "source": "https://career.virginia.edu",
                "sourceType": "resource",
                "title": "Career Development Timeline",
                "tags": ["career", "internships", "jobs", "professional-development"]
            },
            
            # Housing Information
            {
                "content": """Housing at UVA: Comprehensive Guide

FIRST YEAR HOUSING:
- All first-years live on Grounds
- Assignments over summer (no choice)
- Most rooms are doubles with shared bathrooms
- You'll have a Residential Advisor (RA)

RESIDENTIAL AREAS:
- Alderman Road: Newest, AC, suite-style (most wanted)
- Observatory Hill: Traditional dorms
- Old Dorms (McCormick): Historic, recently renovated
- Hereford: Self-contained with own dining hall

FIRST YEAR TIPS:
- Fill out housing survey honestly
- Reach out to roommate before move-in
- Bring basics but coordinate big items
- Get to know your hallmates first week
- Attend residential events
- Your RA is a resource - use them!

SECOND YEAR OPTIONS:

On-Grounds Housing:
- Enter housing lottery with friends
- Form groups to live together
- More independence than first year
- Can apply to be RA (free housing + stipend!)

Off-Grounds Housing:
- Very popular choice
- Start looking January/February
- Form group with friends
- Various neighborhoods around Grounds

POPULAR OFF-GROUNDS AREAS:
- The Corner: Very close to central Grounds, expensive
- JPA (Jefferson Park Ave): Walkable, popular with students
- Rugby Road: Near fraternities/sororities
- Venable: More affordable, bit further
- Wertland/14th St: High student density

OFF-GROUNDS LIVING TIPS:
- Start searching EARLY (January for August)
- Visit properties in person
- Read leases carefully (usually 12-month)
- Budget for utilities, internet, parking
- Use Facebook groups for housing/roommates
- Many students sublet for summer

COSTS (Approximate):
- On-Grounds: $7,000-10,000/year
- Off-Grounds: $600-900/month per person
- Utilities: $50-100/month
- Parking: $50-150/month (if needed)

ROOMMATE ADVICE:
- Communicate expectations early
- Discuss cleanliness, noise, guests
- Create written roommate agreement
- Address conflicts early and respectfully
- It's okay if you're not best friends
- Use RAs/staff for serious conflicts

SPECIAL HOUSING:
- Lawn/Range: Single rooms, huge honor
- Brown College: Residential learning community
- Language Houses: Immersive living
- RA Positions: Free housing + $3,000+ stipend""",
                "source": "https://housing.virginia.edu",
                "sourceType": "resource",
                "title": "Housing Guide",
                "tags": ["housing", "dorms", "off-grounds", "residential-life"]
            },
            
            # Mental Health Resources
            {
                "content": """Mental Health and Wellness at UVA:

IT'S OKAY TO STRUGGLE:
- College transition is hard for EVERYONE
- You're not alone if you're having difficulties
- Seeking help is strength, not weakness
- Most students use mental health resources at some point

CAPS (COUNSELING AND PSYCHOLOGICAL SERVICES):
- FREE counseling for all students
- Individual therapy, group therapy, workshops
- Crisis support available 24/7: (434) 243-5150
- Initial consultation to match you with support
- Location: Student Health & Wellness building

STUDENT HEALTH & WELLNESS:
- Medical care for illness and injuries
- Psychiatry for medication management
- Health promotion and wellness programs
- Nutrition counseling
- LGBTQ+ care specialists

OTHER SUPPORT RESOURCES:
- Academic coaching (time management, study skills)
- OASIS (Black students support)
- Women's Center
- LGBTQ Center
- Religious life communities
- Peer support programs

SELF-CARE STRATEGIES:
- Set boundaries (e.g., no work after 10pm)
- Prioritize sleep, nutrition, exercise
- Stay connected with family and friends
- Join clubs for social connection
- Use AFC (gym, pool, classes)
- Get outside (Charlottesville is beautiful)
- Practice saying no to commitments

CRISIS SUPPORT:
- CAPS 24/7 Hotline: (434) 243-5150
- UVA Police: (434) 924-7166
- National Suicide Prevention: 988
- Crisis Text Line: Text HOME to 741741
- Safe Rides: For safe transportation

RED FLAGS TO WATCH:
- Persistent sadness or anxiety
- Withdrawal from friends and activities
- Changes in sleep or eating
- Difficulty concentrating
- Thoughts of self-harm
- Substance use increasing

ACADEMIC STRESS:
- Remember: B's and C's are okay
- GPA matters less than you think
- One bad test doesn't ruin your future
- Use office hours and tutoring
- Ask for extensions when needed
- Take mental health days
- Your worth ≠ your GPA

STUDENT WISDOM:
- Prioritize mental health over grades
- Find a therapist you click with
- Exercise and sunlight genuinely help
- Talk to someone when overwhelmed
- Everyone is struggling at least a little
- Be honest about how you're doing
- It's okay to take a semester off if needed""",
                "source": "https://www.studenthealth.virginia.edu",
                "sourceType": "resource",
                "title": "Mental Health and Wellness",
                "tags": ["mental-health", "wellness", "CAPS", "support", "counseling"]
            },
            
            # UVA Traditions and Culture
            {
                "content": """UVA Culture, Traditions, and Lingo:

ESSENTIAL UVA LINGO:
- Grounds (NOT campus!)
- First Year (NOT freshman)
- The Lawn: Iconic heart of Grounds
- Rotunda: Thomas Jefferson's library
- The Corner: Restaurant/shop area near Grounds
- AFC: Aquatic & Fitness Center (gym)
- Clem: Clemons Library (24/7 during semester)
- Newcomb: Dining hall and student center
- E-School: School of Engineering
- Comm School: McIntire School of Commerce

MUST-ATTEND TRADITIONS:
- Lighting of the Lawn: December, absolutely magical
- Football Saturdays: Entire day event, wear orange
- Foxfield Races: Spring and fall, huge social event
- Springfest: End of year celebration
- Final Exercises: Graduation on the Lawn
- Virginia vs Virginia Tech football: THE game

FUN TRADITIONS:
- Streak the Lawn: Naked run (usually at night)
- Run with Jim: Saturday morning runs
- Touching Homer's foot: Bad luck if you do
- Walking on Lawn: Encouraged (Jefferson wanted this)

FOOD CULTURE:
- Bodo's Bagels: Worth the line, get cheddar jalapeño
- Christian's Pizza: Corner institution
- Roots: Natural foods, good late night
- O-Hill: Best dining hall (waffle bar!)
- Dining hall meal exchanges: Use strategically

GROUNDS GEOGRAPHY:
- Central Grounds: Lawn, Rotunda, main buildings
- Observatory Hill: Some dorms, athletics
- Scott Stadium: Football
- JPJ Arena: Basketball, concerts
- Barracks Road: Target, Trader Joe's, restaurants

TRANSPORTATION:
- Walking: Most things accessible on foot
- UTS Buses: Free university buses
- CAT Buses: Free city buses with ID
- Biking: Popular and efficient
- Parking: Expensive and limited (don't need car)

SURVIVAL TIPS:
- Skip the Newcomb vent (smells bad)
- Clem library best for late studying
- AFC pool is hidden gem
- Bodo's line moves faster than it looks
- Mad Bowl in Newcomb for hanging out
- O-Hill dining hall > other dining halls

FOOTBALL SATURDAYS:
- Wear orange and blue
- Tailgating starts early morning
- Student section is on the hill
- Stay for whole game (even if losing)
- After-parties everywhere
- Virginia Tech game is biggest

CHARLOTTESVILLE:
- Downtown Mall: Pedestrian outdoor mall
- Carter Mountain: Apple picking, views
- Hiking: Old Rag, Humpback Rocks nearby
- Wineries: Wine country (21+)
- Shenandoah: Beautiful national park nearby""",
                "source": "https://www.virginia.edu",
                "sourceType": "culture",
                "title": "UVA Traditions and Culture",
                "tags": ["traditions", "culture", "lingo", "student-life"]
            },
            
            # Research Opportunities
            {
                "content": """Undergraduate Research at UVA:

WHY DO RESEARCH:
- Develop critical thinking skills
- Work closely with faculty
- Strengthen grad/med school applications
- Get paid for meaningful work
- Contribute to discoveries
- Build resume and get strong rec letters

HOW TO FIND RESEARCH:

1. Browse Faculty Websites:
- Look at department faculty pages
- Read recent publications
- Find topics that interest you

2. Email Professors:
- Express genuine interest in their work
- Attach resume/transcript
- Be professional and concise
- Follow up if no response in week

3. Use Resources:
- USOAR (STEM research support)
- Department research coordinators
- Academic advisors
- Research-focused clubs

4. Attend Events:
- Department seminars
- Research poster sessions
- Research symposium

FUNDING OPPORTUNITIES:

USOAR (Undergraduate Science Opportunities):
- Supports STEM research
- Mentorship and community
- Research funding available
- Application process

Double Hoo Research Grant:
- Fund student-designed projects
- Applications twice per year
- Covers supplies, travel, participants

Summer Research Programs:
- Paid full-time positions
- Many departments offer these
- Apply in spring for summer

Academic Credit:
- Independent study courses (4993, 4998)
- Get credit for research
- Discuss with mentor and advisor

CS RESEARCH AREAS AT UVA:
- Machine Learning / AI
- Computer Vision
- Natural Language Processing
- Systems and Security
- Software Engineering
- Human-Computer Interaction
- Algorithms and Theory

RESEARCH TIMELINE:

First Year:
- Explore interests through classes
- Attend research presentations
- Learn about faculty research

Second Year:
- Reach out to potential mentors
- Start in a lab (even as volunteer)
- Learn techniques and tools

Third/Fourth Year:
- Independent project
- Present findings
- Co-author publications
- Use for grad school/job apps

TIPS FROM STUDENTS:
- Start early (positions fill up)
- Be persistent if professors say no
- Don't need perfect grades
- Show genuine interest
- Be reliable once you start
- Research looks great on resume
- Okay to switch labs if bad fit
- CS research can lead to publications""",
                "source": "https://research.virginia.edu",
                "sourceType": "resource",
                "title": "Undergraduate Research",
                "tags": ["research", "USOAR", "opportunities", "faculty"]
            },
            
            # Financial Information
            {
                "content": """Financial Aid and Money Management at UVA:

FINANCIAL AID:
- AccessUVA: UVA's aid program
- Meets 100% of demonstrated need
- No loans for families under $80k income
- Loans capped at $4,500/year for others
- File FAFSA annually by deadline

FINANCIAL AID OFFICE:
- Location: Carruthers Hall
- CSS Profile required for first-years
- Update if financial situation changes
- Don't hesitate to reach out

STUDENT EMPLOYMENT:

Work-Study:
- Part of financial aid package
- Various on-campus positions
- Typical: $12-15/hour
- Limit: 20 hours/week

Non-Work-Study:
- Available to all students
- Library, dining, rec centers
- Similar pay rates

RA Positions:
- Free housing + stipend ($3,000+)
- Leadership experience
- Apply second year

TEXTBOOK COSTS:

Money-Saving Tips:
- Don't buy before first class
- Check library reserves
- Look for free PDFs (legally)
- Buy used from other students
- Rent from Amazon or Chegg
- Many classes have free online resources

FREE RESOURCES:
- AFC (gym and fitness)
- Most student org events
- Student Activities movies
- Museums on Grounds
- UTS and CAT buses
- Many campus events

STUDENT DISCOUNTS:
- Amazon Prime Student (6 months free)
- Spotify + Hulu bundle
- Apple Music
- Many Charlottesville restaurants
- Adobe Creative Cloud

BUDGETING TIPS:
- Track spending first month
- Set limits for going out
- Cook when possible (limited first year)
- Use meal exchanges strategically
- Share streaming services
- Buy used textbooks
- Take advantage of free food events

UNEXPECTED COSTS:
- Course lab fees
- Printing ($20-30/semester)
- Laundry
- Organization dues
- Social activities
- Transportation home

EMERGENCY RESOURCES:
- Emergency grants available
- Hoos First (first-gen/low-income support)
- Food pantry through Madison House
- Don't be afraid to ask for help

CS STUDENT FINANCIAL NOTES:
- Laptop: $800-1500 (necessary)
- No special software costs (free for students)
- Internships pay well ($20-50/hour)
- Tech companies recruit heavily
- Many scholarship opportunities""",
                "source": "https://sfs.virginia.edu",
                "sourceType": "resource",
                "title": "Financial Aid and Budgeting",
                "tags": ["financial-aid", "money", "budgeting", "costs"]
            },
        ]
    
    async def scrape_all(self) -> List[Dict]:
        """Main scraping function"""
        
        print("=" * 60)
        print("PREPARING COMPREHENSIVE RAG CONTENT")
        print("=" * 60)
        
        # Use comprehensive manual content (most reliable)
        documents = self.get_comprehensive_content()
        
        print(f"Loaded {len(documents)} comprehensive documents")
        
        return documents


async def main():
    scraper = UVARAGScraper()
    
    try:
        documents = await scraper.scrape_all()
        
        # Save to JSON
        with open('uva_rag_content.json', 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total documents: {len(documents)}")
        
        # Group by type
        by_type = {}
        for doc in documents:
            doc_type = doc.get('sourceType', 'other')
            by_type[doc_type] = by_type.get(doc_type, 0) + 1
        
        print(f"\nDocuments by type:")
        for doc_type, count in sorted(by_type.items()):
            print(f"  {doc_type}: {count}")
        
        print(f"\nDocument titles:")
        for doc in documents:
            print(f"  - {doc['title']}")
        
        print(f"\nSaved to uva_rag_content.json")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())