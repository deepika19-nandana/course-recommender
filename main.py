import os
import time
import json
import uuid
import sqlite3
from typing import List, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from db import init_db, DB_NAME

load_dotenv()
init_db()

app = FastAPI(title="Universal 6-Constraint Adaptive Roadmap Engine")

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key and api_key != "your_gemini_api_key_here" else None

# Pydantic Schemas with Strict Enum & Literal Validation
class DailyTaskItem(BaseModel):
    global_day: int
    week_number: int
    day_number: int
    difficulty_level: str          # "Foundational", "Intermediate", "Advanced / Mastery"
    week_title: str
    task_title: str
    task_description: str
    purpose_alignment_note: str    # How this day serves user's specific purpose
    baseline_connection_note: str  # How this builds directly on their existing skills
    resource_type: Literal["FREE", "PAID"] = Field(description="Must be strictly 'FREE' or 'PAID'")
    resource_name: str            # Real documentation, YouTube channel, book, or certified course
    resource_url: str             # Verified live deep link

class MasteryGuideItem(BaseModel):
    pillar_topic: str
    progression_stage: str
    actionable_strategy: str

class AIResponseSchema(BaseModel):
    domain_summary: str
    education_calibration: str
    skills_gap_audit: str
    purpose_deliverable_plan: str
    budget_adherence_summary: str
    core_competencies: List[str]
    tooling_and_methods: List[str]
    mastery_guide: List[MasteryGuideItem]
    roadmap: List[DailyTaskItem]

class GenerateRequest(BaseModel):
    education: str
    goal_type: str
    goal_name: str
    purpose_of_study: str
    existing_skills: str
    cost_preference: str
    timeline_weeks: int

class SaveRequest(BaseModel):
    education: str
    domain: str
    timeline_weeks: int
    reasoning: str
    market_trends: str
    core_skills: List[str]
    other_skills: List[str]
    mastery_guide: List[dict]
    tasks: List[dict]

CACHED_WORKING_MODEL = None

def get_candidate_models() -> List[str]:
    pool = []
    if client:
        try:
            for m in client.models.list():
                name = getattr(m, "name", "").replace("models/", "")
                if "gemini" in name.lower() and not any(x in name.lower() for x in ["embed", "imagen"]):
                    pool.append(name)
        except Exception as e:
            print(f"⚠️ Model query notice: {e}")

    defaults = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    for d in defaults:
        if d not in pool:
            pool.append(d)
    return pool

# ==============================================================================
# 1. UNIVERSAL AI ROADMAP GENERATOR
# ==============================================================================
@app.post("/api/generate-roadmap")
def generate_roadmap(req: GenerateRequest):
    global CACHED_WORKING_MODEL

    if not client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing in your .env file! Please add a valid key."
        )

    total_days = req.timeline_weeks * 5

    # Determine strict budget enforcement rule
    if "Free" in req.cost_preference:
        budget_instruction = "EVERY single task MUST have resource_type: 'FREE'. Use YouTube, Official Docs, GitHub, Wikipedia, or Free University OpenCourseWare. ZERO paid courses allowed."
    elif "Paid" in req.cost_preference:
        budget_instruction = "EVERY single task MUST have resource_type: 'PAID'. Use Coursera, Udemy, O'Reilly, Pluralsight, or official paid certification books."
    else:
        budget_instruction = "Tag each resource accurately as either 'FREE' or 'PAID'."

    prompt = f"""
    You are an elite, universal curriculum architect for ALL human disciplines, trades, crafts, and sciences.

    USER CONSTRAINTS:
    - TARGET DOMAIN: '{req.goal_name}' (Scope: '{req.goal_type}')
    - EDUCATION: '{req.education}'
    - CURRENT KNOWN SKILLS: '{req.existing_skills or 'None / Absolute Beginner'}'
    - PURPOSE OF STUDY: '{req.purpose_of_study}'
    - BUDGET PREFERENCE: '{req.cost_preference}'
    - TIMELINE: {req.timeline_weeks} Weeks ({total_days} total learning days, 5 days/week)

    CRITICAL RULES:
    1. BUDGET MANDATE: {budget_instruction}
    2. STRICT VALUE FOR resource_type: Must be exactly the string 'FREE' or 'PAID' (all uppercase).
    3. ZERO DOMAIN PREJUDICE: Focus 100% on '{req.goal_name}'. Do not default to programming/data science unless '{req.goal_name}' is in that field.
    4. SKILL GAP SUBTRACTION: Subtract what the student already knows ('{req.existing_skills}'). Start Day 1 at their learning frontier.
    5. PURPOSE DELIVERABLE: Calibrate all daily tasks and projects to '{req.purpose_of_study}'.
    6. NO REPETITION: Every day from Day 1 to Day {total_days} must have a unique sub-topic. Day 5 of each week is a practical sprint.
    """

    models_to_try = []
    if CACHED_WORKING_MODEL:
        models_to_try.append(CACHED_WORKING_MODEL)
    for m in get_candidate_models():
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        try:
            print(f"🚀 Generating roadmap for '{req.goal_name}' with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIResponseSchema,
                    temperature=0.2,
                )
            )
            data = json.loads(response.text)
            
            # Post-processing normalization: Ensure 100% strict adherence to user budget
            if "Free" in req.cost_preference:
                for task in data.get("roadmap", []):
                    task["resource_type"] = "FREE"
            elif "Paid" in req.cost_preference:
                for task in data.get("roadmap", []):
                    task["resource_type"] = "PAID"
            
            data["model_used"] = model_name
            CACHED_WORKING_MODEL = model_name
            print(f"✅ Generated customized roadmap for '{req.goal_name}'.")
            return {"success": True, "data": data}

        except Exception as e:
            last_error = str(e)
            print(f"⚠️ Model '{model_name}' notice: {last_error}")
            if "503" in last_error or "UNAVAILABLE" in last_error:
                time.sleep(1)
            continue

    raise HTTPException(status_code=500, detail=f"All models failed. Last error: {last_error}")

