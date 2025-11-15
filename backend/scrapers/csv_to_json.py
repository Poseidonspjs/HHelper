#!/usr/bin/env python3
"""
Convert searchData.csv to uva_courses.json format
"""

import csv
import json
from typing import Dict, List

def parse_csv_to_courses(csv_file: str) -> List[Dict]:
    """
    Parse CSV and convert to course JSON format
    Deduplicates by unique course code (Mnemonic + Number)
    """
    courses_dict = {}  # Use dict to deduplicate by course code
    
    print("Reading CSV file...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row_count = 0
        
        for row in reader:
            row_count += 1
            
            # Extract fields
            mnemonic = row['Mnemonic'].strip()
            number = row['Number'].strip()
            title = row['Title'].strip()
            description = row['Description'].strip()
            units = row['Units'].strip().strip('"')
            instructor = row['Instructor(s)'].strip().strip('"')
            days = row['Days'].strip()
            section = row['Section'].strip()
            type_str = row['Type'].strip()
            
            # Create unique course code
            course_code = f"{mnemonic} {number}"
            
            # Calculate level (first digit * 1000)
            try:
                level = int(number[0]) * 1000 if number else 0
            except:
                level = 0
            
            # Only process main lecture sections for course info
            # But collect all sections for a course
            if course_code not in courses_dict:
                courses_dict[course_code] = {
                    "courseCode": course_code,
                    "title": title,
                    "description": description,
                    "credits": int(units) if units.isdigit() else 3,
                    "department": mnemonic,
                    "level": level,
                    "prerequisites": [],
                    "semesters": ["Spring 2026"],
                    "source": "louslist",
                    "url": f"https://louslist.org/page.php?Semester=1262&Type=Group&Group={mnemonic}",
                    "sections": []
                }
            
            # Add section information
            course = courses_dict[course_code]
            
            # Update description if current one is empty and we have a new one
            if not course["description"] and description:
                course["description"] = description
            
            # Add section details
            if section and instructor != "To Be Announced":
                section_info = {
                    "section": section,
                    "type": type_str,
                    "instructor": instructor,
                    "days": days,
                    "status": row['Status'].strip()
                }
                
                # Only add if not already present (avoid duplicates)
                if section_info not in course["sections"]:
                    course["sections"].append(section_info)
            
            if row_count % 1000 == 0:
                print(f"  Processed {row_count} rows...")
    
    print(f"✓ Processed {row_count} total rows")
    print(f"✓ Found {len(courses_dict)} unique courses")
    
    # Convert dict to list and sort by course code
    courses_list = list(courses_dict.values())
    courses_list.sort(key=lambda x: (x['department'], x['level'], x['courseCode']))
    
    return courses_list

def main():
    print("="*60)
    print("CSV TO JSON CONVERTER")
    print("="*60)
    
    input_file = "searchData.csv"
    output_file = "uva_courses.json"
    
    # Parse CSV
    courses = parse_csv_to_courses(input_file)
    
    # Save to JSON
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(courses)} courses to {output_file}")
    
    # Statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    
    # Count by department
    dept_counts = {}
    courses_with_desc = 0
    
    for course in courses:
        dept = course['department']
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
        if course['description']:
            courses_with_desc += 1
    
    print(f"Total courses: {len(courses)}")
    print(f"Courses with descriptions: {courses_with_desc}")
    print(f"Total departments: {len(dept_counts)}")
    
    # Show top 10 departments
    print("\nTop 10 departments by course count:")
    sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
    for dept, count in sorted_depts[:10]:
        print(f"  {dept}: {count} courses")
    
    # Show sample courses
    print("\nSample courses:")
    for course in courses[:5]:
        print(f"\n  {course['courseCode']}: {course['title']}")
        desc = course['description']
        if desc:
            if len(desc) > 100:
                desc = desc[:100] + "..."
            print(f"    Description: {desc}")
        print(f"    Credits: {course['credits']}")
        print(f"    Sections: {len(course['sections'])}")

if __name__ == "__main__":
    main()

