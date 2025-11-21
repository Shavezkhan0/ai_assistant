from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StudentResult(Base):
    __tablename__ = "student_results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)  # Enrollment number
    student_name = Column(String)
    programme = Column(String, nullable=True)  # e.g., B.Tech
    branch = Column(String, nullable=True)  # e.g., Computer Science and Engineering
    institute = Column(String, nullable=True)  # Institute name
    subject = Column(String)
    marks = Column(Float)
    grade = Column(String)
    semester = Column(String)
    # Additional fields for detailed results
    paper_id = Column(String, nullable=True)  # Paper ID like "027302"
    internal_marks = Column(Float, nullable=True)  # Internal assessment marks
    external_marks = Column(Float, nullable=True)  # External assessment marks
    credits = Column(Integer, nullable=True)  # Credit hours for the subject

class NotesMetadata(Base):
    __tablename__ = "notes_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String)
    stored_filename = Column(String)  # UUID-based filename on disk
    subject = Column(String)
    topic = Column(String)
    file_size = Column(Integer)  # Size in bytes
    file_path = Column(String)
    chunk_count = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)

class Syllabus(Base):
    __tablename__ = "syllabus"
    
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String)
    department = Column(String)
    semester = Column(String)
    credits = Column(Integer)
    syllabus_content = Column(Text)