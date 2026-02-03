from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

from agent import run_campus_sync

app = FastAPI()

# --- 1. Database Setup ---
def init_db():
    conn = sqlite3.connect('campussync.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_config 
                 (id INTEGER PRIMARY KEY, target_contact TEXT, alarm_offset INTEGER)''')
    # REMOVED: The hardcoded INSERT line. We start fresh now.
    conn.commit()
    conn.close()

init_db()

# --- 2. Data Models ---
class UserConfig(BaseModel):
    target_contact: str
    alarm_offset: int

# --- 3. Serve Frontend ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# --- 4. API Endpoints ---

@app.get("/config")
def get_config():
    conn = sqlite3.connect('campussync.db')
    c = conn.cursor()
    c.execute("SELECT target_contact, alarm_offset FROM user_config WHERE id=1")
    data = c.fetchone()
    conn.close()
    
    # SCALABILITY FIX: If no data, return empty values so the UI knows it's a fresh user.
    if data:
        return {"target_contact": data[0], "alarm_offset": data[1]}
    else:
        return {"target_contact": "", "alarm_offset": 0}

@app.post("/config")
def update_config(config: UserConfig):
    conn = sqlite3.connect('campussync.db')
    c = conn.cursor()
    
    # Check if row exists
    c.execute("SELECT id FROM user_config WHERE id=1")
    exists = c.fetchone()
    
    if exists:
        c.execute("UPDATE user_config SET target_contact = ?, alarm_offset = ? WHERE id=1", 
                  (config.target_contact, config.alarm_offset))
    else:
        # First time setup for this user
        c.execute("INSERT INTO user_config (id, target_contact, alarm_offset) VALUES (1, ?, ?)", 
                  (config.target_contact, config.alarm_offset))
        
    conn.commit()
    conn.close()
    return {"status": "Config updated"}

@app.post("/run-agent")
async def trigger_agent():  # removed background_tasks
    conn = sqlite3.connect('campussync.db')
    c = conn.cursor()
    c.execute("SELECT target_contact, alarm_offset FROM user_config WHERE id=1")
    row = c.fetchone()
    conn.close()

    if not row or not row[0]:
        raise HTTPException(status_code=400, detail="Configuration missing. Please save settings first.")

    target, offset = row

    # CHANGED: We now 'await' the function. The browser will wait here until it's done.
    try:
        result = await run_campus_sync(target, offset)
        
        # Check if the agent actually succeeded
        if result["success"]:
            return {"status": "success", "message": "Class scheduled to Calendar and Clock"}
        else:
            return {"status": "failed", "message": "Agent failed to schedule."}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))