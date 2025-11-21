"""
Comprehensive Syllabus Extraction Script
Extracts all 7 courses from PDF using pdfplumber and stores as JSON
"""

import pdfplumber
import json
import re
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.postgres_db_helper import PostgresDB
from app.models.database_models import Base
from app.database.postgres_db import engine

def extract_credits(text: str) -> dict:
    """Extract L P C credits from text"""
    credits = {"L": 3, "P": 0, "C": 3}  # Default
    
    # Pattern 1: "L P C 3 0 3" format
    match = re.search(r'L\s+P\s+C\s+(\d+)\s+(\d+)\s+(\d+)', text, re.IGNORECASE)
    if match:
        credits = {
            "L": int(match.group(1)),
            "P": int(match.group(2)),
            "C": int(match.group(3))
        }
    else:
        # Pattern 2: Just numbers like "3  3" or "3 0 3"
        match = re.search(r'(\d+)\s+(\d+)(?:\s+(\d+))?', text[:300])
        if match:
            if match.group(3):
                credits = {
                    "L": int(match.group(1)),
                    "P": int(match.group(2)),
                    "C": int(match.group(3))
                }
            else:
                credits = {
                    "L": int(match.group(1)),
                    "P": 0,
                    "C": int(match.group(2))
                }
    
    return credits

def extract_department(text: str) -> str:
    """Extract department from discipline table"""
    # Look for discipline patterns
    dept_patterns = [
        r'Discipline[:\s]*(?:\(s\))?[:\s/]*([A-Z/]+)',
        r'CSE/IT/CST/ITE',
        r'CSE-AI/CSE-AIML',
        r'ECE',
    ]
    
    for pattern in dept_patterns:
        match = re.search(pattern, text[:500], re.IGNORECASE)
        if match:
            dept = match.group(1) if match.lastindex else match.group(0)
            # Clean up
            dept = re.sub(r'Discipline[:\s]*(?:\(s\))?[:\s/]*', '', dept, flags=re.IGNORECASE)
            if dept:
                return dept.strip()
    
    return "CSE"

def extract_paper_codes(text: str) -> list:
    """Extract paper codes table"""
    paper_codes = []
    
    # Find discipline table section
    # Pattern: Discipline | Semester | Group | Sub-group | Paper Code
    table_start = re.search(r'Discipline[:\s]*(?:\(s\))?', text, re.IGNORECASE)
    if not table_start:
        return paper_codes
    
    # Extract table rows (lines after table header)
    lines = text.split('\n')
    in_table = False
    header_found = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check if we're at the table header
        if re.search(r'Discipline|Semester|Group|Sub-group|Paper\s*Code', line, re.IGNORECASE):
            header_found = True
            in_table = True
            continue
        
        if header_found and in_table:
            # Extract table row data
            # Format: Discipline | Semester | Group | Sub-group | Paper Code
            parts = [p.strip() for p in re.split(r'[|\t]+', line) if p.strip()]
            
            if len(parts) >= 5:
                try:
                    paper_code = {
                        "discipline": parts[0],
                        "semester": parts[1],
                        "group": parts[2],
                        "sub_group": parts[3],
                        "code": parts[4]
                    }
                    # Only add if it has a valid course code pattern
                    if re.match(r'[A-Z]{2,4}-\d{3}[TP]', paper_code["code"]):
                        paper_codes.append(paper_code)
                except:
                    pass
            
            # Stop at next major section
            if re.search(r'Marking\s*Scheme|Course\s*Objectives|UNIT', line, re.IGNORECASE):
                break
    
    return paper_codes

