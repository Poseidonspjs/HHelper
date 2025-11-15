#!/usr/bin/env python3
"""
Import UVA clubs from JSON to Supabase database
"""
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

CLUBS_FILE = Path(__file__).parent / "uva_clubs.json"

def main():
    print("=" * 60)
    print("IMPORTING CLUBS TO SUPABASE")
    print("=" * 60)
    
    # Get Supabase credentials
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("✗ Error: Supabase credentials not found in .env")
        sys.exit(1)
    
    print(f"✓ Supabase URL: {supabase_url[:30]}...")
    
    # Connect to Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Connected to Supabase")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Load clubs from JSON
    print(f"\nLoading clubs from {CLUBS_FILE}...")
    try:
        with open(CLUBS_FILE, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
        print(f"✓ Loaded {len(clubs)} clubs")
    except Exception as e:
        print(f"✗ Error loading clubs: {e}")
        sys.exit(1)
    
    # Check existing clubs
    print("\nChecking existing clubs in database...")
    try:
        existing_response = supabase.table("clubs").select("name").execute()
        existing_names = {club['name'] for club in existing_response.data}
        print(f"Found {len(existing_names)} existing clubs")
    except Exception as e:
        print(f"Warning: Could not check existing clubs: {e}")
        existing_names = set()
    
    # Import clubs
    print(f"\nImporting clubs to database...")
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, club in enumerate(clubs, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(clubs)} clubs processed...")
        
        club_name = club.get('name')
        
        # Skip if already exists
        if club_name in existing_names:
            skip_count += 1
            continue
        
        try:
            # Generate UUID and timestamp for the club
            club_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            # Prepare club data for database
            club_data = {
                "id": club_id,
                "name": club_name,
                "description": club.get('description', ''),
                "category": club.get('category', ''),
                "email": club.get('email', ''),
                "website": club.get('website', ''),
                "instagramHandle": None,  # Not provided by API
                "source": "presence.io",
                "externalId": club.get('website', '').split('/')[-1] if club.get('website') else None,
                "createdAt": now,
                "updatedAt": now,
            }
            
            # Insert club
            response = supabase.table("clubs").insert(club_data).execute()
            
            # Insert tags
            tags = club.get('tags', [])
            if tags and response.data:
                tag_data = []
                for tag in tags:
                    tag_id = str(uuid.uuid4())
                    tag_data.append({
                        "id": tag_id,
                        "clubId": club_id,
                        "tag": tag
                    })
                
                try:
                    supabase.table("club_tags").insert(tag_data).execute()
                except Exception as tag_error:
                    # Ignore duplicate tag errors
                    if "duplicate key" not in str(tag_error).lower():
                        print(f"  Warning: Failed to insert tags for {club_name}: {tag_error}")
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Only print first 5 errors
                print(f"  ✗ Error importing '{club_name}': {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully imported: {success_count} clubs")
    print(f"⊘ Skipped (already exist): {skip_count} clubs")
    print(f"✗ Errors: {error_count} clubs")
    print(f"Total processed: {len(clubs)} clubs")
    print("=" * 60)
    
    if success_count > 0:
        print(f"\n✓ Successfully added {success_count} new clubs to the database!")
    
    if error_count > 0:
        print(f"\n⚠ {error_count} clubs failed to import. Check errors above.")

if __name__ == "__main__":
    main()

