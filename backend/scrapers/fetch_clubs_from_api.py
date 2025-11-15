#!/usr/bin/env python3
"""
Fetch all UVA clubs/organizations from the Presence.io API
API: https://api.presence.io/virginia/v1/organizations
"""
import json
import httpx
import os
from pathlib import Path

API_URL = "https://api.presence.io/virginia/v1/organizations"
OUTPUT_FILE = Path(__file__).parent / "uva_clubs.json"

def fetch_clubs():
    """Fetch all clubs from the Presence.io API"""
    print(f"Fetching clubs from: {API_URL}")
    
    try:
        response = httpx.get(API_URL, timeout=30.0)
        response.raise_for_status()
        
        clubs_data = response.json()
        print(f"✓ Successfully fetched {len(clubs_data)} clubs from API")
        
        return clubs_data
    except Exception as e:
        print(f"✗ Error fetching clubs: {e}")
        return []

def format_clubs(clubs_data):
    """Format clubs into our database schema"""
    formatted_clubs = []
    
    for club in clubs_data:
        formatted_club = {
            "name": club.get("name", "Unknown Club"),
            "description": club.get("description", ""),
            "category": ", ".join(club.get("categories", [])),
            "meetingTime": club.get("regularMeetingTime", ""),
            "meetingLocation": club.get("regularMeetingLocation", ""),
            "website": f"https://presence.virginia.edu/{club.get('uri', '')}" if club.get('uri') else "",
            "email": club.get("contactEmail", ""),
            "imageUrl": f"https://se-images.campuslabs.com/clink/images/{club.get('photoUriWithVersion', '')}" if club.get('photoUriWithVersion') else "",
            "memberCount": club.get("memberCount", 0),
            "tags": club.get("categories", []),
        }
        
        formatted_clubs.append(formatted_club)
    
    return formatted_clubs

def save_to_json(clubs, output_file):
    """Save clubs to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clubs, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(clubs)} clubs to {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error saving to JSON: {e}")
        return False

def main():
    print("=" * 60)
    print("UVA CLUBS SCRAPER - Presence.io API")
    print("=" * 60)
    
    # Fetch clubs from API
    clubs_data = fetch_clubs()
    
    if not clubs_data:
        print("No clubs data fetched. Exiting.")
        return
    
    # Format clubs
    print(f"\nFormatting {len(clubs_data)} clubs...")
    formatted_clubs = format_clubs(clubs_data)
    
    # Save to JSON
    print(f"\nSaving to {OUTPUT_FILE}...")
    save_to_json(formatted_clubs, OUTPUT_FILE)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total clubs: {len(formatted_clubs)}")
    print(f"Output file: {OUTPUT_FILE}")
    
    # Show sample
    if formatted_clubs:
        print(f"\nSample club:")
        sample = formatted_clubs[0]
        print(f"  Name: {sample['name']}")
        print(f"  Category: {sample['category']}")
        print(f"  Members: {sample['memberCount']}")
        print(f"  Description: {sample['description'][:100]}...")
    
    print("\n✓ Done! Now run the import script to push to Supabase.")

if __name__ == "__main__":
    main()

