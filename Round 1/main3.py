import os
import time
import datetime
import subprocess
import re

# --- LANGCHAIN & GEMINI IMPORTS ---
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

# --- CONFIGURATION ---

os.environ["GOOGLE_API_KEY"] = "AIzaSyA27v2WwM1WL2H7UYUfTcjaay_IoomNjcU"

DEVICE_ID = "emulator-5554" 
TARGET_CONTACT = "Amit Kumar"

# --- 1. THE CONTROLLER (Standard ADB Wrapper) ---
class PhoneController:
    """
    Controls the Android device via ADB. 
    """
    def __init__(self, device_id):
        self.device_id = device_id
        print(f"[*] Connected to {self.device_id}")

    def _shell(self, cmd):
        # Run ADB command
        full_cmd = f"adb -s {self.device_id} shell {cmd}"
        subprocess.run(full_cmd, shell=True, stdout=subprocess.DEVNULL)

    def open_app(self, package):
        print(f"[*] Opening {package}...")
        self._shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        time.sleep(2)

    def tap(self, x, y):
        self._shell(f"input tap {x} {y}")
        time.sleep(1)

    def type(self, text):
        # Replace spaces with %s for ADB input
        clean_text = text.replace(" ", "%s")
        self._shell(f"input text {clean_text}")
        time.sleep(1)

    def find_and_tap(self, identifier, type='id'):
        # Dump UI to XML
        os.system(f"adb -s {self.device_id} shell uiautomator dump /sdcard/window_dump.xml > nul 2>&1")
        os.system(f"adb -s {self.device_id} pull /sdcard/window_dump.xml . > nul 2>&1")

        if not os.path.exists("window_dump.xml"):
            return False

        with open("window_dump.xml", "r", encoding="utf-8") as f:
            xml = f.read()

        # Regex to find coordinates based on ID, Text, or Description
        if type == 'id':
            pattern = f'resource-id="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        elif type == 'text':
            pattern = f'text="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        elif type == 'desc':
            pattern = f'content-desc="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        
        match = re.search(pattern, xml)
        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"    -> Tapping '{identifier}' at ({center_x}, {center_y})")
            self.tap(center_x, center_y)
            return True
        return False

    def get_text_from_id(self, resource_id):
        # Extract text from a specific UI element
        os.system(f"adb -s {self.device_id} shell uiautomator dump /sdcard/window_dump.xml > nul 2>&1")
        os.system(f"adb -s {self.device_id} pull /sdcard/window_dump.xml . > nul 2>&1")
        try:
            with open("window_dump.xml", "r", encoding="utf-8") as f:
                xml = f.read()
            pattern = f'resource-id="{resource_id}"[^>]*text="([^"]+)"'
            match = re.search(pattern, xml)
            return match.group(1) if match else None
        except:
            return None

# Initialize Controller
phone = PhoneController(DEVICE_ID)

# --- 2. LANGCHAIN TOOLS (The "Arms" of the Agent) ---

@tool
def get_whatsapp_message(contact_name: str) -> str:
    """
    Opens WhatsApp, searches for a contact, and returns the latest message text.
    """
    try:
        phone.open_app("com.whatsapp")
        time.sleep(1)
        
        # Search for contact
        if not phone.find_and_tap("com.whatsapp:id/search_icon", type='id'):
             phone.find_and_tap("Search", type='desc')
             
        phone.type(contact_name)
        time.sleep(1)
        
        # Read the message preview
        msg_text = phone.get_text_from_id("com.whatsapp:id/single_msg_tv")
        
        # Tap to open chat (clears notification)
        phone.find_and_tap(contact_name, type='text')
        
        if msg_text:
            return msg_text
        return "No message found."
    except Exception as e:
        return f"Error reading WhatsApp: {e}"

@tool
def create_calendar_event(event_title: str) -> str:
    """
    Opens Google Calendar and types in the event title.
    """
    try:
        phone.open_app("com.google.android.calendar")
        
        # Click + button
        if not phone.find_and_tap("com.google.android.calendar:id/floating_action_button", type='id'):
            phone.find_and_tap("Create new event", type='desc')
        
        phone.find_and_tap("Event", type='text')
        time.sleep(1)
        
        # Type Title
        phone.type(event_title)
        phone.find_and_tap("Save", type='text')
        return "Calendar event created."
    except Exception as e:
        return f"Error creating event: {e}"

@tool
def set_alarm_clock(hour: int, minute: int) -> str:
    """
    Sets an alarm for the given hour and minute (24-hour format).
    Example: set_alarm_clock(14, 30) for 2:30 PM.
    """
    try:
        phone.open_app("com.google.android.deskclock")
        phone.find_and_tap("Alarm", type='text')
        
        # Add Alarm
        if not phone.find_and_tap("Add alarm", type='desc'):
             phone.find_and_tap("com.google.android.deskclock:id/fab", type='id')

        # Switch to Keyboard Mode
        phone.find_and_tap("com.google.android.deskclock:id/material_timepicker_mode_button", type='id')
        
        # Set Hour
        phone.find_and_tap("com.google.android.deskclock:id/material_hour_text_input", type='id')
        phone.type(str(hour))
        
        # Set Minute
        phone.find_and_tap("com.google.android.deskclock:id/material_minute_text_input", type='id')
        phone.type(str(minute))

        # Simple AM/PM Logic
        if hour >= 12:
            phone.find_and_tap("PM", type='text')
        else:
            phone.find_and_tap("AM", type='text')
            
        phone.find_and_tap("OK", type='text')
        return f"Alarm set for {hour}:{minute}"
    except Exception as e:
        return f"Error setting alarm: {e}"

# --- 3. MAIN AGENT LOGIC ---

def main():
    # SWITCHED TO GEMINI HERE
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # Fast and efficient
        temperature=0
    )

    tools = [get_whatsapp_message, create_calendar_event, set_alarm_clock]

    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # We give the agent the current time so it can calculate "Tomorrow" or "In 2 hours"
    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    prompt = f"""
    You are an automated assistant managing an Android phone.
    Current Date/Time: {current_time_str}
    
    INSTRUCTIONS:
    1. Read the latest WhatsApp message from '{TARGET_CONTACT}'.
    2. If the message mentions a class or meeting time, create a Calendar Event for it.
    3. Calculate a time 30 minutes BEFORE that event and set an Alarm for that time.
    
    Example: If message is "Class at 10 AM", set alarm for 09:30.
    """

    print("[-] Launching Gemini Agent...")
    try:
        agent.run(prompt)
    except Exception as e:
        print(f"Agent Error: {e}")

if __name__ == "__main__":
    main()