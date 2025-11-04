from gui import StudyTimerApp
import tkinter as tk

def main():
    # Create main window
    root = tk.Tk()
    
    # Create application
    app = StudyTimerApp(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()