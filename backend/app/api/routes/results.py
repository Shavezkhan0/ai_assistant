from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from app.database.postgres_db import get_db
from app.models.database_models import StudentResult
from app.services.document_processor import DocumentProcessor
from sqlalchemy.orm import Session
from typing import Optional
import re

router = APIRouter(tags=["results"])

# Initialize document processor
doc_processor = DocumentProcessor()

class AddResultRequest(BaseModel):
    studentId: str  # Enrollment number
    studentName: Optional[str] = None  # Optional, can be added later
    semester: str
    course: str  # Subject name
    grade: str
    credits: Optional[int] = 4
    marks: Optional[float] = None  # Optional, can be calculated from grade

@router.post("/upload")
async def upload_results(
    file: UploadFile = File(...), 
    semester: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload results PDF and extract student data (semester-wise)"""
    try:
        # Validate file
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Extract text from PDF
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            if not content or len(content) == 0:
                raise HTTPException(status_code=400, detail="File is empty")
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            text_content = doc_processor.extract_text_from_pdf(tmp_path)
            
            if not text_content or len(text_content.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract enough text from PDF. Make sure it's not scanned/image-based."
                )
            
            # Parse results from text (pass semester if provided)
            students_processed = parse_results_from_text(text_content, db, semester=semester)
            
            return {
                "success": True,
                "message": f"Results uploaded successfully. Processed {students_processed} student(s).",
                "students_processed": students_processed,
                "semester": semester or "auto-detected"
            }
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Upload results error: {error_msg}")
        traceback.print_exc()
        # Provide more specific error messages
        if "filename" in error_msg.lower() or "file" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"File error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {error_msg}")


def parse_results_from_text(text: str, db: Session, semester: Optional[str] = None) -> int:
    """Parse student results from extracted text - handles multiple students, semester-wise"""
    students_processed = 0
    all_students = []
    
    # Try to detect semester from text if not provided
    if not semester:
        semester = detect_semester_from_text(text)
        if semester:
            print(f"📅 Detected semester: {semester}")
        else:
            semester = "1"  # Default
            print(f"⚠️  Could not detect semester, using default: {semester}")
    else:
        print(f"📅 Using provided semester: {semester}")
    
    # Multiple patterns for enrollment number - catch all variations (10-11 digits)
    # PDF format: Enrollment numbers can be 10 or 11 digits
    enrollment_patterns = [
        r'\b(\d{11})\b',  # Standard 11-digit pattern
        r'\b(\d{10})\b',  # 10-digit pattern (e.g., 2022279049)
        r'(?:Enrollment\s*No\.?\s*:?\s*)?(\d{10,11})',  # With "Enrollment No:" prefix
        r'(?:Enrolment\s*No\.?\s*:?\s*)?(\d{10,11})',  # Alternative spelling
        r'(?:Roll\s*No\.?\s*:?\s*)?(\d{10,11})',  # With "Roll No:" prefix
        r'(\d{3}\d{8})',  # Pattern like 00214802722 (3 digits + 8 digits = 11)
        r'(\d{2}\d{8})',  # Pattern like 20127202722 (2 digits + 9 digits = 11)
        r'(\d{10,11})',  # Any 10-11 consecutive digits (fallback)
    ]
    
    # Find all enrollment numbers with their positions using multiple patterns
    enrollments_with_pos = []
    seen_enrollments = set()  # Avoid duplicates
    
    for pattern in enrollment_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            enrollment = match.group(1) if match.groups() else match.group(0)
            # Validate it's 10 or 11 digits (enrollment numbers)
            if len(enrollment) >= 10 and len(enrollment) <= 11 and enrollment.isdigit():
                # Normalize to 11 digits by padding with leading zero if needed
                if len(enrollment) == 10:
                    enrollment = '0' + enrollment  # Pad to 11 digits
                
                if enrollment not in seen_enrollments:
                    enrollments_with_pos.append((enrollment, match.start()))
                    seen_enrollments.add(enrollment)
    
    # Sort by position to maintain order
    enrollments_with_pos.sort(key=lambda x: x[1])
    
    if not enrollments_with_pos:
        print("⚠️  No enrollment numbers found in PDF")
        return 0
    
    print(f"📊 Found {len(enrollments_with_pos)} enrollment number(s) in PDF")
    
    # Debug: Check for specific enrollment numbers
    test_enrollments = ['00114802722', '00214802722', '00414802722', '00614802722', '01114802722', '01414807220', '00413207223']
    found_test = [e for e in test_enrollments if e in seen_enrollments]
    missing_test = [e for e in test_enrollments if e not in seen_enrollments]
    if found_test:
        print(f"✅ Test enrollments found: {', '.join(found_test)}")
    if missing_test:
        print(f"⚠️  Test enrollments missing: {', '.join(missing_test)}")
    
    print(f"⏱️  Estimated time: ~{len(enrollments_with_pos) * 0.5:.0f} seconds ({len(enrollments_with_pos) * 0.5 / 60:.1f} minutes)")
    print(f"🚀 Starting optimized batch processing...\n")
    
    # Process each enrollment
    for i, (enrollment, enrollment_pos) in enumerate(enrollments_with_pos):
        # Show progress every 50 students or for first/last, or for specific test enrollments
        is_test_enrollment = enrollment in ['00413207223', '00114802722', '00214802722', '00414802722', '01114802722']
        if (i + 1) % 50 == 0 or i == 0 or i == len(enrollments_with_pos) - 1 or is_test_enrollment:
            progress_pct = ((i + 1) / len(enrollments_with_pos)) * 100
            print(f"\n🔍 Processing student {i+1}/{len(enrollments_with_pos)} ({progress_pct:.1f}%) - Enrollment: {enrollment}")
        else:
            print(f"\n🔍 Processing enrollment: {enrollment}")
        
        # Determine context boundaries - IMPORTANT: IPU uses TABULAR format
        # Multiple students appear on same page in columns, so we need larger context
        # Start: previous enrollment or beginning of text
        if i > 0:
            # In tabular format, students share the same page, so don't skip too much
            prev_pos = enrollments_with_pos[i-1][1]
            # Only skip if enrollments are far apart (different pages)
            if enrollment_pos - prev_pos > 5000:
                context_start = prev_pos + 2000  # Different page, skip more
            else:
                context_start = max(0, prev_pos - 500)  # Same page, include more context
        else:
            context_start = max(0, enrollment_pos - 1000)  # More context at start
        
        # End: next enrollment or end of text
        # In tabular format, subjects appear AFTER all students, so need larger window
        if i < len(enrollments_with_pos) - 1:
            next_pos = enrollments_with_pos[i+1][1]
            # If next enrollment is close (same page), include it for subject extraction
            if next_pos - enrollment_pos < 5000:
                context_end = min(len(text), next_pos + 2000)  # Include next student's area
            else:
                context_end = min(len(text), enrollment_pos + 5000)  # Different page, larger window
        else:
            context_end = min(len(text), enrollment_pos + 5000)  # Much more context for last student
        
        context = text[context_start:context_end]
        
        # Extract student details from context
        # PDF format: Enrollment number is ALWAYS on top, then name below it
        # Format:
        #   00413207223          <- Enrollment (top line)
        #   MOHD NADEEM ANSARI    <- Name (next line)
        #   SID: 190000139685
        #   SchemeID: 190272021002
        student_name = None
        
        lines = context.split('\n')
        enrollment_line_idx = -1
        
        # Find the line containing enrollment number
        for idx, line in enumerate(lines):
            if enrollment in line:
                enrollment_line_idx = idx
                break
        
        if enrollment_line_idx >= 0:
            # Pattern 1: Name on the line IMMEDIATELY after enrollment (most common)
            if enrollment_line_idx + 1 < len(lines):
                next_line = lines[enrollment_line_idx + 1].strip()
                # Check if it looks like a name (starts with uppercase, 1-5 words, all caps or mixed)
                if re.match(r'^[A-Z][A-Za-z\s]{2,50}$', next_line):
                    words = next_line.split()
                    excluded = ['SID', 'SCHEME', 'OF', 'EXAMINATION', 'RESULT', 'STUDENT', 'NAME', 'ENROLLMENT', 'PROGRAMME', 'BRANCH', 'INSTITUTE', 'INSTITUTION', 'SCHEMEID']
                    # Check if it's not an excluded word and has valid name structure
                    if (1 <= len(words) <= 5 and 
                        not any(w.upper() in excluded for w in words) and
                        len(next_line) > 3):
                        student_name = next_line
                        student_name = re.sub(r'\s+', ' ', student_name)  # Normalize spaces
            
            # Pattern 2: Name on same line as enrollment (if they're together)
            if not student_name:
                enrollment_line = lines[enrollment_line_idx]
                # Look for name after enrollment on same line
                # Format: "00413207223 MOHD NADEEM ANSARI"
                name_pattern2 = rf'{re.escape(enrollment)}\s+([A-Z][A-Za-z\s]{2,50}?)(?:\s+SID|\s+SchemeID|$)'
                name_match = re.search(name_pattern2, enrollment_line, re.MULTILINE)
                if name_match:
                    candidate_name = name_match.group(1).strip()
                    candidate_name = re.sub(r'\s+', ' ', candidate_name)
                    words = candidate_name.split()
                    excluded = ['SID', 'SCHEME', 'OF', 'EXAMINATION', 'RESULT', 'STUDENT', 'NAME', 'ENROLLMENT', 'PROGRAMME', 'BRANCH', 'INSTITUTE', 'INSTITUTION']
                    if len(candidate_name) > 3 and 1 <= len(words) <= 5 and not any(w.upper() in excluded for w in words):
                        student_name = candidate_name
            
            # Pattern 3: Name before SID or SchemeID (if name extraction from line 2 failed)
            if not student_name:
                # Look in the enrollment line area for SID/SchemeID, name should be before it
                for line_idx in range(max(0, enrollment_line_idx), min(enrollment_line_idx + 3, len(lines))):
                    line = lines[line_idx]
                    name_pattern3 = r'([A-Z][A-Za-z\s]{2,50}?)\s+(?:SID|SchemeID)[:\s]'
                    name_match = re.search(name_pattern3, line)
                    if name_match:
                        candidate_name = name_match.group(1).strip()
                        candidate_name = re.sub(r'\s+', ' ', candidate_name)
                        words = candidate_name.split()
                        excluded = ['SCHEME', 'OF', 'EXAMINATION', 'RESULT', 'STUDENT', 'NAME', 'ENROLLMENT', 'PROGRAMME', 'BRANCH', 'INSTITUTE', 'INSTITUTION']
                        if len(candidate_name) > 3 and 1 <= len(words) <= 5 and not any(w.upper() in excluded for w in words):
                            student_name = candidate_name
                            break
        
        if not student_name:
            student_name = f"Student_{enrollment}"
        
        # Extract programme
        programme_patterns = [
            r'(?:Programme|Program)[:\s]+([A-Za-z\s\(\)\.]+?)(?:\n|Branch|Institute|$)',
            r'Bachelor of ([A-Za-z\s]+)',
        ]
        programme = None
        for pattern in programme_patterns:
            prog_match = re.search(pattern, context, re.IGNORECASE)
            if prog_match:
                programme = prog_match.group(1).strip()
                if programme:
                    break
        
        # Extract branch
        branch_patterns = [
            r'(?:Branch|Department|Discipline)[:\s]+([A-Za-z\s&,]+?)(?:\n|Institute|Programme|$)',
        ]
        branch = None
        for pattern in branch_patterns:
            branch_match = re.search(pattern, context, re.IGNORECASE)
            if branch_match:
                branch = branch_match.group(1).strip()
                if branch:
                    break
        
        # Extract institute - look in header section of PDF
        institute = None
        # Check header section (first 20k chars) for institute name
        header_section = text[:min(len(text), 20000)]
        
        # Pattern 1: "Institution: NAME" or "Institution Code: XXX Institution: NAME"
        institute_patterns = [
            r'Institution\s*Code[:\s]*\d+\s+Institution[:\s]+([A-Z][A-Za-z\s\.]+?)(?:\n|Programme|Scheme|$)',
            r'Institution[:\s]+([A-Z][A-Za-z\s\.]+?)(?:\n|Programme|Scheme|Code|$)',
            r'Institute[:\s]+([A-Z][A-Za-z\s\.]+?)(?:\n|Programme|Scheme|Code|$)',
        ]
        for pattern in institute_patterns:
            inst_match = re.search(pattern, header_section, re.IGNORECASE | re.MULTILINE)
            if inst_match:
                institute = inst_match.group(1).strip()
                institute = re.sub(r'\s+', ' ', institute)
                if len(institute) > 5:  # Valid institute name
                    break
        
        # Use provided semester or try to extract from context
        student_semester = semester  # Use the semester parameter (from form or detected)
        
        # Try to extract semester from this specific student's context if not provided
        if not semester or semester == "1":
            semester_pattern = r'(?:Semester|Sem)[:\s]*(\d+)'
            semester_match = re.search(semester_pattern, context, re.IGNORECASE)
            if semester_match:
                student_semester = semester_match.group(1)
        
        # Final fallback
        if not student_semester:
            student_semester = "1"
        
        # Extract subject results based on ACTUAL PDF structure
        # Format: PaperID(Credits)    Internal    External    Total(Grade)
        # Example: 027302(3)    23   57    80(A+)
        #         096302(1)    35   53    88(A+)
        subjects = []
        
        # Extract subject code (Paper ID) to name mapping from scheme section
        scheme_section = text[:min(len(text), 100000)]  # First 100k chars usually contain scheme
        subject_code_map = {}
        
        # Pattern 1: Extract Paper ID and Subject Name from scheme table
        # Format: "S.No. Paper ID Code Subject Credit Type..."
        scheme_pattern1 = r'\d+\s+(\d{6})\s+[A-Z0-9]+\s+([A-Z][A-Za-z0-9\s&,\(\)\/\-\.]{5,120}?)(?:\s+\d+\s+(?:THEORY|PRACTICAL|COMPULSORY)|$)'
        scheme_matches1 = re.findall(scheme_pattern1, scheme_section, re.MULTILINE)
        for match in scheme_matches1:
            paper_id = match[0]
            subject_name = match[1].strip()
            subject_name = re.sub(r'\s+', ' ', subject_name)
            subject_name = re.sub(r'\s+\d+\s*$', '', subject_name)
            subject_name = re.sub(r'\s+(?:THEORY|PRACTICAL|COMPULSORY|MANDATORY|DROPPABLE)\s*$', '', subject_name, flags=re.IGNORECASE)
            if paper_id not in subject_code_map and len(subject_name) > 5:
                subject_code_map[paper_id] = subject_name
        
        # Pattern 2: Alternative format - "Paper ID Subject"
        scheme_pattern2 = r'(\d{6})\s+([A-Z][A-Za-z0-9\s&,\(\)\/\-\.]{5,120}?)(?:\s+\d+\s+(?:THEORY|PRACTICAL)|$)'
        scheme_matches2 = re.findall(scheme_pattern2, scheme_section, re.MULTILINE)
        for match in scheme_matches2:
            paper_id = match[0]
            subject_name = match[1].strip()
            subject_name = re.sub(r'\s+', ' ', subject_name)
            subject_name = re.sub(r'\s+\d+\s*$', '', subject_name)
            subject_name = re.sub(r'\s+(?:THEORY|PRACTICAL|COMPULSORY|MANDATORY|DROPPABLE)\s*$', '', subject_name, flags=re.IGNORECASE)
            if paper_id not in subject_code_map and len(subject_name) > 5:
                subject_code_map[paper_id] = subject_name
        
        # Pattern 3: Look for Paper ID followed by subject name
        scheme_pattern3 = r'(\d{6})\s+([A-Z][A-Z][A-Za-z0-9\s&,\(\)\/\-\.]{3,120}?)(?:\s+\d|$)'
        scheme_matches3 = re.findall(scheme_pattern3, scheme_section, re.MULTILINE)
        for match in scheme_matches3:
            paper_id = match[0]
            subject_name = match[1].strip()
            subject_name = re.sub(r'\s+', ' ', subject_name)
            if paper_id not in subject_code_map and len(subject_name) > 5 and re.match(r'^[A-Z]', subject_name):
                subject_code_map[paper_id] = subject_name
        
        print(f"📚 Extracted {len(subject_code_map)} subject mappings from scheme")
        
        # Extract subjects from student's context using ACTUAL PDF format
        # Format: 027302(3)    23   57    80(A+)
        # Pattern: PaperID(Credits)    Internal    External    Total(Grade)
        # The pattern needs to handle:
        # - PaperID(credits) followed by internal marks (optional), external marks, total marks(grade)
        # - Internal marks may be missing (shown as "-")
        # - Multiple spaces between values
        
        # Primary pattern: PaperID(Credits)    Internal    External    Total(Grade)
        # This matches: 027302(3)    23   57    80(A+)
        # Note: In tabular format, spacing can vary significantly
        # Pattern must handle: multiple spaces, tabs, and line breaks
        subject_pattern = r'(\d{6})\((\d+)\)\s+(?:(\d+|-)\s+)?(\d+)\s+(\d{1,3})\(([A-Z\+\-]+)\)'
        
        # Also try pattern without internal marks: PaperID(Credits)    External    Total(Grade)
        # This matches: 096302(1)    35   53    88(A+)
        subject_pattern2 = r'(\d{6})\((\d+)\)\s+(\d+)\s+(\d{1,3})\(([A-Z\+\-]+)\)'
        
        # Pattern 3: More flexible - handles cases where marks might be on separate lines
        # Matches: 027302(3) followed by marks anywhere in next 200 chars
        subject_pattern3 = r'(\d{6})\((\d+)\)(?:\s+[-\d]+\s+)*(\d{1,3})\(([A-Z\+\-]+)\)'
        
        # Find all subject matches in the context
        # IMPORTANT: In IPU tabular format, subjects appear AFTER all student names
        # In tabular format: Students are in columns, subjects/marks are in rows below
        # So subjects might be far from the enrollment number
        enrollment_pos_in_context = context.find(enrollment)
        if enrollment_pos_in_context >= 0:
            # Strategy 1: Search in area after enrollment (for non-tabular pages)
            search_start = enrollment_pos_in_context
            search_end = min(len(context), enrollment_pos_in_context + 4000)
            student_section = context[search_start:search_end]
            
            # Strategy 2: Also search entire context for tabular format
            # In tabular format, subjects appear in a table below all students
            # So we need to search the full context window
            full_context_section = context  # Use entire context for tabular format
            
            # Normalize whitespace but preserve structure for better matching
            # Replace multiple spaces/tabs with single space, but keep newlines
            student_section_normalized = re.sub(r'[ \t]+', ' ', student_section)
            student_section_normalized = re.sub(r'\n\s*\n', '\n', student_section_normalized)
            
            # Also normalize full context for tabular format search
            full_context_normalized = re.sub(r'[ \t]+', ' ', full_context_section)
            full_context_normalized = re.sub(r'\n\s*\n', '\n', full_context_normalized)
            
            # Try primary pattern first in student section (with MULTILINE flag to handle line breaks)
            matches = re.finditer(subject_pattern, student_section_normalized, re.MULTILINE)
            for match in matches:
                paper_id = match.group(1)
                credits = match.group(2)
                internal = match.group(3) if match.group(3) and match.group(3) != '-' else '0'
                external = match.group(4)
                total = match.group(5)
                grade = match.group(6)
                
                # Get subject name from scheme mapping
                subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                
                # Validate grade
                valid_grades = ['O', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'P']
                if grade in valid_grades or '+' in grade or '-' in grade:
                    try:
                        total_marks = float(total)
                        internal_marks_float = float(internal) if internal and internal != '-' else 0.0
                        external_marks_float = float(external) if external else 0.0
                        credits_int = int(credits) if credits else 0
                        if 0 <= total_marks <= 100:
                            # Store as dict with all fields: paper_id, subject_name, credits, internal, external, total, grade
                            subjects.append({
                                'paper_id': paper_id,
                                'subject_name': subject_name,
                                'credits': credits_int,
                                'internal_marks': internal_marks_float,
                                'external_marks': external_marks_float,
                                'total_marks': total_marks,
                                'grade': grade
                            })
                    except ValueError:
                        pass
            
            # If no matches in student section, try full context (for tabular format)
            if not subjects:
                matches_full = re.finditer(subject_pattern, full_context_normalized, re.MULTILINE)
                for match in matches_full:
                    paper_id = match.group(1)
                    credits = match.group(2)
                    internal = match.group(3) if match.group(3) and match.group(3) != '-' else '0'
                    external = match.group(4)
                    total = match.group(5)
                    grade = match.group(6)
                    
                    subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                    
                    valid_grades = ['O', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'P']
                    if grade in valid_grades or '+' in grade or '-' in grade:
                        try:
                            total_marks = float(total)
                            internal_marks_float = float(internal) if internal and internal != '-' else 0.0
                            external_marks_float = float(external) if external else 0.0
                            credits_int = int(credits) if credits else 0
                            if 0 <= total_marks <= 100:
                                subjects.append({
                                    'paper_id': paper_id,
                                    'subject_name': subject_name,
                                    'credits': credits_int,
                                    'internal_marks': internal_marks_float,
                                    'external_marks': external_marks_float,
                                    'total_marks': total_marks,
                                    'grade': grade
                                })
                        except ValueError:
                            pass
            
            # If no matches with primary pattern, try pattern 2 (without internal)
            if not subjects:
                matches2 = re.finditer(subject_pattern2, student_section_normalized, re.MULTILINE)
                for match in matches2:
                    paper_id = match.group(1)
                    credits = match.group(2)
                    external = match.group(3)
                    total = match.group(4)
                    grade = match.group(5)
                    
                    subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                    
                    valid_grades = ['O', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'P']
                    if grade in valid_grades or '+' in grade or '-' in grade:
                        try:
                            total_marks = float(total)
                            internal_marks_float = 0.0  # Pattern 2 doesn't have internal
                            external_marks_float = float(external) if external else 0.0
                            credits_int = int(credits) if credits else 0
                            if 0 <= total_marks <= 100:
                                subjects.append({
                                    'paper_id': paper_id,
                                    'subject_name': subject_name,
                                    'credits': credits_int,
                                    'internal_marks': internal_marks_float,
                                    'external_marks': external_marks_float,
                                    'total_marks': total_marks,
                                    'grade': grade
                                })
                        except ValueError:
                            pass
            
            # If pattern 2 fails in student section, try full context
            if not subjects:
                matches2_full = re.finditer(subject_pattern2, full_context_normalized, re.MULTILINE)
                for match in matches2_full:
                    paper_id = match.group(1)
                    credits = match.group(2)
                    external = match.group(3)
                    total = match.group(4)
                    grade = match.group(5)
                    
                    subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                    
                    valid_grades = ['O', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'P']
                    if grade in valid_grades or '+' in grade or '-' in grade:
                        try:
                            total_marks = float(total)
                            internal_marks_float = 0.0  # Pattern 2 doesn't have internal
                            external_marks_float = float(external) if external else 0.0
                            credits_int = int(credits) if credits else 0
                            if 0 <= total_marks <= 100:
                                subjects.append({
                                    'paper_id': paper_id,
                                    'subject_name': subject_name,
                                    'credits': credits_int,
                                    'internal_marks': internal_marks_float,
                                    'external_marks': external_marks_float,
                                    'total_marks': total_marks,
                                    'grade': grade
                                })
                        except ValueError:
                            pass
            
            # Pattern 3: More flexible - handles tabular format where marks might be separated
            if not subjects:
                matches3 = re.finditer(subject_pattern3, student_section_normalized, re.MULTILINE | re.DOTALL)
                for match in matches3:
                    paper_id = match.group(1)
                    credits = match.group(2)
                    total = match.group(3)
                    grade = match.group(4)
                    
                    subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                    
                    valid_grades = ['O', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'E', 'F', 'P']
                    if grade in valid_grades or '+' in grade or '-' in grade:
                        try:
                            total_marks = float(total)
                            internal_marks_float = 0.0  # Pattern 2 doesn't have internal
                            external_marks_float = float(external) if external else 0.0
                            credits_int = int(credits) if credits else 0
                            if 0 <= total_marks <= 100:
                                subjects.append({
                                    'paper_id': paper_id,
                                    'subject_name': subject_name,
                                    'credits': credits_int,
                                    'internal_marks': internal_marks_float,
                                    'external_marks': external_marks_float,
                                    'total_marks': total_marks,
                                    'grade': grade
                                })
                        except ValueError:
                            pass
            
            # Fallback: Try simpler pattern if still no matches
            # Pattern: PaperID(Credits) followed by numbers and grade (more flexible)
            if not subjects:
                fallback_pattern = r'(\d{6})\((\d+)\)\s+.*?(\d{1,3})\(([A-Z\+\-]+)\)'
                fallback_matches = re.finditer(fallback_pattern, student_section_normalized, re.MULTILINE | re.DOTALL)
                for match in fallback_matches:
                    paper_id = match.group(1)
                    credits = match.group(2)
                    total = match.group(3)
                    grade = match.group(4)
                    
                    subject_name = subject_code_map.get(paper_id, f"SUBJECT_{paper_id}")
                    
                    try:
                        total_marks = float(total)
                        internal_marks_float = 0.0  # Fallback pattern doesn't extract internal/external
                        external_marks_float = 0.0
                        credits_int = int(credits) if credits else 0
                        if 0 <= total_marks <= 100:
                            subjects.append({
                                'paper_id': paper_id,
                                'subject_name': subject_name,
                                'credits': credits_int,
                                'internal_marks': internal_marks_float,
                                'external_marks': external_marks_float,
                                'total_marks': total_marks,
                                'grade': grade
                            })
                    except ValueError:
                        pass
            
            # Debug output for test enrollments
            is_test_enrollment = enrollment in ['00413207223', '00114802722', '00214802722', '00414802722', '01114802722']
            if is_test_enrollment and len(subjects) == 0:
                print(f"   🔍 DEBUG for {enrollment}: No subjects found with patterns")
                print(f"   📄 Student section preview (first 800 chars):")
                print(f"   {student_section_normalized[:800]}")
                print(f"   📋 Available paper IDs in student section: {re.findall(r'(\d{6})\(', student_section_normalized[:800])}")
                print(f"   📋 Available paper IDs in full context: {len(re.findall(r'(\d{6})\(', full_context_normalized))} found")
                # Show a sample of full context where subjects might be
                subject_areas = re.finditer(r'(\d{6})\(', full_context_normalized)
                for i, area_match in enumerate(list(subject_areas)[:3]):  # Show first 3 subject areas
                    area_start = max(0, area_match.start() - 100)
                    area_end = min(len(full_context_normalized), area_match.start() + 200)
                    print(f"   📄 Subject area {i+1}: {full_context_normalized[area_start:area_end]}")
        
        # Deduplicate subjects (keep first occurrence) - now subjects are dicts
        seen_subjects = set()
        unique_subjects = []
        for subject_data in subjects:
            if isinstance(subject_data, dict):
                subject_name = subject_data.get('subject_name', '')
                subject_key = (subject_name.strip().upper(), student_semester)
                if subject_key not in seen_subjects:
                    seen_subjects.add(subject_key)
                    unique_subjects.append(subject_data)
            else:
                # Handle old tuple format for backward compatibility
                subject_name, marks_str, grade = subject_data
                subject_key = (subject_name.strip().upper(), student_semester)
                if subject_key not in seen_subjects:
                    seen_subjects.add(subject_key)
                    unique_subjects.append({
                        'paper_id': None,
                        'subject_name': subject_name,
                        'credits': 0,
                        'internal_marks': 0.0,
                        'external_marks': 0.0,
                        'total_marks': float(marks_str),
                        'grade': grade
                    })
        subjects = unique_subjects
        
        # Print details for progress milestones or test enrollments
        is_test_enrollment = enrollment in ['00413207223', '00114802722', '00214802722', '00414802722', '01114802722']
        if (i + 1) % 50 == 0 or i == 0 or is_test_enrollment:
            print(f"   Name: {student_name} | Subjects: {len(subjects)} (after deduplication)")
            if is_test_enrollment and len(subjects) == 0:
                print(f"   ⚠️  WARNING: No subjects extracted for test enrollment {enrollment}")
                print(f"   📄 Context preview (first 500 chars): {context[:500]}")
        
        # OPTIMIZATION: Fetch all existing records for this student in ONE query
        # Check for duplicates: same student_id, semester, AND subject
        try:
            existing_results = db.query(StudentResult).filter(
                StudentResult.student_id == enrollment,
                StudentResult.semester == student_semester
            ).all()
            # Create set of (subject, semester) tuples for duplicate checking
            existing_subjects = {(r.subject.upper().strip(), r.semester) for r in existing_results}
        except Exception as e:
            db.rollback()
            existing_subjects = set()
        
        # Save results to database for this student (batch processing)
        student_results_saved = 0
        new_results = []
        
        for subject_data in subjects:
            try:
                # Handle both dict and tuple formats
                if isinstance(subject_data, dict):
                    paper_id = subject_data.get('paper_id')
                    subject_name = subject_data.get('subject_name', '')
                    credits = subject_data.get('credits', 0)
                    internal_marks = subject_data.get('internal_marks', 0.0)
                    external_marks = subject_data.get('external_marks', 0.0)
                    total_marks = subject_data.get('total_marks', 0.0)
                    grade = subject_data.get('grade', '')
                else:
                    # Old tuple format for backward compatibility
                    subject_name, marks_str, grade = subject_data
                    paper_id = None
                    credits = 0
                    internal_marks = 0.0
                    external_marks = 0.0
                    total_marks = float(marks_str) if isinstance(marks_str, str) else marks_str
                
                # Normalize subject name for duplicate checking (case-insensitive, trimmed)
                subject_key = (subject_name.upper().strip(), student_semester)
                
                # Check if result already exists (using in-memory set - much faster!)
                if subject_key not in existing_subjects:
                    result = StudentResult(
                        student_id=enrollment,
                        student_name=student_name,
                        programme=programme,
                        branch=branch,
                        institute=institute,
                        subject=subject_name,  # Store original case
                        marks=total_marks,
                        grade=grade.upper(),
                        semester=student_semester,
                        paper_id=paper_id,  # Store paper ID
                        internal_marks=internal_marks,  # Store internal marks
                        external_marks=external_marks,  # Store external marks
                        credits=credits  # Store credits
                    )
                    new_results.append(result)
                    existing_subjects.add(subject_key)  # Track to avoid duplicates in same batch
                # Skip duplicates silently for speed
            except Exception as e:
                # Skip invalid subjects but continue processing
                print(f"   ⚠️  Error processing subject: {e}")
                continue
        
        # Bulk insert all new results for this student
        is_test_enrollment = enrollment in ['00413207223', '00114802722', '00214802722', '00414802722', '01114802722']
        if new_results:
            try:
                db.add_all(new_results)
                db.commit()
                student_results_saved = len(new_results)
                students_processed += 1
                if (i + 1) % 50 == 0 or is_test_enrollment:  # Progress update every 50 students or for test enrollments
                    print(f"   ✅ Saved {student_results_saved} result(s) | Progress: {i+1}/{len(enrollments_with_pos)} students")
                    if is_test_enrollment:
                        print(f"   📋 Subjects saved: {[r.subject for r in new_results]}")
                else:
                    print(f"   ✅ Saved {student_results_saved} result(s) for {student_name}")
            except Exception as e:
                db.rollback()
                print(f"   ❌ Error committing results for {student_name}: {e}")
                if is_test_enrollment:
                    import traceback
                    traceback.print_exc()
        else:
            if (i + 1) % 100 == 0 or is_test_enrollment:  # Progress update for skipped students too
                reason = "All duplicates" if len(subjects) > 0 else "No subjects extracted"
                print(f"   ⏭️  {reason} | Progress: {i+1}/{len(enrollments_with_pos)} students")
                if is_test_enrollment:
                    print(f"   🔍 Debug for {enrollment}: {len(subjects)} subjects extracted, {len(existing_results)} existing in DB")
    
    # Final summary
    if students_processed > 0:
        print(f"\n✅ Successfully processed {students_processed} student(s)")
    else:
        print(f"\n⚠️  No students were successfully processed")
    
    return students_processed


def detect_semester_from_text(text: str) -> Optional[str]:
    """Detect semester number from PDF text"""
    # Common patterns for semester
    patterns = [
        r'(?:Semester|Sem)[:\s]*(\d+)',
        r'Sem[.\s]*(\d+)',
        r'(\d+)(?:st|nd|rd|th)\s+Semester',
        r'Result\s+of\s+Semester\s+(\d+)',
        r'Semester\s+(\d+)\s+Result',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sem = match.group(1)
            # Validate it's a reasonable semester number (1-10)
            if sem.isdigit() and 1 <= int(sem) <= 10:
                return sem
    
    return None


@router.post("/add")
async def add_result(request: AddResultRequest, db: Session = Depends(get_db)):
    """Add a student result"""
    try:
        # Convert grade to marks if not provided (approximate conversion)
        if request.marks is None:
            grade_to_marks = {
                'O': 95, 'A+': 90, 'A': 85, 'B+': 80, 'B': 75,
                'C': 65, 'D': 55, 'F': 0, 'P': 50
            }
            request.marks = grade_to_marks.get(request.grade.upper(), 0)
        
        # Create result entry
        result = StudentResult(
            student_id=request.studentId,
            student_name=request.studentName or f"Student_{request.studentId}",  # Default name if not provided
            programme=None,  # Can be added later
            branch=None,  # Can be added later
            institute=None,  # Can be added later
            subject=request.course,
            marks=request.marks,
            grade=request.grade.upper(),
            semester=str(request.semester)
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "success": True,
            "message": "Result added successfully",
            "result_id": result.id
        }
        
    except Exception as e:
        db.rollback()
        print(f"Add result error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add result: {str(e)}")

@router.get("/student/{enrollment_no}")
async def get_student_results(enrollment_no: str, db: Session = Depends(get_db)):
    """Get all results for a student by enrollment number"""
    try:
        results = db.query(StudentResult).filter(
            StudentResult.student_id == enrollment_no
        ).order_by(StudentResult.semester, StudentResult.subject).all()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No results found for enrollment: {enrollment_no}")
        
        return {
            "success": True,
            "enrollment_no": enrollment_no,
            "student_name": results[0].student_name if results else "Unknown",
            "results": [
                {
                    "id": r.id,
                    "subject": r.subject,
                    "marks": r.marks,
                    "grade": r.grade,
                    "semester": r.semester
                }
                for r in results
            ],
            "total": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.get("/debug/enrollments")
async def debug_enrollments(db: Session = Depends(get_db)):
    """Debug endpoint to check enrollment numbers in database"""
    try:
        from app.models.database_models import StudentResult
        # Get sample enrollment numbers
        enrollments = db.query(StudentResult.student_id).distinct().limit(100).all()
        enrollment_list = [e[0] for e in enrollments]
        
        # Check for specific test enrollments
        test_enrollments = ['20222790494', '00413207223', '00114802722', '01114802722', '00214802722']
        found = []
        missing = []
        
        for test_enroll in test_enrollments:
            exists = db.query(StudentResult).filter(
                StudentResult.student_id == test_enroll
            ).first()
            if exists:
                found.append(test_enroll)
            else:
                missing.append(test_enroll)
        
        return {
            "total_unique_enrollments": len(enrollment_list),
            "sample_enrollments": enrollment_list[:20],
            "test_enrollments_found": found,
            "test_enrollments_missing": missing
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/search/{name}")
async def search_results_by_name(name: str, db: Session = Depends(get_db)):
    """Search results by student name"""
    try:
        results = db.query(StudentResult).filter(
            StudentResult.student_name.ilike(f"%{name}%")
        ).order_by(StudentResult.student_id, StudentResult.semester).all()
        
        if not results:
            return {
                "success": True,
                "message": f"No results found for name: {name}",
                "results": []
            }
        
        # Group by student
        students = {}
        for r in results:
            if r.student_id not in students:
                students[r.student_id] = {
                    "enrollment_no": r.student_id,
                    "student_name": r.student_name,
                    "results": []
                }
            students[r.student_id]["results"].append({
                "subject": r.subject,
                "marks": r.marks,
                "grade": r.grade,
                "semester": r.semester
            })
        
        return {
            "success": True,
            "students": list(students.values()),
            "total": len(students)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search results: {str(e)}")

