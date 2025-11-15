"""
Course Scraper for UVA Course Catalog
Scrapes course data from UVA CS Advising and other sources
"""

import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import asyncio

async def scrape_uva_cs_courses() -> List[Dict]:
    """Scrape courses from UVA CS Advising site"""
    
    courses = []
    base_url = "https://uvacsadvising.org"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to get course list page
            response = await client.get(f"{base_url}/courses.html")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse course listings
                course_divs = soup.find_all('div', class_='course')
                
                for div in course_divs:
                    try:
                        # Extract course code
                        code_elem = div.find('h3')
                        if not code_elem:
                            continue
                        
                        course_code = code_elem.text.strip()
                        
                        # Extract title
                        title_elem = div.find('h4')
                        title = title_elem.text.strip() if title_elem else ""
                        
                        # Extract description
                        desc_elem = div.find('p', class_='description')
                        description = desc_elem.text.strip() if desc_elem else ""
                        
                        # Extract prerequisites
                        prereq_elem = div.find('p', class_='prerequisites')
                        prerequisites = []
                        if prereq_elem:
                            prereq_text = prereq_elem.text
                            # Parse course codes from text (e.g., "CS 2100")
                            prereq_matches = re.findall(r'[A-Z]{2,4}\s+\d{4}', prereq_text)
                            prerequisites = prereq_matches
                        
                        # Extract department and level
                        dept_match = re.match(r'([A-Z]{2,4})\s+(\d{4})', course_code)
                        if dept_match:
                            department = dept_match.group(1)
                            level = int(dept_match.group(2)[0]) * 1000
                        else:
                            department = "CS"
                            level = 1000
                        
                        courses.append({
                            "courseCode": course_code,
                            "title": title,
                            "description": description,
                            "credits": 3,  # Default
                            "department": department,
                            "level": level,
                            "prerequisites": prerequisites,
                            "semesters": ["Fall", "Spring"]  # Default
                        })
                    
                    except Exception as e:
                        print(f"Error parsing course: {e}")
                        continue
    
    except Exception as e:
        print(f"Error scraping courses: {e}")
    
    return courses

def get_fallback_courses() -> List[Dict]:
    """Fallback course data if scraping fails"""
    
    return [
        {
            "courseCode": "CS 1110",
            "title": "Introduction to Programming",
            "description": "A first course in programming using Python. Topics include variables, conditionals, loops, functions, and basic data structures.",
            "credits": 3,
            "department": "CS",
            "level": 1000,
            "prerequisites": [],
            "semesters": ["Fall", "Spring", "Summer"]
        },
        {
            "courseCode": "CS 2100",
            "title": "Data Structures and Algorithms I",
            "description": "Introduction to fundamental data structures (arrays, lists, stacks, queues, trees) and algorithms. Analysis of algorithm efficiency.",
            "credits": 3,
            "department": "CS",
            "level": 2000,
            "prerequisites": ["CS 1110"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 2120",
            "title": "Discrete Mathematics and Theory I",
            "description": "Mathematical foundations of computer science including logic, proofs, sets, functions, relations, and graphs.",
            "credits": 3,
            "department": "CS",
            "level": 2000,
            "prerequisites": ["CS 2100"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 2130",
            "title": "Computer Systems and Organization I",
            "description": "Introduction to computer systems including C/C++ programming, memory management, and low-level programming.",
            "credits": 3,
            "department": "CS",
            "level": 2000,
            "prerequisites": ["CS 2100"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 3100",
            "title": "Data Structures and Algorithms II",
            "description": "Advanced data structures and algorithm analysis. Topics include graphs, hash tables, balanced trees, and algorithm design techniques.",
            "credits": 3,
            "department": "CS",
            "level": 3000,
            "prerequisites": ["CS 2100", "CS 2120"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 3140",
            "title": "Software Development Essentials",
            "description": "Modern software development practices including version control, testing, agile methods, and team collaboration.",
            "credits": 3,
            "department": "CS",
            "level": 3000,
            "prerequisites": ["CS 2100"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 4414",
            "title": "Operating Systems",
            "description": "Operating system design and implementation. Topics include processes, threads, synchronization, memory management, and file systems.",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2130"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 4710",
            "title": "Artificial Intelligence",
            "description": "Introduction to artificial intelligence including search, knowledge representation, machine learning, and neural networks.",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2120"],
            "semesters": ["Fall"]
        },
        {
            "courseCode": "CS 4750",
            "title": "Database Systems",
            "description": "Database design, relational model, SQL, normalization, transactions, and database management systems.",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2120"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "CS 4501",
            "title": "Special Topics in Computer Science",
            "description": "Advanced topics in computer science. Content varies by semester.",
            "credits": 3,
            "department": "CS",
            "level": 4000,
            "prerequisites": ["CS 2120"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "MATH 1310",
            "title": "Calculus I",
            "description": "Limits, continuity, derivatives, and applications of derivatives.",
            "credits": 4,
            "department": "MATH",
            "level": 1000,
            "prerequisites": [],
            "semesters": ["Fall", "Spring", "Summer"]
        },
        {
            "courseCode": "MATH 1320",
            "title": "Calculus II",
            "description": "Techniques of integration, applications of integrals, sequences, and series.",
            "credits": 4,
            "department": "MATH",
            "level": 1000,
            "prerequisites": ["MATH 1310"],
            "semesters": ["Fall", "Spring", "Summer"]
        },
        {
            "courseCode": "MATH 2310",
            "title": "Calculus III",
            "description": "Multivariable calculus including vectors, partial derivatives, and multiple integrals.",
            "credits": 4,
            "department": "MATH",
            "level": 2000,
            "prerequisites": ["MATH 1320"],
            "semesters": ["Fall", "Spring"]
        },
        {
            "courseCode": "APMA 3080",
            "title": "Linear Algebra",
            "description": "Vector spaces, linear transformations, matrices, eigenvalues, and eigenvectors.",
            "credits": 3,
            "department": "APMA",
            "level": 3000,
            "prerequisites": ["MATH 1320"],
            "semesters": ["Fall", "Spring"]
        },
    ]

def scrape_courses() -> List[Dict]:
    """Main scraping function with fallback"""
    
    print("Starting course scraping...")
    
    # Try to scrape real data
    try:
        courses = asyncio.run(scrape_uva_cs_courses())
        
        if courses and len(courses) > 5:
            print(f"Successfully scraped {len(courses)} courses")
            return courses
    
    except Exception as e:
        print(f"Scraping failed: {e}")
    
    # Fall back to static data
    print("Using fallback course data")
    return get_fallback_courses()

if __name__ == "__main__":
    courses = scrape_courses()
    print(f"Total courses: {len(courses)}")
    for course in courses[:3]:
        print(f"  {course['courseCode']}: {course['title']}")

