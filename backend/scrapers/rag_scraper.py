"""
RAG Content Scraper
Scrapes content for the RAG (Retrieval-Augmented Generation) system
Sources: HGR guides, UVA policies, student resources
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio

async def scrape_hgr_content() -> List[Dict]:
    """Scrape Hoos Getting Ready program content"""
    
    documents = []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # HGR website
            url = "https://orientation.virginia.edu/hoos-getting-ready"
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract main content
                content_div = soup.find('div', class_='content')
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = '\n\n'.join([p.text.strip() for p in paragraphs])
                    
                    documents.append({
                        "content": content,
                        "source": url,
                        "sourceType": "hgr_guide",
                        "title": "Hoos Getting Ready Program"
                    })
    
    except Exception as e:
        print(f"Error scraping HGR content: {e}")
    
    return documents

def get_fallback_rag_content() -> List[Dict]:
    """Fallback RAG content if scraping fails"""
    
    return [
        {
            "content": """Hoos Getting Ready (HGR) is UVA's comprehensive orientation program for first-year students. 
            The program begins in the summer before your first year and continues through your first semester. 
            HGR includes online modules covering topics like academic planning, health and wellness, diversity and inclusion, 
            and student life. Students complete these modules at their own pace before arriving on Grounds.
            
            During orientation week, you'll participate in small group discussions led by peer advisors, 
            attend sessions about academic requirements and registration, and get to know your classmates. 
            The program is designed to help you transition to college life and set you up for success at UVA.""",
            "source": "https://orientation.virginia.edu/hoos-getting-ready",
            "sourceType": "hgr_guide",
            "title": "Hoos Getting Ready Program Overview"
        },
        {
            "content": """UVA operates on a semester system with Fall and Spring semesters, plus optional Summer terms.
            
            Full-time enrollment requires 12-18 credits per semester. Most courses are 3-4 credits.
            Students typically take 4-5 courses per semester to stay on track for graduation.
            
            Registration occurs during pre-registration periods before each semester. First-years register 
            after orientation with their academic advisors. Upper-class students register based on class standing.
            
            Add/drop periods allow students to adjust their schedules early in each semester without penalty.
            Withdrawal deadlines are published in the academic calendar.""",
            "source": "https://records.ureg.virginia.edu",
            "sourceType": "policy",
            "title": "UVA Enrollment and Registration Policies"
        },
        {
            "content": """Computer Science prerequisites at UVA follow a structured sequence:
            
            CS 1110 (Introduction to Programming) is the entry point with no prerequisites.
            
            CS 2100 (Data Structures and Algorithms I) requires CS 1110. This is the foundational course 
            for the CS major and must be completed before taking most upper-level courses.
            
            CS 2120 (Discrete Mathematics) requires CS 2100 and is a prerequisite for almost all 
            3000 and 4000-level CS courses.
            
            CS 2130 (Computer Systems and Organization) requires CS 2100 and is needed for systems-focused courses.
            
            Students should plan to complete CS 1110, 2100, and 2120 in their first two years to have 
            flexibility in choosing upper-level electives.""",
            "source": "https://uvacsadvising.org",
            "sourceType": "course_catalog",
            "title": "CS Prerequisites Guide"
        },
        {
            "content": """UVA offers extensive academic support resources:
            
            The Writing Center provides free one-on-one consultations for any writing project at any stage.
            No appointment needed during walk-in hours.
            
            Tutoring services are available through the Teaching Resource Center for most introductory courses.
            Peer tutors are upper-class students who excelled in the course.
            
            Office hours are your direct line to professors and TAs. Don't hesitate to attend - 
            faculty want to help you succeed and office hours are often underutilized.
            
            Study groups and review sessions are offered before major exams, especially in large lecture courses.
            
            Academic coaching is available through Student Health and Wellness to help with time management, 
            study strategies, and academic planning.""",
            "source": "https://college.as.virginia.edu/academic-support",
            "sourceType": "resource",
            "title": "Academic Support Resources at UVA"
        },
        {
            "content": """Student clubs and organizations are central to UVA's student experience. 
            With over 1,000 recognized student organizations, there's something for everyone.
            
            ATuva is UVA's official platform for discovering and joining clubs. Browse by category, 
            search by interest, and sign up for mailing lists.
            
            Activities Fair (formerly Student Activities Fair) is held at the beginning of Fall semester. 
            This is the best opportunity to explore clubs, meet members, and sign up.
            
            Most clubs hold open meetings early in the semester - attend a few to find your fit before committing.
            
            Madison House coordinates volunteer opportunities and service-focused clubs.
            
            CIOs (Contracted Independent Organizations) like Student Council receive University funding and support.
            
            Starting a new club is possible through the Student Activities Office if you don't find what you're looking for.""",
            "source": "https://studentactivities.virginia.edu",
            "sourceType": "resource",
            "title": "Student Clubs and Organizations"
        },
        {
            "content": """Career services at UVA are provided through the Center for Career Development (CCD).
            
            First-years can explore careers through assessments like Focus 2, which helps identify interests and potential majors.
            
            UVA Career Connect is the main platform for finding internships, jobs, and on-campus recruiting opportunities.
            
            On-Grounds recruiting brings hundreds of employers to UVA each year for interviews and information sessions.
            Major companies in tech, finance, consulting, and other industries recruit directly from UVA.
            
            Resume reviews and mock interviews are available by appointment with career counselors.
            
            Industry-specific career fairs are held throughout the year (Tech Fair, Healthcare Fair, etc.).
            
            Networking events and alumni connections help students learn about different career paths and make professional contacts.
            
            Internship funding through the Virginia Internship Funding Program can help support unpaid or low-paid internships 
            in public service, non-profit, and government sectors.""",
            "source": "https://career.virginia.edu",
            "sourceType": "resource",
            "title": "Career Development at UVA"
        },
        {
            "content": """UVA requires all students to complete General Education requirements across multiple categories:
            
            Writing Requirement: Typically fulfilled through writing-intensive courses in your first two years.
            
            Foreign Language: Complete through the second semester of a single foreign language or demonstrate proficiency.
            
            Historical Perspectives: One course examining historical developments and their contemporary significance.
            
            Social and Cultural Perspectives: One course analyzing social structures and cultural practices.
            
            Natural Sciences: Two courses with at least one lab, covering physical and life sciences.
            
            Humanities: Courses exploring human expression through literature, philosophy, and arts.
            
            The specifics vary by school (College of Arts & Sciences, Engineering, etc.). 
            Check with your advisor to ensure you're meeting all requirements for your degree.""",
            "source": "https://college.as.virginia.edu/requirements",
            "sourceType": "policy",
            "title": "General Education Requirements"
        },
        {
            "content": """Research opportunities at UVA are available to undergraduates across all disciplines.
            
            Faculty are actively looking for undergraduate research assistants. Browse faculty profiles in your 
            department and reach out to professors whose work interests you.
            
            USOAR (Undergraduate Science, Opportunity, Access & Research) supports students interested in STEM research 
            with funding, mentorship, and community.
            
            Double Hoo Research Grant provides funding for student-designed research projects. 
            Applications are reviewed twice per year.
            
            Summer research programs offer paid positions for intensive research experiences. Many students work 
            in labs full-time during summer breaks.
            
            The Undergraduate Research Network hosts workshops on finding research positions, writing proposals, 
            and presenting findings.
            
            Research symposia like the Undergraduate Research Symposium showcase student work and provide 
            presentation experience.
            
            Independent study courses (4993, 4998, etc.) provide academic credit for research work.""",
            "source": "https://research.virginia.edu/undergraduate",
            "sourceType": "resource",
            "title": "Undergraduate Research Opportunities"
        },
    ]

def scrape_rag_content() -> List[Dict]:
    """Main scraping function with fallback"""
    
    print("Starting RAG content scraping...")
    
    # Try to scrape real data
    try:
        documents = asyncio.run(scrape_hgr_content())
        
        if documents and len(documents) > 5:
            print(f"Successfully scraped {len(documents)} documents")
            return documents
    
    except Exception as e:
        print(f"Scraping failed: {e}")
    
    # Fall back to static data
    print("Using fallback RAG content")
    return get_fallback_rag_content()

if __name__ == "__main__":
    documents = scrape_rag_content()
    print(f"Total documents: {len(documents)}")
    for doc in documents[:3]:
        print(f"  {doc['title']}")