# ==============================================================================
# 2. DATABASE PERSISTENCE ENDPOINTS
# ==============================================================================
@app.post("/api/save-roadmap")
def save_roadmap(req: SaveRequest):
    roadmap_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO roadmaps (id, domain, education, timeline_weeks, reasoning, market_trends) VALUES (?, ?, ?, ?, ?, ?)",
        (roadmap_id, req.domain, req.education, req.timeline_weeks, req.reasoning, req.market_trends)
    )
    
    for task in req.tasks:
        res_type = str(task.get("resource_type", "FREE")).upper()
        res_badge = f"[{res_type}]"
        purpose_note = task.get("purpose_alignment_note", "")
        baseline_note = task.get("baseline_connection_note", "")
        
        desc_with_resource = (
            f"**Level:** {task.get('difficulty_level', 'Core')}\n\n"
            f"{task['task_description']}\n\n"
            f"🎯 **Purpose Target:** {purpose_note}\n\n"
            f"💡 **Knowledge Anchor:** {baseline_note}\n\n"
            f"🔗 **Resource {res_badge}:** [{task.get('resource_name', 'Documentation')}]({task.get('resource_url', '#')})"
        )
        cursor.execute(
            "INSERT INTO daily_tasks (roadmap_id, day_number, phase_title, task_title, task_description) VALUES (?, ?, ?, ?, ?)",
            (roadmap_id, task["global_day"], task["week_title"], task["task_title"], desc_with_resource)
        )
        
    conn.commit()
    conn.close()
    return {"success": True, "roadmap_id": roadmap_id}

@app.get("/api/roadmaps")
def get_all_roadmaps():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    roadmaps = cursor.execute("SELECT * FROM roadmaps ORDER BY created_at DESC").fetchall()
    conn.close()
    return {"roadmaps": [dict(r) for r in roadmaps]}

@app.get("/api/tracker/{roadmap_id}")
def get_tracker(roadmap_id: str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    roadmap = cursor.execute("SELECT * FROM roadmaps WHERE id = ?", (roadmap_id,)).fetchone()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    tasks = cursor.execute("SELECT * FROM daily_tasks WHERE roadmap_id = ? ORDER BY day_number ASC", (roadmap_id,)).fetchall()
    conn.close()
    return {"roadmap": dict(roadmap), "tasks": [dict(t) for t in tasks]}

@app.patch("/api/tasks/{task_id}")
def toggle_task(task_id: int, completed: bool):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    status = 1 if completed else 0
    cursor.execute("UPDATE daily_tasks SET is_completed = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    return {"success": True}