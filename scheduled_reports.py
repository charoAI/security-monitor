"""
Scheduled Reports Database Models and Manager
"""
import sqlite3
import json
from datetime import datetime, time
from typing import List, Dict, Optional
import pytz

class ScheduledReport:
    def __init__(self):
        # Create a new connection for each instance to avoid threading issues
        self.conn = sqlite3.connect('security_monitor.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Create scheduled reports table if it doesn't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_reports (
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

        # Create report history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT,
                report_data TEXT,
                FOREIGN KEY (report_id) REFERENCES scheduled_reports (id)
            )
        ''')
        self.conn.commit()

    def create_report(self, name: str, countries: List[str], prompt: str,
                     schedule_type: str, schedule_time: str, timezone: str = 'America/New_York',
                     email_recipients: List[str] = None) -> int:
        """Create a new scheduled report"""
        cursor = self.conn.cursor()

        # Calculate next run time
        next_run = self._calculate_next_run(schedule_type, schedule_time, timezone)

        cursor.execute('''
            INSERT INTO scheduled_reports
            (name, countries, prompt, schedule_type, schedule_time, timezone, email_recipients, next_run)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            json.dumps(countries),
            prompt if prompt else '',
            schedule_type,
            schedule_time,
            timezone,
            json.dumps(email_recipients) if email_recipients else '[]',
            next_run
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_all_reports(self) -> List[Dict]:
        """Get all scheduled reports"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, countries, prompt, schedule_type, schedule_time,
                   timezone, email_recipients, is_active, last_run, next_run, created_at
            FROM scheduled_reports
            ORDER BY created_at DESC
        ''')

        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row[0],
                'name': row[1],
                'countries': json.loads(row[2]),
                'prompt': row[3] if row[3] else '',
                'schedule_type': row[4],
                'schedule_time': row[5],
                'timezone': row[6],
                'email_recipients': json.loads(row[7]) if row[7] else [],
                'is_active': bool(row[8]),
                'last_run': row[9],
                'next_run': row[10],
                'created_at': row[11]
            })

        return reports

    def get_report(self, report_id: int) -> Optional[Dict]:
        """Get a specific scheduled report"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, countries, prompt, schedule_type, schedule_time,
                   timezone, email_recipients, is_active, last_run, next_run
            FROM scheduled_reports
            WHERE id = ?
        ''', (report_id,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'countries': json.loads(row[2]),
                'prompt': row[3] if row[3] else '',
                'schedule_type': row[4],
                'schedule_time': row[5],
                'timezone': row[6],
                'email_recipients': json.loads(row[7]) if row[7] else [],
                'is_active': bool(row[8]),
                'last_run': row[9],
                'next_run': row[10]
            }
        return None

    def update_report(self, report_id: int, **kwargs) -> bool:
        """Update a scheduled report"""
        allowed_fields = ['name', 'countries', 'prompt', 'schedule_type',
                         'schedule_time', 'timezone', 'email_recipients', 'is_active']

        updates = []
        values = []

        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                value = kwargs[field]

                # Convert lists to JSON
                if field in ['countries', 'email_recipients']:
                    value = json.dumps(value)

                values.append(value)

        if not updates:
            return False

        # Recalculate next run if schedule changed
        if 'schedule_type' in kwargs or 'schedule_time' in kwargs or 'timezone' in kwargs:
            report = self.get_report(report_id)
            schedule_type = kwargs.get('schedule_type', report['schedule_type'])
            schedule_time = kwargs.get('schedule_time', report['schedule_time'])
            timezone = kwargs.get('timezone', report['timezone'])

            next_run = self._calculate_next_run(schedule_type, schedule_time, timezone)
            updates.append("next_run = ?")
            values.append(next_run)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(report_id)

        cursor = self.conn.cursor()
        cursor.execute(f'''
            UPDATE scheduled_reports
            SET {', '.join(updates)}
            WHERE id = ?
        ''', values)

        self.conn.commit()
        return cursor.rowcount > 0

    def delete_report(self, report_id: int) -> bool:
        """Delete a scheduled report"""
        cursor = self.conn.cursor()

        # Delete history first
        cursor.execute('DELETE FROM report_history WHERE report_id = ?', (report_id,))

        # Delete report
        cursor.execute('DELETE FROM scheduled_reports WHERE id = ?', (report_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def toggle_report(self, report_id: int) -> bool:
        """Toggle report active status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE scheduled_reports
            SET is_active = NOT is_active,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (report_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def get_due_reports(self) -> List[Dict]:
        """Get reports that are due to run"""
        cursor = self.conn.cursor()
        current_time = datetime.now().isoformat()

        cursor.execute('''
            SELECT id, name, countries, prompt, schedule_type, schedule_time,
                   timezone, email_recipients
            FROM scheduled_reports
            WHERE is_active = 1 AND next_run <= ?
        ''', (current_time,))

        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row[0],
                'name': row[1],
                'countries': json.loads(row[2]),
                'prompt': row[3] if row[3] else '',
                'schedule_type': row[4],
                'schedule_time': row[5],
                'timezone': row[6],
                'email_recipients': json.loads(row[7]) if row[7] else []
            })

        return reports

    def mark_report_run(self, report_id: int, status: str = 'success',
                       error_message: str = None, report_data: str = None):
        """Mark a report as run and calculate next run time"""
        cursor = self.conn.cursor()

        # Log to history
        cursor.execute('''
            INSERT INTO report_history (report_id, status, error_message, report_data)
            VALUES (?, ?, ?, ?)
        ''', (report_id, status, error_message, report_data))

        # Update last run and calculate next run
        report = self.get_report(report_id)
        next_run = self._calculate_next_run(
            report['schedule_type'],
            report['schedule_time'],
            report['timezone']
        )

        cursor.execute('''
            UPDATE scheduled_reports
            SET last_run = CURRENT_TIMESTAMP,
                next_run = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (next_run, report_id))

        self.conn.commit()

    def get_report_history(self, report_id: int, limit: int = 10) -> List[Dict]:
        """Get report run history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT run_time, status, error_message
            FROM report_history
            WHERE report_id = ?
            ORDER BY run_time DESC
            LIMIT ?
        ''', (report_id, limit))

        history = []
        for row in cursor.fetchall():
            history.append({
                'run_time': row[0],
                'status': row[1],
                'error_message': row[2]
            })

        return history

    def _calculate_next_run(self, schedule_type: str, schedule_time: str,
                           timezone_str: str) -> str:
        """Calculate the next run time based on schedule"""
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)

        # Parse schedule_time (format: "HH:MM")
        hour, minute = map(int, schedule_time.split(':'))

        if schedule_type == 'daily':
            # Next occurrence of the specified time
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # If time has passed today, schedule for tomorrow
                from datetime import timedelta
                next_run = next_run + timedelta(days=1)

        elif schedule_type == 'weekly':
            # For weekly, schedule_time might be "MON:14:00"
            if ':' in schedule_time and len(schedule_time.split(':')) == 3:
                day_str, hour_str, minute_str = schedule_time.split(':')
                hour = int(hour_str)
                minute = int(minute_str)

                # Map day string to weekday number
                days = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
                target_day = days.get(day_str, 0)

                # Find next occurrence of this weekday
                days_ahead = target_day - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7

                from datetime import timedelta
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Default to same time next week
                from datetime import timedelta
                next_run = now + timedelta(weeks=1)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

        elif schedule_type == 'hourly':
            # Run at the same minute every hour
            minute = int(schedule_time) if schedule_time.isdigit() else 0
            next_run = now.replace(minute=minute, second=0, microsecond=0)
            if next_run <= now:
                from datetime import timedelta
                next_run = next_run + timedelta(hours=1)

        else:  # Default to daily
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                from datetime import timedelta
                next_run = next_run + timedelta(days=1)

        return next_run.isoformat()

    def close(self):
        """Close database connection"""
        self.conn.close()