def extract_objectives(text: str) -> list:
    """Extract 4 course objectives"""
    objectives = []
    
    # Find Course Objectives section - be more flexible with pattern
    obj_section = re.search(r'Course\s*Objectives?[:\s]*(.*?)(?=Course\s*Outcomes?|UNIT|Textbook|Reference|Marking\s*Scheme|$)', text, re.IGNORECASE | re.DOTALL)
    
    if obj_section:
        content = obj_section.group(1)
        
        # Pattern 1: Numbered objectives (1. 2. 3. 4.)
        pattern1 = r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*(?:\d+\.|Course\s*Outcomes?|UNIT|Textbook|Reference|Marking|$))'
        matches = re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        
        for match in matches:
            obj_num = match.group(1)
            obj_text = match.group(2).strip()
            # Clean up
            obj_text = re.sub(r'\n+', ' ', obj_text)
            obj_text = re.sub(r'\s+', ' ', obj_text)
            obj_text = re.sub(r'^To\s+', '', obj_text, flags=re.IGNORECASE)  # Remove "To" prefix if present
            if len(obj_text) > 10:
                objectives.append(obj_text)
        
        # Pattern 2: Lines starting with "To " (common format)
        if not objectives:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('To ') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.')):
                    # Remove numbering if present
                    line = re.sub(r'^\d+\.\s*', '', line)
                    line = re.sub(r'^\s*To\s+', '', line, flags=re.IGNORECASE)
                    line = re.sub(r'\n+', ' ', line)
                    line = re.sub(r'\s+', ' ', line)
                    if len(line) > 10:
                        objectives.append(line)
    
    return objectives[:4]  # Return max 4

