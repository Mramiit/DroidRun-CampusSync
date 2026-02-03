import time
import datetime
import subprocess
import re
import os
import sys

# Try importing the agent, but we probably won't use it directly
# to avoid version mismatch errors.
try:
    import droidrun
except ImportError:
    pass  # We'll use our own simple controller below

from smart_parser import parse_message

# --- CONFIGURATION ---
# TODO: PASTE YOUR REAL DEVICE ID HERE FROM 'adb devices'
DEVICE_ID = "emulator-5554" 
TARGET_NAME = "Amit Kumar"

class PhoneController:
    """
    Simple wrapper to control the phone via ADB.
    Keeps things clean without needing complex library dependencies.
    """
    def __init__(self, device_id):
        self.device_id = device_id
        print(f"[*] Connected to {self.device_id}")

    def _shell(self, cmd):
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
        # Replace spaces because ADB input text hates them
        clean_text = text.replace(" ", "%s")
        self._shell(f"input text {clean_text}")
        time.sleep(1)

    def find_and_tap(self, identifier, type='id'):
        """
        Dumps the screen, finds the coordinates of an element, and taps it.
        identifier: The text or resource-id to look for.
        type: 'id' for resource-id, 'text' for visible text, 'desc' for content-desc.
        """
        # 1. Dump UI
        os.system(f"adb -s {self.device_id} shell uiautomator dump /sdcard/window_dump.xml > nul 2>&1")
        os.system(f"adb -s {self.device_id} pull /sdcard/window_dump.xml . > nul 2>&1")

        if not os.path.exists("window_dump.xml"):
            print("[-] Failed to dump UI. Check connection.")
            return False

        with open("window_dump.xml", "r", encoding="utf-8") as f:
            xml = f.read()

        # 2. Search using Regex
        # We look for the bounds="[x1,y1][x2,y2]"
        if type == 'id':
            pattern = f'resource-id="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        elif type == 'text':
            pattern = f'text="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        elif type == 'desc':
            pattern = f'content-desc="{identifier}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        
        match = re.search(pattern, xml)
        
        if match:
            # Calculate center point
            x1, y1, x2, y2 = map(int, match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"    -> Tapping '{identifier}' at ({center_x}, {center_y})")
            self.tap(center_x, center_y)
            return True
        else:
            print(f"[-] Could not find element: {identifier}")
            return False

    def get_text_from_id(self, resource_id):
        # Quick helper to read text (like a message)
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

def main():
    #if DEVICE_ID == "PASTE_YOUR_ID_HERE":
    #    print("ERROR: You forgot to set your DEVICE_ID in the script!")
    #    return

    phone = PhoneController(DEVICE_ID)

    # --- 1. WhatsApp ---
    phone.open_app("com.whatsapp")
    
    # Search for contact
    phone.find_and_tap("com.whatsapp:id/search_icon", type='id')
    phone.type(TARGET_NAME)
    
    # Read the message preview (sneaky way to get text without opening)
    print("[*] Reading latest message...")
    msg_text = phone.get_text_from_id("com.whatsapp:id/single_msg_tv")
    
    if msg_text:
        print(f"    -> Found: {msg_text}")
    else:
        print("    -> No message found, using dummy text.")
        msg_text = "Project meeting tomorrow at 5 pm"

    # Open chat just to clear notification
    phone.find_and_tap(TARGET_NAME, type='text')
    
    # --- 2. Parse Data ---
    print("[*] Parsing schedule...")
    schedule = parse_message(msg_text)
    
    try:
        # Construct datetime objects
        event_dt = datetime.datetime(
            schedule['event_year'], schedule['event_month'], schedule['event_day'],
            schedule['event_hour'], schedule['event_minute']
        )
        alarm_dt = event_dt - datetime.timedelta(minutes=30)
        print(f"    -> Event: {schedule['event_title']} @ {event_dt}")
    except Exception as e:
        print(f"[-] Date error: {e}")
        return

    # --- 3. Calendar ---
    phone.open_app("com.google.android.calendar")
    
    # Click + button -> Event
    if not phone.find_and_tap("com.google.android.calendar:id/floating_action_button", type='id'):
        phone.find_and_tap("Create new event", type='desc') # Fallback
    
    phone.find_and_tap("Event", type='text')
    
    # Type Title
    print(f"[*] Creating Event: {schedule['event_title']}")
    phone.type(schedule['event_title']) # Cursor is usually auto-focused here
    
    # Save
    phone.find_and_tap("Save", type='text')

    # --- 4. Alarm ---
    phone.open_app("com.google.android.deskclock")
    phone.find_and_tap("Alarm", type='text')
    
    # Add Alarm
    if not phone.find_and_tap("Add alarm", type='desc'):
         # Some phones use a text button or ID
         phone.find_and_tap("com.google.android.deskclock:id/fab", type='id')

    # Switch to keyboard input (the little keyboard icon)
    print("[*] Setting time...")
    phone.find_and_tap("com.google.android.deskclock:id/material_timepicker_mode_button", type='id')
    
    # Type Hour & Minute (Clear fields first by double tapping or relying on focus)
    # We use explicit IDs for the input boxes
    phone.find_and_tap("com.google.android.deskclock:id/material_hour_text_input", type='id')
    phone.type(str(alarm_dt.hour))
    
    phone.find_and_tap("com.google.android.deskclock:id/material_minute_text_input", type='id')
    phone.type(str(alarm_dt.minute))

    # AM/PM Check
    if alarm_dt.hour >= 12:
        phone.find_and_tap("PM", type='text')
    else:
        phone.find_and_tap("AM", type='text')
        
    phone.find_and_tap("OK", type='text')
    print("[*] Done! System automated.")

if __name__ == "__main__":
    main()