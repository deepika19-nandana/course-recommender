import sqlite3
import pytest
from fastapi.testclient import TestClient
from main import app
from db import init_db, DB_NAME

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    yield

def test_database_initialization():
    """Verify that tables exist and can be queried."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    assert "roadmaps" in tables
    assert "daily_tasks" in tables

def test_get_all_roadmaps_endpoint():
    """Verify GET /api/roadmaps returns a 200 status code."""
    response = client.get("/api/roadmaps")
    assert response.status_code == 200
    data = response.json()
    assert "roadmaps" in data
    assert isinstance(data["roadmaps"], list)

def test_save_and_retrieve_roadmap():
    """Test saving a complete roadmap and retrieving it from tracker."""
    sample_payload = {
        "education": "6th Sem Computer Science",
        "domain": "Embedded IoT (Job Placement)",
        "timeline_weeks": 2,
        "reasoning": "Focus on hardware fundamentals and firmware interview prep.",
        "market_trends": "Skipped basic C variables; frontier starts at RTOS.",
        "core_skills": ["C/C++", "FreeRTOS", "I2C/SPI Protocols"],
        "other_skills": ["ESP-IDF", "Logic Analyzer"],
        "mastery_guide": [
            {
                "skill": "FreeRTOS",
                "stage": "Phase 1: Core",
                "actionable_strategy": "Build queue-based task synchronization."
            }
        ],
        "tasks": [
            {
                "global_day": 1,
                "week_number": 1,
                "day_number": 1,
                "difficulty_level": "Core",
                "week_title": "Week 1: Firmware Architecture",
                "task_title": "ESP32 Memory & Task Allocation",
                "task_description": "Initialize dual-core tasks and monitor heap usage.",
                "purpose_alignment_note": "Technical interview viva questions.",
                "baseline_connection_note": "Builds directly on prior C knowledge.",
                "resource_type": "FREE",
                "resource_name": "Espressif Official Documentation",
                "resource_url": "https://docs.espressif.com"
            }
        ]
    }

    # 1. Test POST /api/save-roadmap
    save_res = client.post("/api/save-roadmap", json=sample_payload)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["success"] is True
    roadmap_id = save_data["roadmap_id"]

    # 2. Test GET /api/tracker/{roadmap_id}
    tracker_res = client.get(f"/api/tracker/{roadmap_id}")
    assert tracker_res.status_code == 200
    tracker_data = tracker_res.json()
    assert tracker_data["roadmap"]["id"] == roadmap_id
    assert len(tracker_data["tasks"]) == 1
    assert tracker_data["tasks"][0]["task_title"] == "ESP32 Memory & Task Allocation"

def test_toggle_task_completion():
    """Test checking off a task in the database checklist."""
    # Insert a guaranteed test task
    sample_payload = {
        "education": "CS Student",
        "domain": "Unit Test Track",
        "timeline_weeks": 1,
        "reasoning": "Quick test.",
        "market_trends": "Test trends.",
        "core_skills": ["Python"],
        "other_skills": ["Git"],
        "mastery_guide": [],
        "tasks": [
            {
                "global_day": 1,
                "week_number": 1,
                "day_number": 1,
                "difficulty_level": "Core",
                "week_title": "Phase 1",
                "task_title": "Test Toggle Task",
                "task_description": "Task for toggle check.",
                "purpose_alignment_note": "None",
                "baseline_connection_note": "None",
                "resource_type": "FREE",
                "resource_name": "Python Docs",
                "resource_url": "https://python.org"
            }
        ]
    }
    save_res = client.post("/api/save-roadmap", json=sample_payload)
    roadmap_id = save_res.json()["roadmap_id"]

    tracker_res = client.get(f"/api/tracker/{roadmap_id}")
    tasks = tracker_res.json()["tasks"]
    target_task_id = tasks[0]["id"]
    
    # Toggle completed -> True (1)
    patch_res = client.patch(f"/api/tasks/{target_task_id}?completed=true")
    assert patch_res.status_code == 200
    assert patch_res.json()["success"] is True

def test_generate_roadmap_validation_error():
    """Verify that malformed requests return 422 Unprocessable Entity."""
    incomplete_payload = {
        "education": "CS Student"
    }
    response = client.post("/api/generate-roadmap", json=incomplete_payload)
    assert response.status_code == 422