from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    content_preview = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.file_type}')>"

class MetadataStore:
    def __init__(self):
        db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_document(self, title, file_path, file_type, file_size, content_preview):
        doc = Document(
            title=title,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            content_preview=content_preview
        )
        self.session.add(doc)
        self.session.commit()
        return doc.id
    
    def get_document(self, doc_id):
        return self.session.query(Document).filter(Document.id == doc_id).first()
    
    def get_all_documents(self):
        return self.session.query(Document).all()
    
    def mark_processed(self, doc_id):
        doc = self.get_document(doc_id)
        if doc:
            doc.processed = 1
            self.session.commit()
    
    def delete_document(self, doc_id):
        doc = self.get_document(doc_id)
        if doc:
            self.session.delete(doc)
            self.session.commit()
    
    def close(self):
        self.session.close()