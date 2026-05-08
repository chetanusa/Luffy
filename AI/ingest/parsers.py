from pathlib import Path
from typing import Optional
import PyPDF2
import docx
import markdown

class DocumentParser:
    """Parse different document types and extract text"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return '\n'.join(text)
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """Extract text from Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # Convert markdown to plain text (remove formatting)
            html = markdown.markdown(content)
            # Simple HTML tag removal
            import re
            text = re.sub(r'<[^>]+>', '', html)
            return text
        except Exception as e:
            raise Exception(f"Error parsing Markdown: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error parsing TXT: {str(e)}")
    
    @staticmethod
    def parse_document(file_path: str) -> Optional[str]:
        """Auto-detect file type and parse"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        parsers = {
            '.pdf': DocumentParser.parse_pdf,
            '.docx': DocumentParser.parse_docx,
            '.doc': DocumentParser.parse_docx,
            '.md': DocumentParser.parse_markdown,
            '.markdown': DocumentParser.parse_markdown,
            '.txt': DocumentParser.parse_txt,
        }
        
        parser = parsers.get(extension)
        if parser:
            return parser(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    @staticmethod
    def get_preview(text: str, max_length: int = 500) -> str:
        """Get preview of text"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."