def extract_outcomes(text: str) -> list:
    """Extract 4 course outcomes (CO 1, CO 2, CO 3, CO 4)"""
    outcomes = []
    
    # Find Course Outcomes section - be more flexible
    outcome_section = re.search(r'Course\s*Outcomes?[:\s]*(?:\(CO\))?\s*(.*?)(?=UNIT|Textbook|Reference|CO\s*to\s*PO|Syllabus\s*Content|$)', text, re.IGNORECASE | re.DOTALL)
    
    if outcome_section:
        content = outcome_section.group(1)
        
        # Pattern 1: CO 1: description or CO1: description (with space)
        pattern1 = r'(?:^|\n)\s*CO\s*(\d+)[:]\s*(.+?)(?=\n\s*(?:CO\s*\d+|UNIT|Textbook|Reference|CO\s*to|$))'
        matches = re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        
        for match in matches:
            co_num = f"CO {match.group(1)}"
            co_desc = match.group(2).strip()
            # Clean up
            co_desc = re.sub(r'\n+', ' ', co_desc)
            co_desc = re.sub(r'\s+', ' ', co_desc)
            if len(co_desc) > 10:
                outcomes.append({
                    "co": co_num,
                    "description": co_desc
                })
        
        # Pattern 2: CO 1: or CO1: without newline (same line)
        if not outcomes:
            pattern2 = r'CO\s*(\d+)[:]\s*(.+?)(?=\s*CO\s*\d+[:]|UNIT|Textbook|Reference|$)'
            matches = re.finditer(pattern2, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                co_num = f"CO {match.group(1)}"
                co_desc = match.group(2).strip()
                co_desc = re.sub(r'\n+', ' ', co_desc)
                co_desc = re.sub(r'\s+', ' ', co_desc)
                if len(co_desc) > 10:
                    outcomes.append({
                        "co": co_num,
                        "description": co_desc
                    })
    
    return outcomes[:4]  # Return max 4

def extract_co_po_mapping(text: str) -> dict:
    """Extract CO to PO mapping table"""
    mapping = {}
    
    # Find CO to PO mapping section
    mapping_section = re.search(r'CO\s*to\s*PO\s*Mapping|Course\s*Outcomes?\s*to\s*Programme\s*Outcomes?', text, re.IGNORECASE | re.DOTALL)
    
    if mapping_section:
        # Extract mapping table (simplified - can be enhanced)
        # For now, return empty dict - table parsing is complex
        pass
    
    return mapping

def extract_unit_content(text: str, unit_number: int) -> dict:
    """Extract UNIT-I, UNIT-II, UNIT-III, or UNIT-IV content"""
    unit_roman = ["I", "II", "III", "IV"][unit_number - 1]
    
    # Multiple patterns for unit headers
    patterns = [
        rf'UNIT\s*[- ]+\s*{unit_roman}[:.]?\s*\n(.*?)(?=UNIT\s*[- ]+\s*[IVX]+|Textbook|Reference|$)',
        rf'UNIT\s+{unit_roman}[:.]?\s*\n(.*?)(?=UNIT\s+[IVX]+|Textbook|Reference|$)',
        rf'UNIT[-]{unit_roman}[:.]?\s*\n(.*?)(?=UNIT[-][IVX]+|Textbook|Reference|$)',
    ]
    
    unit_content_text = ""
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            unit_content_text = match.group(1).strip()
            break
    
    if not unit_content_text:
        return {"topics": []}
    
    # Clean up unit content
    # Remove handbook footers
    unit_content_text = re.sub(r'Handbook\s+of\s+B\.Tech\..*?University\.', '', unit_content_text, flags=re.IGNORECASE | re.DOTALL)
    unit_content_text = re.sub(r'Applicable\s+from\s+Batch.*?Onwards', '', unit_content_text, flags=re.IGNORECASE | re.DOTALL)
    unit_content_text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', unit_content_text, flags=re.IGNORECASE)
    unit_content_text = re.sub(r'\[No\.\s*of\s*hrs\.\s*\d+\]', '', unit_content_text, flags=re.IGNORECASE)
    
    # Extract topics - split by newlines and commas
    lines = unit_content_text.split('\n')
    topics = []
    current_topic = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip metadata lines
        if re.match(r'^[A-Z]{2,4}-\d{3}[TP]', line):
            continue
        if re.search(r'Handbook|Applicable|Page\s+\d+', line, re.IGNORECASE):
            continue
        
        # If line contains commas, split them
        if ',' in line:
            # Split by comma and add each as a topic
            parts = [p.strip() for p in line.split(',') if p.strip() and len(p.strip()) > 3]
            for part in parts:
                # Clean up
                part = re.sub(r'\[.*?\]', '', part).strip()
                if len(part) > 5 and len(part) < 500:
                    topics.append(part)
        else:
            # Add whole line as topic if it's substantial
            line = re.sub(r'\[.*?\]', '', line).strip()
            if len(line) > 5 and len(line) < 500:
                # Check if it's not a stopword section
                if not re.search(r'Textbook|Reference|Course\s*Objectives?|Course\s*Outcomes?', line, re.IGNORECASE):
                    topics.append(line)
    
    # Combine topics into a single string if they're very short (likely comma-separated)
    if len(topics) > 10:
        # Likely comma-separated list, combine them
        combined = ', '.join(topics)
        topics = [combined]
    elif not topics:
        # Fallback: use cleaned text
        cleaned = re.sub(r'\n+', ', ', unit_content_text).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if len(cleaned) > 20:
            topics = [cleaned]
    
    return {"topics": topics}

def extract_textbooks(text: str) -> list:
    """Extract textbooks"""
    textbooks = []
    
    # Find textbook section - stop before CO/PO mapping or references
    # Look for "Textbook(s):" header first
    textbook_match = re.search(r'Textbook(?:s)?[:]?\s*\n', text, re.IGNORECASE)
    if not textbook_match:
        return textbooks
    
    # Get text after textbook header, but stop before references or CO/PO mapping
    start_pos = textbook_match.end()
    
    # Find where to stop (references, CO/PO mapping, or end)
    stop_patterns = [
        r'Reference(?:s)?[:]?\s*\n',
        r'Course\s*Outcomes?\s*to\s*Programme\s*Outcomes?',
        r'PO\d+\s+PO\d+',  # PO01 PO02 pattern
        r'CO\s*to\s*PO',
        r'UNIT[- ]?[IVX]',  # Next unit
    ]
    
    end_pos = len(text)
    for pattern in stop_patterns:
        match = re.search(pattern, text[start_pos:], re.IGNORECASE)
        if match:
            end_pos = start_pos + match.start()
            break
    
    content = text[start_pos:end_pos]
    
    # Remove CO/PO mapping content if it appears
    content = re.sub(r'Course\s*Outcomes?\s*to\s*Programme\s*Outcomes?.*', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'PO\d+\s+PO\d+.*', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'CO\s*\d+\s+[\d\-\s]+', '', content, flags=re.IGNORECASE)
    
    # Split by numbered items (1. 2. etc.)
    pattern = r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*(?:\d+\.|Reference|Course\s*Outcomes?\s*to|PO\d+|UNIT|Handbook|Applicable|Page|$))'
    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    for match in matches:
        num = int(match.group(1))
        text_line = match.group(2).strip()
        
        # Skip if it looks like CO/PO mapping or instructions
        if (re.search(r'PO\d+|PO01|PO02|PO03|PO04|PO05|PO06|PO07|PO08|PO09|PO10|PO11|PO12|CO\s*\d+\s+[\d\-]|Course\s*Objectives?|Course\s*Outcomes?|requirement.*calculators|log.*tables|data.*tables|scientific.*calculators|mapping.*scale', 
                   text_line, re.IGNORECASE) or
            re.match(r'^\d+\s+\d+\s+\d+', text_line)):  # Pattern like "3 2 2 3" (mapping values)
            continue
        
        # Clean up
        text_line = re.sub(r'\n+', ' ', text_line)
        text_line = re.sub(r'\s+', ' ', text_line)
        
        # Skip very long lines (likely instructions or metadata)
        if len(text_line) > 200:
            continue
        
        # Skip if it's only numbers and dashes (CO/PO mapping row)
        if re.match(r'^[\d\s\-]+$', text_line):
            continue
        
        # Parse: Author, "Title", Publisher
        # Try pattern: Author, "Title", Publisher
        author_match = re.match(r'^(.+?)[,\-]\s*["\']([^"\']+)["\'][,\s]+(.+?)$', text_line)
        if author_match:
            author = author_match.group(1).strip()
            title = author_match.group(2).strip()
            publisher = author_match.group(3).strip()
        else:
            # Pattern: Author - Title, Publisher
            author_match = re.match(r'^(.+?)[,\-]\s*(.+?)[,\s]+(.+?)$', text_line)
            if author_match:
                author = author_match.group(1).strip()
                title = author_match.group(2).strip()
                publisher = author_match.group(3).strip()
            else:
                # Fallback: try to split by commas
                parts = [p.strip() for p in text_line.split(',') if p.strip()]
                if len(parts) >= 3:
                    author = parts[0]
                    title = parts[1]
                    publisher = ', '.join(parts[2:])
                else:
                    author = ""
                    title = text_line
                    publisher = ""
        
        # Remove leading dash from title
        if title.startswith('-'):
            title = title[1:].strip()
        
        # Validate textbook entry - must look like a book reference
        if (title and len(title) > 5 and len(title) < 200 and 
            not re.search(r'Course\s*Objectives?|Course\s*Outcomes?|PO\d+|CO\s*\d+|requirement|calculators|log.*tables|mapping', 
                         title, re.IGNORECASE) and
            not re.match(r'^[\d\s\-]+$', title)):  # Not just numbers/dashes
            textbooks.append({
                "number": num,
                "author": author,
                "title": title,
                "publisher": publisher
            })
    
    return textbooks

