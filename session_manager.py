import json
import datetime
from config import SESSION_FILE

class SessionManager:
    def __init__(self):
        self.sessions = self.load_sessions()
    
    def load_sessions(self):
        """Load sessions from JSON file"""
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                return data.get('sessions', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_session(self, session_type, duration, completed=True, notes=""):
        """Save a new session to JSON"""
        session_data = {
            "id": len(self.sessions) + 1,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "start_time": datetime.datetime.now().strftime("%H:%M:%S"),
            "session_type": session_type,
            "duration": duration,
            "completed": completed,
            "notes": notes,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.sessions.append(session_data)
        self._save_to_file()
        
        return session_data
    
    def _save_to_file(self):
        """Save all sessions to JSON file"""
        data = {
            "metadata": {
                "last_updated": datetime.datetime.now().isoformat(),
                "total_sessions": len(self.sessions)
            },
            "sessions": self.sessions
        }
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_today_stats(self):
        """Get statistics for today"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_sessions = [s for s in self.sessions if s['date'] == today]
        
        focus_sessions = [s for s in today_sessions if s['session_type'] == 'focus']
        total_focus_minutes = sum(s['duration'] for s in focus_sessions)
        completed_sessions = len(focus_sessions)
        
        return {
            'total_focus_minutes': total_focus_minutes,
            'completed_sessions': completed_sessions,
            'total_sessions': len(today_sessions),
            'productivity_score': min(100, (total_focus_minutes / 120) * 100)  # Based on 2-hour goal
        }
    
    def get_weekly_stats(self):
        """Get statistics for the current week"""
        today = datetime.datetime.now()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        week_sessions = []
        for session in self.sessions:
            session_date = datetime.datetime.strptime(session['date'], "%Y-%m-%d")
            if session_date >= week_start:
                week_sessions.append(session)
        
        focus_sessions = [s for s in week_sessions if s['session_type'] == 'focus']
        total_focus_minutes = sum(s['duration'] for s in focus_sessions)
        
        # Group by day
        daily_stats = {}
        for session in week_sessions:
            if session['session_type'] == 'focus':
                day = session['date']
                daily_stats[day] = daily_stats.get(day, 0) + session['duration']
        
        return {
            'total_focus_minutes': total_focus_minutes,
            'daily_focus': daily_stats,
            'average_daily_minutes': total_focus_minutes / 7 if week_sessions else 0
        }
    
    def get_session_history(self, limit=50):
        """Get recent session history"""
        return self.sessions[-limit:] if self.sessions else []