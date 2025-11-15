#!/usr/bin/env python3
"""
Quick script to test what column names Supabase actually uses
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load .env from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"Loading .env from: {env_path}")
print(f"File exists: {env_path.exists()}\n")

supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {supabase_url[:30] if supabase_url else 'NOT SET'}...")
print(f"SUPABASE_KEY: {'SET' if supabase_key else 'NOT SET'}\n")

if not supabase_url or not supabase_key:
    print("ERROR: Missing Supabase credentials")
    print("Please check your .env file has SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_KEY)")
    exit(1)

print("Testing Supabase connection and column names...\n")

supabase = create_client(supabase_url, supabase_key)

# Test 1: Get one course to see column structure
print("=" * 60)
print("TEST 1: Fetching one course to see column structure")
print("=" * 60)
try:
    response = supabase.table("courses").select("*").limit(1).execute()
    if response.data and len(response.data) > 0:
        course = response.data[0]
        print("✓ Successfully fetched a course!")
        print("\nColumn names found:")
        for key in course.keys():
            print(f"  - {key}: {type(course[key]).__name__}")
        print("\nSample course data:")
        print(f"  Course Code: {course.get('courseCode') or course.get('course_code') or 'NOT FOUND'}")
        print(f"  Title: {course.get('title', 'NOT FOUND')}")
        print(f"  Department: {course.get('department', 'NOT FOUND')}")
    else:
        print("✗ No courses found in database!")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Try searching for "MATH" with camelCase
print("\n" + "=" * 60)
print("TEST 2: Searching for 'MATH' with camelCase (courseCode)")
print("=" * 60)
try:
    response = supabase.table("courses").select("*").ilike("courseCode", "%MATH%").limit(5).execute()
    print(f"✓ Found {len(response.data)} courses")
    for course in response.data[:3]:
        print(f"  - {course.get('courseCode') or course.get('course_code')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Try searching for "MATH" with snake_case
print("\n" + "=" * 60)
print("TEST 3: Searching for 'MATH' with snake_case (course_code)")
print("=" * 60)
try:
    response = supabase.table("courses").select("*").ilike("course_code", "%MATH%").limit(5).execute()
    print(f"✓ Found {len(response.data)} courses")
    for course in response.data[:3]:
        print(f"  - {course.get('courseCode') or course.get('course_code')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Count total courses
print("\n" + "=" * 60)
print("TEST 4: Total course count")
print("=" * 60)
try:
    response = supabase.table("courses").select("*", count="exact").limit(1).execute()
    print(f"✓ Total courses in database: {response.count}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Search for specific course "CS 2100"
print("\n" + "=" * 60)
print("TEST 5: Searching for 'CS 2100' specifically")
print("=" * 60)
try:
    # Try camelCase
    response = supabase.table("courses").select("*").ilike("courseCode", "%CS 2100%").limit(5).execute()
    print(f"CamelCase search: {len(response.data)} results")
    
    # Try snake_case
    response = supabase.table("courses").select("*").ilike("course_code", "%CS 2100%").limit(5).execute()
    print(f"Snake_case search: {len(response.data)} results")
    
    # Try exact match
    response = supabase.table("courses").select("*").eq("courseCode", "CS 2100").limit(5).execute()
    print(f"Exact camelCase: {len(response.data)} results")
    
    response = supabase.table("courses").select("*").eq("course_code", "CS 2100").limit(5).execute()
    print(f"Exact snake_case: {len(response.data)} results")
    
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("DONE!")
print("=" * 60)

