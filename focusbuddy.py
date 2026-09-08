import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time

# File to store data
DATA_FILE = "focusbuddy_data.json"

# Motivational messages for different activities
MOTIVATIONAL_MESSAGES = {
    "Studying": [
        "Great focus session! Keep it up! 📚",
        "You're doing amazing! Stay focused! 💪",
        "Learning is a superpower! Keep going! 🚀",
        "Your future self will thank you! 📖",
        "Excellence is earned through dedication! ⭐",
    ],
    "Gaming": [
        "Having fun? Don't forget to take breaks! 🎮",
        "Remember to rest your eyes soon! 👀",
        "Balance is key! Consider a study session next! 🎯",
        "Gaming is cool, but health comes first! 🏥",
    ],
    "Entertainment": [
        "Enjoying yourself? That's great! 🎬",
        "Don't forget your daily goals! 🎯",
        "Time for a break? Your eyes need it! 👁️",
        "You deserve entertainment, but balance matters! ⚖️",
    ],
    "Other": [
        "Keep up the good work! 💯",
        "You're making progress! 🌟",
        "Stay consistent! 🎯",
    ]
}

BREAK_MESSAGES = [
    "Time for a break! Look away from the screen! 👀",
    "Your eyes need a rest! Take 5 minutes off! 🧘",
    "Stretch it out! Your body will thank you! 🤸",
    "Hydration break! Grab some water! 💧",
    "Time to move! Walk around for a bit! 🚶",
    "Rest your mind! Close your eyes for a moment! 😌",
]


class FocusBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusBuddy - Smart Screen-Time Nudge App")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Set modern color scheme
        self.bg_color = "#f0f2f5"
        self.primary_color = "#4CAF50"
        self.secondary_color = "#2196F3"
        self.warning_color = "#FF9800"
        self.root.configure(bg=self.bg_color)
        
        # Data variables
        self.current_activity = tk.StringVar(value="Studying")
        self.session_data = self.load_data()
        self.session_timer = 0
        self.is_tracking = False
        self.break_reminder_thread = None
        self.break_counter = 0
        
        # Create UI
        self.create_ui()
        self.update_dashboard()
        
        # Start break reminder thread
        self.start_break_reminder()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Check if data is from today
                    if data.get('date') == str(datetime.now().date()):
                        return data
            except:
                pass
        
        # Return default data structure
        return {
            'date': str(datetime.now().date()),
            'daily_goal': 480,  # 8 hours in minutes
            'total_screen_time': 0,
            'breaks_taken': 0,
            'sessions': [],
            'activity_time': {
                'Studying': 0,
                'Gaming': 0,
                'Entertainment': 0,
                'Other': 0
            }
        }
    
    def save_data(self):
        """Save data to JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.session_data, f, indent=4)
    
    def create_ui(self):
        """Create the main UI"""
        # Title
        title_frame = tk.Frame(self.root, bg=self.primary_color)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 FocusBuddy - Smart Screen-Time Nudge App",
            font=("Helvetica", 18, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Dashboard Section
        self.create_dashboard_section(main_frame)
        
        # Activity Selection Section
        self.create_activity_section(main_frame)
        
        # Tracking Section
        self.create_tracking_section(main_frame)
        
        # Statistics Section
        self.create_statistics_section(main_frame)
        
        # Button Section
        self.create_button_section(main_frame)
    
    def create_dashboard_section(self, parent):
        """Create dashboard with daily goal, progress, and breaks"""
        dash_frame = tk.LabelFrame(
            parent,
            text="📊 Today's Dashboard",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        dash_frame.pack(fill=tk.X, pady=10)
        
        # Create grid for dashboard items
        dash_content = tk.Frame(dash_frame, bg=self.bg_color)
        dash_content.pack(fill=tk.X, padx=10, pady=10)
        
        # Left column - Screen time and goal
        left_col = tk.Frame(dash_content, bg=self.bg_color)
        left_col.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.screen_time_label = tk.Label(
            left_col,
            text="Total Screen Time: 0h 0m",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg="#333"
        )
        self.screen_time_label.pack(anchor=tk.W, pady=5)
        
        self.daily_goal_label = tk.Label(
            left_col,
            text="Daily Goal: 8h 0m",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg="#333"
        )
        self.daily_goal_label.pack(anchor=tk.W, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            left_col,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(anchor=tk.W, pady=10, fill=tk.X)
        
        self.progress_label = tk.Label(
            left_col,
            text="0% of daily goal used",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666"
        )
        self.progress_label.pack(anchor=tk.W)
        
        # Right column - Breaks
        right_col = tk.Frame(dash_content, bg=self.bg_color)
        right_col.pack(side=tk.RIGHT, padx=5)
        
        self.breaks_label = tk.Label(
            right_col,
            text="Breaks Taken: 0",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg=self.secondary_color
        )
        self.breaks_label.pack(pady=5)
        
        self.motivational_label = tk.Label(
            right_col,
            text="Keep up the good work! 💪",
            font=("Helvetica", 9, "italic"),
            bg=self.bg_color,
            fg=self.primary_color,
            wraplength=250
        )
        self.motivational_label.pack(pady=10)
    
    def create_activity_section(self, parent):
        """Create activity selection section"""
        act_frame = tk.LabelFrame(
            parent,
            text="🎯 What Are You Doing?",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        act_frame.pack(fill=tk.X, pady=10)
        
        act_content = tk.Frame(act_frame, bg=self.bg_color)
        act_content.pack(fill=tk.X, padx=10, pady=10)
        
        activities = ["Studying", "Gaming", "Entertainment", "Other"]
        
        for activity in activities:
            rb = tk.Radiobutton(
                act_content,
                text=activity,
                variable=self.current_activity,
                value=activity,
                font=("Helvetica", 10),
                bg=self.bg_color,
                activebackground=self.bg_color,
                selectcolor=self.primary_color
            )
            rb.pack(anchor=tk.W, pady=5)
    
    def create_tracking_section(self, parent):
        """Create screen time tracking section"""
        track_frame = tk.LabelFrame(
            parent,
            text="⏱️ Screen-Time Tracking",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        track_frame.pack(fill=tk.X, pady=10)
        
        track_content = tk.Frame(track_frame, bg=self.bg_color)
        track_content.pack(fill=tk.X, padx=10, pady=10)
        
        # Quick add buttons
        quick_frame = tk.Frame(track_content, bg=self.bg_color)
        quick_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            quick_frame,
            text="Quick Add:",
            font=("Helvetica", 10, "bold"),
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        for minutes in [15, 30, 60]:
            btn = tk.Button(
                quick_frame,
                text=f"{minutes} min",
                command=lambda m=minutes: self.add_screen_time(m),
                font=("Helvetica", 9),
                bg=self.secondary_color,
                fg="white",
                padx=10,
                pady=5,
                relief=tk.RAISED
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Custom time input
        custom_frame = tk.Frame(track_content, bg=self.bg_color)
        custom_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            custom_frame,
            text="Add Custom Time (minutes):",
            font=("Helvetica", 10),
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.custom_time_entry = tk.Entry(
            custom_frame,
            width=10,
            font=("Helvetica", 10)
        )
        self.custom_time_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(
            custom_frame,
            text="Add",
            command=self.add_custom_time,
            font=("Helvetica", 9),
            bg=self.primary_color,
            fg="white",
            padx=15,
            pady=5
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Current session timer
        timer_frame = tk.Frame(track_content, bg=self.bg_color)
        timer_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            timer_frame,
            text="Current Session Timer:",
            font=("Helvetica", 10, "bold"),
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="0h 0m 0s",
            font=("Helvetica", 10, "bold"),
            bg=self.bg_color,
            fg=self.warning_color
        )
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        button_frame = tk.Frame(timer_frame, bg=self.bg_color)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            button_frame,
            text="Start",
            command=self.start_session,
            font=("Helvetica", 9),
            bg=self.primary_color,
            fg="white",
            padx=10,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop_session,
            font=("Helvetica", 9),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
    
    def create_statistics_section(self, parent):
        """Create activity-wise statistics section"""
        stats_frame = tk.LabelFrame(
            parent,
            text="📈 Activity-wise Statistics",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_content = tk.Frame(stats_frame, bg=self.bg_color)
        stats_content.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_labels = {}
        for activity in ["Studying", "Gaming", "Entertainment", "Other"]:
            activity_frame = tk.Frame(stats_content, bg=self.bg_color)
            activity_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                activity_frame,
                text=f"{activity}:",
                font=("Helvetica", 10, "bold"),
                bg=self.bg_color,
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=5)
            
            self.stats_labels[activity] = tk.Label(
                activity_frame,
                text="0h 0m",
                font=("Helvetica", 10),
                bg=self.bg_color,
                fg=self.secondary_color
            )
            self.stats_labels[activity].pack(side=tk.LEFT, padx=5)
    
    def create_button_section(self, parent):
        """Create action buttons section"""
        btn_frame = tk.Frame(parent, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=15)
        
        # Daily goal settings
        goal_frame = tk.Frame(btn_frame, bg=self.bg_color)
        goal_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            goal_frame,
            text="Daily Goal (hours):",
            font=("Helvetica", 10),
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.goal_entry = tk.Entry(
            goal_frame,
            width=5,
            font=("Helvetica", 10)
        )
        self.goal_entry.pack(side=tk.LEFT, padx=2)
        self.goal_entry.insert(0, str(self.session_data['daily_goal'] // 60))
        
        goal_btn = tk.Button(
            goal_frame,
            text="Set Goal",
            command=self.set_daily_goal,
            font=("Helvetica", 9),
            bg=self.secondary_color,
            fg="white",
            padx=10,
            pady=5
        )
        goal_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = tk.Button(
            btn_frame,
            text="Reset Daily Data",
            command=self.reset_daily_data,
            font=("Helvetica", 9),
            bg=self.warning_color,
            fg="white",
            padx=15,
            pady=5
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)
        
        # Take break button
        break_btn = tk.Button(
            btn_frame,
            text="Take a Break Now",
            command=self.take_break,
            font=("Helvetica", 9),
            bg=self.primary_color,
            fg="white",
            padx=15,
            pady=5
        )
        break_btn.pack(side=tk.RIGHT, padx=5)
    
    def add_screen_time(self, minutes):
        """Add screen time"""
        activity = self.current_activity.get()
        self.session_data['total_screen_time'] += minutes
        self.session_data['activity_time'][activity] += minutes
        self.session_data['sessions'].append({
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'activity': activity,
            'duration': minutes
        })
        self.save_data()
        self.update_dashboard()
        messagebox.showinfo("Success", f"Added {minutes} minutes of {activity}!")
    
    def add_custom_time(self):
        """Add custom screen time"""
        try:
            minutes = int(self.custom_time_entry.get())
            if minutes <= 0:
                messagebox.showerror("Error", "Please enter a positive number!")
                return
            self.add_screen_time(minutes)
            self.custom_time_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def start_session(self):
        """Start a screen time session"""
        self.is_tracking = True
        self.session_timer = 0
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_timer()
    
    def stop_session(self):
        """Stop the current session"""
        self.is_tracking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.session_timer > 0:
            # Convert seconds to minutes
            minutes = self.session_timer // 60
            if minutes > 0:
                self.add_screen_time(minutes)
                messagebox.showinfo("Success", f"Session ended! Added {minutes} minute(s).")
            self.session_timer = 0
            self.timer_label.config(text="0h 0m 0s")
    
    def update_timer(self):
        """Update the timer display"""
        if self.is_tracking:
            self.session_timer += 1
            hours = self.session_timer // 3600
            minutes = (self.session_timer % 3600) // 60
            seconds = self.session_timer % 60
            self.timer_label.config(text=f"{hours}h {minutes}m {seconds}s")
            self.root.after(1000, self.update_timer)
    
    def set_daily_goal(self):
        """Set daily screen time goal"""
        try:
            hours = float(self.goal_entry.get())
            if hours <= 0:
                messagebox.showerror("Error", "Please enter a positive number!")
                return
            self.session_data['daily_goal'] = int(hours * 60)
            self.save_data()
            self.update_dashboard()
            messagebox.showinfo("Success", f"Daily goal set to {hours} hours!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def take_break(self):
        """Record a break"""
        self.session_data['breaks_taken'] += 1
        self.save_data()
        self.update_dashboard()
        
        import random
        message = random.choice(BREAK_MESSAGES)
        messagebox.showinfo("Break Time", message)
    
    def reset_daily_data(self):
        """Reset daily data"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset today's data?"):
            self.session_data = {
                'date': str(datetime.now().date()),
                'daily_goal': 480,
                'total_screen_time': 0,
                'breaks_taken': 0,
                'sessions': [],
                'activity_time': {
                    'Studying': 0,
                    'Gaming': 0,
                    'Entertainment': 0,
                    'Other': 0
                }
            }
            self.save_data()
            self.update_dashboard()
            messagebox.showinfo("Success", "Daily data has been reset!")
    
    def update_dashboard(self):
        """Update all dashboard elements"""
        total_time = self.session_data['total_screen_time']
        daily_goal = self.session_data['daily_goal']
        
        # Update screen time label
        hours = total_time // 60
        minutes = total_time % 60
        self.screen_time_label.config(text=f"Total Screen Time: {hours}h {minutes}m")
        
        # Update daily goal label
        goal_hours = daily_goal // 60
        goal_minutes = daily_goal % 60
        self.daily_goal_label.config(text=f"Daily Goal: {goal_hours}h {goal_minutes}m")
        
        # Update progress bar
        progress = (total_time / daily_goal * 100) if daily_goal > 0 else 0
        progress = min(progress, 100)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}% of daily goal used")
        
        # Update breaks label
        self.breaks_label.config(text=f"Breaks Taken: {self.session_data['breaks_taken']}")
        
        # Update motivational message
        import random
        activity = self.current_activity.get()
        message = random.choice(MOTIVATIONAL_MESSAGES.get(activity, MOTIVATIONAL_MESSAGES["Other"]))
        self.motivational_label.config(text=message)
        
        # Update statistics
        for activity in ["Studying", "Gaming", "Entertainment", "Other"]:
            time_minutes = self.session_data['activity_time'][activity]
            hours = time_minutes // 60
            minutes = time_minutes % 60
            self.stats_labels[activity].config(text=f"{hours}h {minutes}m")
    
    def start_break_reminder(self):
        """Start background thread for break reminders"""
        def reminder_loop():
            while True:
                time.sleep(60)  # Check every minute
                if self.is_tracking:
                    self.break_counter += 1
                    # Show reminder every 25 minutes (Pomodoro style)
                    if self.break_counter >= 25:
                        self.show_break_reminder()
                        self.break_counter = 0
                else:
                    self.break_counter = 0
        
        self.break_reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
        self.break_reminder_thread.start()
    
    def show_break_reminder(self):
        """Show break reminder popup"""
        import random
        activity = self.current_activity.get()
        
        if activity == "Studying":
            message = "You've been studying for 25 minutes! Time for a short break! 📚\n\nConsider taking 5 minutes to rest your eyes and mind."
        else:
            message = "You've been at it for a while! Time to take a break! 🧘\n\nStand up, stretch, and give your eyes a rest!"
        
        if messagebox.askyesno("Break Reminder", message + "\n\nDid you take a break?"):
            self.take_break()


def main():
    root = tk.Tk()
    app = FocusBuddyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
