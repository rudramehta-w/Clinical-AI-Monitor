import os
import json
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from google import genai
#from google.api_core import exceptions 
from dotenv import load_dotenv
from database import SessionLocal, ClinicalPaper

load_dotenv(override=True) 

# Grab the key and debug the last 4 characters so we KNOW it's the new one
api_key = os.getenv("GEMINI_API_KEY")
logging.info(f"DEBUG: Booting AI with API Key ending in: ...{api_key[-4:] if api_key else 'None'}")

client = genai.Client(api_key=api_key)

def process_unsummarized_papers() -> None:
    db = SessionLocal()
    # Find papers that haven't been summarized yet
    unprocessed_papers = db.query(ClinicalPaper).filter(ClinicalPaper.ai_summary == None).all()
    
    if not unprocessed_papers:
        logging.info("Database is up to date!")
        db.close()
        return

    logging.info(f"Found {len(unprocessed_papers)} unread papers. Starting resilient processing...")

    for paper in unprocessed_papers:
        logging.info(f"Analyzing: {paper.title[:50]}...")
        
        # Explainable Scoring (Roadmap Item 3) & Evaluation (Roadmap Item 1)
        prompt = f"""
        Analyze this medical abstract for a Clinical Research Dashboard.
        1. FACTORS: Identify Study Type (e.g. RCT, Case Study) and Sample Size.
        2. SUMMARY: 3 bullet points of findings.
        3. SCORING: 1-10 clinical relevance score.
        4. EVAL: Rate the clarity of the abstract from 0.0 to 1.0.

        Return JSON:
        {{
            "summary": "...",
            "score": 8,
            "study_type": "...",
            "sample_size": 100,
            "eval_score": 0.9
        }}
        Abstract: {paper.abstract}
        """

        # Failure Handling Logic (Roadmap Item 6)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Switched to 2.5-flash for potentially better quota availability
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt
                )
                
                clean_text = response.text.replace('```json', '').replace('```', '').strip()
                ai_data = json.loads(clean_text)
                
               # Saving explainable factors
                
                # FIX: Handle cases where the AI returns a list of bullet points instead of a string
                raw_summary = ai_data.get('summary')
                if isinstance(raw_summary, list):
                    # Join the list into a single string with line breaks
                    paper.ai_summary = "\n".join(f"• {str(item)}" for item in raw_summary)
                else:
                    paper.ai_summary = str(raw_summary)

                paper.clinical_relevance_score = ai_data.get('score')
                paper.study_type = ai_data.get('study_type')
                paper.sample_size = str(ai_data.get('sample_size')) # Ensure sample size is stringified too
                paper.eval_score = ai_data.get('eval_score')
                
                db.commit()
                logging.info(f"{paper.study_type} (N={paper.sample_size}) | Score: {paper.clinical_relevance_score}/10")
                
                # 10s cooldown to respect RPM limits
                time.sleep(10) 
                break 

            except Exception as e:
                if "429" in str(e):
                    wait = (attempt + 1) * 30 
                    logging.warning(f"Rate limited. Retrying in {wait}s... ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    logging.error(f"Error: {e}")
                    db.rollback()
                    break

    db.close()

if __name__ == "__main__":
    process_unsummarized_papers()