from sqlalchemy import Column, String, Text, Integer
from db.database import Base

class Challenge(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    difficulty = Column(String)
    url = Column(Text)
    starter_code = Column(Text)
    solutions = Column(Text)
    dataset_type = Column(String, nullable=False)