def extract_references(text: str) -> list:
    """Extract references"""
    references = []
    
    # Find reference section - stop before CO/PO mapping or units
    # Look for "References:" or "Reference:" header first
    ref_match = re.search(r'Reference(?:s)?[:]?\s*\n', text, re.IGNORECASE)
    if not ref_match:
        return references
    
    # Get text after reference header, but stop before CO/PO mapping or units
    start_pos = ref_match.end()
    
    # Find where to stop (CO/PO mapping, units, or end)
    stop_patterns = [
        r'Course\s*Outcomes?\s*to\s*Programme\s*Outcomes?',
        r'PO\d+\s+PO\d+',  # PO01 PO02 pattern
        r'CO\s*to\s*PO',
        r'CO\s*\d+\s+[\d\s\-]+',  # CO 1 3 2 2 3 pattern
        r'UNIT[- ]?[IVX]',  # Next unit
    ]
    
    end_pos = len(text)
    for pattern in stop_patterns:
        match = re.search(pattern, text[start_pos:], re.IGNORECASE)
        if match:
            end_pos = start_pos + match.start()
            break
    
    content = text[start_pos:end_pos]
    
    # Remove CO/PO mapping content if it appears
    content = re.sub(r'Course\s*Outcomes?\s*to\s*Programme\s*Outcomes?.*', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'PO\d+\s+PO\d+.*', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'CO\s*\d+\s+[\d\-\s]+', '', content, flags=re.IGNORECASE)
    
    # Split by numbered items (1. 2. etc.)
    pattern = r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*(?:\d+\.|Course\s*Outcomes?\s*to|PO\d+|UNIT|Textbook|Handbook|Applicable|Page|$))'
    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    for match in matches:
        num = int(match.group(1))
        text_line = match.group(2).strip()
        
        # Skip if it looks like CO/PO mapping or instructions
        if (re.search(r'PO\d+|PO01|PO02|PO03|PO04|PO05|PO06|PO07|PO08|PO09|PO10|PO11|PO12|CO\s*\d+\s+[\d\-]|Course\s*Objectives?|Course\s*Outcomes?|mapping.*scale|requirement.*calculators|log.*tables|data.*tables|scientific.*calculators', 
                   text_line, re.IGNORECASE) or
            re.match(r'^\d+\s+\d+\s+\d+', text_line)):  # Pattern like "3 2 2 3" (mapping values)
            continue
        
        # Clean up
        text_line = re.sub(r'\n+', ' ', text_line)
        text_line = re.sub(r'\s+', ' ', text_line)
        
        # Skip very long lines (likely instructions or metadata)
        if len(text_line) > 200:
            continue
        
        # Skip if it's only numbers and dashes (CO/PO mapping row)
        if re.match(r'^[\d\s\-]+$', text_line):
            continue
        
        # Parse: Author, "Title", Publisher
        author_match = re.match(r'^(.+?)[,\-]\s*["\']?([^"\']+)["\']?[,\s]+(.+?)$', text_line)
        if author_match:
            author = author_match.group(1).strip()
            title = author_match.group(2).strip()
            publisher = author_match.group(3).strip()
        else:
            # Pattern: Author - Title, Publisher
            author_match = re.match(r'^(.+?)[,\-]\s*(.+?)[,\s]+(.+?)$', text_line)
            if author_match:
                author = author_match.group(1).strip()
                title = author_match.group(2).strip()
                publisher = author_match.group(3).strip()
            else:
                # Fallback: split by commas
                parts = [p.strip() for p in text_line.split(',') if p.strip()]
                if len(parts) >= 2:
                    author = parts[0]
                    title = parts[1] if len(parts) > 1 else ""
                    publisher = ', '.join(parts[2:]) if len(parts) > 2 else ""
                else:
                    author = ""
                    title = text_line
                    publisher = ""
        
        # Remove leading dash from title
        if title.startswith('-'):
            title = title[1:].strip()
        
        # Validate reference entry - must look like a book reference
        if (title and len(title) > 5 and len(title) < 200 and 
            not re.search(r'Course\s*Objectives?|Course\s*Outcomes?|PO\d+|CO\s*\d+|requirement|calculators|log.*tables|mapping', 
                         title, re.IGNORECASE) and
            not re.match(r'^[\d\s\-]+$', title)):  # Not just numbers/dashes
            references.append({
                "number": num,
                "author": author,
                "title": title,
                "publisher": publisher
            })
    
    return references

