import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
from config import COLORS

class Dashboard:
    def __init__(self, parent, session_manager):
        self.parent = parent
        self.session_manager = session_manager
        self.setup_dashboard()
    
    def setup_dashboard(self):
        # Main dashboard frame
        self.dashboard_frame = ttk.Frame(self.parent)
        self.dashboard_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Today's Summary
        self.setup_today_summary()
        
        # Progress Visualization
        self.setup_progress_charts()
        
        # Recent Sessions
        self.setup_recent_sessions()
    
    def setup_today_summary(self):
        summary_frame = ttk.LabelFrame(self.dashboard_frame, text="Today's Summary", padding=10)
        summary_frame.pack(fill='x', pady=(0, 10))
        
        stats = self.session_manager.get_today_stats()
        
        # Create metrics grid
        metrics = [
            ("Total Focus", f"{stats['total_focus_minutes']}m", COLORS['work']),
            ("Sessions", str(stats['completed_sessions']), COLORS['primary']),
            ("Productivity", f"{stats['productivity_score']:.0f}%", COLORS['success']),
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_frame = ttk.Frame(summary_frame)
            metric_frame.grid(row=0, column=i, padx=20, sticky='ew')
            
            ttk.Label(metric_frame, text=value, font=('Arial', 16, 'bold'), 
                     foreground=color).pack()
            ttk.Label(metric_frame, text=label, font=('Arial', 9)).pack()
    
    def setup_progress_charts(self):
        # Create a frame for charts
        charts_frame = ttk.LabelFrame(self.dashboard_frame, text="Progress Analytics", padding=10)
        charts_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Weekly progress chart
        self.create_weekly_chart(charts_frame)
        
        # Session distribution
        self.create_distribution_chart(charts_frame)
    
    def create_weekly_chart(self, parent):
        weekly_stats = self.session_manager.get_weekly_stats()
        
        fig = Figure(figsize=(6, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        days = list(weekly_stats['daily_focus'].keys())[-7:]  # Last 7 days
        minutes = [weekly_stats['daily_focus'][day] for day in days]
        
        # Use full day names for display
        day_names = [datetime.datetime.strptime(day, "%Y-%m-%d").strftime("%a") for day in days]
        
        bars = ax.bar(day_names, minutes, color=COLORS['work'], alpha=0.7)
        ax.set_ylabel('Focus Minutes')
        ax.set_title('Weekly Focus Time')
        
        # Add value labels on bars
        for bar, value in zip(bars, minutes):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       str(int(value)), ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side='left', padx=(0, 10))
    
    def create_distribution_chart(self, parent):
        sessions = self.session_manager.get_session_history(20)  # Last 20 sessions
        
        if not sessions:
            return
        
        # Count session types
        session_types = {}
        for session in sessions:
            session_type = session['session_type']
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        if not session_types:
            return
            
        fig = Figure(figsize=(4, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        labels = []
        sizes = []
        colors = []
        
        type_colors = {
            'focus': COLORS['work'],
            'short_break': COLORS['short_break'],
            'long_break': COLORS['long_break']
        }
        
        type_names = {
            'focus': 'Focus',
            'short_break': 'Short Break',
            'long_break': 'Long Break'
        }
        
        for session_type, count in session_types.items():
            labels.append(type_names.get(session_type, session_type))
            sizes.append(count)
            colors.append(type_colors.get(session_type, COLORS['secondary']))
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        ax.set_title('Session Distribution')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(side='left')
    
    def setup_recent_sessions(self):
        sessions_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Sessions", padding=10)
        sessions_frame.pack(fill='both', expand=True)
        
        # Create treeview for sessions
        columns = ('Time', 'Type', 'Duration', 'Status')
        tree = ttk.Treeview(sessions_frame, columns=columns, show='headings', height=6)
        
        # Define headings
        tree.heading('Time', text='Time')
        tree.heading('Type', text='Type')
        tree.heading('Duration', text='Duration (min)')
        tree.heading('Status', text='Status')
        
        # Configure columns
        tree.column('Time', width=100)
        tree.column('Type', width=100)
        tree.column('Duration', width=100)
        tree.column('Status', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(sessions_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate with recent sessions
        recent_sessions = self.session_manager.get_session_history(10)
        for session in reversed(recent_sessions):  # Show newest first
            session_type = 'Focus' if session['session_type'] == 'focus' else 'Break'
            status = '✓' if session['completed'] else '✗'
            tree.insert('', 'end', values=(
                session['start_time'],
                session_type,
                session['duration'],
                status
            ))
    
    def refresh(self):
        """Refresh all dashboard data"""
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        self.setup_dashboard()