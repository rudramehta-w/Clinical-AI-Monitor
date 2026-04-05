import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class ClinicalPaper(Base):
    __tablename__ = 'clinical_papers'

    id = Column(Integer, primary_key=True)
    pubmed_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    
    # AI Processing Fields
    ai_summary = Column(Text, nullable=True)
    clinical_relevance_score = Column(Integer, nullable=True) 
    
    # Explainable Factors (Roadmap Item 3)
    study_type = Column(String, nullable=True) 
    sample_size = Column(Integer, nullable=True)
    
    # Evaluation Layer (Roadmap Item 1)
    eval_score = Column(Float, nullable=True) 
    
    # Feedback Loop (Roadmap Item 10)
    user_feedback = Column(Integer, nullable=True) 
    corrected_relevance = Column(Integer, nullable=True) 
    
    date_added = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ClinicalPaper(pubmed_id='{self.pubmed_id}', title='{self.title[:30]}...')>"

DB_URL = "sqlite:///data/clinical_monitor.db" 
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db() -> None:
    logging.info("Creating updated database tables...")
    Base.metadata.create_all(bind=engine)
    logging.info("Success! Database initialized with Evaluation and Feedback layers.")

if __name__ == "__main__":
    init_db()