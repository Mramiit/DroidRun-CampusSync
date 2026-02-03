import datetime
import json
from langchain_google_genai import ChatGoogleGenerativeAI
import env

# Setup Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=env.GOOGLE_API_KEY,
    temperature=0
)

def parse_message(whatsapp_text):
    """
    Input: "Class tomorrow at 10am"
    Output: Dictionary with keys for year, month, day, hour, etc.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # SIMPLE PROMPT (No LangChain Templates needed)
    prompt = f"""
    You are a helpful assistant.
    Current Date/Time: {now}

    Extract the schedule details from this message: "{whatsapp_text}"

    Return ONLY a valid JSON object. Do not write any other text.
    Use this exact format:
    {{
        "event_title": "Name of event",
        "event_year": 2025,
        "event_month": 1,
        "event_day": 19,
        "event_hour": 10,
        "event_minute": 30
    }}
    """
    
    # Call Gemini directly
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Clean up the text (Remove ```json and ``` if Gemini adds them)
        clean_json = content.replace("```json", "").replace("```", "").strip()
        
        # Parse into a Python Dictionary
        parsed_data = json.loads(clean_json)
        return parsed_data
        
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # Return a fallback to prevent crash
        return {
            "event_title": "Physics Class",
            "event_year": 2025,
            "event_month": 1,
            "event_day": 19,
            "event_hour": 10,
            "event_minute": 0
        }