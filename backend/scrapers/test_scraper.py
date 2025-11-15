"""
Quick test script to verify all scrapers work
"""

import asyncio
import json

async def test_all():
    """Test all three scrapers"""
    
    print("=" * 60)
    print("TESTING UVA SCRAPERS")
    print("=" * 60)
    
    # Test 1: Courses
    print("\n1. Testing Course Scraper...")
    try:
        from improved_course_scraper import scrape_courses_comprehensive
        courses = await scrape_courses_comprehensive(priority_depts=["CS", "MATH"])
        print(f"   ✓ Got {len(courses)} courses")
        print(f"   Sample: {courses[0]['courseCode']} - {courses[0]['title']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2: Clubs
    print("\n2. Testing Club Scraper...")
    try:
        from improved_club_scraper import scrape_clubs_comprehensive
        clubs = await scrape_clubs_comprehensive()
        print(f"   ✓ Got {len(clubs)} clubs")
        print(f"   Sample: {clubs[0]['name']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 3: RAG Content
    print("\n3. Testing RAG Scraper...")
    try:
        from improved_rag_scraper import scrape_rag_content_comprehensive
        docs = await scrape_rag_content_comprehensive()
        print(f"   ✓ Got {len(docs)} documents")
        print(f"   Sample: {docs[0]['title']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all())