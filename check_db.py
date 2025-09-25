import sqlite3

conn = sqlite3.connect('security_monitor.db')
cursor = conn.cursor()

print("Table columns:")
cursor.execute('PRAGMA table_info(scheduled_reports)')
for col in cursor.fetchall():
    print(f"  {col[0]}: {col[1]} ({col[2]})")

print("\nCalling test API to see what's returned:")
from scheduled_reports import ScheduledReport
db = ScheduledReport()
reports = db.get_all_reports()
print(f"Number of reports: {len(reports)}")
if reports:
    print("First report:")
    for key, value in reports[0].items():
        print(f"  {key}: {value}")
db.close()

conn.close()