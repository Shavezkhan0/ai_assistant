from app.database.vector_db import vector_db
from app.services.llm_service import llm_service
from app.models.database_models import NotesMetadata
from app.database.postgres_db_helper import PostgresDB
from typing import Dict, List
from sqlalchemy.orm import Session

class NotesAgent:
    def __init__(self):
        self.name = "notes_agent"
        self.postgres_db = PostgresDB()
    
    def _get_unique_pdfs(self, metadatas: List[Dict]) -> List[Dict]:
        """Extract unique PDF files from search results"""
        seen_files = set()
        pdf_files = []
        
        print(f"   Processing {len(metadatas)} metadata entries...")
        
        for i, metadata in enumerate(metadatas):
            file_id = metadata.get("file_id")
            # Try different field names for filename
            filename = metadata.get("filename") or metadata.get("source", "Unknown")
            subject = metadata.get("subject", "Unknown")
            topic = metadata.get("topic", "Unknown")
            
            print(f"   [{i+1}] file_id: {file_id}, filename: {filename}")
            
            if file_id and file_id not in seen_files:
                seen_files.add(file_id)
                # Try to get full info from database
                db_info = self.postgres_db.get_file_by_id(file_id)
                if db_info:
                    pdf_info = {
                        'file_id': db_info['file_id'],
                        'filename': db_info['filename'],
                        'subject': db_info['subject'],
                        'topic': db_info['topic'],
                        'download_url': f'/api/notes/download/{db_info["file_id"]}'
                    }
                else:
                    # Fallback to metadata info
                    pdf_info = {
                        'file_id': file_id,
                        'filename': filename,
                        'subject': subject,
                        'topic': topic,
                        'download_url': f'/api/notes/download/{file_id}'
                    }
                pdf_files.append(pdf_info)
                print(f"   ✅ Added: {pdf_info['filename']}")
            else:
                print(f"   ⏭️  Skipped (duplicate or missing file_id)")
        
        return pdf_files
    
    def process_query(self, query: str) -> dict:
        """Process a query and return relevant notes"""
        try:
            print(f"\n🔍 Searching for: {query}")
            
            query_lower = query.lower().strip()
            
            # Check if query is actually about notes/studies or just casual
            casual_indicators = [
                'how are you', 'what are you', 'who are you', 'where are you',
                'what do you do', 'what can you do', 'tell me about yourself',
                'what is this', 'what is that', 'explain yourself'
            ]
            
            is_casual_question = any(indicator in query_lower for indicator in casual_indicators)
            
            # Search for similar content in ChromaDB
            search_results = vector_db.search(query, n_results=5)
            
            print(f"📊 ChromaDB returned {len(search_results.get('documents', []))} results")
            
            if not search_results or not search_results.get("documents") or not search_results["documents"]:
                return {
                    "response": "I couldn't find any relevant notes for your query. Please make sure you've uploaded notes on this topic.",
                    "sources": [],
                    "pdf_files": [],
                    "has_pdfs": False
                }
            
            # Get the top results
            documents = search_results["documents"]
            metadatas = search_results.get("metadatas", [])
            
            # Get unique PDF files from results
            print(f"📝 Extracting PDF files from metadata...")
            pdf_files = self._get_unique_pdfs(metadatas)
            print(f"📄 Found {len(pdf_files)} unique PDF files")
            
            # If no PDFs found from metadata, try searching by topic in query
            if len(pdf_files) == 0:
                print("⚠️  No PDFs found in metadata, trying topic search...")
                # Extract potential topic from query
                # Try to find topic keywords
                for metadata in metadatas[:3]:
                    topic = metadata.get("topic", "")
                    if topic:
                        print(f"   Trying topic: {topic}")
                        topic_pdfs = self.postgres_db.get_pdfs_by_topic(topic)
                        if topic_pdfs:
                            pdf_files = topic_pdfs
                            print(f"   ✅ Found {len(pdf_files)} PDFs by topic")
                            break
            
            # Create context from retrieved chunks
            context = "\n\n".join(documents[:5])
            
            # Generate AI response with better prompt for casual questions
            if is_casual_question:
                prompt = f"""You are a helpful college AI assistant. The user asked: "{query}"

The following notes content was found, but this question seems to be about you or a casual conversation, not about the notes themselves.

Notes Content (for context only):
{context}

Please respond naturally and helpfully. If the question is about you, explain that you're a college AI assistant that helps with notes, results, and syllabus. Be friendly and conversational. Don't force information from the notes if it's not relevant to the question."""
            else:
                prompt = f"""Based on the following notes content, answer the user's question.

Question: {query}

Notes Content:
{context}

Please provide a helpful answer based on the notes. If you're explaining concepts, be clear and educational. If the question doesn't relate to the notes content, politely say so and offer to help with what you can."""

            print(f"💭 Generating AI response...")
            llm_response = llm_service.generate_response(prompt)
            
            # Prepare sources
            sources = []
            for i, metadata in enumerate(metadatas[:5]):
                filename = metadata.get("filename") or metadata.get("source", "Unknown")
                sources.append({
                    "filename": filename,
                    "subject": metadata.get("subject", "Unknown"),
                    "topic": metadata.get("topic", "Unknown"),
                    "chunk_index": metadata.get("chunk_index", 0)
                })
            
            response_data = {
                "response": llm_response,
                "sources": sources,
                "pdf_files": pdf_files,
                "has_pdfs": len(pdf_files) > 0
            }
            
            print(f"✅ Response prepared with {len(pdf_files)} PDF files")
            print(f"   has_pdfs: {response_data['has_pdfs']}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ Notes agent error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "pdf_files": [],
                "has_pdfs": False
            }
    
    def search_notes(self, query: str, db: Session = None) -> dict:
        """Search notes and return with PDF file information"""
        result = self.process_query(query)
        
        # PDF files are already enriched in process_query via PostgresDB
        # But we can double-check with SQLAlchemy session if provided
        if result.get("pdf_files") and db:
            enriched_pdfs = []
            for pdf in result["pdf_files"]:
                file_id = pdf.get("file_id")
                if file_id:
                    # Get file metadata from database (using SQLAlchemy)
                    note = db.query(NotesMetadata).filter(
                        NotesMetadata.file_id == file_id
                    ).first()
                    
                    if note:
                        enriched_pdfs.append({
                            "file_id": note.file_id,
                            "filename": note.filename,
                            "subject": note.subject,
                            "topic": note.topic,
                            "download_url": f"/api/notes/download/{note.file_id}"
                        })
            
            if enriched_pdfs:
                result["pdf_files"] = enriched_pdfs
                result["has_pdfs"] = True
        
        return result
    
    def get_pdf_for_topic(self, topic: str) -> List[Dict]:
        """Get all PDFs related to a specific topic"""
        print(f"🔍 Getting PDFs for topic: {topic}")
        pdfs = self.postgres_db.get_pdfs_by_topic(topic)
        print(f"📄 Found {len(pdfs)} PDFs")
        return pdfs

# Create singleton instance
notes_agent = NotesAgent()