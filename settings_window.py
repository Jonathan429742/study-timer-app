import tkinter as tk
from tkinter import ttk, messagebox
from config import load_settings, save_settings, DEFAULT_SETTINGS

class SettingsWindow:
    def __init__(self, parent, timer, on_settings_save):
        self.parent = parent
        self.timer = timer
        self.on_settings_save = on_settings_save
        self.settings = load_settings()
        
        self.create_window()
    
    def create_window(self):
        """Create the settings window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Timer Settings")
        self.window.geometry("400x400")  # Increased height to show buttons
        self.window.resizable(False, False)
        self.window.transient(self.parent)  # Set to be on top of parent
        self.window.grab_set()  # Modal window
        
        # Center the window
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.window.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Create a main frame with padding
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Timer Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Create a frame for all settings with more spacing
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # Work duration
        work_frame = ttk.Frame(settings_frame)
        work_frame.pack(fill='x', pady=15)
        
        ttk.Label(work_frame, text="Work Duration (minutes):", 
                 font=('Arial', 10)).pack(side='left', anchor='w')
        self.work_var = tk.StringVar(value=str(self.settings['work_duration']))
        work_spinbox = ttk.Spinbox(work_frame, from_=1, to=120, width=8,
                                  textvariable=self.work_var, font=('Arial', 10))
        work_spinbox.pack(side='right', padx=(10, 0))
        
        # Short break duration
        short_break_frame = ttk.Frame(settings_frame)
        short_break_frame.pack(fill='x', pady=15)
        
        ttk.Label(short_break_frame, text="Short Break (minutes):", 
                 font=('Arial', 10)).pack(side='left', anchor='w')
        self.short_break_var = tk.StringVar(value=str(self.settings['short_break_duration']))
        short_break_spinbox = ttk.Spinbox(short_break_frame, from_=1, to=30, width=8,
                                         textvariable=self.short_break_var, font=('Arial', 10))
        short_break_spinbox.pack(side='right', padx=(10, 0))
        
        # Long break duration
        long_break_frame = ttk.Frame(settings_frame)
        long_break_frame.pack(fill='x', pady=15)
        
        ttk.Label(long_break_frame, text="Long Break (minutes):", 
                 font=('Arial', 10)).pack(side='left', anchor='w')
        self.long_break_var = tk.StringVar(value=str(self.settings['long_break_duration']))
        long_break_spinbox = ttk.Spinbox(long_break_frame, from_=1, to=60, width=8,
                                        textvariable=self.long_break_var, font=('Arial', 10))
        long_break_spinbox.pack(side='right', padx=(10, 0))
        
        # Sessions before long break
        sessions_frame = ttk.Frame(settings_frame)
        sessions_frame.pack(fill='x', pady=15)
        
        ttk.Label(sessions_frame, text="Sessions before long break:", 
                 font=('Arial', 10)).pack(side='left', anchor='w')
        self.sessions_var = tk.StringVar(value=str(self.settings['sessions_before_long_break']))
        sessions_spinbox = ttk.Spinbox(sessions_frame, from_=1, to=10, width=8,
                                      textvariable=self.sessions_var, font=('Arial', 10))
        sessions_spinbox.pack(side='right', padx=(10, 0))
        
        # Buttons frame - with more space at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Left side buttons
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side='left')
        
        ttk.Button(left_button_frame, text="Reset to Defaults", 
                  command=self.reset_to_defaults).pack(side='left')
        
        # Right side buttons
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.pack(side='right')
        
        ttk.Button(right_button_frame, text="Cancel", 
                  command=self.window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(right_button_frame, text="Save", 
                  command=self.save_settings).pack(side='right')
        
        # Add some instructional text
        info_label = ttk.Label(main_frame, 
                              text="Changes will take effect immediately after saving.",
                              font=('Arial', 8), 
                              foreground='gray')
        info_label.pack(pady=(20, 0))
    
    def save_settings(self):
        """Save the settings and update the timer"""
        try:
            new_settings = {
                'work_duration': int(self.work_var.get()),
                'short_break_duration': int(self.short_break_var.get()),
                'long_break_duration': int(self.long_break_var.get()),
                'sessions_before_long_break': int(self.sessions_var.get())
            }
            
            # Validate settings
            if (new_settings['work_duration'] < 1 or 
                new_settings['short_break_duration'] < 1 or 
                new_settings['long_break_duration'] < 1 or 
                new_settings['sessions_before_long_break'] < 1):
                raise ValueError("All values must be positive")
            
            save_settings(new_settings)
            self.timer.update_settings(new_settings)
            self.on_settings_save()
            self.window.destroy()
            
        except ValueError as e:
            tk.messagebox.showerror("Invalid Input", 
                                  "Please enter valid positive numbers for all fields.")
    
    def reset_to_defaults(self):
        """Reset settings to default values"""
        self.work_var.set(str(DEFAULT_SETTINGS['work_duration']))
        self.short_break_var.set(str(DEFAULT_SETTINGS['short_break_duration']))
        self.long_break_var.set(str(DEFAULT_SETTINGS['long_break_duration']))
        self.sessions_var.set(str(DEFAULT_SETTINGS['sessions_before_long_break']))