from typing import List, Dict, Optional
from app.database.postgres_db_helper import PostgresDB
from app.services.llm_service import LLMService

class ResultsAgent:
    def __init__(self):
        self.postgres_db = PostgresDB()
        self.llm_service = LLMService()
    
    def get_results_by_enrollment(self, enrollment_no: str) -> Dict:
        """
        Get student results by enrollment number
        """
        print(f"🔍 Searching results for enrollment: {enrollment_no}")
        
        results = self.postgres_db.get_results_by_enrollment(enrollment_no)
        
        if not results:
            return {
                "found": False,
                "message": f"No results found for enrollment number: {enrollment_no}",
                "results": []
            }
        
        # Get student info from first result
        first_result = results[0] if results else {}
        student_name = first_result.get('student_name', 'Unknown')
        student_id = first_result.get('student_id', enrollment_no)
        programme = first_result.get('programme')
        branch = first_result.get('branch')
        institute = first_result.get('institute')
        
        # Calculate summary
        summary = self._calculate_summary(results)
        
        return {
            "found": True,
            "student": {
                "name": student_name,
                "enrollment_no": student_id,
                "student_id": student_id,
                "programme": programme,
                "branch": branch,
                "institute": institute
            },
            "results": results,
            "summary": summary,
            "message": f"Found {len(results)} subjects for {student_name}"
        }
    
    def get_results_by_name(self, name: str) -> Dict:
        """
        Get student results by name (searches partial match)
        """
        print(f"🔍 Searching results for name: {name}")
        
        # First check for unique students
        students = self.postgres_db.get_unique_students_by_name(name)
        
        if not students:
            return {
                "found": False,
                "message": f"No students found with name: {name}",
                "students": []
            }
        
        # If multiple students found
        if len(students) > 1:
            return {
                "found": True,
                "multiple": True,
                "message": f"Found {len(students)} students matching '{name}'",
                "students": students
            }
        
        # If single student found, get their results
        student = students[0]
        results = self.postgres_db.get_results_by_enrollment(student['enrollment_no'])
        summary = self._calculate_summary(results)
        
        return {
            "found": True,
            "multiple": False,
            "student": student,
            "results": results,
            "summary": summary,
            "message": f"Found results for {student['name']}"
        }
    
    def _calculate_summary(self, results: List[Dict]) -> Dict:
        """
        Calculate SGPA, percentage, etc.
        Extract credits from subject names or use defaults
        """
        if not results:
            return {}
        
        total_marks = 0
        max_marks = 0
        total_credits = 0
        obtained_credits = 0
        total_credit_marks = 0  # Credit marks = marks * credits
        max_credit_marks = 0
        grade_points = {
            'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6,
            'C': 5, 'D': 4, 'F': 0, 'P': 5
        }
        total_grade_points = 0
        
        for result in results:
            # Extract credits from subject name pattern: "SUBJECT (Credits: X)" or "SUBJECT (X)"
            import re
            subject = result.get('subject', '')
            credits_match = re.search(r'\(Credits?[:\s]*(\d+)\)|\((\d+)\)', subject)
            credits = int(credits_match.group(1) or credits_match.group(2)) if credits_match else 4
            
            # Marks calculation
            marks = result.get('marks', 0) or 0
            total_marks += marks
            max_marks += 100  # Assuming 100 per subject
            
            # Credit marks calculation
            total_credit_marks += marks * credits
            max_credit_marks += 100 * credits
            
            # Credits calculation
            total_credits += credits
            
            grade = result.get('grade', 'F')
            grade_upper = grade.upper().strip()
            
            # Map grade to points
            if grade_upper in grade_points:
                grade_point = grade_points[grade_upper]
                if grade_point > 0:  # Not F grade
                    obtained_credits += credits
                total_grade_points += grade_point * credits
        
        # Calculate percentages and SGPA
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
        sgpa = (total_grade_points / total_credits) if total_credits > 0 else 0
        credit_percentage = (total_credit_marks / max_credit_marks * 100) if max_credit_marks > 0 else 0
        equivalent_percentage = sgpa * 10
        
        return {
            "marks": round(total_marks, 2),
            "max_marks": max_marks,
            "percentage": round(percentage, 3),
            "credit_marks": round(total_credit_marks, 0),
            "max_credit_marks": max_credit_marks,
            "credit_percentage": round(credit_percentage, 3),
            "total_credits": total_credits,
            "credit_percentage": round(credit_percentage, 3),
            "sgpa": round(sgpa, 3),
            "equivalent_percentage": round(equivalent_percentage, 1),
            "credits_obtained": f"{obtained_credits} / {total_credits}"
        }
    
    def format_result_response(self, result_data: Dict) -> str:
        """
        Format results into a natural language response
        """
        if not result_data.get('found'):
            return result_data.get('message', 'No results found.')
        
        # If multiple students found
        if result_data.get('multiple'):
            students = result_data.get('students', [])
            response = f"Found {len(students)} students matching that name:\n\n"
            for student in students:
                response += f"• {student['name']} (Enrollment: {student['enrollment_no']})\n"
            response += "\nPlease provide the enrollment number to see specific results."
            return response
        
        # Single student with results
        student = result_data.get('student', {})
        results = result_data.get('results', [])
        summary = result_data.get('summary', {})
        
        if not results:
            return result_data.get('message', 'No results available.')
        
        # Return minimal response - UI cards will display the detailed results
        # Only return a simple confirmation message
        student_name = student.get('name', 'Student')
        enrollment = student.get('enrollment_no', 'N/A')
        return f"Results for {student_name} (Enrollment: {enrollment})"
    
    def process_query(self, query: str) -> Dict:
        """
        Process a natural language query about results
        Returns dict with response and structured data
        """
        query_lower = query.lower()
        
        # Extract enrollment number if present (pattern: numbers, typically 8-12 digits)
        import re
        enrollment_match = re.search(r'\b\d{8,12}\b', query)
        
        if enrollment_match:
            enrollment_no = enrollment_match.group(0)
            result_data = self.get_results_by_enrollment(enrollment_no)
            return {
                "response": self.format_result_response(result_data),
                "result_data": result_data,
                "agent": "results_agent"
            }
        
        # Extract name if asking about results
        if any(keyword in query_lower for keyword in ['result', 'marks', 'score', 'grade', 'cgpa', 'sgpa']):
            # Try to extract name (words that are capitalized or after "for", "of", etc.)
            # Look for patterns like "result for John" or "John's result"
            name_patterns = [
                r'(?:result|marks|score|grade)\s+(?:for|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\'?s?\s+(?:result|marks|score)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ]
            
            name = None
            for pattern in name_patterns:
                match = re.search(pattern, query)
                if match:
                    name = match.group(1).strip()
                    # Filter out common words
                    if name.lower() not in ['my', 'the', 'show', 'get', 'give', 'what']:
                        break
            
            if name:
                result_data = self.get_results_by_name(name)
                return {
                    "response": self.format_result_response(result_data),
                    "result_data": result_data,
                    "agent": "results_agent"
                }
        
        return {
            "response": "Please provide either an enrollment number or a student name to fetch results.\n\nExample:\n• \"Show result for enrollment 20232435\"\n• \"What are the marks for John Doe\"",
            "result_data": None,
            "agent": "results_agent"
        }

# Create singleton instance
results_agent = ResultsAgent()
