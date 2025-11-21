from app.database.postgres_db_helper import PostgresDB
from typing import Dict, List, Optional
import json
import re

class SyllabusAgent:
    def __init__(self):
        self.name = "syllabus_agent"
        self.postgres_db = PostgresDB()
    
    def _format_syllabus_response(self, syllabus_data: Dict) -> str:
        """Format syllabus data into readable markdown response"""
        if not syllabus_data:
            return "No syllabus found."
        
        response = "📚 **Syllabus Information**\n\n"
        response += f"**Course Code:** {syllabus_data.get('course_code', 'N/A')}\n"
        response += f"**Course Name:** {syllabus_data.get('course_name', 'N/A')}\n"
        response += f"**Department:** {syllabus_data.get('department', 'N/A')}\n"
        response += f"**Semester:** {syllabus_data.get('semester', 'N/A')}\n"
        
        credits = syllabus_data.get('credits', {})
        if isinstance(credits, dict):
            response += f"**Credits:** {credits.get('C', 3)} (L:{credits.get('L', 0)}, P:{credits.get('P', 0)})\n\n"
        else:
            response += f"**Credits:** {credits}\n\n"
        
        # Course Objectives
        objectives = syllabus_data.get('objectives', [])
        if objectives:
            response += "**Course Objectives:**\n\n"
            for i, obj in enumerate(objectives, 1):
                response += f"{i}. {obj}\n"
            response += "\n"
        
        # Course Outcomes
        outcomes = syllabus_data.get('outcomes', [])
        if outcomes:
            response += "**Course Outcomes (CO):**\n\n"
            for outcome in outcomes:
                co = outcome.get('co', '')
                desc = outcome.get('description', '')
                response += f"**{co}:** {desc}\n"
            response += "\n"
        
        # Syllabus Content (Units)
        syllabus = syllabus_data.get('syllabus', {})
        if syllabus:
            response += "**Syllabus Content:**\n\n"
            for unit_name in ["UNIT-I", "UNIT-II", "UNIT-III", "UNIT-IV"]:
                unit_data = syllabus.get(unit_name, {})
                if unit_data:
                    topics = unit_data.get('topics', [])
                    if topics:
                        response += f"**{unit_name}**\n\n"
                        for topic in topics:
                            # Split topic by common delimiters for better formatting
                            if isinstance(topic, str):
                                # If topic contains commas, split them
                                if ',' in topic and len(topic) > 50:
                                    subtopics = [s.strip() for s in topic.split(',') if s.strip() and len(s.strip()) > 3]
                                    for subtopic in subtopics:
                                        if subtopic:
                                            response += f"  • {subtopic}\n"
                                else:
                                    response += f"  • {topic}\n"
                        response += "\n"
        
        # Textbooks
        textbooks = syllabus_data.get('textbooks', [])
        if textbooks:
            # Filter out invalid textbooks (CO/PO mapping, instructions, etc.)
            valid_textbooks = []
            for book in textbooks:
                title = book.get('title', '')
                author = book.get('author', '')
                
                # Skip if it looks like instructions or CO/PO mapping
                if re.search(r'PO\d+|CO\s*\d+|Course\s*Objectives?|Course\s*Outcomes?|mapping.*scale|requirement.*calculators|log.*tables', 
                           f"{title} {author}", re.IGNORECASE):
                    continue
                
                # Skip if too short or too long (likely invalid)
                if not title or len(title) < 5 or len(title) > 200:
                    continue
                
                valid_textbooks.append(book)
            
            if valid_textbooks:
                response += "**Textbooks:**\n\n"
                for book in valid_textbooks:
                    num = book.get('number', '')
                    author = book.get('author', '')
                    title = book.get('title', '')
                    publisher = book.get('publisher', '')
                    
                    # Clean up quotes and dashes
                    title = title.replace('"', '').replace("'", '').strip()
                    author = author.replace('"', '').replace("'", '').strip()
                    publisher = publisher.replace('"', '').replace("'", '').strip()
                    
                    # Remove leading dash from title if present
                    if title.startswith('-'):
                        title = title[1:].strip()
                    
                    # Remove trailing periods from publisher
                    if publisher.endswith('.'):
                        publisher = publisher[:-1].strip()
                    
                    if author and title:
                        response += f"{num}. {author}, \"{title}\", {publisher}\n"
                    elif title:
                        response += f"{num}. {title}\n"
                response += "\n"
        
        # References
        references = syllabus_data.get('references', [])
        if references:
            # Filter out invalid references (CO/PO mapping, instructions, etc.)
            valid_references = []
            for ref in references:
                title = str(ref.get('title', '')).strip()
                author = str(ref.get('author', '')).strip()
                publisher = str(ref.get('publisher', '')).strip()
                
                # Skip if empty
                if not title:
                    continue
                
                # Skip if it looks like instructions or CO/PO mapping
                full_text = f"{title} {author} {publisher}".lower()
                if (re.search(r'po\d+|po01|po02|po03|po04|po05|po06|po07|po08|po09|po10|po11|po12|co\s*\d+\s+[\d\-]|course\s*objectives?|course\s*outcomes?|mapping.*scale|requirement.*calculators|log.*tables|data.*tables|scientific.*calculators', 
                           full_text, re.IGNORECASE)):
                    continue
                
                # Skip if it contains CO/PO mapping numbers pattern (like "3 2 2 3 2")
                if re.search(r'^\d+\s+\d+\s+\d+\s+\d+', title) or re.search(r'\d+\s+\d+\s+\d+\s+\d+\s+\d+', title):
                    continue
                
                # Skip if title is too short or too long (likely invalid)
                if len(title) < 5 or len(title) > 200:
                    continue
                
                # Skip if it looks like CO/PO mapping row (contains only numbers and dashes)
                if re.match(r'^[\d\s\-]+$', title):
                    continue
                
                valid_references.append(ref)
            
            if valid_references:
                response += "**References:**\n\n"
                for ref in valid_references:
                    num = ref.get('number', '')
                    author = ref.get('author', '')
                    title = ref.get('title', '')
                    publisher = ref.get('publisher', '')
                    
                    # Clean up quotes and dashes
                    title = title.replace('"', '').replace("'", '').strip()
                    author = author.replace('"', '').replace("'", '').strip()
                    publisher = publisher.replace('"', '').replace("'", '').strip()
                    
                    # Remove leading dash from title if present
                    if title.startswith('-'):
                        title = title[1:].strip()
                    
                    # Remove trailing periods from publisher
                    if publisher.endswith('.'):
                        publisher = publisher[:-1].strip()
                    
                    if author and title:
                        response += f"{num}. {author}, \"{title}\", {publisher}\n"
                    elif title:
                        response += f"{num}. {title}\n"
        
        return response.strip()
    
    def search_syllabus(self, query: str) -> Dict:
        """Search for syllabus by course name or code"""
        # Extract course code if present (pattern: XXX-###T or XXX-###)
        code_match = re.search(r'([A-Z]{2,4}-\d{3}[TP]?)', query.upper())
        
        if code_match:
            course_code = code_match.group(1)
            result = self.postgres_db.get_syllabus_by_code(course_code)
            if result:
                try:
                    # Try to parse as JSON first
                    if isinstance(result.get('syllabus_content'), str):
                        syllabus_content = json.loads(result['syllabus_content'])
                    else:
                        syllabus_content = result.get('syllabus_content', {})
                    
                    # Merge database fields with JSON content
                    syllabus_data = {
                        **syllabus_content,
                        'course_code': result.get('course_code'),
                        'course_name': syllabus_content.get('course_name') or result.get('course_name'),
                        'department': syllabus_content.get('department') or result.get('department'),
                        'semester': syllabus_content.get('semester') or result.get('semester'),
                        'credits': syllabus_content.get('credits') or result.get('credits')
                    }
                    
                    return {
                        "found": True,
                        "syllabus_data": syllabus_data
                    }
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error parsing JSON for course code {course_code}: {e}")
                    # Fallback: return raw data
                    return {
                        "found": True,
                        "syllabus_data": {
                            'course_code': result.get('course_code'),
                            'course_name': result.get('course_name'),
                            'department': result.get('department'),
                            'semester': result.get('semester'),
                            'credits': result.get('credits'),
                            'syllabus_content': result.get('syllabus_content')
                        }
                    }
        
        # Search by course name (case-insensitive partial match)
        # Clean query - remove common words but keep the core course name
        search_query = query.lower()
        # Remove common query words but keep course name parts (don't remove "in" as it's part of course names like "Programming in Python")
        search_query = re.sub(r'\b(syllabus|of|for|course|show|give|me|get|the|a|an|please|can|you|want)\b', '', search_query).strip()
        search_query = ' '.join(search_query.split())  # Clean extra spaces
        
        # Try search by name first - prioritize exact or close matches
        if search_query:
            # First try with the cleaned query
            result = self.postgres_db.search_syllabus_by_name(search_query)
            
            # If no result and query contains "python", try searching for courses with "python" in name
            if not result and 'python' in search_query:
                result = self.postgres_db.search_syllabus_by_name('python')
            
            # If no result and query contains "programming", try searching for courses with both words
            if not result and 'programming' in search_query:
                # Extract key words
                words = [w for w in search_query.split() if len(w) > 3]
                if len(words) >= 2:
                    # Try matching all key words
                    result = self.postgres_db.search_syllabus_by_name(' '.join(words))
        if result:
            try:
                # Try to parse as JSON first
                if isinstance(result.get('syllabus_content'), str):
                    syllabus_content = json.loads(result['syllabus_content'])
                else:
                    syllabus_content = result.get('syllabus_content', {})
                
                # Merge database fields with JSON content
                syllabus_data = {
                    **syllabus_content,
                    'course_code': result.get('course_code'),
                    'course_name': syllabus_content.get('course_name') or result.get('course_name'),
                    'department': syllabus_content.get('department') or result.get('department'),
                    'semester': syllabus_content.get('semester') or result.get('semester'),
                    'credits': syllabus_content.get('credits') or result.get('credits')
                }
                
                return {
                    "found": True,
                    "syllabus_data": syllabus_data
                }
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing JSON for course: {query}: {e}")
                # Fallback: return raw data
                return {
                    "found": True,
                    "syllabus_data": {
                        'course_code': result.get('course_code'),
                        'course_name': result.get('course_name'),
                        'department': result.get('department'),
                        'semester': result.get('semester'),
                        'credits': result.get('credits'),
                        'syllabus_content': result.get('syllabus_content')
                    }
                }
        
        # Try general search if name search didn't work
        # This searches in course_name, course_code, and syllabus_content
        if search_query:
            results = self.postgres_db.search_syllabus(search_query)
            if results:
                # Find the best matching result by checking JSON course_name first
                best_result = None
                best_score = 0
                
                for result in results:
                    score = 0
                    # Check if JSON has matching course_name
                    try:
                        if isinstance(result.get('syllabus_content'), str):
                            content_str = result['syllabus_content'].strip()
                            if content_str.startswith('{'):
                                json_data = json.loads(content_str)
                                json_course_name = json_data.get('course_name', '').lower()
                                # Check if query matches JSON course name (highest priority)
                                if search_query.lower() in json_course_name or all(word in json_course_name for word in search_query.split()):
                                    score += 100
                                # Check if any query word is in JSON course name
                                for word in search_query.split():
                                    if len(word) > 3 and word in json_course_name:
                                        score += 20
                    except:
                        pass
                    
                    # Check database course_name match
                    db_course_name = result.get('course_name', '').lower()
                    if search_query.lower() in db_course_name:
                        score += 50
                    
                    if score > best_score:
                        best_score = score
                        best_result = result
                
                # If no best result found, use first one
                if not best_result:
                    best_result = results[0]
                try:
                    # Try to parse as JSON first
                    if isinstance(best_result.get('syllabus_content'), str):
                        # Check if it's valid JSON
                        content_str = best_result['syllabus_content'].strip()
                        if content_str.startswith('{') or content_str.startswith('['):
                            syllabus_content = json.loads(content_str)
                        else:
                            # Not JSON, use raw content
                            syllabus_content = {}
                            syllabus_content['syllabus_content'] = content_str
                    else:
                        syllabus_content = best_result.get('syllabus_content', {})
                    
                    # Merge database fields with JSON content
                    if isinstance(syllabus_content, dict):
                        syllabus_data = {
                            **syllabus_content,
                            'course_code': best_result.get('course_code'),
                            'course_name': syllabus_content.get('course_name') or best_result.get('course_name'),
                            'department': syllabus_content.get('department') or best_result.get('department'),
                            'semester': syllabus_content.get('semester') or best_result.get('semester'),
                            'credits': syllabus_content.get('credits') or best_result.get('credits')
                        }
                    else:
                        # Fallback if not dict
                        syllabus_data = {
                            'course_code': best_result.get('course_code'),
                            'course_name': best_result.get('course_name'),
                            'department': best_result.get('department'),
                            'semester': best_result.get('semester'),
                            'credits': best_result.get('credits'),
                            'syllabus_content': syllabus_content
                        }
                    
                    return {
                        "found": True,
                        "syllabus_data": syllabus_data
                    }
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error parsing JSON: {e}")
                    # Fallback: return raw data
                    syllabus_data = {
                        'course_code': best_result.get('course_code'),
                        'course_name': best_result.get('course_name'),
                        'department': best_result.get('department'),
                        'semester': best_result.get('semester'),
                        'credits': best_result.get('credits'),
                        'syllabus_content': best_result.get('syllabus_content', '')
                    }
                    return {
                        "found": True,
                        "syllabus_data": syllabus_data
                    }
        
        return {
            "found": False,
            "syllabus_data": None
        }
    
    def process_query(self, query: str) -> Dict:
        """Process syllabus query and return formatted response"""
        result = self.search_syllabus(query)
        
        if result["found"]:
            response = self._format_syllabus_response(result["syllabus_data"])
            return {
                "response": response,
                "syllabus_data": result["syllabus_data"],
                "agent": "syllabus_agent"
            }
        else:
            return {
                "response": f"I couldn't find syllabus for '{query}'. Please check the course name or code.\n\nAvailable courses:\n• Advanced Java Programming\n• Artificial Intelligence\n• Programming in Python\n• Web Technologies\n• Statistics, Statistical Modelling & Data Analytics\n• Principles of Management for Engineers\n• Universal Human Values",
                "syllabus_data": None,
                "agent": "syllabus_agent"
            }

# Create singleton instance
syllabus_agent = SyllabusAgent()
