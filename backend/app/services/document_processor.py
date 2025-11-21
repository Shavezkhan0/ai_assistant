from PyPDF2 import PdfReader
from typing import List
import re

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file with improved extraction"""
        try:
            reader = PdfReader(file_path)
            text = ""
            page_count = 0
            
            for page in reader.pages:
                page_count += 1
                page_text = page.extract_text()
                
                # Normalize whitespace but preserve structure
                # Replace multiple spaces with single space, but keep newlines
                page_text = re.sub(r'[ \t]+', ' ', page_text)
                page_text = re.sub(r'\n\s*\n', '\n\n', page_text)  # Normalize multiple newlines
                
                text += page_text + "\n"
                
                # Progress indicator for large PDFs
                if page_count % 50 == 0:
                    print(f"   📄 Extracted text from {page_count} pages...")
            
            print(f"✅ Extracted text from {page_count} pages")
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end within overlap range
                for i in range(end, max(start, end - self.chunk_overlap), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks