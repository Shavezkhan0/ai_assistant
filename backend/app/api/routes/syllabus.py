from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from app.database.postgres_db_helper import PostgresDB
from app.services.document_processor import DocumentProcessor
from PyPDF2 import PdfReader
import io
import re
from typing import List, Optional

router = APIRouter(tags=["syllabus"])

# Initialize components
db = PostgresDB()
doc_processor = DocumentProcessor()

@router.post("/upload")
async def upload_syllabus(
    file: UploadFile = File(...),
    department: str = Form(...),
    semester: str = Form(...)
):
    """Upload and process syllabus PDF"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read PDF content
        contents = await file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))
        
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        if not full_text or len(full_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough text from PDF. Make sure it's not scanned/image-based."
            )
        
        # Parse courses from PDF
        courses = parse_syllabus_pdf(full_text, department, semester)
        
        if not courses:
            raise HTTPException(
                status_code=400,
                detail="Could not parse any courses from the PDF. Please ensure the PDF contains course codes (e.g., CIE-306T) and course information."
            )
        
        # Deduplicate courses by course_code (keep the one with more content)
        unique_courses = {}
        for course in courses:
            course_code = course['course_code']
            if course_code not in unique_courses:
                unique_courses[course_code] = course
            else:
                # If duplicate, keep the one with more content
                if len(course.get('content', '')) > len(unique_courses[course_code].get('content', '')):
                    unique_courses[course_code] = course
        
        courses = list(unique_courses.values())
        print(f"📚 Found {len(courses)} unique courses after deduplication")
        
        # Store each course in database
        stored_count = 0
        stored_courses = []
        
        for course in courses:
            syllabus_id = db.add_syllabus(
                course_code=course['course_code'],
                course_name=course['course_name'],
                department=department,
                semester=semester,
                credits=course.get('credits', 3),
                syllabus_content=course['content']
            )
            
            if syllabus_id:
                stored_count += 1
                stored_courses.append({
                    'course_code': course['course_code'],
                    'course_name': course['course_name']
                })
        
        if stored_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to store any courses in the database"
            )
        
        return {
            "success": True,
            "message": f"Successfully processed and stored {stored_count} course(s)",
            "courses_stored": stored_count,
            "courses": stored_courses
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing syllabus: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing syllabus: {str(e)}")

def parse_syllabus_pdf(text: str, department: str, semester: str) -> List[dict]:
    """
    Parse PDF text and extract course information
    Based on the syllabus structure with units, course codes, etc.
    """
    courses = []
    
    # Normalize text
    text = text.replace('\r', '\n')
    lines = text.split('\n')
    
    # First, try to find the main course title at the top (before course codes)
    # Look for patterns like "Advanced Java Programming" at the beginning
    main_course_title = None
    skip_keywords = ['handbook', 'applicable', 'page', 'batch', 'academic', 'session', 'offered', 'usict', 'affiliated', 'institutions', 'university', 'b.tech', 'programmes', 'discipline', 'semester', 'group', 'sub-group', 'paper code', 'marking scheme', 'instructions', 'paper setter', 'course objectives', 'course outcomes', 'programme outcomes', 'mapping', 'scale', 'low', 'medium', 'high', 'unit', 'textbook', 'reference', 'l', 'p', 'c', 'lecture', 'practical', 'credits', 'eae', 'oae', 'pce', 'icb', 'fsd', 'ml']
    
    # Check first 80 lines more carefully
    for i, line in enumerate(lines[:80]):
        line_clean = line.strip()
        
        # Skip empty lines, very short lines, and metadata lines
        if len(line_clean) < 8:
            continue
            
        # Skip lines that are clearly not course titles
        line_lower = line_clean.lower()
        if any(skip_kw in line_lower for skip_kw in skip_keywords):
            continue
            
        # Skip lines that are just course codes or numbers
        if re.match(r'^[A-Z]{2,4}-\d{3}[TP]', line_clean) or re.match(r'^\d+$', line_clean):
            continue
        
        # Skip table headers and metadata
        if re.match(r'^(UNIT|Course|Subject|Paper|Discipline|EAE|OAE|PCE|ICB)', line_clean, re.IGNORECASE):
            continue
        
        # Skip lines that look like table rows (contain patterns like "6 PCE PCE-1")
        if re.search(r'\d+\s+[A-Z/]+\s+\d+\s+[A-Z]+\s+[A-Z]+-', line_clean):
            continue
        
        # Look for meaningful course title (multiple words, capitalized)
        if len(line_clean.split()) >= 2 and len(line_clean) > 10:
            # Check if it looks like a course title (has relevant keywords)
            title_keywords = [
                'programming', 'engineering', 'science', 'technology', 'design', 
                'system', 'management', 'analysis', 'java', 'python', 'data',
                'database', 'network', 'web', 'software', 'algorithm', 'structure',
                'advanced', 'introduction', 'fundamentals', 'principles', 'computer',
                'information', 'communication', 'electronics', 'electrical', 'mechanical',
                'artificial', 'intelligence', 'machine', 'learning', 'deep', 'neural',
                'servlet', 'jsp', 'bean', 'application', 'development'
            ]
            
            # Check if line contains course title keywords
            if any(keyword in line_lower for keyword in title_keywords):
                # Additional validation: should not contain slashes in the middle (table rows)
                if '/' not in line_clean or line_clean.count('/') < 2:
                    # Should not start with department codes
                    if not re.match(r'^(CSE|IT|ECE|EE|ME|CST|ITE|EAE|OAE)[/\s]', line_clean):
                        main_course_title = line_clean
                        print(f"📖 Found main course title at line {i}: {main_course_title}")
                        break
    
    # If still not found, look for the largest capitalized title (likely the course name)
    if not main_course_title:
        potential_titles = []
        for i, line in enumerate(lines[:60]):
            line_clean = line.strip()
            # Look for capitalized titles
            if (len(line_clean) > 12 and 
                len(line_clean.split()) >= 2 and
                line_clean[0].isupper() and
                not any(skip_kw in line_clean.lower() for skip_kw in skip_keywords) and
                not re.match(r'^[A-Z]{2,4}-\d{3}[TP]', line_clean) and
                '/' not in line_clean):
                potential_titles.append((i, line_clean))
        
        # Use the first substantial capitalized title
        if potential_titles:
            main_course_title = potential_titles[0][1]
            print(f"📖 Using potential title: {main_course_title}")
    
    # Last resort: Search the full text for common patterns
    if not main_course_title:
        # Try to find "Advanced [Something] Programming" pattern
        title_patterns = [
            r'(Advanced\s+[A-Za-z\s]+Programming)',
            r'([A-Za-z\s]+Programming(?:\s+Lab)?)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',  # Three capitalized words
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text[:1000], re.IGNORECASE)  # Check first 1000 chars
            if match:
                candidate = match.group(1).strip()
                if len(candidate.split()) >= 2 and len(candidate) > 10:
                    # Make sure it's not a skip keyword
                    if not any(skip_kw in candidate.lower() for skip_kw in skip_keywords):
                        main_course_title = candidate
                        print(f"📖 Found title via pattern matching: {main_course_title}")
                        break
    
    # Look for course code patterns (e.g., CIE-306T, FSD-318T, OSD-453T)
    course_code_pattern = r'([A-Z]{2,4}-\d{3}[TP])'
    
    current_course = None
    current_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line contains a course code
        code_match = re.search(course_code_pattern, line.upper())
        
        if code_match:
            # Save previous course if exists
            if current_course and current_content:
                current_course['content'] = '\n'.join(current_content).strip()
                courses.append(current_course)
            
            # Start new course
            course_code = code_match.group(1)
            
            # Skip lab/practical courses (ending with 'P')
            # Only process theory courses (ending with 'T')
            if course_code.endswith('P'):
                print(f"⏭️  Skipping lab/practical course: {course_code}")
                current_course = None
                current_content = []
                i += 1
                continue
            
            # Try to extract course name
            course_name = None
            
            # Priority 1: Use main course title if found and we haven't used it yet
            if main_course_title and not any(c['course_name'] == main_course_title for c in courses):
                course_name = main_course_title
            else:
                # Priority 2: Look before and after for course name
                for offset in [-2, -1, 0, 1, 2, 3]:
                    idx = i + offset
                    if 0 <= idx < len(lines):
                        potential_name = lines[idx].strip()
                        # Skip empty lines, course codes, and metadata lines
                        if (len(potential_name) > 10 and 
                            course_code not in potential_name and
                            not re.match(r'^[A-Z]{2,4}-\d{3}[TP]', potential_name) and
                            not re.match(r'^(UNIT|Discipline|Semester|Group|Paper|Course|Subject)', potential_name, re.IGNORECASE) and
                            len(potential_name.split()) >= 2):
                            # Check if it looks like a course name
                            if any(word in potential_name.lower() for word in [
                                'programming', 'engineering', 'science', 'technology', 'design', 
                                'system', 'management', 'analysis', 'java', 'python', 'data',
                                'database', 'network', 'web', 'software', 'algorithm'
                            ]) or main_course_title:
                                course_name = potential_name
                                break
                
                # Priority 3: Try to extract from the same line
                if not course_name:
                    # Remove course code from line
                    name_part = re.sub(course_code_pattern, '', line, flags=re.IGNORECASE).strip()
                    # Clean up common prefixes
                    name_part = re.sub(r'^(Course|Subject|Paper)[:\s]*', '', name_part, flags=re.IGNORECASE)
                    if len(name_part) > 5:
                        course_name = name_part
                    else:
                        course_name = main_course_title or "Unknown Course"
            
            # Extract credits (look for pattern like "Credits: 3" or "C: 3" or in table format)
            credits = 3  # default
            credits_match = re.search(r'(?:Credits?|C)[:\s]*(\d+)', line, re.IGNORECASE)
            if credits_match:
                credits = int(credits_match.group(1))
            else:
                # Look in nearby lines for credits table
                for offset in [-2, -1, 1, 2]:
                    idx = i + offset
                    if 0 <= idx < len(lines):
                        credits_match = re.search(r'(?:Credits?|C)[:\s]*(\d+)', lines[idx], re.IGNORECASE)
                        if credits_match:
                            credits = int(credits_match.group(1))
                            break
            
            current_course = {
                'course_code': course_code,
                'course_name': course_name,
                'credits': credits,
                'content': ''
            }
            current_content = [line]
        elif current_course:
            # Continue collecting content for current course
            current_content.append(line)
            
            # Stop at next course code or major section break
            if (re.search(course_code_pattern, line.upper()) or
                (line.startswith('UNIT-') or line.startswith('UNIT ')) and len(current_content) > 5):
                # Don't stop yet, continue collecting
                pass
        
        i += 1
    
    # Save last course
    if current_course and current_content:
        current_course['content'] = '\n'.join(current_content).strip()
        courses.append(current_course)
    
    # Post-process: Update all courses to use main_course_title if available and their names are poor
    # Also filter out any lab/practical courses that might have been added
    filtered_courses = []
    if main_course_title:
        for course in courses:
            # Skip lab/practical courses (ending with 'P')
            if course.get('course_code', '').endswith('P'):
                print(f"⏭️  Filtering out lab/practical course: {course.get('course_code')}")
                continue
            
            current_name = course.get('course_name', '')
            # If course name looks like metadata (contains slashes, numbers, or is too short)
            if (len(current_name) < 15 or 
                '/' in current_name or 
                re.search(r'\d+\s+[A-Z]+', current_name) or  # Contains patterns like "6 PCE"
                current_name == "Unknown Course" or
                re.match(r'^[A-Z/]+\s+\d+', current_name)):  # Matches patterns like "CSE/IT/CST/ITE 6"
                course['course_name'] = main_course_title
                print(f"📝 Updated course {course['course_code']} name from '{current_name}' to '{main_course_title}'")
            
            filtered_courses.append(course)
    else:
        # Still filter out lab courses even if no main title
        filtered_courses = [c for c in courses if not c.get('course_code', '').endswith('P')]
    
    courses = filtered_courses
    
    # Remove any lab/practical content from theory course content
    # Look for lab sections and remove them
    for course in courses:
        content = course.get('content', '')
        if content:
            # Remove lab/practical sections
            # Look for patterns like "Lab", "Practical", "CIE-XXXP", etc.
            lines = content.split('\n')
            cleaned_lines = []
            skip_lab_section = False
            
            for line in lines:
                line_lower = line.lower()
                # Check if we hit a lab section marker
                if any(marker in line_lower for marker in [
                    ' lab', 'laboratory', 'practical', 'practical component',
                    'lab syllabus', 'practical syllabus', 'lab list', 'practical list',
                    'practical list shall be notified', 'atleast 10 experiments',
                    'atleast 5 experiments', 'experiments must be performed'
                ]) or re.search(r'[A-Z]{2,4}-\d{3}P', line):
                    skip_lab_section = True
                    continue
                
                # Check if we hit a new theory section (stops skipping)
                if skip_lab_section and (
                    re.search(r'UNIT[- ]?[IVX\d]+', line, re.IGNORECASE) or
                    'textbook' in line_lower or 'reference' in line_lower or
                    'course objectives' in line_lower or 'course outcomes' in line_lower
                ):
                    skip_lab_section = False
                
                # Also skip lines that mention lab/practical in instructions
                if 'practical component' in line_lower or 'lab component' in line_lower:
                    continue
                
                if not skip_lab_section:
                    cleaned_lines.append(line)
            
            course['content'] = '\n'.join(cleaned_lines).strip()
    
    # If no courses found with course codes, try alternative parsing
    if not courses:
        # Try to find course information by looking for unit sections
        # This handles cases where the PDF structure is different
        unit_pattern = r'UNIT[- ]?[IVX\d]+[:]?'
        units = re.finditer(unit_pattern, text, re.IGNORECASE)
        
        if units:
            # Extract everything as a single course
            course_name = department + " Syllabus"
            course_code = department.upper() + "-" + semester + "XX"
            
            courses.append({
                'course_code': course_code,
                'course_name': course_name,
                'credits': 3,
                'content': text.strip()
            })
    
    return courses

@router.get("/search")
async def search_syllabus(query: str = Query(..., description="Search term for course name or code")):
    """Search syllabus by course name or code"""
    try:
        results = db.search_syllabus(query)
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        print(f"❌ Error searching syllabus: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching syllabus: {str(e)}")

@router.get("/course/{course_code}")
async def get_syllabus_by_code(course_code: str):
    """Get syllabus by course code"""
    try:
        results = db.get_syllabus_by_course_code(course_code)
        if not results:
            raise HTTPException(status_code=404, detail=f"No syllabus found for course code: {course_code}")
        
        return {
            "success": True,
            "course_code": course_code,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting syllabus by code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting syllabus: {str(e)}")

@router.get("/semester/{semester}")
async def get_semester_syllabus(semester: str):
    """Get all courses for a semester"""
    try:
        results = db.get_syllabus_by_semester(semester)
        return {
            "success": True,
            "semester": semester,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        print(f"❌ Error getting semester syllabus: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting semester syllabus: {str(e)}")

@router.get("/department/{department}")
async def get_department_syllabus(department: str):
    """Get all courses for a department"""
    try:
        results = db.get_syllabus_by_department(department)
        return {
            "success": True,
            "department": department,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        print(f"❌ Error getting department syllabus: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting department syllabus: {str(e)}")

