import os
import sys
import asyncio
from dotenv import load_dotenv

# Import the DroidRun framework
from droidrun import DroidAgent
from droidrun.config_manager.config_manager import DroidrunConfig, AgentConfig, LoggingConfig
from llama_index.llms.google_genai import GoogleGenAI

# Load environment variables
load_dotenv()

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found. Please check your .env file.")
    sys.exit(1)

async def main():
    print("--- Starting CampusSync Agent ---")
    
    # 1. Setup Configuration
    # We want the agent to reason through steps and save logs so we can debug later
    config = DroidrunConfig(
        agent=AgentConfig(
            max_steps=50,       # Don't let it run forever
            reasoning=True,     # Enable "Chain of Thought"
        ),
        logging=LoggingConfig(
            debug=True, 
            save_trajectory="action", # Save screenshots/logs to folder
            rich_text=True
        ),
    )

    # 2. Setup the LLM
    # Using Gemini 2.5 Flash because it's fast and smart enough for this task
    print("Initializing Gemini 2.5 Flash...")
    llm = GoogleGenAI(
        model="models/gemini-2.5-flash",
        api_key=api_key,
        temperature=0.1 # Keep it focused, not creative
    )

    # 3. Define the Goal
    # This matches the logic: Read Chat -> Calendar -> Alarm
    goal = (
        "You are my personal assistant. Please do the following tasks in order: "
        "1. Open 'WhatsApp' and search for 'Amit Kumar'. Read his last message to find the class subject and time. "
        "2. Go to the 'Calendar' app and create a new event for that class at the correct time. "
        "3. Open the 'Clock' app and set an alarm for 30 minutes before the class starts. "
        "4. Go back to the home screen when you are done."
    )

    print(f"Goal set: {goal}")

    # 4. Create the Agent
    agent = DroidAgent(
        goal=goal,
        config=config,
        llms=llm,
    )

    # 5. Run it!
    print("Agent is running... (Check the emulator screen)")
    result = await agent.run()

    # 6. Show results
    if result.success:
        print("\nSuccess! The agent completed the task.")
        print(f"Reasoning: {result.reason}")
    else:
        print("\nFailed.")
        print(f"Error: {result.reason}")

if __name__ == "__main__":
    # Ignore the google deprecation warnings that clog up the terminal
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")