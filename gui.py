import tkinter as tk
from tkinter import ttk, messagebox
import threading
from timer_logic import PomodoroTimer
from session_manager import SessionManager
from visualization import Dashboard
from settings_window import SettingsWindow
from config import COLORS
import os

# Try to import pygame for sound, fall back to winsound
try:
    import pygame
    PYGAME_AVAILABLE = True
    pygame.mixer.init()
except ImportError:
    PYGAME_AVAILABLE = False
    import winsound

class StudyTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Timer - Stay Productive")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['light'])
        
        # Initialize components
        self.timer = PomodoroTimer()
        self.session_manager = SessionManager()
        
        # Setup GUI
        self.setup_gui()
        
        # Start timer update loop
        self.update_timer()
    
    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Timer Tab
        self.timer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.timer_frame, text='Timer')
        
        # Dashboard Tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text='Dashboard')
        
        self.setup_timer_tab()
        self.setup_dashboard_tab()
    
    def setup_timer_tab(self):
        # Timer display
        self.time_label = tk.Label(self.timer_frame, text="25:00", font=('Arial', 48, 'bold'),
                                  fg=COLORS['primary'], bg=COLORS['light'])
        self.time_label.pack(pady=20)
        
        # Session info
        self.session_label = tk.Label(self.timer_frame, text="Focus Time", font=('Arial', 16),
                                     fg=COLORS['dark'], bg=COLORS['light'])
        self.session_label.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.timer_frame, variable=self.progress_var,
                                           maximum=100, length=300)
        self.progress_bar.pack(pady=10)
        
        # Stats label
        self.stats_label = tk.Label(self.timer_frame, text="Sessions completed: 0", 
                                   font=('Arial', 10), fg=COLORS['dark'], bg=COLORS['light'])
        self.stats_label.pack(pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.timer_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_timer)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.skip_button = ttk.Button(button_frame, text="Skip", command=self.skip_session)
        self.skip_button.grid(row=0, column=2, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=3, padx=5)
        
        # Settings button
        self.settings_button = ttk.Button(button_frame, text="Settings", 
                                         command=self.open_settings)
        self.settings_button.grid(row=0, column=4, padx=5)
    
    def setup_dashboard_tab(self):
        # Initialize dashboard
        self.dashboard = Dashboard(self.dashboard_frame, self.session_manager)
        
        # Refresh button
        refresh_btn = ttk.Button(self.dashboard_frame, text="Refresh", 
                                command=self.dashboard.refresh)
        refresh_btn.pack(pady=10)
    
    def open_settings(self):
        """Open the settings window"""
        SettingsWindow(self.root, self.timer, self.on_settings_updated)
    
    def on_settings_updated(self):
        """Called when settings are saved"""
        self.update_display()
        messagebox.showinfo("Settings Updated", "Timer settings have been updated!")
    
    def start_timer(self):
        self.timer.start()
        self.start_button.config(text="Resume", state='disabled')
        self.pause_button.config(state='normal')
    
    def pause_timer(self):
        self.timer.pause()
        self.start_button.config(text="Resume", state='normal')
        self.pause_button.config(state='disabled')
    
    def skip_session(self):
        old_session = self.timer.current_session
        new_session = self.timer.skip()
        
        # Log the skipped session as incomplete
        if old_session == "work":
            self.session_manager.save_session("focus", 0, completed=False, notes="Skipped")
        
        self.update_display()
        self.play_sound()
    
    def reset_timer(self):
        self.timer.reset()
        self.start_button.config(text="Start", state='normal')
        self.pause_button.config(state='disabled')
        self.update_display()
    
    def update_timer(self):
        if self.timer.is_running:
            still_running = self.timer.update()
            
            if not still_running:
                # Session ended naturally
                session_info = self.timer.get_session_info()
                
                # Log completed session
                if self.timer.current_session == "work":
                    duration = self.timer.work_duration // 60
                    self.session_manager.save_session("focus", duration, completed=True)
                else:
                    break_type = "short_break" if self.timer.current_session == "short_break" else "long_break"
                    duration = (self.timer.short_break_duration if break_type == "short_break" 
                               else self.timer.long_break_duration) // 60
                    self.session_manager.save_session(break_type, duration, completed=True)
                
                self.play_sound()
                messagebox.showinfo("Session Complete!", 
                                  f"{session_info['name']} finished!\n"
                                  f"Ready for {session_info['next_session']}?")
        
        self.update_display()
        self.root.after(1000, self.update_timer)  # Update every second
    
    def update_display(self):
        # Update time display
        self.time_label.config(text=self.timer.get_time_display())
        
        # Update session info and colors
        session_info = self.timer.get_session_info()
        self.session_label.config(text=session_info['name'])
        
        # Update progress
        self.progress_var.set(session_info['progress'])
        
        # Update stats
        self.stats_label.config(text=f"Sessions completed: {session_info['completed_sessions']}")
        
        # Update colors based on session type
        color = COLORS.get(self.timer.current_session, COLORS['primary'])
        self.time_label.config(fg=color)
    
    def play_sound(self):
        """Play notification sound using available library"""
        try:
            sound_file = os.path.join(os.path.dirname(__file__), 'assets', 'beep.wav')
            
            if PYGAME_AVAILABLE:
                # Use pygame for sound support
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            else:
                # Fallback to winsound (requires WAV)
                winsound.PlaySound(sound_file, winsound.SND_FILENAME)
                
        except Exception as e:
            print(f"Sound error: {e}")
            try:
                # Final fallback: system beep
                import winsound
                winsound.Beep(1000, 500)
            except:
                # Silent fail if sound doesn't work
                pass