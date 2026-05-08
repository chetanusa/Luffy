import re
from typing import List

class DocumentPreprocessor:
    """Clean and chunk documents for processing"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)]', '', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def process_document(text: str, chunk_size: int = 1000) -> dict:
        """Process document: clean and chunk"""
        cleaned = DocumentPreprocessor.clean_text(text)
        chunks = DocumentPreprocessor.chunk_text(cleaned, chunk_size=chunk_size)
        
        return {
            'cleaned_text': cleaned,
            'chunks': chunks,
            'num_chunks': len(chunks),
            'total_words': len(cleaned.split()),
            'total_chars': len(cleaned)
        }