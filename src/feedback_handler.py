import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from database import SessionLocal, ClinicalPaper

def add_user_feedback(paper_id: int, rating: int, actual_score: int | None = None) -> None:
    """
    Allows a human to 'grade' the AI's performance.
    rating: 1 (Upvote) or -1 (Downvote)
    """
    db = SessionLocal()
    paper = db.query(ClinicalPaper).filter_by(id=paper_id).first()
    
    if paper:
        paper.user_feedback = rating
        if actual_score:
            paper.corrected_relevance = actual_score # Human correction
        db.commit()
        logging.info(f"Feedback recorded for Paper {paper_id}.")
    else:
        logging.warning(f"Paper {paper_id} not found in database.")
        
    db.close()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("HUMAN FEEDBACK TERMINAL")
    print("="*50)
    
    try:
        # 1. Ask the human for the Paper ID
        p_id_str = input("\nEnter the Paper ID you want to grade: ")
        p_id = int(p_id_str)
        
        # 2. Ask for the Upvote/Downvote
        rating_str = input("Enter Rating (1 for Good, -1 for Bad): ")
        rating = int(rating_str)
        
        # 3. Ask for the corrected score (optional)
        score_input = input("Enter your Corrected Score 1-10 (or press Enter to skip): ")
        
        # Process the optional score
        actual_score = int(score_input) if score_input.strip() else None
        
        print("\nSaving to database...")
        # Send the HUMAN'S inputs to the function
        add_user_feedback(paper_id=p_id, rating=rating, actual_score=actual_score)
        
    except ValueError:
        print("\nError: Please enter valid numbers.")