"""PostgreSQL database helper using psycopg directly"""
import psycopg
import re
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresDB:
    def __init__(self):
        # Get connection string from environment
        self.connection_string = os.getenv('POSTGRES_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("POSTGRES_CONNECTION_STRING not found in environment variables")
    
    def get_connection(self):
        """Get database connection with timeout"""
        return psycopg.connect(
            self.connection_string,
            connect_timeout=10  # 10 second connection timeout
        )
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """Get file information by file_id"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT file_id, filename, stored_filename, subject, topic, 
                               file_size, file_path, chunk_count, upload_date
                        FROM notes_metadata
                        WHERE file_id = %s
                    """, (file_id,))
                    
                    row = cur.fetchone()
                    if row:
                        return {
                            'file_id': row[0],
                            'filename': row[1],
                            'stored_filename': row[2],
                            'subject': row[3],
                            'topic': row[4],
                            'file_size': row[5],
                            'file_path': row[6],
                            'chunk_count': row[7],
                            'uploaded_at': row[8].isoformat() if row[8] else None
                        }
                    return None
        except Exception as e:
            print(f"❌ Error getting file by ID: {str(e)}")
            return None
    
    def get_pdfs_by_topic(self, topic: str) -> List[Dict]:
        """Get all PDFs for a specific topic"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT file_id, filename, subject, topic, file_size, upload_date
                        FROM notes_metadata
                        WHERE LOWER(topic) LIKE LOWER(%s) OR LOWER(subject) LIKE LOWER(%s)
                        ORDER BY upload_date DESC
                    """, (f'%{topic}%', f'%{topic}%'))
                    
                    rows = cur.fetchall()
                    print(f"🔍 Found {len(rows)} PDFs for topic: {topic}")
                    return [
                        {
                            'file_id': row[0],
                            'filename': row[1],
                            'subject': row[2],
                            'topic': row[3],
                            'file_size': row[4],
                            'uploaded_at': row[5].isoformat() if row[5] else None,
                            'download_url': f'/api/notes/download/{row[0]}'
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting PDFs by topic: {str(e)}")
            return []
    
    def get_results_by_enrollment(self, enrollment_no: str) -> List[Dict]:
        """Get all results for a student by enrollment number (student_id)
        Optimized to try exact matches first (uses index), then fallback to partial matches
        """
        try:
            # Clean enrollment number (remove spaces, normalize)
            enrollment_no = enrollment_no.strip()
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    matched_enrollment = None
                    
                    # Strategy 1: Try exact match first (fastest, uses index)
                    cur.execute("""
                        SELECT DISTINCT student_id, student_name
                        FROM student_results
                        WHERE student_id = %s
                        LIMIT 1
                    """, (enrollment_no,))
                    student_row = cur.fetchone()
                    
                    if student_row:
                        matched_enrollment = student_row[0]
                    else:
                        # Strategy 2: Try cleaned version (without leading zeros)
                        enrollment_cleaned = enrollment_no.lstrip('0')
                        if enrollment_cleaned and enrollment_cleaned != enrollment_no:
                            cur.execute("""
                                SELECT DISTINCT student_id, student_name
                                FROM student_results
                                WHERE student_id = %s
                                LIMIT 1
                            """, (enrollment_cleaned,))
                            student_row = cur.fetchone()
                            if student_row:
                                matched_enrollment = student_row[0]
                    
                    # Strategy 3: Try partial match (last 11 digits) - only if still no match
                    if not matched_enrollment and len(enrollment_no) >= 11:
                        last_11 = enrollment_no[-11:]
                        cur.execute("""
                            SELECT DISTINCT student_id, student_name
                            FROM student_results
                            WHERE student_id LIKE %s
                            LIMIT 1
                        """, (f'%{last_11}',))
                        student_row = cur.fetchone()
                        if student_row:
                            matched_enrollment = student_row[0]
                    
                    # Strategy 4: Try partial match (last 10 digits) - only if still no match
                    if not matched_enrollment and len(enrollment_no) >= 10:
                        last_10 = enrollment_no[-10:]
                        cur.execute("""
                            SELECT DISTINCT student_id, student_name
                            FROM student_results
                            WHERE student_id LIKE %s
                            LIMIT 1
                        """, (f'%{last_10}',))
                        student_row = cur.fetchone()
                        if student_row:
                            matched_enrollment = student_row[0]
                    
                    if not matched_enrollment:
                        return []
                    
                    # Get all results for this student using the matched enrollment
                    # Include new fields: paper_id, internal_marks, external_marks, credits
                    cur.execute("""
                        SELECT id, student_id, student_name, programme, branch, institute, 
                               subject, marks, grade, semester, paper_id, internal_marks, external_marks, credits
                        FROM student_results
                        WHERE student_id = %s
                        ORDER BY semester, subject
                    """, (matched_enrollment,))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'student_id': row[1],
                            'student_name': row[2],
                            'programme': row[3],
                            'branch': row[4],
                            'institute': row[5],
                            'subject': row[6],
                            'marks': float(row[7]) if row[7] else 0,
                            'grade': row[8],
                            'semester': row[9],
                            'paper_id': row[10] if len(row) > 10 else None,
                            'internal_marks': float(row[11]) if len(row) > 11 and row[11] is not None else 0.0,
                            'external_marks': float(row[12]) if len(row) > 12 and row[12] is not None else 0.0,
                            'credits': int(row[13]) if len(row) > 13 and row[13] is not None else 0
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting results by enrollment: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_results_by_name(self, name: str) -> List[Dict]:
        """Get all results for students matching a name"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # First, get unique students matching the name
                    cur.execute("""
                        SELECT DISTINCT student_id, student_name
                        FROM student_results
                        WHERE LOWER(student_name) LIKE LOWER(%s)
                        ORDER BY student_name
                    """, (f'%{name}%',))
                    
                    student_rows = cur.fetchall()
                    
                    if not student_rows:
                        return []
                    
                    # Get all results for all matching students
                    student_ids = [row[0] for row in student_rows]
                    placeholders = ','.join(['%s'] * len(student_ids))
                    
                    cur.execute(f"""
                        SELECT id, student_id, student_name, subject, marks, grade, semester
                        FROM student_results
                        WHERE student_id IN ({placeholders})
                        ORDER BY student_id, semester, subject
                    """, tuple(student_ids))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'student_id': row[1],
                            'student_name': row[2],
                            'subject': row[3],
                            'marks': float(row[4]) if row[4] else 0,
                            'grade': row[5],
                            'semester': row[6]
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting results by name: {str(e)}")
            return []
    
    def get_unique_students_by_name(self, name: str) -> List[Dict]:
        """Get unique students matching a name"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT DISTINCT student_id, student_name
                        FROM student_results
                        WHERE LOWER(student_name) LIKE LOWER(%s)
                        ORDER BY student_name
                    """, (f'%{name}%',))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'student_id': row[0],
                            'name': row[1],
                            'enrollment_no': row[0]  # student_id is enrollment
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting students by name: {str(e)}")
            return []
    
    def add_syllabus(self, course_code: str, course_name: str, department: str, 
                     semester: str, credits: int, syllabus_content: str) -> Optional[int]:
        """Add syllabus to database. Updates if course_code already exists."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Use ON CONFLICT to update if course_code already exists
                    cur.execute("""
                        INSERT INTO syllabus (course_code, course_name, department, semester, credits, syllabus_content)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (course_code) 
                        DO UPDATE SET
                            course_name = EXCLUDED.course_name,
                            department = EXCLUDED.department,
                            semester = EXCLUDED.semester,
                            credits = EXCLUDED.credits,
                            syllabus_content = EXCLUDED.syllabus_content
                        RETURNING id
                    """, (course_code, course_name, department, semester, credits, syllabus_content))
                    
                    row = cur.fetchone()
                    if row:
                        conn.commit()
                        print(f"✅ Added/Updated syllabus: {course_code} - {course_name}")
                        return row[0]
                    return None
        except Exception as e:
            print(f"❌ Error adding syllabus: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_syllabus_by_course_code(self, course_code: str) -> List[Dict]:
        """Get syllabus by course code"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus
                        WHERE LOWER(course_code) = LOWER(%s)
                    """, (course_code,))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting syllabus by course code: {str(e)}")
            return []
    
    def get_syllabus_by_department(self, department: str) -> List[Dict]:
        """Get all syllabi for a department"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus
                        WHERE LOWER(department) = LOWER(%s)
                        ORDER BY semester, course_code
                    """, (department,))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting syllabus by department: {str(e)}")
            return []
    
    def get_syllabus_by_semester(self, semester: str) -> List[Dict]:
        """Get all syllabi for a semester"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus
                        WHERE semester = %s
                        ORDER BY course_code
                    """, (semester,))
                    
                    rows = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in rows
                    ]
        except Exception as e:
            print(f"❌ Error getting syllabus by semester: {str(e)}")
            return []
    
    def get_syllabus_by_code(self, course_code: str) -> Optional[Dict]:
        """Get syllabus by exact course code"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus 
                        WHERE course_code = %s
                    """, (course_code,))
                    
                    row = cur.fetchone()
                    if row:
                        return {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                    return None
        except Exception as e:
            print(f"❌ Error getting syllabus by code: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def search_syllabus_by_name(self, course_name: str) -> Optional[Dict]:
        """Search syllabus by course name (case-insensitive partial match)"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Clean up search query - extract key words
                    search_words = course_name.split()
                    # Remove very short words (articles, prepositions)
                    search_words = [w for w in search_words if len(w) > 2]
                    
                    if not search_words:
                        return None
                    
                    # Try exact match first (prioritize course name matches)
                    # First try if course name contains all words
                    conditions_all = " AND ".join(["LOWER(course_name) LIKE LOWER(%s)" for _ in search_words])
                    params_all = tuple([f"%{word}%" for word in search_words])
                    cur.execute(f"""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus 
                        WHERE {conditions_all}
                        ORDER BY 
                            CASE WHEN LOWER(course_name) = LOWER(%s) THEN 1
                                 WHEN LOWER(course_name) LIKE LOWER(%s) THEN 2
                                 ELSE 3 END,
                            course_name
                        LIMIT 1
                    """, params_all + (course_name, f"{course_name}%"))
                    
                    row = cur.fetchone()
                    if row:
                        return {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                    
                    # Try partial match with full query
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus 
                        WHERE LOWER(course_name) LIKE LOWER(%s)
                        ORDER BY 
                            CASE WHEN LOWER(course_name) LIKE LOWER(%s) THEN 1
                                 ELSE 2 END,
                            course_name
                        LIMIT 1
                    """, (f"%{course_name}%", f"{course_name}%"))
                    
                    row = cur.fetchone()
                    if row:
                        return {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                    
                    # Try matching all key words (more flexible)
                    if len(search_words) > 1:
                        conditions = " AND ".join(["LOWER(course_name) LIKE LOWER(%s)" for _ in search_words])
                        params = tuple([f"%{word}%" for word in search_words])
                        cur.execute(f"""
                            SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                            FROM syllabus 
                            WHERE {conditions}
                            ORDER BY course_name
                            LIMIT 1
                        """, params)
                        
                        row = cur.fetchone()
                        if row:
                            return {
                                'id': row[0],
                                'course_code': row[1],
                                'course_name': row[2],
                                'department': row[3],
                                'semester': row[4],
                                'credits': row[5],
                                'syllabus_content': row[6]
                            }
                    
                    # Try matching any key word (fallback)
                    if search_words:
                        conditions = " OR ".join(["LOWER(course_name) LIKE LOWER(%s)" for _ in search_words])
                        params = tuple([f"%{word}%" for word in search_words])
                        cur.execute(f"""
                            SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                            FROM syllabus 
                            WHERE {conditions}
                            ORDER BY course_name
                            LIMIT 1
                        """, params)
                        
                        row = cur.fetchone()
                        if row:
                            return {
                                'id': row[0],
                                'course_code': row[1],
                                'course_name': row[2],
                                'department': row[3],
                                'semester': row[4],
                                'credits': row[5],
                                'syllabus_content': row[6]
                            }
                    
                    return None
        except Exception as e:
            print(f"❌ Error searching syllabus by name: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_syllabi(self) -> List[Dict]:
        """Get all syllabi"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus 
                        ORDER BY semester, course_name
                    """)
                    
                    results = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in results
                    ]
        except Exception as e:
            print(f"❌ Error getting all syllabi: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_syllabi_by_semester(self, semester: str) -> List[Dict]:
        """Get all syllabi for a specific semester"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus 
                        WHERE semester = %s 
                        ORDER BY course_name
                    """, (semester,))
                    
                    results = cur.fetchall()
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in results
                    ]
        except Exception as e:
            print(f"❌ Error getting syllabi by semester: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_syllabus(self, search_term: str) -> List[Dict]:
        """Search syllabus by course name, code, or content (supports partial matches)"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Remove "lab" from search if present (for matching Theory courses)
                    search_cleaned = re.sub(r'\b(lab|laboratory|practical)\b', '', search_term.lower(), flags=re.IGNORECASE).strip()
                    search_term = search_cleaned if search_cleaned else search_term
                    
                    # Split search term into words for better matching
                    search_words = search_term.split()
                    
                    # Build search pattern for each word
                    # Try to match if all words appear (in any order)
                    search_pattern = f'%{search_term}%'
                    
                    # Also search for individual words
                    word_patterns = [f'%{word}%' for word in search_words if len(word) > 2]
                    
                    # First try: exact phrase match in course_name, course_code, OR syllabus_content
                    cur.execute("""
                        SELECT id, course_code, course_name, department, semester, credits, syllabus_content
                        FROM syllabus
                        WHERE LOWER(course_name) LIKE LOWER(%s)
                        OR LOWER(course_code) LIKE LOWER(%s)
                        OR LOWER(syllabus_content) LIKE LOWER(%s)
                        ORDER BY 
                            CASE 
                                WHEN LOWER(course_name) LIKE LOWER(%s) THEN 1
                                WHEN LOWER(course_code) LIKE LOWER(%s) THEN 2
                                WHEN LOWER(syllabus_content) LIKE LOWER(%s) THEN 3
                                ELSE 4
                            END,
                            course_code
                    """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
                    
                    results = cur.fetchall()
                    
                    # If no results, try searching for all words in content (must match all)
                    if not results and len(word_patterns) > 1:
                        # Build query with AND conditions for all words in content
                        conditions = " AND ".join([f"(LOWER(course_name) LIKE LOWER(%s) OR LOWER(syllabus_content) LIKE LOWER(%s))" for _ in word_patterns])
                        params = tuple([p for pattern in word_patterns for p in [pattern, pattern]])
                        cur.execute(f"""
                            SELECT DISTINCT id, course_code, course_name, department, semester, credits, syllabus_content
                            FROM syllabus
                            WHERE {conditions}
                            ORDER BY course_code
                        """, params)
                        results = cur.fetchall()
                    
                    # If still no results, try ANY word match in content
                    if not results and word_patterns:
                        conditions = " OR ".join([f"(LOWER(course_name) LIKE LOWER(%s) OR LOWER(course_code) LIKE LOWER(%s) OR LOWER(syllabus_content) LIKE LOWER(%s))" for _ in word_patterns])
                        params = tuple([p for pattern in word_patterns for p in [pattern, pattern, pattern]])
                        cur.execute(f"""
                            SELECT DISTINCT id, course_code, course_name, department, semester, credits, syllabus_content
                            FROM syllabus
                            WHERE {conditions}
                            ORDER BY course_code
                            LIMIT 10
                        """, params)
                        results = cur.fetchall()
                    
                    return [
                        {
                            'id': row[0],
                            'course_code': row[1],
                            'course_name': row[2],
                            'department': row[3],
                            'semester': row[4],
                            'credits': row[5],
                            'syllabus_content': row[6]
                        }
                        for row in results
                    ]
        except Exception as e:
            print(f"❌ Error searching syllabus: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

