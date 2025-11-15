"""
Fixed Comprehensive Course Scraper for UVA
Scrapes course data from Lou's List with descriptions
Author: Enhanced for HoosHelper
"""

import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import asyncio
import json

class UVACourseScraper:
    """Scrapes comprehensive course data from Lou's List"""
    
    BASE_URL = "https://louslist.org"
    
    # Major departments at UVA
    DEPARTMENTS = [
        "CS", "MATH", "APMA", "STAT", "PHYS", "CHEM", "BIOL", 
        "ECON", "COMM", "PSYC", "ENGL", "HIST", "POLI", "SOC",
        "DS", "ECE", "MAE", "BME", "CE", "CHE", "SYS",
        "SPAN", "FREN", "GERM", "ARAB", "CHIN",
        "ART", "MUS", "DRAM", "ARCH"
    ]
    
    def __init__(self):
        self.courses = []
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def scrape_department_catalog(self, dept_code: str) -> List[Dict]:
        """Scrape all courses for a department from Lou's List catalog"""
        
        courses = []
        url = f"{self.BASE_URL}/CC/{dept_code}.html"
        
        try:
            print(f"Scraping {dept_code}...")
            response = await self.client.get(url)
            
            if response.status_code != 200:
                print(f"  Failed (status {response.status_code})")
                return courses
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Lou's List format: Course entries are typically separated by line breaks
            # Format: "DEPT ####Course Title (credits) Description"
            
            # Get all text and parse line by line
            text = soup.get_text()
            lines = text.split('\n')
            
            current_course = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines and headers
                if not line or len(line) < 5:
                    continue
                
                # Look for course code pattern: DEPT ####
                course_match = re.match(r'^([A-Z]{2,4})\s+(\d{4})', line)
                
                if course_match:
                    # Save previous course
                    if current_course and current_course['description']:
                        courses.append(current_course)
                    
                    dept = course_match.group(1)
                    number = course_match.group(2)
                    
                    # Extract title and credits from same line
                    # Format: "CS 1110Introduction to Programming (3)"
                    rest_of_line = line[course_match.end():].strip()
                    
                    # Find credits in parentheses
                    credits = 3  # default
                    credit_match = re.search(r'\((\d+(?:\s*-\s*\d+)?)\)', rest_of_line)
                    if credit_match:
                        credits_str = credit_match.group(1)
                        try:
                            if '-' in credits_str:
                                credits = int(credits_str.split('-')[0].strip())
                            else:
                                credits = int(credits_str)
                        except:
                            credits = 3
                        
                        # Title is between course number and credits
                        title = rest_of_line[:credit_match.start()].strip()
                    else:
                        # No credits found, whole rest is title
                        title = rest_of_line
                    
                    # Determine level
                    try:
                        level = int(number[0]) * 1000
                    except:
                        level = 1000
                    
                    current_course = {
                        "courseCode": f"{dept} {number}",
                        "title": title,
                        "description": "",
                        "credits": credits,
                        "department": dept,
                        "level": level,
                        "prerequisites": [],
                        "semesters": [],
                        "source": "louslist",
                        "url": url
                    }
                
                elif current_course:
                    # This line might be part of description
                    # Skip lines that are "Course was offered" 
                    if "Course was offered" not in line and "Offered" not in line[:20]:
                        # Add to description if it looks like descriptive text
                        if len(line) > 20 and not line.startswith('http'):
                            if current_course['description']:
                                current_course['description'] += " "
                            current_course['description'] += line
                    
                    # Extract semesters if present
                    if "Course was offered" in line or "Offered" in line:
                        if "Fall" in line:
                            if "Fall" not in current_course['semesters']:
                                current_course['semesters'].append("Fall")
                        if "Spring" in line:
                            if "Spring" not in current_course['semesters']:
                                current_course['semesters'].append("Spring")
                        if "Summer" in line or "January" in line:
                            if "Summer" not in current_course['semesters']:
                                current_course['semesters'].append("Summer")
            
            # Add last course
            if current_course and current_course['description']:
                courses.append(current_course)
            
            # Clean up descriptions
            for course in courses:
                course['description'] = course['description'][:500].strip()
                if not course['semesters']:
                    course['semesters'] = ["Fall", "Spring"]  # Default
            
            print(f"  Found {len(courses)} courses")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        return courses
    
    async def scrape_all_departments(self, limit_depts: Optional[List[str]] = None) -> List[Dict]:
        """Scrape courses from all departments"""
        
        departments = limit_depts if limit_depts else self.DEPARTMENTS
        
        all_courses = []
        
        for dept in departments:
            dept_courses = await self.scrape_department_catalog(dept)
            all_courses.extend(dept_courses)
            
            # Be nice to the server
            await asyncio.sleep(0.3)
        
        return all_courses
    
    def get_comprehensive_fallback_courses(self) -> List[Dict]:
        """Comprehensive fallback course data"""
        return [
            # Computer Science
            {
                "courseCode": "CS 1110",
                "title": "Introduction to Programming",
                "description": "A first course in programming using Python. Topics include variables, conditionals, loops, functions, and basic data structures. Designed for students with no prior programming experience.",
                "credits": 3,
                "department": "CS",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring", "Summer"]
            },
            {
                "courseCode": "CS 1111",
                "title": "Introduction to Programming (Accelerated)",
                "description": "An accelerated introduction to programming for students with prior experience. Covers Python programming at a faster pace with more advanced topics.",
                "credits": 3,
                "department": "CS",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 2100",
                "title": "Data Structures and Algorithms I",
                "description": "Introduction to fundamental data structures including arrays, linked lists, stacks, queues, and trees. Analysis of algorithm efficiency using Big-O notation. Essential foundation for all upper-level CS courses.",
                "credits": 3,
                "department": "CS",
                "level": 2000,
                "prerequisites": ["CS 1110 or CS 1111"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 2120",
                "title": "Discrete Mathematics and Theory I",
                "description": "Mathematical foundations of computer science including propositional logic, proofs, sets, functions, relations, and basic graph theory. Required for almost all 3000/4000 level CS courses.",
                "credits": 3,
                "department": "CS",
                "level": 2000,
                "prerequisites": ["CS 2100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 2130",
                "title": "Computer Systems and Organization I",
                "description": "Introduction to computer systems including C/C++ programming, memory management, pointers, and low-level programming concepts. Explores how computers work at the hardware level.",
                "credits": 3,
                "department": "CS",
                "level": 2000,
                "prerequisites": ["CS 2100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 3100",
                "title": "Data Structures and Algorithms II",
                "description": "Advanced data structures and algorithm analysis including graphs, hash tables, balanced trees, heaps, and advanced algorithm design techniques like dynamic programming and greedy algorithms.",
                "credits": 3,
                "department": "CS",
                "level": 3000,
                "prerequisites": ["CS 2100", "CS 2120"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 3140",
                "title": "Software Development Essentials",
                "description": "Modern software development practices including version control (Git), testing frameworks, agile methodologies, and team collaboration. Hands-on group project throughout the semester.",
                "credits": 3,
                "department": "CS",
                "level": 3000,
                "prerequisites": ["CS 2100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 3240",
                "title": "Advanced Software Development",
                "description": "Advanced topics in software engineering including design patterns, software architecture, databases, and large-scale development. Semester-long team project building a web application.",
                "credits": 3,
                "department": "CS",
                "level": 3000,
                "prerequisites": ["CS 3140"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4102",
                "title": "Algorithms",
                "description": "Design and analysis of algorithms covering dynamic programming, greedy algorithms, divide and conquer, graph algorithms, and NP-completeness. One of the most challenging and important CS courses.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2120", "CS 3100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4414",
                "title": "Operating Systems",
                "description": "Operating system design and implementation covering processes, threads, synchronization, deadlock, memory management, file systems, and I/O. Includes programming assignments in C/Rust.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2130", "CS 3100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4710",
                "title": "Artificial Intelligence",
                "description": "Introduction to artificial intelligence including search algorithms, knowledge representation, machine learning, neural networks, and AI applications. Programming projects in Python.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2120", "CS 3100"],
                "semesters": ["Fall"]
            },
            {
                "courseCode": "CS 4750",
                "title": "Database Systems",
                "description": "Database design and implementation covering relational model, SQL, normalization, transactions, concurrency control, and NoSQL databases. Includes database design project.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2120", "CS 3100"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4774",
                "title": "Machine Learning",
                "description": "Supervised and unsupervised learning, neural networks, deep learning, decision trees, SVMs, and practical applications of machine learning. Requires linear algebra background.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2120", "MATH 3351 or APMA 3080"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4630",
                "title": "Defense Against the Dark Arts",
                "description": "Computer security including cryptography, network security, web security, software vulnerabilities, and ethical hacking. Hands-on labs with real security tools.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2130"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CS 4640",
                "title": "Programming Languages for Web Applications",
                "description": "Web development covering HTML, CSS, JavaScript, frontend frameworks, backend development, databases, and deployment. Build full-stack web applications.",
                "credits": 3,
                "department": "CS",
                "level": 4000,
                "prerequisites": ["CS 2100"],
                "semesters": ["Fall", "Spring"]
            },
            
            # Data Science
            {
                "courseCode": "DS 1001",
                "title": "Foundations of Data Science",
                "description": "Introduction to data science including data wrangling, visualization, exploratory data analysis, and basic machine learning using Python.",
                "credits": 3,
                "department": "DS",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "DS 2001",
                "title": "Programming for Data Science",
                "description": "Python programming for data science focusing on pandas, numpy, matplotlib, and data manipulation. Hands-on projects with real datasets.",
                "credits": 3,
                "department": "DS",
                "level": 2000,
                "prerequisites": ["DS 1001 or CS 1110"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "DS 3001",
                "title": "Foundations of Machine Learning",
                "description": "Supervised and unsupervised learning, model evaluation, feature engineering, and practical machine learning applications. Uses Python and scikit-learn.",
                "credits": 3,
                "department": "DS",
                "level": 3000,
                "prerequisites": ["DS 2001", "STAT 2120"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "DS 4001",
                "title": "Ethics of Big Data",
                "description": "Ethical considerations in data science including privacy, bias, fairness, transparency, and societal impacts of data-driven systems.",
                "credits": 3,
                "department": "DS",
                "level": 4000,
                "prerequisites": ["DS 2001"],
                "semesters": ["Fall", "Spring"]
            },
            
            # Mathematics
            {
                "courseCode": "MATH 1310",
                "title": "Calculus I",
                "description": "Limits, continuity, derivatives, applications of derivatives, exponential and logarithmic functions. First course in calculus sequence.",
                "credits": 4,
                "department": "MATH",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring", "Summer"]
            },
            {
                "courseCode": "MATH 1320",
                "title": "Calculus II",
                "description": "Techniques of integration, applications of integrals, sequences and series, Taylor series. Second course in calculus sequence.",
                "credits": 4,
                "department": "MATH",
                "level": 1000,
                "prerequisites": ["MATH 1310"],
                "semesters": ["Fall", "Spring", "Summer"]
            },
            {
                "courseCode": "MATH 2310",
                "title": "Calculus III",
                "description": "Multivariable calculus including vectors, partial derivatives, multiple integrals, line integrals, surface integrals, and vector calculus theorems.",
                "credits": 4,
                "department": "MATH",
                "level": 2000,
                "prerequisites": ["MATH 1320"],
                "semesters": ["Fall", "Spring", "Summer"]
            },
            {
                "courseCode": "MATH 3351",
                "title": "Elementary Linear Algebra",
                "description": "Vector spaces, linear transformations, matrices, determinants, eigenvalues and eigenvectors, and applications. Essential for machine learning.",
                "credits": 3,
                "department": "MATH",
                "level": 3000,
                "prerequisites": ["MATH 1320"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "APMA 3080",
                "title": "Linear Algebra",
                "description": "Applied linear algebra with applications to engineering and science. Covers similar topics to MATH 3351 with engineering focus.",
                "credits": 3,
                "department": "APMA",
                "level": 3000,
                "prerequisites": ["MATH 1320"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "STAT 2120",
                "title": "Introduction to Statistical Analysis",
                "description": "Descriptive statistics, probability, random variables, sampling distributions, confidence intervals, and hypothesis testing. Uses R programming.",
                "credits": 3,
                "department": "STAT",
                "level": 2000,
                "prerequisites": ["MATH 1310"],
                "semesters": ["Fall", "Spring"]
            },
            
            # Economics
            {
                "courseCode": "ECON 2010",
                "title": "Principles of Microeconomics",
                "description": "Supply and demand, market structures, consumer theory, firm behavior, and resource allocation. Foundation for economics major.",
                "credits": 3,
                "department": "ECON",
                "level": 2000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "ECON 2020",
                "title": "Principles of Macroeconomics",
                "description": "GDP, inflation, unemployment, economic growth, monetary and fiscal policy, and international trade. Complements microeconomics.",
                "credits": 3,
                "department": "ECON",
                "level": 2000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            
            # Commerce
            {
                "courseCode": "COMM 2010",
                "title": "Accounting and Financial Analysis I",
                "description": "Introduction to financial accounting including financial statements, accounting principles, and financial analysis. Foundation for Commerce School.",
                "credits": 3,
                "department": "COMM",
                "level": 2000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "COMM 3020",
                "title": "Corporate Finance",
                "description": "Financial management, time value of money, capital budgeting, risk and return, and corporate valuation. Core Commerce course.",
                "credits": 3,
                "department": "COMM",
                "level": 3000,
                "prerequisites": ["COMM 2010"],
                "semesters": ["Fall", "Spring"]
            },
            
            # Sciences
            {
                "courseCode": "PHYS 1425",
                "title": "General Physics I",
                "description": "Mechanics, waves, and thermodynamics with calculus. For engineering and science majors. Lab included.",
                "credits": 4,
                "department": "PHYS",
                "level": 1000,
                "prerequisites": ["MATH 1310"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "PHYS 2415",
                "title": "General Physics II",
                "description": "Electricity, magnetism, optics, and modern physics with calculus. Continuation of PHYS 1425. Lab included.",
                "credits": 4,
                "department": "PHYS",
                "level": 2000,
                "prerequisites": ["PHYS 1425", "MATH 1320"],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "CHEM 1410",
                "title": "General Chemistry I",
                "description": "Atomic structure, periodic table, chemical bonding, stoichiometry, and chemical reactions. Lab included.",
                "credits": 3,
                "department": "CHEM",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            {
                "courseCode": "BIOL 2100",
                "title": "Introduction to Biology",
                "description": "Cell biology, genetics, evolution, and ecology. Foundation for biology major and pre-med students.",
                "credits": 3,
                "department": "BIOL",
                "level": 2000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
            
            # Psychology
            {
                "courseCode": "PSYC 1010",
                "title": "Introduction to Psychology",
                "description": "Survey of psychology covering cognition, development, social psychology, and clinical psychology. Popular gen ed course.",
                "credits": 3,
                "department": "PSYC",
                "level": 1000,
                "prerequisites": [],
                "semesters": ["Fall", "Spring"]
            },
        ]
    
    async def close(self):
        await self.client.aclose()


async def main():
    scraper = UVACourseScraper()
    
    try:
        print("=" * 60)
        print("SCRAPING UVA COURSES FROM LOU'S LIST")
        print("=" * 60)
        
        # Scrape priority departments
        priority_depts = ["CS", "MATH", "DS", "STAT", "ECON", "COMM", "PSYC", "PHYS", "CHEM", "BIOL"]
        courses = await scraper.scrape_all_departments(limit_depts=priority_depts)
        
        # Add fallback data for comprehensiveness
        print("\nAdding comprehensive fallback data...")
        fallback = scraper.get_comprehensive_fallback_courses()
        
        # Merge: keep scraped if we got it, otherwise use fallback
        scraped_codes = {c['courseCode'] for c in courses}
        for fb_course in fallback:
            if fb_course['courseCode'] not in scraped_codes:
                courses.append(fb_course)
        
        # Save to JSON
        with open('uva_courses.json', 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total courses: {len(courses)}")
        
        # Group by department
        by_dept = {}
        for course in courses:
            dept = course['department']
            by_dept[dept] = by_dept.get(dept, 0) + 1
        
        print(f"\nCourses by department:")
        for dept, count in sorted(by_dept.items()):
            print(f"  {dept}: {count}")
        
        # Show sample with descriptions
        print(f"\nSample courses with descriptions:")
        for course in courses[:3]:
            print(f"\n  {course['courseCode']}: {course['title']}")
            print(f"    {course['description'][:100]}...")
        
        print(f"\nSaved to uva_courses.json")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())