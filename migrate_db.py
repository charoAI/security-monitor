"""
Database migration script to update keywords to prompt
"""
import sqlite3

def migrate_database():
    conn = sqlite3.connect('security_monitor.db')
    cursor = conn.cursor()

    # Check if the table exists and has the old schema
    cursor.execute("PRAGMA table_info(scheduled_reports)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    if 'keywords' in column_names and 'prompt' not in column_names:
        print("Migrating database: keywords -> prompt")

        # Add the new prompt column
        cursor.execute("ALTER TABLE scheduled_reports ADD COLUMN prompt TEXT")

        # Copy data from keywords to prompt (if any)
        cursor.execute("UPDATE scheduled_reports SET prompt = keywords WHERE keywords IS NOT NULL")

        # Note: SQLite doesn't support dropping columns easily, so we'll leave keywords column
        # but the application will use prompt instead

        conn.commit()
        print("Migration completed successfully")
    elif 'prompt' in column_names:
        print("Database already migrated")
    else:
        print("Creating fresh table with new schema")
        # Drop old table if it exists
        cursor.execute("DROP TABLE IF EXISTS scheduled_reports")
        cursor.execute("DROP TABLE IF EXISTS report_history")

        # Create with new schema
        cursor.execute('''
            CREATE TABLE scheduled_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                countries TEXT NOT NULL,
                prompt TEXT,
                schedule_type TEXT NOT NULL,
                schedule_time TEXT NOT NULL,
                timezone TEXT DEFAULT 'America/New_York',
                email_recipients TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT,
                report_data TEXT,
                FOREIGN KEY (report_id) REFERENCES scheduled_reports (id)
            )
        ''')

        conn.commit()
        print("Fresh tables created with new schema")

    conn.close()

if __name__ == "__main__":
    migrate_database()