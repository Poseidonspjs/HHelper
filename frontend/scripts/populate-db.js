/**
 * Database Population Script
 * Populates Supabase with courses, clubs, and RAG documents
 */

const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// Sample courses data
const courses = [
  {
    courseCode: "CS 1110",
    title: "Introduction to Programming",
    description: "A first course in programming using Python. Topics include variables, conditionals, loops, functions, and basic data structures.",
    credits: 3,
    department: "CS",
    level: 1000,
    semesters: ["Fall", "Spring", "Summer"],
    prerequisites: []
  },
  {
    courseCode: "CS 2100",
    title: "Data Structures and Algorithms I",
    description: "Introduction to fundamental data structures (arrays, lists, stacks, queues, trees) and algorithms. Analysis of algorithm efficiency.",
    credits: 3,
    department: "CS",
    level: 2000,
    semesters: ["Fall", "Spring"],
    prerequisites: ["CS 1110"]
  },
  {
    courseCode: "CS 2120",
    title: "Discrete Mathematics and Theory I",
    description: "Mathematical foundations of computer science including logic, proofs, sets, functions, relations, and graphs.",
    credits: 3,
    department: "CS",
    level: 2000,
    semesters: ["Fall", "Spring"],
    prerequisites: ["CS 2100"]
  },
  {
    courseCode: "CS 3100",
    title: "Data Structures and Algorithms II",
    description: "Advanced data structures and algorithm analysis. Topics include graphs, hash tables, balanced trees, and algorithm design techniques.",
    credits: 3,
    department: "CS",
    level: 3000,
    semesters: ["Fall", "Spring"],
    prerequisites: ["CS 2100", "CS 2120"]
  },
  {
    courseCode: "CS 4750",
    title: "Database Systems",
    description: "Database design, relational model, SQL, normalization, transactions, and database management systems.",
    credits: 3,
    department: "CS",
    level: 4000,
    semesters: ["Fall", "Spring"],
    prerequisites: ["CS 2120"]
  },
  {
    courseCode: "CS 4710",
    title: "Artificial Intelligence",
    description: "Introduction to artificial intelligence including search, knowledge representation, machine learning, and neural networks.",
    credits: 3,
    department: "CS",
    level: 4000,
    semesters: ["Fall"],
    prerequisites: ["CS 2120"]
  },
  {
    courseCode: "MATH 1310",
    title: "Calculus I",
    description: "Limits, continuity, derivatives, and applications of derivatives.",
    credits: 4,
    department: "MATH",
    level: 1000,
    semesters: ["Fall", "Spring", "Summer"],
    prerequisites: []
  },
  {
    courseCode: "MATH 1320",
    title: "Calculus II",
    description: "Techniques of integration, applications of integrals, sequences, and series.",
    credits: 4,
    department: "MATH",
    level: 1000,
    semesters: ["Fall", "Spring", "Summer"],
    prerequisites: ["MATH 1310"]
  }
];

// Sample clubs data
const clubs = [
  {
    name: "UVA Computer Science Society",
    description: "The Computer Science Society is a community for CS students to network, collaborate on projects, and learn about technology careers.",
    category: "Academic",
    email: "css@virginia.edu",
    website: "https://css.virginia.edu"
  },
  {
    name: "Hoos Hacking",
    description: "UVA's premier hackathon organization. We host HooHacks, Virginia's largest collegiate hackathon.",
    category: "Tech",
    website: "https://hooshacking.org",
    instagramHandle: "hooshacking"
  },
  {
    name: "Madison House",
    description: "UVA's student volunteer center connecting students with meaningful community service opportunities.",
    category: "Service",
    website: "https://madisonhouse.org"
  },
  {
    name: "Data Science Club",
    description: "Learn and apply data science, machine learning, and analytics through workshops, projects, and competitions.",
    category: "Academic",
    email: "datascience@virginia.edu"
  }
];

async function populateCourses() {
  console.log('\n📚 Populating Courses...');
  
  for (const course of courses) {
    try {
      const created = await prisma.course.upsert({
        where: { courseCode: course.courseCode },
        update: {
          title: course.title,
          description: course.description,
          credits: course.credits,
          department: course.department,
          level: course.level,
          semesters: course.semesters
        },
        create: {
          courseCode: course.courseCode,
          title: course.title,
          description: course.description,
          credits: course.credits,
          department: course.department,
          level: course.level,
          semesters: course.semesters
        }
      });
      console.log(`   ✓ ${created.courseCode}: ${created.title}`);
    } catch (error) {
      console.error(`   ✗ Error inserting ${course.courseCode}:`, error.message);
    }
  }
  
  console.log(`\n✅ Inserted ${courses.length} courses`);
}

async function populateClubs() {
  console.log('\n🎯 Populating Clubs...');
  
  for (const club of clubs) {
    try {
      const created = await prisma.club.upsert({
        where: { name: club.name },
        update: {
          description: club.description,
          category: club.category,
          email: club.email,
          website: club.website,
          instagramHandle: club.instagramHandle
        },
        create: {
          name: club.name,
          description: club.description,
          category: club.category,
          email: club.email,
          website: club.website,
          instagramHandle: club.instagramHandle
        }
      });
      console.log(`   ✓ ${created.name}`);
    } catch (error) {
      console.error(`   ✗ Error inserting ${club.name}:`, error.message);
    }
  }
  
  console.log(`\n✅ Inserted ${clubs.length} clubs`);
}

async function main() {
  console.log('=' .repeat(60));
  console.log('🎓 HoosHelper Database Population');
  console.log('='.repeat(60));
  
  try {
    await populateCourses();
    await populateClubs();
    
    console.log('\n' + '='.repeat(60));
    console.log('🎉 Database population complete!');
    console.log('='.repeat(60));
    console.log('\n✅ Your Supabase database now has:');
    console.log('   • Sample courses for course planning');
    console.log('   • Student organizations for discovery');
    console.log('\nYou can now use the app with real database data!');
    console.log('Visit: http://localhost:3000\n');
    
  } catch (error) {
    console.error('\n❌ Error:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

main();

