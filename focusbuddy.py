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

# Custom color schemes
THEMES = {
    "Dark Mode": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "primary": "#7c3aed",
        "secondary": "#06b6d4",
        "accent": "#ec4899",
        "success": "#10b981",
        "warning": "#f59e0b",
        "card_bg": "#2d2d2d",
        "text_dark": "#e5e5e5"
    },
    "Light Mode": {
        "bg": "#f0f2f5",
        "fg": "#1a1a1a",
        "primary": "#4CAF50",
        "secondary": "#2196F3",
        "accent": "#FF5722",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "card_bg": "#ffffff",
        "text_dark": "#333333"
    },
    "Ocean": {
        "bg": "#0a1628",
        "fg": "#e0f2fe",
        "primary": "#0ea5e9",
        "secondary": "#06b6d4",
        "accent": "#22d3ee",
        "success": "#10b981",
        "warning": "#f59e0b",
        "card_bg": "#164e63",
        "text_dark": "#cffafe"
    },
    "Forest": {
        "bg": "#1a3a1a",
        "fg": "#e8f5e9",
        "primary": "#4ade80",
        "secondary": "#22c55e",
        "accent": "#84cc16",
        "success": "#10b981",
        "warning": "#f59e0b",
        "card_bg": "#2d5f2d",
        "text_dark": "#c6f6d5"
    },
    "Sunset": {
        "bg": "#2a1810",
        "fg": "#fef3c7",
        "primary": "#fb923c",
        "secondary": "#f97316",
        "accent": "#ea580c",
        "success": "#10b981",
        "warning": "#f59e0b",
        "card_bg": "#3f2d1d",
        "text_dark": "#fed7aa"
    }
}


class FocusBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusBuddy - Smart Screen-Time Nudge App")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Theme selection
        self.current_theme = "Dark Mode"
        self.colors = THEMES[self.current_theme].copy()
        
        self.root.configure(bg=self.colors["bg"])
        
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
    
    def change_theme(self, theme_name):
        """Change the app theme"""
        self.current_theme = theme_name
        self.colors = THEMES[theme_name].copy()
        self.root.configure(bg=self.colors["bg"])
        
        # Recreate UI with new colors
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_ui()
        self.update_dashboard()
    
    def create_ui(self):
        """Create the main UI"""
        # Top navbar with theme selector
        navbar = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        navbar.pack(fill=tk.X, padx=0, pady=0)
        navbar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            navbar,
            text="🎯 FocusBuddy - Smart Screen-Time Nudge App",
            font=("Helvetica", 16, "bold"),
            bg=self.colors["primary"],
            fg="#ffffff"
        )
        title_label.pack(side=tk.LEFT, pady=15, padx=20)
        
        # Theme selector
        theme_frame = tk.Frame(navbar, bg=self.colors["primary"])
        theme_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=("Helvetica", 9),
            bg=self.colors["primary"],
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        theme_combo = ttk.Combobox(
            theme_frame,
            values=list(THEMES.keys()),
            state="readonly",
            width=12,
            font=("Helvetica", 9)
        )
        theme_combo.set(self.current_theme)
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_combo.get()))
        
        # Main scrollable container
        main_canvas = tk.Canvas(
            self.root,
            bg=self.colors["bg"],
            highlightthickness=0,
            height=700
        )
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Premium Dashboard Section
        self.create_premium_dashboard(scrollable_frame)
        
        # Quick Stats
        self.create_quick_stats(scrollable_frame)
        
        # Activity Selection Section
        self.create_activity_section(scrollable_frame)
        
        # Tracking Section
        self.create_tracking_section(scrollable_frame)
        
        # Statistics Section
        self.create_statistics_section(scrollable_frame)
        
        # Button Section
        self.create_button_section(scrollable_frame)
    
    def create_card(self, parent, bg_color=None):
        """Helper to create a styled card"""
        if bg_color is None:
            bg_color = self.colors["card_bg"]
        return tk.Frame(parent, bg=bg_color, relief=tk.FLAT, bd=0)
    
    def create_premium_dashboard(self, parent):
        """Create a premium-looking main dashboard"""
        dash_frame = self.create_card(parent)
        dash_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Main dashboard header
        header = tk.Frame(dash_frame, bg=self.colors["primary"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Today's Performance",
            font=("Helvetica", 14, "bold"),
            bg=self.colors["primary"],
            fg="white"
        ).pack(side=tk.LEFT, pady=12, padx=20)
        
        # Main stats grid
        stats_grid = tk.Frame(dash_frame, bg=self.colors["card_bg"])
        stats_grid.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Screen time box
        time_box = self.create_stat_box(
            stats_grid,
            "⏱️ Total Screen Time",
            "0h 0m",
            self.colors["secondary"]
        )
        time_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.screen_time_display = time_box.winfo_children()[1]
        
        # Daily goal box
        goal_box = self.create_stat_box(
            stats_grid,
            "🎯 Daily Goal",
            "8h 0m",
            self.colors["accent"]
        )
        goal_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.goal_display = goal_box.winfo_children()[1]
        
        # Breaks box
        breaks_box = self.create_stat_box(
            stats_grid,
            "☕ Breaks Taken",
            "0",
            self.colors["success"]
        )
        breaks_box.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.breaks_display = breaks_box.winfo_children()[1]
        
        # Configure grid weights
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)
        
        # Progress section
        progress_section = tk.Frame(dash_frame, bg=self.colors["card_bg"])
        progress_section.pack(fill=tk.X, padx=15, pady=10)
        
        progress_label = tk.Label(
            progress_section,
            text="Progress to Goal",
            font=("Helvetica", 11, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"]
        )
        progress_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Custom progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_section,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(
            progress_section,
            text="0% of daily goal used",
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["primary"]
        )
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Motivational message
        self.motivational_label = tk.Label(
            dash_frame,
            text="Keep up the good work! 💪",
            font=("Helvetica", 10, "italic"),
            bg=self.colors["card_bg"],
            fg=self.colors["secondary"],
            wraplength=600
        )
        self.motivational_label.pack(pady=15)
    
    def create_stat_box(self, parent, title, value, color):
        """Create a stat box for dashboard"""
        box = tk.Frame(parent, bg=self.colors["card_bg"], relief=tk.RAISED, bd=1)
        
        title_label = tk.Label(
            box,
            text=title,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["card_bg"],
            fg=color
        )
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(
            box,
            text=value,
            font=("Helvetica", 20, "bold"),
            bg=self.colors["card_bg"],
            fg=color
        )
        value_label.pack(pady=(0, 10))
        
        return box
    
    def create_quick_stats(self, parent):
        """Create quick stats overview"""
        stats_frame = self.create_card(parent)
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        
        header = tk.Frame(stats_frame, bg=self.colors["secondary"], height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📈 Quick Activity Summary",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["secondary"],
            fg="white"
        ).pack(side=tk.LEFT, pady=10, padx=15)
        
        content = tk.Frame(stats_frame, bg=self.colors["card_bg"])
        content.pack(fill=tk.X, padx=15, pady=15)
        
        self.quick_stats_labels = {}
        for i, activity in enumerate(["Studying", "Gaming", "Entertainment", "Other"]):
            activity_frame = tk.Frame(content, bg=self.colors["card_bg"])
            activity_frame.pack(fill=tk.X, pady=8)
            
            # Activity indicator
            tk.Label(
                activity_frame,
                text="●",
                font=("Helvetica", 16),
                bg=self.colors["card_bg"],
                fg=self.colors["primary"]
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(
                activity_frame,
                text=f"{activity}:",
                font=("Helvetica", 10, "bold"),
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"],
                width=18,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=5)
            
            self.quick_stats_labels[activity] = tk.Label(
                activity_frame,
                text="0h 0m",
                font=("Helvetica", 10, "bold"),
                bg=self.colors["card_bg"],
                fg=self.colors["secondary"]
            )
            self.quick_stats_labels[activity].pack(side=tk.LEFT, padx=5)
    
    def create_activity_section(self, parent):
        """Create activity selection section"""
        act_frame = self.create_card(parent)
        act_frame.pack(fill=tk.X, padx=15, pady=10)
        
        header = tk.Frame(act_frame, bg=self.colors["warning"], height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🎯 What Are You Doing?",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["warning"],
            fg="white"
        ).pack(side=tk.LEFT, pady=10, padx=15)
        
        act_content = tk.Frame(act_frame, bg=self.colors["card_bg"])
        act_content.pack(fill=tk.X, padx=15, pady=15)
        
        activities = ["Studying", "Gaming", "Entertainment", "Other"]
        
        for activity in activities:
            rb = tk.Radiobutton(
                act_content,
                text=activity,
                variable=self.current_activity,
                value=activity,
                font=("Helvetica", 10),
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"],
                activebackground=self.colors["card_bg"],
                selectcolor=self.colors["warning"]
            )
            rb.pack(anchor=tk.W, pady=5)
    
    def create_tracking_section(self, parent):
        """Create screen time tracking section"""
        track_frame = self.create_card(parent)
        track_frame.pack(fill=tk.X, padx=15, pady=10)
        
        header = tk.Frame(track_frame, bg=self.colors["success"], height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⏱️ Screen-Time Tracking",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["success"],
            fg="white"
        ).pack(side=tk.LEFT, pady=10, padx=15)
        
        track_content = tk.Frame(track_frame, bg=self.colors["card_bg"])
        track_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Quick add buttons
        quick_frame = tk.Frame(track_content, bg=self.colors["card_bg"])
        quick_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            quick_frame,
            text="Quick Add:",
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT, padx=5)
        
        for minutes in [15, 30, 60]:
            btn = tk.Button(
                quick_frame,
                text=f"+ {minutes}m",
                command=lambda m=minutes: self.add_screen_time(m),
                font=("Helvetica", 9, "bold"),
                bg=self.colors["secondary"],
                fg="white",
                padx=12,
                pady=6,
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Custom time input
        custom_frame = tk.Frame(track_content, bg=self.colors["card_bg"])
        custom_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            custom_frame,
            text="Custom Time (min):",
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT, padx=5)
        
        self.custom_time_entry = tk.Entry(
            custom_frame,
            width=8,
            font=("Helvetica", 10),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"],
            insertbackground=self.colors["primary"]
        )
        self.custom_time_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(
            custom_frame,
            text="Add",
            command=self.add_custom_time,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["primary"],
            fg="white",
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Current session timer
        timer_frame = tk.Frame(track_content, bg=self.colors["card_bg"])
        timer_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(
            timer_frame,
            text="Live Timer:",
            font=("Helvetica", 10, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT, padx=5)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="0h 0m 0s",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["accent"]
        )
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        button_frame = tk.Frame(timer_frame, bg=self.colors["card_bg"])
        button_frame.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start",
            command=self.start_session,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["success"],
            fg="white",
            padx=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_session,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["warning"],
            fg="white",
            padx=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
    
    def create_statistics_section(self, parent):
        """Create activity-wise statistics section"""
        stats_frame = self.create_card(parent)
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        
        header = tk.Frame(stats_frame, bg=self.colors["accent"], height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Detailed Statistics",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["accent"],
            fg="white"
        ).pack(side=tk.LEFT, pady=10, padx=15)
        
        stats_content = tk.Frame(stats_frame, bg=self.colors["card_bg"])
        stats_content.pack(fill=tk.X, padx=15, pady=15)
        
        self.stats_labels = {}
        colors_for_activities = [self.colors["primary"], self.colors["secondary"], 
                                  self.colors["warning"], self.colors["accent"]]
        
        for idx, activity in enumerate(["Studying", "Gaming", "Entertainment", "Other"]):
            activity_frame = tk.Frame(stats_content, bg=self.colors["card_bg"])
            activity_frame.pack(fill=tk.X, pady=8)
            
            tk.Label(
                activity_frame,
                text=f"{activity}:",
                font=("Helvetica", 10, "bold"),
                bg=self.colors["card_bg"],
                fg=self.colors["text_dark"],
                width=18,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=5)
            
            # Mini progress bar for each activity
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                activity_frame,
                variable=progress_var,
                maximum=100,
                length=150,
                mode='determinate'
            )
            progress_bar.pack(side=tk.LEFT, padx=5)
            
            self.stats_labels[f"{activity}_progress"] = progress_var
            
            self.stats_labels[activity] = tk.Label(
                activity_frame,
                text="0h 0m",
                font=("Helvetica", 10, "bold"),
                bg=self.colors["card_bg"],
                fg=colors_for_activities[idx]
            )
            self.stats_labels[activity].pack(side=tk.LEFT, padx=5)
    
    def create_button_section(self, parent):
        """Create action buttons section"""
        btn_frame = tk.Frame(parent, bg=self.colors["bg"])
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Daily goal settings
        goal_frame = tk.Frame(btn_frame, bg=self.colors["card_bg"], relief=tk.RAISED, bd=1)
        goal_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            goal_frame,
            text="Daily Goal (hours):",
            font=("Helvetica", 9, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"]
        ).pack(side=tk.LEFT, padx=5, pady=8)
        
        self.goal_entry = tk.Entry(
            goal_frame,
            width=5,
            font=("Helvetica", 10),
            bg=self.colors["card_bg"],
            fg=self.colors["text_dark"],
            insertbackground=self.colors["primary"]
        )
        self.goal_entry.pack(side=tk.LEFT, padx=2, pady=8)
        self.goal_entry.insert(0, str(self.session_data['daily_goal'] // 60))
        
        goal_btn = tk.Button(
            goal_frame,
            text="Set",
            command=self.set_daily_goal,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["secondary"],
            fg="white",
            padx=10,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        goal_btn.pack(side=tk.LEFT, padx=5, pady=8)
        
        # Take break button
        break_btn = tk.Button(
            btn_frame,
            text="☕ Take a Break",
            command=self.take_break,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["success"],
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        break_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = tk.Button(
            btn_frame,
            text="🔄 Reset Daily Data",
            command=self.reset_daily_data,
            font=("Helvetica", 9, "bold"),
            bg=self.colors["warning"],
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)
    
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
        messagebox.showinfo("✅ Success", f"Added {minutes} minutes of {activity}! 🎉")
    
    def add_custom_time(self):
        """Add custom screen time"""
        try:
            minutes = int(self.custom_time_entry.get())
            if minutes <= 0:
                messagebox.showerror("❌ Error", "Please enter a positive number!")
                return
            self.add_screen_time(minutes)
            self.custom_time_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid number!")
    
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
                messagebox.showinfo("✅ Success", f"Session ended! Added {minutes} minute(s). 🎯")
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
                messagebox.showerror("❌ Error", "Please enter a positive number!")
                return
            self.session_data['daily_goal'] = int(hours * 60)
            self.save_data()
            self.update_dashboard()
            messagebox.showinfo("✅ Success", f"Daily goal set to {hours} hours! 🎯")
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid number!")
    
    def take_break(self):
        """Record a break"""
        self.session_data['breaks_taken'] += 1
        self.save_data()
        self.update_dashboard()
        
        import random
        message = random.choice(BREAK_MESSAGES)
        messagebox.showinfo("☕ Break Time", message)
    
    def reset_daily_data(self):
        """Reset daily data"""
        if messagebox.askyesno("⚠️ Confirm", "Are you sure you want to reset today's data?"):
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
            messagebox.showinfo("✅ Success", "Daily data has been reset! 🔄")
    
    def update_dashboard(self):
        """Update all dashboard elements"""
        total_time = self.session_data['total_screen_time']
        daily_goal = self.session_data['daily_goal']
        
        # Update screen time display
        hours = total_time // 60
        minutes = total_time % 60
        self.screen_time_display.config(text=f"{hours}h {minutes}m")
        
        # Update daily goal display
        goal_hours = daily_goal // 60
        goal_minutes = daily_goal % 60
        self.goal_display.config(text=f"{goal_hours}h {goal_minutes}m")
        
        # Update breaks display
        self.breaks_display.config(text=str(self.session_data['breaks_taken']))
        
        # Update progress bar
        progress = (total_time / daily_goal * 100) if daily_goal > 0 else 0
        progress = min(progress, 100)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}% of daily goal used")
        
        # Update motivational message
        import random
        activity = self.current_activity.get()
        message = random.choice(MOTIVATIONAL_MESSAGES.get(activity, MOTIVATIONAL_MESSAGES["Other"]))
        self.motivational_label.config(text=message)
        
        # Update quick stats
        total_activities = sum(self.session_data['activity_time'].values())
        
        for activity in ["Studying", "Gaming", "Entertainment", "Other"]:
            time_minutes = self.session_data['activity_time'][activity]
            hours = time_minutes // 60
            minutes = time_minutes % 60
            self.quick_stats_labels[activity].config(text=f"{hours}h {minutes}m")
            
            # Update activity progress bars
            if total_activities > 0:
                activity_progress = (time_minutes / total_activities * 100)
            else:
                activity_progress = 0
            self.stats_labels[f"{activity}_progress"].set(activity_progress)
            
            self.stats_labels[activity].config(text=f"{hours}h {minutes}m")
    
    def start_break_reminder(self):
        """Start background thread for break reminders"""
        def reminder_loop():
            while True:
                time.sleep(60)
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
        
        if messagebox.askyesno("⏰ Break Reminder", message + "\n\nDid you take a break?"):
            self.take_break()


def main():
    root = tk.Tk()
    app = FocusBuddyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
