"""
Fixed Comprehensive Club Scraper for UVA Student Organizations
Author: Enhanced for HoosHelper
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
import json
import re

class UVAClubScraper:
    """Scrapes UVA student organizations from multiple sources"""
    
    def __init__(self):
        self.clubs = {}  # Use dict to deduplicate by name
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def scrape_cs_clubs(self) -> List[Dict]:
        """Scrape CS-specific clubs from Engineering website"""
        
        clubs = []
        url = "https://engineering.virginia.edu/department/computer-science/about/cs-student-clubs-and-groups"
        
        try:
            print(f"Scraping CS clubs from: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Parse club sections - they follow a pattern
                club_sections = []
                
                # Find sections with club names (typically h3 or h2)
                for header in soup.find_all(['h2', 'h3', 'h4']):
                    club_name = header.get_text().strip()
                    
                    # Skip non-club headers
                    if not club_name or len(club_name) < 3:
                        continue
                    if club_name in ['Social', 'Site Menu', 'Close', 'Search']:
                        continue
                        
                    # Get the section content after this header
                    content_parts = []
                    next_elem = header.find_next_sibling()
                    
                    while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                        if next_elem.name == 'p':
                            content_parts.append(next_elem.get_text().strip())
                        next_elem = next_elem.find_next_sibling()
                    
                    description = ' '.join(content_parts)
                    
                    if description and len(description) > 20:
                        # Extract contact info
                        contact_match = re.search(r'Contact[s]?:\s*(.+?)(?=\n|Who\?|Meeting|More|$)', description, re.IGNORECASE | re.DOTALL)
                        contact = contact_match.group(1).strip() if contact_match else None
                        
                        # Extract email if present
                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', description)
                        email = email_match.group(1) if email_match else None
                        
                        club = {
                            "name": club_name,
                            "description": description[:500],  # Limit length
                            "category": "Technology",
                            "tags": ["Technology", "Computer Science"],
                            "source": "cs_department",
                            "url": url
                        }
                        
                        if email:
                            club["email"] = email
                        if contact:
                            club["contact"] = contact
                            
                        clubs.append(club)
                        print(f"  Found: {club_name}")
        
        except Exception as e:
            print(f"Error scraping CS clubs: {e}")
        
        return clubs
    
    async def scrape_student_activities(self) -> List[Dict]:
        """Try to scrape from Student Activities pages"""
        
        clubs = []
        
        # Try multiple potential sources
        urls = [
            "https://atuva.student.virginia.edu/organizations",
            "https://studentaffairs.virginia.edu/topic/activities-organizations"
        ]
        
        for url in urls:
            try:
                print(f"Trying: {url}")
                response = await self.client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for organization listings
                    # The atuva site has specific org cards
                    for org_elem in soup.find_all(['div', 'article'], class_=re.compile('org|organization|club', re.I)):
                        name_elem = org_elem.find(['h2', 'h3', 'h4', 'a'])
                        if name_elem:
                            name = name_elem.get_text().strip()
                            
                            # Get description
                            desc_elem = org_elem.find(['p', 'div'], class_=re.compile('desc|summary', re.I))
                            description = desc_elem.get_text().strip() if desc_elem else ""
                            
                            if name and len(name) > 2:
                                clubs.append({
                                    "name": name,
                                    "description": description,
                                    "category": "General",
                                    "tags": [],
                                    "source": "student_activities",
                                    "url": url
                                })
                                print(f"  Found: {name}")
            
            except Exception as e:
                print(f"Error with {url}: {e}")
        
        return clubs
    
    def get_comprehensive_fallback_data(self) -> List[Dict]:
        """Enhanced fallback data with CIO information"""
        return [
            # Technology & CS Clubs
            {
                "name": "Computer Science Society (CSS)",
                "description": "The Computer Science Society is UVA's largest CS community, hosting tech talks, workshops, and social events. We connect students with industry professionals and provide mentorship opportunities.",
                "category": "Academic",
                "tags": ["Technology", "Computer Science", "Networking", "Career"],
                "email": "css@virginia.edu",
                "website": "https://css.virginia.edu",
                "instagramHandle": "uva_css",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Association for Computing Machinery (ACM)",
                "description": "UVA's chapter of ACM hosting competitive programming competitions, tech talks, and academic discussions. Includes ICPC team.",
                "category": "Academic",
                "tags": ["Technology", "Computer Science", "Competition", "Programming"],
                "email": "acm-officers@virginia.edu",
                "website": "https://acm.virginia.edu",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "HooHacks",
                "description": "UVA's premier hackathon organization hosting HooHacks, Virginia's largest collegiate hackathon with 500+ students annually.",
                "category": "Technology",
                "tags": ["Technology", "Hackathons", "Programming", "Events"],
                "website": "https://hooshacking.org",
                "instagramHandle": "hooshacking",
                "email": "hackathon.virginia@gmail.com",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Women in Computing Sciences (WICS)",
                "description": "Supporting women and non-binary individuals in technology through mentorship, technical workshops, networking events, and industry partnerships.",
                "category": "Academic",
                "tags": ["Technology", "Computer Science", "Women", "Diversity"],
                "website": "https://wics.virginia.edu",
                "instagramHandle": "uva_wics",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Data Science Club",
                "description": "Learn and apply data science, machine learning, and analytics through hands-on workshops, Kaggle competitions, and industry speaker events.",
                "category": "Academic",
                "tags": ["Technology", "Data Science", "Machine Learning", "Analytics"],
                "email": "dsacatuva@gmail.com",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Special Interest Group on AI (SIGAI)",
                "description": "Comprehensive AI club expanding accessibility and engagement of AI through projects, lectures, guest speakers, hackathons, and networking events.",
                "category": "Technology",
                "tags": ["Technology", "AI", "Machine Learning", "Research"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Cyber Security Club",
                "description": "Hands-on workshops on cybersecurity topics, hosting guest speakers, and competing in CTFs, CCDC, and CPTC competitions.",
                "category": "Technology",
                "tags": ["Technology", "Cybersecurity", "Hacking", "Competition"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Developer Student Club (DSC)",
                "description": "Google-sponsored organization teaching developer technologies used in the real world with project-based learning opportunities.",
                "category": "Technology",
                "tags": ["Technology", "Programming", "Google", "Projects"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Girls Who Code",
                "description": "Empowering inclusive team of next CS leaders breaking down barriers in tech due to resource inequality, race, and gender biases.",
                "category": "Technology",
                "tags": ["Technology", "Women", "Diversity", "Programming"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "UVA Blockchain",
                "description": "Exploring blockchain technology, cryptocurrency, and decentralized applications through projects, speakers, and discussions about Web3.",
                "category": "Technology",
                "tags": ["Technology", "Blockchain", "Cryptocurrency", "Web3"],
                "instagramHandle": "uva_blockchain",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Machine Learning Club (MLC)",
                "description": "Organized review of online ML courses, topic presentations, industry speakers, and collaborative learning about machine learning.",
                "category": "Academic",
                "tags": ["Technology", "Machine Learning", "AI", "Academic"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Student Game Developers",
                "description": "Game development club with game jams, long-term projects, workshops, game nights, and community events for aspiring game developers.",
                "category": "Technology",
                "tags": ["Technology", "Game Development", "Programming", "Creative"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "UI/UX Design at UVA",
                "description": "Fostering community of aspiring designers with workshops, speaker sessions, portfolio reviews focused on professional development.",
                "category": "Technology",
                "tags": ["Technology", "Design", "UI/UX", "Professional"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Project Code",
                "description": "Hands-on projects reflecting real-life CS applications, connecting passionate students with diverse skills for practical experience.",
                "category": "Technology",
                "tags": ["Technology", "Projects", "Programming", "Collaboration"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Forge (formerly HackCville)",
                "description": "Member-supported community of designers, programmers, makers, and creatives sharing, learning, and creating together.",
                "category": "Technology",
                "tags": ["Technology", "Startups", "Makers", "Community"],
                "website": "https://joinforge.co",
                "isCIO": True,
                "source": "manual"
            },
            
            # Service & Volunteering
            {
                "name": "Madison House",
                "description": "UVA's student volunteer center connecting 2,000+ students with community service including tutoring, elderly care, environmental work.",
                "category": "Service",
                "tags": ["Service", "Volunteering", "Community", "Leadership"],
                "website": "https://madisonhouse.org",
                "email": "madisonhouse@virginia.edu",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Hoos Against Hunger",
                "description": "Fighting food insecurity through food bank volunteering, donation drives, and raising awareness about hunger in Charlottesville.",
                "category": "Service",
                "tags": ["Service", "Food Security", "Advocacy", "Community"],
                "instagramHandle": "hoos_against_hunger",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Habitat for Humanity",
                "description": "Build homes and hope in Charlottesville. Weekly build days constructing affordable housing for local families.",
                "category": "Service",
                "tags": ["Service", "Construction", "Housing", "Community"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Alternative Spring Break (ASB)",
                "description": "Week-long service trips focusing on environmental conservation, education, poverty, and disaster relief across the country.",
                "category": "Service",
                "tags": ["Service", "Travel", "Immersion", "Social Justice"],
                "isCIO": True,
                "source": "manual"
            },
            
            # Business & Professional
            {
                "name": "Entrepreneurship Club",
                "description": "Supporting student entrepreneurs through mentorship, networking, pitch competitions, and connections to startup ecosystem.",
                "category": "Business",
                "tags": ["Business", "Entrepreneurship", "Startups", "Innovation"],
                "website": "https://eclub.virginia.edu",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Madison Investment Group",
                "description": "Student-managed investment fund focused on equity research and portfolio management with competitive application and intensive training.",
                "category": "Business",
                "tags": ["Business", "Finance", "Investing", "Research"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Investment Management Club (IMC)",
                "description": "Managing student-run investment portfolio, stock pitch competitions, and learning about finance, investing, and markets.",
                "category": "Business",
                "tags": ["Business", "Finance", "Investing", "Markets"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Women in Business",
                "description": "Empowering women in business through professional development, networking, mentorship, and connections with female executives.",
                "category": "Business",
                "tags": ["Business", "Women", "Professional Development", "Leadership"],
                "isCIO": True,
                "source": "manual"
            },
            
            # Media & Publications
            {
                "name": "The Cavalier Daily",
                "description": "UVA's independent student newspaper since 1890 covering news, sports, arts, and opinion with reporting, editing, and photography opportunities.",
                "category": "Media",
                "tags": ["Journalism", "Writing", "News", "Media"],
                "website": "https://www.cavalierdaily.com",
                "instagramHandle": "cavalierdaily",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "WUVA Radio",
                "description": "Student-run radio station broadcasting music, talk shows, and UVA sports. Learn radio production, DJing, and broadcasting.",
                "category": "Media",
                "tags": ["Radio", "Music", "Broadcasting", "Media"],
                "website": "https://www.wuvaradio.org",
                "isCIO": True,
                "source": "manual"
            },
            
            # Arts & Performance
            {
                "name": "UVA Drama",
                "description": "Student theater producing plays, musicals, and experimental performances with opportunities for acting, directing, stage crew, and design.",
                "category": "Arts",
                "tags": ["Theater", "Performance", "Arts", "Drama"],
                "website": "https://drama.virginia.edu",
                "instagramHandle": "uvadrama",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Hullabahoos",
                "description": "UVA's premier all-male a cappella group known for energetic performances, tight harmonies, and entertaining shows.",
                "category": "Arts",
                "tags": ["Music", "A Cappella", "Performance", "Singing"],
                "website": "https://hullabahoos.com",
                "instagramHandle": "hullabahoos",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Virginia Belles",
                "description": "All-female a cappella group performing pop, jazz, and contemporary music. One of UVA's oldest a cappella groups.",
                "category": "Arts",
                "tags": ["Music", "A Cappella", "Performance", "Singing"],
                "isCIO": True,
                "source": "manual"
            },
            
            # Cultural Organizations
            {
                "name": "Black Student Alliance (BSA)",
                "description": "Promoting Black culture, advocacy, and community through social events, speakers, and activism. One of UVA's largest cultural organizations.",
                "category": "Cultural",
                "tags": ["Culture", "Black Community", "Advocacy", "Identity"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Latinx Student Alliance (LSA)",
                "description": "Celebrating Latinx culture and supporting Latinx students through cultural events, mentorship, and advocacy.",
                "category": "Cultural",
                "tags": ["Culture", "Latinx", "Community", "Advocacy"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "South Asian Student Association (SASA)",
                "description": "Celebrating South Asian culture through Holi, Garba, cultural shows, and community building. Open to all interested students.",
                "category": "Cultural",
                "tags": ["Culture", "South Asian", "Community", "Events"],
                "instagramHandle": "uva_sasa",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Chinese Student Association (CSA)",
                "description": "Promoting Chinese culture through Lunar New Year celebrations, cultural performances, and social events. Largest Asian cultural org.",
                "category": "Cultural",
                "tags": ["Culture", "Chinese", "Community", "Events"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Korean Student Association (KSA)",
                "description": "Sharing Korean culture through K-pop dance workshops, Korean BBQ nights, and cultural festivals.",
                "category": "Cultural",
                "tags": ["Culture", "Korean", "K-pop", "Community"],
                "isCIO": True,
                "source": "manual"
            },
            
            # Governance & Leadership
            {
                "name": "Student Council",
                "description": "UVA's student government representing student interests, allocating funding, and organizing events like Lighting of the Lawn.",
                "category": "Governance",
                "tags": ["Leadership", "Governance", "Community", "Advocacy"],
                "website": "https://studentcouncil.virginia.edu",
                "instagramHandle": "uvastudco",
                "isCIO": True,
                "source": "manual"
            },
            
            # Engineering Organizations
            {
                "name": "Society of Women Engineers (SWE)",
                "description": "Professional development, outreach, and community building for women in engineering through networking, workshops, and events.",
                "category": "Engineering",
                "tags": ["Engineering", "Women", "Professional Development", "STEM"],
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "National Society of Black Engineers (NSBE)",
                "description": "Increasing culturally responsible Black engineers who excel academically, succeed professionally, and impact community positively.",
                "category": "Engineering",
                "tags": ["Engineering", "Black Community", "Professional Development", "STEM"],
                "email": "nsbeatuva.president@gmail.com",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Society of Hispanic Professional Engineers (SHPE)",
                "description": "Promoting engineering in Hispanic/Latino community through recruitment, retention, career development, and nationwide conference.",
                "category": "Engineering",
                "tags": ["Engineering", "Latinx", "Professional Development", "STEM"],
                "email": "shpe.uva@gmail.com",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Society of Asian Scientists and Engineers (SASE)",
                "description": "Preparing Asian heritage students for success, promoting diversity and tolerance, providing career potential opportunities.",
                "category": "Engineering",
                "tags": ["Engineering", "Asian", "Professional Development", "STEM"],
                "email": "uva@saseconnect.org",
                "isCIO": True,
                "source": "manual"
            },
            {
                "name": "Mechatronics and Robotics Society (MARS)",
                "description": "Developing excavating robot for NASA Robotics Mining Competition with workshops on CAD, circuits, machining, and hands-on engineering.",
                "category": "Engineering",
                "tags": ["Engineering", "Robotics", "Competition", "Hands-on"],
                "isCIO": True,
                "source": "manual"
            },
        ]
    
    async def scrape_all(self) -> List[Dict]:
        """Main scraping function"""
        
        all_clubs = []
        
        # Try web scraping
        print("=" * 60)
        print("SCRAPING UVA CLUBS")
        print("=" * 60)
        
        try:
            cs_clubs = await self.scrape_cs_clubs()
            all_clubs.extend(cs_clubs)
            
            await asyncio.sleep(0.5)
            
            activities_clubs = await self.scrape_student_activities()
            all_clubs.extend(activities_clubs)
            
        except Exception as e:
            print(f"Web scraping encountered issues: {e}")
        
        # Always add fallback data (it's comprehensive and accurate)
        print("\nAdding comprehensive manual data...")
        fallback = self.get_comprehensive_fallback_data()
        all_clubs.extend(fallback)
        
        # Deduplicate by name
        unique_clubs = {}
        for club in all_clubs:
            name = club['name']
            if name not in unique_clubs:
                unique_clubs[name] = club
            else:
                # Merge data if scraped version has more info
                existing = unique_clubs[name]
                for key, value in club.items():
                    if key not in existing or not existing[key]:
                        existing[key] = value
        
        final_clubs = list(unique_clubs.values())
        
        # Auto-tag clubs
        for club in final_clubs:
            if 'tags' not in club or not club['tags']:
                club['tags'] = self.auto_tag_club(club)
        
        return final_clubs
    
    def auto_tag_club(self, club: Dict) -> List[str]:
        """Auto-generate tags"""
        tags = set(club.get('tags', []))
        text = f"{club['name']} {club.get('description', '')}".lower()
        
        keywords = {
            "Technology": ['tech', 'computer', 'programming', 'coding', 'software', 'data', 'ai', 'cyber', 'web'],
            "Academic": ['academic', 'study', 'research', 'science', 'learning'],
            "Service": ['service', 'volunteer', 'community', 'charity', 'help'],
            "Arts": ['arts', 'music', 'theater', 'drama', 'dance', 'performance'],
            "Business": ['business', 'entrepreneur', 'consulting', 'finance', 'startup'],
            "Engineering": ['engineering', 'engineer', 'robotics', 'mechanical'],
            "Social": ['social', 'friends', 'networking', 'fun'],
            "Cultural": ['culture', 'cultural', 'identity', 'heritage'],
        }
        
        for tag, words in keywords.items():
            if any(word in text for word in words):
                tags.add(tag)
        
        return list(tags)
    
    async def close(self):
        await self.client.aclose()


async def main():
    scraper = UVAClubScraper()
    
    try:
        clubs = await scraper.scrape_all()
        
        # Save to JSON
        with open('uva_clubs.json', 'w', encoding='utf-8') as f:
            json.dump(clubs, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total clubs: {len(clubs)}")
        
        # Group by category
        by_category = {}
        for club in clubs:
            cat = club.get('category', 'Other')
            by_category[cat] = by_category.get(cat, 0) + 1
        
        print(f"\nClubs by category:")
        for cat, count in sorted(by_category.items()):
            print(f"  {cat}: {count}")
        
        # Count CIOs
        cios = sum(1 for club in clubs if club.get('isCIO'))
        print(f"\nCIOs: {cios}")
        
        print(f"\nSaved to uva_clubs.json")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())