def extract_course_from_pages(pdf, start_page: int, end_page: int, course_name: str, course_code: str, semester: str = "6") -> dict:
    """Extract complete course data from PDF pages"""
    # Combine text from both pages
    text = ""
    for page_num in range(start_page, end_page + 1):
        if page_num < len(pdf.pages):
            page = pdf.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # Extract all components
    credits = extract_credits(text)
    department = extract_department(text)
    paper_codes = extract_paper_codes(text)
    objectives = extract_objectives(text)
    outcomes = extract_outcomes(text)
    co_po_mapping = extract_co_po_mapping(text)
    
    course_data = {
        "course_name": course_name,
        "course_code": course_code,
        "credits": credits,
        "semester": semester,
        "department": department,
        "paper_codes": paper_codes,
        "objectives": objectives,
        "outcomes": outcomes,
        "co_po_mapping": co_po_mapping,
        "syllabus": {
            "UNIT-I": extract_unit_content(text, 1),
            "UNIT-II": extract_unit_content(text, 2),
            "UNIT-III": extract_unit_content(text, 3),
            "UNIT-IV": extract_unit_content(text, 4)
        },
        "textbooks": extract_textbooks(text),
        "references": extract_references(text)
    }
    
    return course_data

def main():
    """Main extraction function"""
    # PDF path - adjust as needed
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "6th sem syllabus_removed.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please ensure the PDF file exists in the backend directory")
        return
    
    # Course definitions: (start_page, end_page, name, code)
    # Pages are 0-indexed (Page 1 = index 0)
    courses_info = [
        (0, 1, "Advanced Java Programming", "CIE-306T"),
        (2, 3, "Statistics, Statistical Modelling & Data Analytics", "DA-304T"),
        (4, 5, "Web Technologies", "CIE-356T"),
        (6, 7, "Programming in Python", "CIE-332T"),
        (8, 9, "Artificial Intelligence", "AI-302T"),
        (10, 11, "Principles of Management for Engineers", "MS-302"),
        (12, 13, "Universal Human Values", "HS-304")
    ]
    
    print(f"📖 Opening PDF: {pdf_path}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"✅ PDF opened successfully ({len(pdf.pages)} pages)")
            
            extracted_courses = []
            
            for start_page, end_page, name, code in courses_info:
                print(f"\n🔍 Extracting: {name} ({code}) - Pages {start_page+1}-{end_page+1}...")
                
                try:
                    course_data = extract_course_from_pages(pdf, start_page, end_page, name, code)
                    
                    print(f"  ✅ Extracted:")
                    print(f"     - Objectives: {len(course_data['objectives'])}")
                    print(f"     - Outcomes: {len(course_data['outcomes'])}")
                    print(f"     - Units: {sum(1 for u in course_data['syllabus'].values() if u.get('topics'))}")
                    print(f"     - Textbooks: {len(course_data['textbooks'])}")
                    print(f"     - References: {len(course_data['references'])}")
                    
                    extracted_courses.append(course_data)
                except Exception as e:
                    print(f"  ❌ Error extracting {name}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Create tables if needed
            Base.metadata.create_all(bind=engine)
            
            # Store in database
            print(f"\n💾 Storing {len(extracted_courses)} courses in database...")
            db = PostgresDB()
            stored_count = 0
            
            for course in extracted_courses:
                try:
                    # Convert to JSON string
                    syllabus_json = json.dumps(course, indent=2, ensure_ascii=False)
                    
                    # Store in database
                    syllabus_id = db.add_syllabus(
                        course_code=course["course_code"],
                        course_name=course["course_name"],
                        department=course.get("department", "CSE"),
                        semester=course.get("semester", "6"),
                        credits=course["credits"].get("C", 3),
                        syllabus_content=syllabus_json
                    )
                    
                    if syllabus_id:
                        stored_count += 1
                        print(f"  ✅ Stored: {course['course_code']} - {course['course_name']}")
                    else:
                        print(f"  ⚠️  Failed to store: {course['course_code']}")
                except Exception as e:
                    print(f"  ❌ Error storing {course['course_code']}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n🎉 Successfully stored {stored_count}/{len(extracted_courses)} courses in database")
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

