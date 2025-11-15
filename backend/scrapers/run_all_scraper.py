"""
Master Script to Run All UVA Scrapers
Runs course, club, and RAG content scrapers and generates comprehensive output
"""

import asyncio
import json
from datetime import datetime
import sys

# Import our scrapers
from improved_course_scraper import scrape_courses_comprehensive, save_courses_to_file
from improved_club_scraper import scrape_clubs_comprehensive, save_clubs_to_file
from improved_rag_scraper import scrape_rag_content_comprehensive, save_rag_content_to_file


async def run_all_scrapers():
    """Run all scrapers and generate comprehensive UVA data"""
    
    print("=" * 70)
    print("UVA COMPREHENSIVE DATA SCRAPER")
    print("HoosHelper - Your Perfect Big Brother for UVA Students")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track results
    results = {
        "timestamp": datetime.now().isoformat(),
        "courses": {"count": 0, "success": False},
        "clubs": {"count": 0, "success": False},
        "rag_content": {"count": 0, "success": False}
    }
    
    # 1. Scrape Courses
    print("\n" + "=" * 70)
    print("STEP 1: SCRAPING COURSES")
    print("=" * 70)
    try:
        courses = await scrape_courses_comprehensive()
        save_courses_to_file(courses, "uva_courses.json")
        results["courses"]["count"] = len(courses)
        results["courses"]["success"] = True
        print(f"✓ Courses: {len(courses)} scraped successfully")
    except Exception as e:
        print(f"✗ Courses failed: {e}")
    
    # 2. Scrape Clubs
    print("\n" + "=" * 70)
    print("STEP 2: SCRAPING CLUBS")
    print("=" * 70)
    try:
        clubs = await scrape_clubs_comprehensive()
        save_clubs_to_file(clubs, "uva_clubs.json")
        results["clubs"]["count"] = len(clubs)
        results["clubs"]["success"] = True
        print(f"✓ Clubs: {len(clubs)} scraped successfully")
    except Exception as e:
        print(f"✗ Clubs failed: {e}")
    
    # 3. Scrape RAG Content
    print("\n" + "=" * 70)
    print("STEP 3: SCRAPING RAG CONTENT")
    print("=" * 70)
    try:
        rag_docs = await scrape_rag_content_comprehensive()
        save_rag_content_to_file(rag_docs, "uva_rag_content.json")
        results["rag_content"]["count"] = len(rag_docs)
        results["rag_content"]["success"] = True
        print(f"✓ RAG Content: {len(rag_docs)} documents scraped successfully")
    except Exception as e:
        print(f"✗ RAG Content failed: {e}")
    
    # 4. Generate Combined Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    total_items = (
        results["courses"]["count"] + 
        results["clubs"]["count"] + 
        results["rag_content"]["count"]
    )
    
    print(f"\nTotal Items Scraped: {total_items}")
    print(f"  - Courses: {results['courses']['count']}")
    print(f"  - Clubs: {results['clubs']['count']}")
    print(f"  - RAG Documents: {results['rag_content']['count']}")
    
    print("\nSuccess Status:")
    print(f"  - Courses: {'✓' if results['courses']['success'] else '✗'}")
    print(f"  - Clubs: {'✓' if results['clubs']['success'] else '✗'}")
    print(f"  - RAG Content: {'✓' if results['rag_content']['success'] else '✗'}")
    
    # Save metadata
    with open("scraper_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Metadata saved to scraper_results.json")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    # Run all scrapers
    results = asyncio.run(run_all_scrapers())
    
    # Exit with appropriate code
    all_success = all([
        results["courses"]["success"],
        results["clubs"]["success"],
        results["rag_content"]["success"]
    ])
    
    sys.exit(0 if all_success else 1)