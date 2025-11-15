"""
Club Scraper for UVA Student Organizations
Scrapes club data from multiple sources
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio

async def scrape_atuva_clubs() -> List[Dict]:
    """Scrape clubs from ATuva (official UVA organization directory)"""
    
    clubs = []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # ATuva API endpoint (if available)
            # This is a placeholder - actual implementation would use real API
            pass
    
    except Exception as e:
        print(f"Error scraping ATuva: {e}")
    
    return clubs

def get_fallback_clubs() -> List[Dict]:
    """Fallback club data if scraping fails"""
    
    return [
        {
            "name": "UVA Computer Science Society",
            "description": "The Computer Science Society is a community for CS students to network, collaborate on projects, and learn about technology careers.",
            "category": "Academic",
            "tags": ["Technology", "Computer Science", "Networking", "Career"],
            "email": "css@virginia.edu",
            "website": "https://css.virginia.edu",
            "source": "manual"
        },
        {
            "name": "Hoos Hacking",
            "description": "UVA's premier hackathon organization. We host HooHacks, Virginia's largest collegiate hackathon, and foster a community of student developers.",
            "category": "Tech",
            "tags": ["Technology", "Hackathons", "Programming", "Events"],
            "website": "https://hooshacking.org",
            "instagramHandle": "hooshacking",
            "source": "manual"
        },
        {
            "name": "Madison House",
            "description": "UVA's student volunteer center connecting students with meaningful community service opportunities in Charlottesville.",
            "category": "Service",
            "tags": ["Service", "Volunteering", "Community", "Outreach"],
            "website": "https://madisonhouse.org",
            "source": "manual"
        },
        {
            "name": "UVA Drama",
            "description": "Student theater organization producing plays, musicals, and other theatrical performances throughout the year.",
            "category": "Arts",
            "tags": ["Theater", "Performance", "Arts", "Drama"],
            "website": "https://drama.virginia.edu",
            "source": "manual"
        },
        {
            "name": "Data Science Club",
            "description": "Learn and apply data science, machine learning, and analytics through workshops, projects, and competitions.",
            "category": "Academic",
            "tags": ["Technology", "Data Science", "Machine Learning", "Analytics"],
            "email": "datascience@virginia.edu",
            "source": "manual"
        },
        {
            "name": "Entrepreneurship Club",
            "description": "Supporting student entrepreneurs through mentorship, networking events, and pitch competitions.",
            "category": "Business",
            "tags": ["Business", "Entrepreneurship", "Startups", "Innovation"],
            "website": "https://eclub.virginia.edu",
            "source": "manual"
        },
        {
            "name": "UVA Robotics",
            "description": "Design, build, and compete with robots. Open to all majors interested in robotics and automation.",
            "category": "Tech",
            "tags": ["Technology", "Robotics", "Engineering", "Competition"],
            "email": "robotics@virginia.edu",
            "source": "manual"
        },
        {
            "name": "Hoo's Reading",
            "description": "Book club for students who love to read and discuss literature across all genres.",
            "category": "Social",
            "tags": ["Literature", "Reading", "Discussion", "Social"],
            "source": "manual"
        },
        {
            "name": "UVA Outdoors",
            "description": "Outdoor recreation and adventure trips including hiking, camping, rock climbing, and kayaking.",
            "category": "Recreation",
            "tags": ["Outdoors", "Recreation", "Adventure", "Nature"],
            "website": "https://www.virginia.edu/uvaoutdoors",
            "source": "manual"
        },
        {
            "name": "Hoos Against Hunger",
            "description": "Fighting food insecurity through volunteering, donations, and awareness campaigns.",
            "category": "Service",
            "tags": ["Service", "Food Security", "Advocacy", "Community"],
            "source": "manual"
        },
        {
            "name": "Women in Computer Science",
            "description": "Supporting and empowering women in technology through mentorship, workshops, and networking.",
            "category": "Academic",
            "tags": ["Technology", "Computer Science", "Women", "Diversity"],
            "email": "wics@virginia.edu",
            "source": "manual"
        },
        {
            "name": "UVA Salsa Club",
            "description": "Learn and practice salsa dancing in a fun, welcoming environment. No experience necessary!",
            "category": "Arts",
            "tags": ["Dance", "Social", "Culture", "Arts"],
            "instagramHandle": "uvasalsa",
            "source": "manual"
        },
        {
            "name": "Hoos in Consulting",
            "description": "Preparing students for careers in consulting through case workshops, networking, and industry insights.",
            "category": "Business",
            "tags": ["Business", "Consulting", "Career", "Professional"],
            "source": "manual"
        },
        {
            "name": "UVA Blockchain",
            "description": "Exploring blockchain technology, cryptocurrency, and decentralized applications through projects and discussions.",
            "category": "Tech",
            "tags": ["Technology", "Blockchain", "Cryptocurrency", "Innovation"],
            "source": "manual"
        },
        {
            "name": "Sustained Dialogue",
            "description": "Facilitating conversations across differences to build understanding and community on Grounds.",
            "category": "Service",
            "tags": ["Dialogue", "Community", "Diversity", "Social Justice"],
            "website": "https://sustained-dialogue.virginia.edu",
            "source": "manual"
        },
        {
            "name": "UVA Quiz Bowl",
            "description": "Competitive trivia team competing in tournaments across the country.",
            "category": "Academic",
            "tags": ["Trivia", "Competition", "Academic", "Games"],
            "source": "manual"
        },
        {
            "name": "Hoos Housing Hoos",
            "description": "Addressing homelessness and housing insecurity through direct service and advocacy.",
            "category": "Service",
            "tags": ["Service", "Housing", "Advocacy", "Community"],
            "source": "manual"
        },
        {
            "name": "UVA Photography Club",
            "description": "Photography enthusiasts sharing skills, going on photo walks, and showcasing work.",
            "category": "Arts",
            "tags": ["Photography", "Arts", "Visual", "Creative"],
            "instagramHandle": "uvaphotography",
            "source": "manual"
        },
        {
            "name": "Student Council",
            "description": "UVA's student government representing student interests and organizing community events.",
            "category": "Governance",
            "tags": ["Leadership", "Governance", "Community", "Advocacy"],
            "website": "https://studentcouncil.virginia.edu",
            "source": "manual"
        },
        {
            "name": "Hoos Coding",
            "description": "Weekly coding practice sessions, interview prep, and algorithm challenges for all skill levels.",
            "category": "Academic",
            "tags": ["Technology", "Programming", "Interview Prep", "Computer Science"],
            "source": "manual"
        },
    ]

def auto_tag_club(club: Dict) -> List[str]:
    """Automatically generate tags based on club name and description"""
    
    tags = set()
    text = f"{club['name']} {club.get('description', '')}".lower()
    
    # Technology keywords
    tech_keywords = ['tech', 'computer', 'programming', 'coding', 'software', 
                     'data', 'ai', 'machine learning', 'robotics', 'blockchain']
    if any(keyword in text for keyword in tech_keywords):
        tags.add("Technology")
    
    # Academic keywords
    academic_keywords = ['academic', 'study', 'research', 'science', 'engineering']
    if any(keyword in text for keyword in academic_keywords):
        tags.add("Academic")
    
    # Service keywords
    service_keywords = ['service', 'volunteer', 'community', 'outreach', 'charity']
    if any(keyword in text for keyword in service_keywords):
        tags.add("Service")
    
    # Arts keywords
    arts_keywords = ['arts', 'music', 'theater', 'drama', 'dance', 'photography']
    if any(keyword in text for keyword in arts_keywords):
        tags.add("Arts")
    
    # Business keywords
    business_keywords = ['business', 'entrepreneur', 'consulting', 'finance', 'startup']
    if any(keyword in text for keyword in business_keywords):
        tags.add("Business")
    
    return list(tags)

def scrape_clubs() -> List[Dict]:
    """Main scraping function with fallback"""
    
    print("Starting club scraping...")
    
    # Try to scrape real data
    try:
        clubs = asyncio.run(scrape_atuva_clubs())
        
        if clubs and len(clubs) > 10:
            print(f"Successfully scraped {len(clubs)} clubs")
            return clubs
    
    except Exception as e:
        print(f"Scraping failed: {e}")
    
    # Fall back to static data
    print("Using fallback club data")
    clubs = get_fallback_clubs()
    
    # Auto-tag clubs
    for club in clubs:
        if 'tags' not in club or not club['tags']:
            club['tags'] = auto_tag_club(club)
    
    return clubs

if __name__ == "__main__":
    clubs = scrape_clubs()
    print(f"Total clubs: {len(clubs)}")
    for club in clubs[:3]:
        print(f"  {club['name']}: {club['category']}")

