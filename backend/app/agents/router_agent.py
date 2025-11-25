from typing import Dict
from app.agents.notes_agent import notes_agent
from app.agents.results_agent import results_agent
from app.agents.syllabus_agent import syllabus_agent
from sqlalchemy.orm import Session

class RouterAgent:
    """
    Routes queries to the appropriate agent based on query content
    """
    def __init__(self):
        self.name = "router_agent"
    
    def route_query(self, query: str, db: Session = None) -> Dict:
        """
        Route query to appropriate agent
        """
        query_lower = query.lower().strip()
        import re
        
        # Check for casual greetings and simple questions first
        greeting_patterns = [
            r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening|sup|what\'?s up|howdy)',
            r'^(how are you|how do you do|what\'?s going on|how\'?s it going)',
            r'^(thanks|thank you|thx|ty)',
            r'^(bye|goodbye|see you|farewell)',
            r'^(yes|no|ok|okay|sure|alright|fine)',
            r'^(please|help|can you|could you)',
        ]
        
        is_greeting = any(re.match(pattern, query_lower) for pattern in greeting_patterns)
        
        # Also check if query is very short and doesn't contain academic keywords
        is_short_casual = (
            len(query.split()) <= 3 and 
            not any(keyword in query_lower for keyword in [
                'result', 'marks', 'syllabus', 'notes', 'pdf', 'course', 'subject',
                'grade', 'cgpa', 'enrollment', 'student', 'semester', 'unit'
            ])
        )
        
        if is_greeting or is_short_casual:
            print(f"👋 Detected greeting/casual query")
            # Generate friendly response
            if 'hi' in query_lower or 'hello' in query_lower or 'hey' in query_lower:
                response = "Hello! 👋 I'm your College AI Assistant. I can help you with:\n\n• 📚 **Notes** - Find study materials and PDFs\n• 📊 **Results** - Check your grades and marks\n• 📖 **Syllabus** - Get course structure and curriculum\n\nWhat would you like to know?"
            elif 'how are you' in query_lower:
                response = "I'm doing great, thank you for asking! 😊 I'm here to help you with your college studies. What can I assist you with today?\n\nYou can ask me about:\n• Notes and study materials\n• Your results and grades\n• Course syllabus and curriculum"
            elif 'thank' in query_lower or 'thanks' in query_lower:
                response = "You're welcome! 😊 Feel free to ask if you need anything else!"
            elif 'bye' in query_lower or 'goodbye' in query_lower:
                response = "Goodbye! 👋 Feel free to come back anytime if you need help with your studies!"
            else:
                response = "Hi there! 👋 I'm your College AI Assistant. How can I help you today?\n\nI can assist with:\n• 📚 Finding notes and study materials\n• 📊 Checking your results and grades\n• 📖 Getting course syllabus information\n\nWhat would you like to know?"
            
            return {
                "response": response,
                "sources": [],
                "pdf_files": [],
                "has_pdfs": False,
                "agent": "router_agent",
                "result_data": None
            }
        
        # Check if query is about results
        result_keywords = [
            'result', 'marks', 'score', 'grade', 'cgpa', 'sgpa',
            'enrollment', 'roll number', 'student id', 'student_id',
            'what are my', 'show my', 'my result', 'my marks'
        ]
        
        is_result_query = any(keyword in query_lower for keyword in result_keywords)
        
        # Check for enrollment number pattern (8-12 digits)
        has_enrollment = bool(re.search(r'\b\d{8,12}\b', query))
        
        # If it's clearly a result query, use results agent
        if is_result_query or has_enrollment:
            print(f"🎯 Routing to results_agent")
            result = results_agent.process_query(query)
            return {
                "response": result.get("response", ""),
                "sources": [],
                "pdf_files": [],
                "has_pdfs": False,
                "agent": "results_agent",
                "result_data": result.get("result_data")
            }
        
        # Check if query is about syllabus
        syllabus_keywords = [
            'syllabus', 'course content', 'course structure', 'curriculum',
            'course code', 'credits', 'textbook', 'reference', 'unit',
            'course outline', 'course details', 'semester syllabus', 'semester',
            'sem', 'lab', 'laboratory', 'practical'
        ]
        
        # Check if query is about notes
        notes_keywords = [
            'notes', 'note', 'pdf', 'material', 'study material', 'lecture',
            'study', 'content', 'document', 'file', 'handout'
        ]
        
        # Check for course code pattern (XXX-###T/P)
        has_course_code = bool(re.search(r'[A-Z]{2,4}-\d{3}[TP]', query.upper()))
        
        # Check if query looks like a course name (capitalized words, likely a course title)
        # Pattern: "Advanced Java Programming", "Data Structures", etc.
        # Course names typically have 2-4 capitalized words
        words = query.strip().split()
        # Check if it looks like a course name (multiple capitalized words)
        looks_like_course_name = (
            len(words) >= 2 and 
            len(words) <= 5 and
            # At least 2 words start with capital letter
            sum(1 for word in words if word and word[0].isupper()) >= 2 and
            # Not a question
            not query.strip().endswith('?') and
            # Has relevant keywords
            any(keyword in query_lower for keyword in [
                'programming', 'engineering', 'science', 'technology', 'design',
                'system', 'management', 'analysis', 'java', 'python', 'data',
                'database', 'network', 'web', 'software', 'algorithm', 'structure',
                'advanced', 'introduction', 'fundamentals', 'principles', 'computer',
                'information', 'communication', 'electronics', 'electrical', 'mechanical',
                'artificial', 'intelligence', 'machine', 'learning', 'servlet', 'jsp'
            ])
        )
        
        # If it's just a course name without clear intent (no syllabus/notes keywords), ask for clarification
        is_ambiguous_course_name = (
            looks_like_course_name and
            not any(keyword in query_lower for keyword in syllabus_keywords) and
            not any(keyword in query_lower for keyword in notes_keywords)
        )
        
        if is_ambiguous_course_name:
            print(f"❓ Ambiguous query - asking for clarification")
            clarification_message = f"I found the subject **{query}**. What would you like?\n\n"
            clarification_message += "• **Syllabus** - Course structure, units, textbooks, and curriculum\n"
            clarification_message += "• **Notes** - Study materials, PDFs, and lecture notes\n\n"
            clarification_message += "Please specify:\n"
            clarification_message += "- \"syllabus for {query}\" or \"{query} syllabus\"\n"
            clarification_message += "- \"notes for {query}\" or \"{query} notes\""
            
            return {
                "response": clarification_message,
                "sources": [],
                "pdf_files": [],
                "has_pdfs": False,
                "agent": "router_agent",
                "result_data": None
            }
        
        # If it has syllabus keywords, course code, or looks like a course name with syllabus intent, try syllabus first
        if any(keyword in query_lower for keyword in syllabus_keywords) or has_course_code or (looks_like_course_name and 'syllabus' in query_lower):
            print(f"🎯 Routing to syllabus_agent")
            result = syllabus_agent.process_query(query)
            
            # Wrap syllabus_data in a dictionary for result_data
            syllabus_data = result.get("syllabus_data")
            result_data = {"syllabus": syllabus_data} if syllabus_data else {}
            
            # If syllabus agent found something, return it
            if syllabus_data or ("found" in result.get("response", "").lower() or "syllabus" in result.get("response", "").lower()):
                # Check if response indicates success (not "couldn't find")
                response_lower = result.get("response", "").lower()
                if "couldn't find" not in response_lower and "no syllabus found" not in response_lower:
                    return {
                        "response": result.get("response", ""),
                        "sources": [],
                        "pdf_files": [],
                        "has_pdfs": False,
                        "agent": "syllabus_agent",
                        "result_data": result_data
                    }
            
            # If syllabus agent didn't find anything but it looks like a course name, 
            # still return syllabus response (don't fall back to notes)
            if looks_like_course_name:
                return {
                    "response": result.get("response", ""),
                    "sources": [],
                    "pdf_files": [],
                    "has_pdfs": False,
                    "agent": "syllabus_agent",
                    "result_data": result_data
                }
        
        # If it has notes keywords or looks like a course name with notes intent, use notes agent
        if any(keyword in query_lower for keyword in notes_keywords) or (looks_like_course_name and any(keyword in query_lower for keyword in notes_keywords)):
            print(f"🎯 Routing to notes_agent")
            result = notes_agent.search_notes(query, db)
            return {
                "response": result.get("response", ""),
                "sources": result.get("sources", []),
                "pdf_files": result.get("pdf_files", []),
                "has_pdfs": result.get("has_pdfs", False),
                "agent": "notes_agent",
                "result_data": None
            }
        
        # Otherwise, use notes agent (default for general queries)
        print(f"🎯 Routing to notes_agent")
        result = notes_agent.search_notes(query, db)
        return {
            "response": result.get("response", ""),
            "sources": result.get("sources", []),
            "pdf_files": result.get("pdf_files", []),
            "has_pdfs": result.get("has_pdfs", False),
            "agent": "notes_agent",
            "result_data": None
        }

# Create singleton instance
router_agent = RouterAgent()

