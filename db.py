import sqlite3

DB_NAME = "agent_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table 1: Roadmaps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            education TEXT,
            timeline_weeks INTEGER,
            reasoning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: Daily Checkbox Tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id TEXT,
            day_number INTEGER,
            phase_title TEXT,
            task_title TEXT,
            task_description TEXT,
            is_completed INTEGER DEFAULT 0,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")