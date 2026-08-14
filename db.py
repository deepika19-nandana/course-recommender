import sqlite3

DB_NAME = "agent_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Roadmaps Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id TEXT PRIMARY KEY,
            domain TEXT,
            education TEXT,
            timeline_weeks INTEGER,
            reasoning TEXT,
            market_trends TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Daily Tasks Table (Matches main.py insertion columns exactly)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id TEXT,
            day_number INTEGER,
            phase_title TEXT,
            task_title TEXT,
            task_description TEXT,
            is_completed INTEGER DEFAULT 0,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id)
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with exact matching columns.")
