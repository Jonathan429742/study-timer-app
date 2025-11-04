import time
import threading
from config import load_settings

class PomodoroTimer:
    def __init__(self):
        self.settings = load_settings()
        self.reset()
    
    def reset(self):
        self.work_duration = self.settings['work_duration'] * 60  # Convert to seconds
        self.short_break_duration = self.settings['short_break_duration'] * 60
        self.long_break_duration = self.settings['long_break_duration'] * 60
        self.sessions_before_long_break = self.settings['sessions_before_long_break']
        
        self.time_remaining = self.work_duration
        self.is_running = False
        self.current_session = "work"
        self.session_count = 0
        self.completed_sessions = 0
    
    def update_settings(self, new_settings):
        """Update timer with new settings"""
        self.settings = new_settings
        self.reset()
    
    def start(self):
        self.is_running = True
    
    def pause(self):
        self.is_running = False
    
    def skip(self):
        self.is_running = False
        if self.current_session == "work":
            self.session_count += 1
            if self.session_count % self.sessions_before_long_break == 0:
                self.current_session = "long_break"
                self.time_remaining = self.long_break_duration
            else:
                self.current_session = "short_break"
                self.time_remaining = self.short_break_duration
        else:
            self.current_session = "work"
            self.time_remaining = self.work_duration
        return self.current_session
    
    def update(self):
        if self.is_running and self.time_remaining > 0:
            self.time_remaining -= 1
            return True
        elif self.time_remaining <= 0:
            self._handle_session_end()
            return False
        return True
    
    def _handle_session_end(self):
        self.is_running = False
        if self.current_session == "work":
            self.completed_sessions += 1
            self.session_count += 1
            if self.session_count % self.sessions_before_long_break == 0:
                self.current_session = "long_break"
                self.time_remaining = self.long_break_duration
            else:
                self.current_session = "short_break"
                self.time_remaining = self.short_break_duration
        else:
            self.current_session = "work"
            self.time_remaining = self.work_duration
    
    def get_time_display(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_session_info(self):
        session_names = {
            "work": "Focus Time",
            "short_break": "Short Break", 
            "long_break": "Long Break"
        }
        return {
            "name": session_names.get(self.current_session, "Focus Time"),
            "type": self.current_session,
            "progress": self.get_progress(),
            "completed_sessions": self.completed_sessions,
            "next_session": "Break" if self.current_session == "work" else "Focus"
        }
    
    def get_progress(self):
        if self.current_session == "work":
            total = self.work_duration
        elif self.current_session == "short_break":
            total = self.short_break_duration
        else:
            total = self.long_break_duration
        
        return 100 - (self.time_remaining / total) * 100