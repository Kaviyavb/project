import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
SPACE_ID = os.getenv("GENIE_SPACE_ID")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def start_conversation(question: str):
    url = f"{HOST}/api/2.0/genie/spaces/{SPACE_ID}/start-conversation"
    resp = requests.post(url, headers=HEADERS, json={"content": question})
    resp.raise_for_status()
    data = resp.json()
    conversation_id = data.get("conversation_id")
    message_id = data.get("message_id")
    return conversation_id, message_id

def extract_full_response(result: dict) -> dict:
    attachments = result.get("attachments", [])
    text_answer = ""
    sql_query = ""
    suggested_questions = []
    statement_id = ""

    for attachment in attachments:
        # 1. Capture Text
        if "text" in attachment:
            text_answer = attachment["text"].get("content", "")
        
        # 2. Capture suggested questions
        if "suggested_questions" in attachment:
            suggested_questions = attachment["suggested_questions"].get("questions", [])

        # 3. Capture Query & Statement ID (Deep Search)
        # Check both the attachment root and nested 'query' objects
        q_obj = attachment.get("query")
        if q_obj and isinstance(q_obj, dict):
            sql_query = q_obj.get("query") or sql_query
            statement_id = q_obj.get("statement_id") or statement_id
        elif "query" in attachment and isinstance(attachment["query"], str):
            sql_query = attachment["query"]

    # Final fallback: some versions put it in the top level of message
    statement_id = statement_id or result.get("statement_id") or ""

    import sys
    print(f"DEBUG: Extracted statement_id: '{statement_id}'", flush=True)

    return {
        "answer": text_answer or "No answer found.",
        "query": sql_query,
        "statement_id": statement_id,
        "suggested_questions": suggested_questions
    }

def ask_genie(question: str) -> dict:
    conversation_id, message_id = start_conversation(question)
    url = f"{HOST}/api/2.0/genie/spaces/{SPACE_ID}/conversations/{conversation_id}/messages/{message_id}"
    
    # Polling logic remains similar but returns full response
    for _ in range(25):
        time.sleep(3)
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") == "COMPLETED":
            return extract_full_response(result)
        elif result.get("status") == "FAILED":
            return {"answer": "Sorry, Genie could not answer that.", "query": "", "suggested_questions": []}
            
    return {"answer": "Request timed out.", "query": "", "suggested_questions": []}
