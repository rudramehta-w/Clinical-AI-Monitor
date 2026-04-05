import os
import smtplib
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from database import SessionLocal, ClinicalPaper
from datetime import datetime, timedelta

load_dotenv()
SENDER_EMAIL = os.getenv("GMAIL_ADDRESS")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL # Sending it to yourself for the MVP

def send_daily_digest() -> None:
    db = SessionLocal()
    
    # Grab papers added in the last 24 hours, ordered by the AI's relevance score
    yesterday = datetime.utcnow() - timedelta(days=1)
    top_papers = db.query(ClinicalPaper)\
                   .filter(ClinicalPaper.date_added >= yesterday)\
                   .filter(ClinicalPaper.clinical_relevance_score != None)\
                   .order_by(ClinicalPaper.clinical_relevance_score.desc())\
                   .limit(5).all()

    if not top_papers:
        logging.info("No new papers to report today.")
        return

    logging.info(f"Formatting email digest for {len(top_papers)} top papers...")

    # Build the HTML Email
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2c3e50;">Daily Clinical Intelligence Briefing</h2>
        <p>Here are the top-scoring medical papers curated by your AI agent today:</p>
        <hr>
    """

    for paper in top_papers:
        html_content += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #2980b9; margin-bottom: 5px;">Score: {paper.clinical_relevance_score}/10 | {paper.title}</h3>
            <p><strong>AI Summary:</strong><br>{paper.ai_summary.replace('- ', '<br>• ')}</p>
            <a href="https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/" style="color: #16a085;">Read Full Paper on PubMed</a>
        </div>
        """

    html_content += "</body></html>"

    # Set up the Email Server
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Top Clinical Papers - {datetime.now().strftime('%b %d, %Y')}"
    msg["From"] = str(SENDER_EMAIL)
    msg["To"] = str(RECEIVER_EMAIL)
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        if SENDER_EMAIL and APP_PASSWORD:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            server.quit()
            logging.info("SUCCESS! Check your email inbox right now.")
        else:
            logging.error("Missing Gmail credentials in environment variables.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_daily_digest()