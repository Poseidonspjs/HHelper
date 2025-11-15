#!/usr/bin/env python3
"""
Diagnostic script to test HoosHelper backend configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*60)
print("HOOSHELPER BACKEND DIAGNOSTIC")
print("="*60)

# Check environment variables
print("\n1. Checking Environment Variables...")
env_vars = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
}

for key, value in env_vars.items():
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"  ✓ {key}: {masked}")
    else:
        print(f"  ✗ {key}: NOT SET")

# Test Supabase connection
print("\n2. Testing Supabase Connection...")
try:
    from supabase import create_client
    supabase_client = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_ANON_KEY", "")
    )
    print("  ✓ Supabase client created successfully")
    
    # Test querying courses
    print("\n3. Testing Course Query...")
    try:
        response = supabase_client.table("courses").select("courseCode, title, department").limit(5).execute()
        if response.data:
            print(f"  ✓ Found {len(response.data)} courses:")
            for course in response.data:
                print(f"    - {course.get('courseCode')}: {course.get('title')}")
        else:
            print("  ⚠ No courses found in database")
    except Exception as e:
        print(f"  ✗ Error querying courses: {e}")
    
    # Test RAG documents
    print("\n4. Testing RAG Documents...")
    try:
        response = supabase_client.table("rag_documents").select("title, sourceType").limit(5).execute()
        if response.data:
            print(f"  ✓ Found {len(response.data)} RAG documents:")
            for doc in response.data:
                print(f"    - {doc.get('title')} ({doc.get('sourceType')})")
        else:
            print("  ⚠ No RAG documents found in database")
    except Exception as e:
        print(f"  ✗ Error querying RAG documents: {e}")
        
except Exception as e:
    print(f"  ✗ Failed to connect to Supabase: {e}")

# Test Claude API
print("\n5. Testing Claude API...")
try:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello from HoosHelper!' in 5 words or less."}
        ]
    )
    response_text = message.content[0].text
    print(f"  ✓ Claude API working: {response_text}")
except Exception as e:
    print(f"  ✗ Claude API error: {e}")

# Test OpenAI Embeddings
print("\n6. Testing OpenAI Embeddings...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input="Test embedding",
        model="text-embedding-3-small"
    )
    print(f"  ✓ OpenAI Embeddings working (dimension: {len(response.data[0].embedding)})")
except Exception as e:
    print(f"  ✗ OpenAI Embeddings error: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\nIf you see any ✗ errors above, fix those issues first!")
print("If everything shows ✓, your backend should be working.\n")

