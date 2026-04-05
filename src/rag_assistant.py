import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from google import genai
from dotenv import load_dotenv
from vector_store import semantic_search

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_medical_rag(user_query: str) -> str:
    logging.info(f"Searching vector database for: '{user_query}'...")
    
    # 1. RETRIEVAL: Find the most relevant papers in our local FAISS index
    relevant_papers = semantic_search(user_query, k=3)
    
    if not relevant_papers:
        return "I couldn't find any relevant papers in the database to answer that."

    # 2. CONTEXT BUILDING: Combine the retrieved abstracts into one string
    context_text = "\n\n".join([f"Source {i+1} ({p.title}): {p.abstract}" for i, p in enumerate(relevant_papers)])
    
    # 3. GENERATION: Ask Gemini to answer using ONLY the provided context
    prompt = f"""
    You are a Clinical Research Assistant. Answer the user's question using ONLY the provided context from medical research papers.
    If the answer is not in the context, say that you don't have enough information.
    
    CONTEXT:
    {context_text}
    
    USER QUESTION:
    {user_query}
    
    INSTRUCTIONS:
    - Cite the papers you use (e.g., "According to Source 1...").
    - Keep the tone professional and clinical.
    """

    logging.info("Generating answer based on retrieved context...")
    
    try:
        # Using 2.5-flash for better quota availability
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Generation Error: {e}"

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Welcome to the Clinical AI Assistant (RAG)")
    print("Type 'exit' or 'quit' to close the program.")
    print("="*50 + "\n")

    # Create an infinite loop to keep asking questions
    while True:
        # Get input from the user
        user_question = input("You: ")

        # Check if the user wants to quit
        if user_question.strip().lower() in ['exit', 'quit']:
            print("\nShutting down Clinical AI. Goodbye!")
            break

        # Skip if the user just presses Enter without typing anything
        if not user_question.strip():
            continue

        # Pass the user's input to the RAG function
        answer = ask_medical_rag(user_question)
        
        print("\n--- CLINICAL AI ASSISTANT RESPONSE ---")
        print(answer)
        print("-" * 50 + "\n")