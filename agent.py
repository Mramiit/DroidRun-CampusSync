import os
import sys
import asyncio
from dotenv import load_dotenv
from droidrun import DroidAgent
from droidrun.config_manager.config_manager import DroidrunConfig, AgentConfig, LoggingConfig
from llama_index.llms.google_genai import GoogleGenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

async def run_campus_sync(target_contact: str, alarm_offset: int):
    """
    Runs the agent with dynamic parameters.
    """
    print(f"--- Starting CampusSync for target: {target_contact} ---")
    
    # 1. Setup Config
    config = DroidrunConfig(
        agent=AgentConfig(max_steps=50, reasoning=True),
        logging=LoggingConfig(debug=True, save_trajectory="action", rich_text=True),
    )

    # 2. Setup LLM
    llm = GoogleGenAI(
        model="models/gemini-2.5-flash",
        api_key=api_key,
        temperature=0.1
    )

    # 3. Dynamic Goal Construction
    # We inject the 'target_contact' variable directly into the prompt
    goal = (
        f"You are my personal assistant. You must perform this sequence EXACTLY ONCE: "
        f"1. Open 'WhatsApp', search for '{target_contact}', and read the last 10 message to find class info. "
        f"2. Go to 'Calendar' and create a SINGLE event for that class on correct day. "
        f"3. Open 'Clock' and set ONE alarm for {alarm_offset} minutes before the class. "
        f"4. Go to the home screen. "
        f"5. STOP IMMEDIATELY. Do not check for more messages. Do not verify. Just output 'Task Completed'."
    )

    # 4. Create and Run Agent
    agent = DroidAgent(goal=goal, config=config, llms=llm)
    result = await agent.run()

    return {"success": result.success, "reason": result.reason}