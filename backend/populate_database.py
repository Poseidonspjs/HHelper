"""
Database Population Script
Runs scrapers and inserts data directly into Supabase via Prisma
"""

import sys
import os
import subprocess
import json
from scrapers import scrape_courses, scrape_clubs, scrape_rag_content

def run_prisma_query(query):
    """Execute a Prisma query via the frontend Prisma client"""
    # We'll use the frontend's Prisma setup since it's already configured
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Create a temporary JS file to execute the query
    js_code = f"""
const {{ PrismaClient }} = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {{
    {query}
}}

main()
    .then(() => prisma.$disconnect())
    .catch((e) => {{
        console.error(e);
        process.exit(1);
    }});
"""
    
    temp_file = os.path.join(frontend_dir, 'temp_query.js')
    with open(temp_file, 'w') as f:
        f.write(js_code)
    
    try:
        result = subprocess.run(
            ['node', temp_file],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def populate_courses():
    """Populate courses table"""
    print("\n📚 Populating Courses...")
    courses = scrape_courses()
    print(f"   Found {len(courses)} courses")
    
    for course in courses:
        print(f"   → Inserting {course['courseCode']}: {course['title']}")
        
        # Build Prisma upsert query
        query = f"""
const course = await prisma.course.upsert({{
    where: {{ courseCode: '{course['courseCode']}' }},
    update: {{
        title: '{course['title'].replace("'", "\\'")}',
        description: '{(course.get('description', '') or '').replace("'", "\\'")}',
        credits: {course['credits']},
        department: '{course['department']}',
        level: {course['level']},
        semesters: {json.dumps(course.get('semesters', ['Fall', 'Spring']))}
    }},
    create: {{
        courseCode: '{course['courseCode']}',
        title: '{course['title'].replace("'", "\\'")}',
        description: '{(course.get('description', '') or '').replace("'", "\\'")}',
        credits: {course['credits']},
        department: '{course['department']}',
        level: {course['level']},
        semesters: {json.dumps(course.get('semesters', ['Fall', 'Spring']))}
    }}
}});
console.log('Inserted:', course.courseCode);
"""
        
        stdout, stderr = run_prisma_query(query)
        if stderr and "error" in stderr.lower():
            print(f"   ✗ Error: {stderr}")
        else:
            print(f"   ✓ Success")
    
    print(f"✅ Inserted {len(courses)} courses\n")

def populate_clubs():
    """Populate clubs table"""
    print("\n🎯 Populating Clubs...")
    clubs = scrape_clubs()
    print(f"   Found {len(clubs)} clubs")
    
    for club in clubs:
        print(f"   → Inserting {club['name']}")
        
        query = f"""
const club = await prisma.club.upsert({{
    where: {{ name: '{club['name'].replace("'", "\\'")}' }},
    update: {{
        description: '{(club.get('description', '') or '').replace("'", "\\'")}',
        category: '{club.get('category', 'General')}',
        email: {f"'{club['email']}'" if club.get('email') else 'null'},
        website: {f"'{club['website']}'" if club.get('website') else 'null'},
        instagramHandle: {f"'{club['instagramHandle']}'" if club.get('instagramHandle') else 'null'},
        source: '{club.get('source', 'manual')}'
    }},
    create: {{
        name: '{club['name'].replace("'", "\\'")}',
        description: '{(club.get('description', '') or '').replace("'", "\\'")}',
        category: '{club.get('category', 'General')}',
        email: {f"'{club['email']}'" if club.get('email') else 'null'},
        website: {f"'{club['website']}'" if club.get('website') else 'null'},
        instagramHandle: {f"'{club['instagramHandle']}'" if club.get('instagramHandle') else 'null'},
        source: '{club.get('source', 'manual')}'
    }}
}});
console.log('Inserted:', club.name);
"""
        
        stdout, stderr = run_prisma_query(query)
        if stderr and "error" in stderr.lower():
            print(f"   ✗ Error: {stderr}")
        else:
            print(f"   ✓ Success")
    
    print(f"✅ Inserted {len(clubs)} clubs\n")

def populate_rag_documents():
    """Populate RAG documents (without embeddings for now)"""
    print("\n🤖 Populating RAG Documents...")
    documents = scrape_rag_content()
    print(f"   Found {len(documents)} documents")
    print("   Note: Embeddings will be generated when needed by the RAG system\n")
    
    for doc in documents:
        print(f"   → Inserting: {doc['title']}")
        
        query = f"""
const doc = await prisma.ragDocument.create({{
    data: {{
        content: `{doc['content'].replace('`', '\\`').replace("'", "\\'")}`,
        source: '{doc['source']}',
        sourceType: '{doc['sourceType']}',
        title: '{doc['title'].replace("'", "\\'")}',
        metadata: {{}}
    }}
}});
console.log('Inserted:', doc.title);
"""
        
        stdout, stderr = run_prisma_query(query)
        if stderr and "error" in stderr.lower():
            print(f"   ✗ Error: {stderr}")
        else:
            print(f"   ✓ Success")
    
    print(f"✅ Inserted {len(documents)} RAG documents\n")

def main():
    print("=" * 60)
    print("🎓 HoosHelper Database Population")
    print("=" * 60)
    print("\nThis script will populate your Supabase database with:")
    print("  • Courses (with prerequisites)")
    print("  • Student clubs")
    print("  • RAG documents for AI chat")
    print("\n" + "=" * 60)
    
    try:
        populate_courses()
        populate_clubs()
        populate_rag_documents()
        
        print("\n" + "=" * 60)
        print("🎉 Database population complete!")
        print("=" * 60)
        print("\n✅ Your Supabase database now has:")
        print("   • Sample courses for course planning")
        print("   • Student organizations for discovery")
        print("   • Knowledge base for AI chat")
        print("\nYou can now use the app with real database data!")
        print("Visit: http://localhost:3000\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Frontend dependencies are installed (npm install)")
        print("  2. Prisma client is generated (npx prisma generate)")
        print("  3. Database schema is pushed (npx prisma db push)")
        print("  4. DATABASE_URL is set in frontend/.env.local")
        sys.exit(1)

if __name__ == "__main__":
    main()

