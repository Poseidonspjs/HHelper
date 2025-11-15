"""
UVA Faculty and Research Scraper
Scrapes faculty information, research areas, and projects
Author: Enhanced for HoosHelper
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
import json
import re

class UVAResearchScraper:
    """Scrapes UVA faculty and research information"""
    
    def __init__(self):
        self.faculty = []
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def scrape_engineering_faculty(self) -> List[Dict]:
        """Scrape engineering faculty"""
        
        faculty = []
        url = "https://engineering.virginia.edu/faculty"
        
        try:
            print(f"Scraping engineering faculty: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for faculty listings
                for faculty_elem in soup.find_all(['div', 'article'], class_=re.compile('faculty|profile|person', re.I)):
                    name_elem = faculty_elem.find(['h2', 'h3', 'h4', 'a'])
                    if name_elem:
                        name = name_elem.get_text().strip()
                        
                        # Get research description
                        desc_elem = faculty_elem.find(['p', 'div'], class_=re.compile('research|bio|description', re.I))
                        research = desc_elem.get_text().strip() if desc_elem else ""
                        
                        if name and len(name) > 3:
                            faculty.append({
                                "name": name,
                                "department": "Engineering",
                                "research": research[:500],
                                "source": "engineering_website"
                            })
                            print(f"  Found: {name}")
        
        except Exception as e:
            print(f"Error scraping engineering faculty: {e}")
        
        return faculty
    
    def get_comprehensive_fallback_data(self) -> List[Dict]:
        """Comprehensive fallback research data"""
        return [
            # Computer Science Faculty
            {
                "name": "Tom Horton",
                "title": "Professor of Computer Science",
                "department": "Computer Science",
                "research": "Software engineering education, active learning techniques, and educational technology. Director of undergraduate programs in CS.",
                "email": "horton@virginia.edu",
                "website": "https://www.cs.virginia.edu/~horton/",
                "researchAreas": ["Software Engineering", "Computer Science Education", "Educational Technology"],
                "courses": ["CS 3140", "CS 3240"]
            },
            {
                "name": "Mark Floryan",
                "title": "Associate Professor of Computer Science",
                "department": "Computer Science",
                "research": "Computer science education, algorithms education, and innovative teaching methods. Teaches core CS courses.",
                "website": "https://www.cs.virginia.edu/~mrf8t/",
                "researchAreas": ["CS Education", "Algorithms", "Teaching Methods"],
                "courses": ["CS 2100", "CS 4102"]
            },
            {
                "name": "Rich Nguyen",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Computer science education, student engagement, and curriculum development. Focus on improving CS education.",
                "researchAreas": ["CS Education", "Curriculum Design", "Student Success"],
                "courses": ["CS 1110", "CS 2100"]
            },
            {
                "name": "Vicente Ordonez",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Computer vision, deep learning, visual reasoning, and multimodal AI. Working on understanding visual content.",
                "website": "https://www.cs.virginia.edu/~vicente/",
                "researchAreas": ["Computer Vision", "Deep Learning", "AI", "Multimodal Learning"],
                "courses": ["CS 4710", "CS 4774"]
            },
            {
                "name": "David Evans",
                "title": "Professor of Computer Science",
                "department": "Computer Science",
                "research": "Security and privacy, adversarial machine learning, programming languages, and computing education.",
                "website": "https://www.cs.virginia.edu/~evans/",
                "researchAreas": ["Security", "Privacy", "Machine Learning Security", "Programming Languages"],
                "courses": ["CS 4630"]
            },
            {
                "name": "Yonghwi Kwon",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Software security, program analysis, malware analysis, and system security.",
                "website": "https://yonghwi-kwon.github.io/",
                "researchAreas": ["Software Security", "Program Analysis", "Systems Security"],
                "courses": ["CS 4630", "CS 4414"]
            },
            {
                "name": "Felix Lin",
                "title": "Associate Professor of Computer Science",
                "department": "Computer Science",
                "research": "Operating systems, mobile systems, embedded systems, and system security.",
                "researchAreas": ["Operating Systems", "Mobile Computing", "Embedded Systems"],
                "courses": ["CS 4414"]
            },
            {
                "name": "Jundong Li",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Data mining, machine learning, graph neural networks, and AI for social good.",
                "website": "https://jundongli.github.io/",
                "researchAreas": ["Machine Learning", "Data Mining", "Graph Learning", "AI Ethics"],
                "courses": ["CS 4774"]
            },
            {
                "name": "Hongning Wang",
                "title": "Associate Professor of Computer Science",
                "department": "Computer Science",
                "research": "Information retrieval, natural language processing, machine learning, and recommender systems.",
                "website": "http://www.cs.virginia.edu/~hw5x/",
                "researchAreas": ["NLP", "Information Retrieval", "Machine Learning", "Recommender Systems"],
                "courses": ["CS 4501"]
            },
            {
                "name": "Yangfeng Ji",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Natural language processing, discourse analysis, text generation, and dialogue systems.",
                "website": "https://yangfengji.net/",
                "researchAreas": ["NLP", "Dialogue Systems", "Text Generation", "Discourse"],
                "courses": ["CS 4501"]
            },
            {
                "name": "Paul McBurney",
                "title": "Associate Professor of Computer Science",
                "department": "Computer Science",
                "research": "Programming languages, software engineering, program analysis, and developer tools.",
                "researchAreas": ["Programming Languages", "Software Engineering", "Program Analysis"],
                "courses": ["CS 3140", "CS 3240"]
            },
            {
                "name": "Nada Basit",
                "title": "Assistant Professor of Computer Science",
                "department": "Computer Science",
                "research": "Computer science education, diversity in computing, and broadening participation in CS.",
                "researchAreas": ["CS Education", "Diversity in Computing", "Student Success"],
                "courses": ["CS 1110"]
            },
            
            # Data Science Faculty
            {
                "name": "Phil Bourne",
                "title": "Dean, School of Data Science",
                "department": "Data Science",
                "research": "Structural bioinformatics, data science for biomedical research, and open science.",
                "website": "https://datascience.virginia.edu/people/philip-bourne",
                "researchAreas": ["Bioinformatics", "Computational Biology", "Open Science", "Data Science"]
            },
            {
                "name": "Brian Wright",
                "title": "Associate Professor of Data Science",
                "department": "Data Science",
                "research": "Machine learning, statistical learning, data visualization, and data science pedagogy.",
                "researchAreas": ["Machine Learning", "Statistics", "Data Visualization", "Education"],
                "courses": ["DS 3001", "DS 4001"]
            },
            {
                "name": "Jon Kropko",
                "title": "Assistant Professor of Data Science",
                "department": "Data Science",
                "research": "Political methodology, statistical modeling, causal inference, and data science applications.",
                "researchAreas": ["Statistics", "Political Science", "Causal Inference", "Modeling"],
                "courses": ["DS 2001"]
            },
            
            # Engineering Faculty (Various Departments)
            {
                "name": "Pamela Norris",
                "title": "Dean, School of Engineering",
                "department": "Mechanical Engineering",
                "research": "Heat transfer, nanoscale energy transport, and thermal management.",
                "researchAreas": ["Heat Transfer", "Nanotechnology", "Energy"]
            },
            {
                "name": "Scott Acton",
                "title": "Professor of Electrical Engineering",
                "department": "Electrical & Computer Engineering",
                "research": "Image and video analysis, medical imaging, machine learning for imaging, and biological image analysis.",
                "website": "https://engineering.virginia.edu/faculty/scott-acton",
                "researchAreas": ["Image Processing", "Computer Vision", "Medical Imaging", "Machine Learning"]
            },
            {
                "name": "Homa Alemzadeh",
                "title": "Assistant Professor of ECE",
                "department": "Electrical & Computer Engineering",
                "research": "Cyber-physical systems, medical device security, safety-critical systems, and resilient computing.",
                "researchAreas": ["CPS", "Security", "Medical Devices", "Safety-Critical Systems"]
            },
            {
                "name": "Barry Johnson",
                "title": "Professor of ECE",
                "department": "Electrical & Computer Engineering",
                "research": "Dependable and secure computing, fault-tolerant systems, and critical infrastructure protection.",
                "researchAreas": ["Dependable Computing", "Security", "Critical Infrastructure"]
            },
            
            # Research Labs and Centers
            {
                "name": "Link Lab",
                "type": "Research Center",
                "department": "Engineering",
                "research": "Cyber-physical systems research spanning IoT, autonomous systems, smart cities, and connected devices.",
                "website": "https://linklab.virginia.edu/",
                "researchAreas": ["CPS", "IoT", "Autonomous Systems", "Smart Cities"],
                "description": "Multi-disciplinary research center focused on cyber-physical systems with state-of-the-art facilities."
            },
            {
                "name": "Center for Advanced Computing and Data Science",
                "type": "Research Center",
                "department": "Data Science",
                "research": "Advanced computing infrastructure, high-performance computing, and data-intensive research.",
                "researchAreas": ["HPC", "Cloud Computing", "Data Infrastructure"],
                "description": "Provides computing resources and expertise for data-intensive research across UVA."
            },
            {
                "name": "Biocomplexity Institute",
                "type": "Research Institute",
                "department": "Data Science",
                "research": "Infectious disease modeling, social networks, health policy, and complex systems.",
                "website": "https://biocomplexity.virginia.edu/",
                "researchAreas": ["Epidemiology", "Modeling", "Complex Systems", "Public Health"],
                "description": "Uses data science and modeling to address societal challenges in health and policy."
            },
            
            # Mathematics Faculty
            {
                "name": "Ken Ono",
                "title": "Thomas Jefferson Professor of Mathematics",
                "department": "Mathematics",
                "research": "Number theory, modular forms, partitions, and mathematical physics.",
                "website": "https://uva.theopenscholar.com/ken-ono",
                "researchAreas": ["Number Theory", "Modular Forms", "Mathematical Physics"]
            },
            
            # Economics Faculty
            {
                "name": "Simon Anderson",
                "title": "Professor of Economics",
                "department": "Economics",
                "research": "Industrial organization, media economics, and spatial competition.",
                "researchAreas": ["Industrial Organization", "Media Economics", "Microeconomics"]
            },
            {
                "name": "Leora Friedberg",
                "title": "Professor of Economics",
                "department": "Economics",
                "research": "Labor economics, household economics, retirement, and public finance.",
                "researchAreas": ["Labor Economics", "Public Finance", "Household Economics"]
            },
            
            # Commerce Faculty
            {
                "name": "Nicole Thorne Jenkins",
                "title": "Dean, McIntire School of Commerce",
                "department": "Commerce",
                "research": "Marketing, brand management, and consumer behavior.",
                "researchAreas": ["Marketing", "Brand Management", "Consumer Behavior"]
            },
            
            # Research Opportunities for Undergrads
            {
                "name": "USOAR (Undergraduate Science Opportunities)",
                "type": "Program",
                "department": "Research",
                "research": "Supporting undergraduate STEM research through mentorship, funding, and community building.",
                "website": "https://college.as.virginia.edu/usoar",
                "description": "Provides resources and support for undergraduate students conducting research in STEM fields.",
                "opportunities": ["Research funding", "Mentorship", "Summer programs", "Research symposium"]
            },
            {
                "name": "Double Hoo Research Grant",
                "type": "Funding",
                "department": "Research",
                "research": "Funding for student-designed research projects across all disciplines.",
                "description": "Provides grants for undergraduate research projects with funding for supplies, travel, and participants.",
                "opportunities": ["Research grants", "Project funding", "Presentation support"]
            },
        ]
    
    async def scrape_all(self) -> List[Dict]:
        """Main scraping function"""
        
        all_faculty = []
        
        print("=" * 60)
        print("SCRAPING UVA RESEARCH & FACULTY")
        print("=" * 60)
        
        try:
            eng_faculty = await self.scrape_engineering_faculty()
            all_faculty.extend(eng_faculty)
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        # Always add comprehensive manual data
        print("\nAdding comprehensive manual research data...")
        fallback = self.get_comprehensive_fallback_data()
        all_faculty.extend(fallback)
        
        # Deduplicate by name
        unique_faculty = {}
        for item in all_faculty:
            name = item.get('name', item.get('type', ''))
            if name not in unique_faculty:
                unique_faculty[name] = item
        
        return list(unique_faculty.values())
    
    async def close(self):
        await self.client.aclose()


async def main():
    scraper = UVAResearchScraper()
    
    try:
        faculty = await scraper.scrape_all()
        
        # Save to JSON
        with open('uva_research_faculty.json', 'w', encoding='utf-8') as f:
            json.dump(faculty, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total faculty/research entries: {len(faculty)}")
        
        # Group by department
        by_dept = {}
        for item in faculty:
            dept = item.get('department', 'Other')
            by_dept[dept] = by_dept.get(dept, 0) + 1
        
        print(f"\nEntries by department:")
        for dept, count in sorted(by_dept.items()):
            print(f"  {dept}: {count}")
        
        # Show sample
        print(f"\nSample entries:")
        for item in faculty[:3]:
            name = item.get('name', item.get('type', 'Unknown'))
            research = item.get('research', item.get('description', ''))[:80]
            print(f"\n  {name}")
            print(f"    {research}...")
        
        print(f"\nSaved to uva_research_faculty.json")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())