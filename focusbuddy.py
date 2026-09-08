import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time
import winsound  # For system sounds on Windows

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

# Modern Color Themes
THEMES = {
    "Neon Purple": {
        "bg": "#0a0e27",
        "primary": "#b721ff",
        "secondary": "#ff006e",
        "accent": "#00d9ff",
        "card_bg": "#1a1f3a",
        "text": "#ffffff",
        "text_light": "#b0b0b0",
        "success": "#00ff88",
        "warning": "#ffa500"
    },
    "Ocean Blue": {
        "bg": "#0f1419",
        "primary": "#00b4d8",
        "secondary": "#0096c7",
        "accent": "#00d9ff",
        "card_bg": "#1a2332",
        "text": "#ffffff",
        "text_light": "#a8dadc",
        "success": "#06d6a0",
        "warning": "#fb5607"
    },
    "Forest Green": {
        "bg": "#0b1929",
        "primary": "#2ecc71",
        "secondary": "#27ae60",
        "accent": "#1abc9c",
        "card_bg": "#1a3a2a",
        "text": "#ecf0f1",
        "text_light": "#95a5a6",
        "success": "#f39c12",
        "warning": "#e74c3c"
    },
    "Sunset Glow": {
        "bg": "#1a0f2e",
        "primary": "#ff6b6b",
        "secondary": "#ff8e3c",
        "accent": "#ffd93d",
        "card_bg": "#2d1b3d",
        "text": "#ffffff",
        "text_light": "#d4a5a5",
        "success": "#6bcf7f",
        "warning": "#ff6348"
    },
    "Cyber Dark": {
        "bg": "#0d0221",
        "primary": "#3a86ff",
        "secondary": "#8338ec",
        "accent": "#fb5607",
        "card_bg": "#1a0033",
        "text": "#ffffff",
        "text_light": "#c0c0c0",
        "success": "#06ffa5",
        "warning": "#ff006e"
    }
}


class FocusBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 FocusBuddy - Smart Screen-Time Nudge App")
        self.root.geometry("1100x900")
        self.root.resizable(True, True)
        
        # Set theme
        self.current_theme = "Neon Purple"
        self.theme = THEMES[self.current_theme].copy()
        self.root.configure(bg=self.theme["bg"])
        
        # Configure style
        self.setup_styles()
        
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
        
        # Start break reminder
        self.start_break_reminder()
    
    def setup_styles(self):
        """Setup ttk styles for the theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure progress bar colors
        style.configure("TProgressbar", 
                       background=self.theme["primary"],
                       troughcolor=self.theme["card_bg"],
                       bordercolor=self.theme["accent"],
                       lightcolor=self.theme["primary"],
                       darkcolor=self.theme["primary"])
        
        # Configure combobox
        style.configure("TCombobox",
                       fieldbackground=self.theme["card_bg"],
                       background=self.theme["primary"],
                       foreground=self.theme["text"])
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == str(datetime.now().date()):
                        return data
            except:
                pass
        
        return {
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
    
    def save_data(self):
        """Save data to JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.session_data, f, indent=4)
    
    def change_theme(self, theme_name):
        """Change the app theme"""
        self.current_theme = theme_name
        self.theme = THEMES[theme_name].copy()
        self.root.configure(bg=self.theme["bg"])
        self.setup_styles()
        
        # Clear and recreate UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_ui()
        self.update_dashboard()
    
    def play_sound(self):
        """Play a notification sound (Windows only)"""
        try:
            winsound.Beep(1000, 200)  # Frequency 1000Hz, Duration 200ms
        except:
            pass
    
    def create_ui(self):
        """Create the main UI with new design"""
        # Top header with gradient effect
        header_frame = tk.Frame(self.root, bg=self.theme["primary"], height=90)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Main title
        title_label = tk.Label(
            header_frame,
            text="⚡ FocusBuddy",
            font=("Arial", 28, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"]
        )
        title_label.pack(pady=(10, 0))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Smart Screen-Time Management for Students",
            font=("Arial", 10),
            bg=self.theme["primary"],
            fg=self.theme["text_light"]
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Theme selector on the right
        theme_selector_frame = tk.Frame(header_frame, bg=self.theme["primary"])
        theme_selector_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        tk.Label(
            theme_selector_frame,
            text="Theme: ",
            font=("Arial", 9, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"]
        ).pack(side=tk.LEFT, padx=5)
        
        theme_combo = ttk.Combobox(
            theme_selector_frame,
            values=list(THEMES.keys()),
            state="readonly",
            width=15,
            font=("Arial", 9)
        )
        theme_combo.set(self.current_theme)
        theme_combo.pack(side=tk.LEFT, padx=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_combo.get()))
        
        # Main content with scrollbar
        main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create sections
        self.create_mega_dashboard(scrollable_frame)
        self.create_activity_section(scrollable_frame)
        self.create_tracking_section(scrollable_frame)
        self.create_stats_section(scrollable_frame)
        self.create_controls_section(scrollable_frame)
    
    def create_card(self, parent, title, icon=""):
        """Create a styled card"""
        card = tk.Frame(parent, bg=self.theme["card_bg"], relief=tk.FLAT)
        card.pack(fill=tk.X, padx=0, pady=8)
        
        # Card header
        header = tk.Frame(card, bg=self.theme["primary"], height=45)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        header_label = tk.Label(
            header,
            text=f"{icon} {title}",
            font=("Arial", 12, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"]
        )
        header_label.pack(side=tk.LEFT, pady=10, padx=15)
        
        # Card content
        content = tk.Frame(card, bg=self.theme["card_bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        return content
    
    def create_mega_dashboard(self, parent):
        """Create the main dashboard with stats"""
        dash = tk.Frame(parent, bg=self.theme["card_bg"], relief=tk.FLAT)
        dash.pack(fill=tk.X, padx=0, pady=8)
        
        # Colorful header
        header = tk.Frame(dash, bg=self.theme["accent"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        header_label = tk.Label(
            header,
            text="🎯 TODAY'S PERFORMANCE",
            font=("Arial", 14, "bold"),
            bg=self.theme["accent"],
            fg=self.theme["bg"]
        )
        header_label.pack(side=tk.LEFT, pady=12, padx=15)
        
        # Stats grid
        stats_frame = tk.Frame(dash, bg=self.theme["card_bg"])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=20)
        
        # Screen Time Stat
        st_frame = tk.Frame(stats_frame, bg=self.theme["card_bg"], relief=tk.RAISED, bd=2)
        st_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(st_frame, text="⏱️", font=("Arial", 28), bg=self.theme["card_bg"]).pack(pady=(10, 0))
        tk.Label(st_frame, text="Screen Time", font=("Arial", 9, "bold"), 
                 bg=self.theme["card_bg"], fg=self.theme["text_light"]).pack()
        
        self.screen_time_label = tk.Label(st_frame, text="0h 0m", font=("Arial", 24, "bold"),
                                          bg=self.theme["card_bg"], fg=self.theme["secondary"])
        self.screen_time_label.pack(pady=(0, 10))
        
        # Daily Goal Stat
        dg_frame = tk.Frame(stats_frame, bg=self.theme["card_bg"], relief=tk.RAISED, bd=2)
        dg_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(dg_frame, text="🎯", font=("Arial", 28), bg=self.theme["card_bg"]).pack(pady=(10, 0))
        tk.Label(dg_frame, text="Daily Goal", font=("Arial", 9, "bold"), 
                 bg=self.theme["card_bg"], fg=self.theme["text_light"]).pack()
        
        self.goal_label = tk.Label(dg_frame, text="8h 0m", font=("Arial", 24, "bold"),
                                   bg=self.theme["card_bg"], fg=self.theme["primary"])
        self.goal_label.pack(pady=(0, 10))
        
        # Breaks Stat
        br_frame = tk.Frame(stats_frame, bg=self.theme["card_bg"], relief=tk.RAISED, bd=2)
        br_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(br_frame, text="☕", font=("Arial", 28), bg=self.theme["card_bg"]).pack(pady=(10, 0))
        tk.Label(br_frame, text="Breaks Taken", font=("Arial", 9, "bold"), 
                 bg=self.theme["card_bg"], fg=self.theme["text_light"]).pack()
        
        self.breaks_label = tk.Label(br_frame, text="0", font=("Arial", 24, "bold"),
                                     bg=self.theme["card_bg"], fg=self.theme["success"])
        self.breaks_label.pack(pady=(0, 10))
        
        # Progress section
        progress_frame = tk.Frame(dash, bg=self.theme["card_bg"])
        progress_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(progress_frame, text="Progress to Goal", font=("Arial", 11, "bold"),
                 bg=self.theme["card_bg"], fg=self.theme["text"]).pack(anchor=tk.W, pady=(0, 8))
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="0% used", font=("Arial", 9, "bold"),
                                       bg=self.theme["card_bg"], fg=self.theme["accent"])
        self.progress_label.pack(anchor=tk.W)
        
        # Motivational message
        self.motivational_label = tk.Label(
            dash,
            text="Keep crushing your goals! 💪",
            font=("Arial", 11, "italic"),
            bg=self.theme["card_bg"],
            fg=self.theme["accent"],
            wraplength=600
        )
        self.motivational_label.pack(pady=10)
    
    def create_activity_section(self, parent):
        """Create activity selection"""
        content = self.create_card(parent, "What Are You Doing?", "🎮")
        
        activities = ["Studying", "Gaming", "Entertainment", "Other"]
        activity_frame = tk.Frame(content, bg=self.theme["card_bg"])
        activity_frame.pack(fill=tk.X)
        
        for i, activity in enumerate(activities):
            rb_frame = tk.Frame(activity_frame, bg=self.theme["card_bg"])
            rb_frame.pack(fill=tk.X, pady=8)
            
            rb = tk.Radiobutton(
                rb_frame,
                text=activity,
                variable=self.current_activity,
                value=activity,
                font=("Arial", 11, "bold"),
                bg=self.theme["card_bg"],
                fg=self.theme["text"],
                activebackground=self.theme["card_bg"],
                activeforeground=self.theme["accent"],
                selectcolor=self.theme["primary"],
                command=self.update_dashboard
            )
            rb.pack(anchor=tk.W, padx=15)
    
    def create_tracking_section(self, parent):
        """Create tracking section"""
        content = self.create_card(parent, "Screen-Time Tracking", "⏱️")
        
        # Quick add buttons
        quick_frame = tk.Frame(content, bg=self.theme["card_bg"])
        quick_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(quick_frame, text="Quick Add:", font=("Arial", 10, "bold"),
                 bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=5)
        
        for minutes in [15, 30, 60]:
            btn = tk.Button(
                quick_frame,
                text=f"+ {minutes}m",
                command=lambda m=minutes: self.add_screen_time(m),
                font=("Arial", 10, "bold"),
                bg=self.theme["secondary"],
                fg=self.theme["text"],
                padx=12,
                pady=6,
                relief=tk.FLAT,
                cursor="hand2",
                activebackground=self.theme["accent"]
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Custom input
        custom_frame = tk.Frame(content, bg=self.theme["card_bg"])
        custom_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(custom_frame, text="Custom Time (min):", font=("Arial", 10, "bold"),
                 bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=5)
        
        self.custom_entry = tk.Entry(
            custom_frame,
            width=8,
            font=("Arial", 10),
            bg=self.theme["card_bg"],
            fg=self.theme["text"],
            insertbackground=self.theme["accent"],
            relief=tk.FLAT,
            bd=2
        )
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(
            custom_frame,
            text="Add",
            command=self.add_custom_time,
            font=("Arial", 9, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"],
            padx=15,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"]
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Timer section
        timer_frame = tk.Frame(content, bg=self.theme["card_bg"])
        timer_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(timer_frame, text="Live Timer:", font=("Arial", 10, "bold"),
                 bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=5)
        
        self.timer_label = tk.Label(
            timer_frame,
            text="0h 0m 0s",
            font=("Arial", 14, "bold"),
            bg=self.theme["card_bg"],
            fg=self.theme["accent"]
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        button_frame = tk.Frame(timer_frame, bg=self.theme["card_bg"])
        button_frame.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Session",
            command=self.start_session,
            font=("Arial", 9, "bold"),
            bg=self.theme["success"],
            fg=self.theme["bg"],
            padx=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"]
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_session,
            font=("Arial", 9, "bold"),
            bg=self.theme["warning"],
            fg=self.theme["bg"],
            padx=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"],
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
    
    def create_stats_section(self, parent):
        """Create statistics section"""
        content = self.create_card(parent, "Activity Statistics", "📊")
        
        self.stats_labels = {}
        colors = [self.theme["primary"], self.theme["secondary"], 
                  self.theme["accent"], self.theme["success"]]
        
        for idx, activity in enumerate(["Studying", "Gaming", "Entertainment", "Other"]):
            act_frame = tk.Frame(content, bg=self.theme["card_bg"])
            act_frame.pack(fill=tk.X, pady=8)
            
            tk.Label(
                act_frame,
                text=f"{activity}:",
                font=("Arial", 10, "bold"),
                bg=self.theme["card_bg"],
                fg=self.theme["text"],
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=5)
            
            self.stats_labels[activity] = tk.Label(
                act_frame,
                text="0h 0m",
                font=("Arial", 10, "bold"),
                bg=self.theme["card_bg"],
                fg=colors[idx]
            )
            self.stats_labels[activity].pack(side=tk.LEFT, padx=5)
    
    def create_controls_section(self, parent):
        """Create control buttons section"""
        content = self.create_card(parent, "Settings & Actions", "⚙️")
        
        # Goal setting
        goal_frame = tk.Frame(content, bg=self.theme["card_bg"])
        goal_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(goal_frame, text="Daily Goal (hours):", font=("Arial", 10, "bold"),
                 bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=5)
        
        self.goal_entry = tk.Entry(
            goal_frame,
            width=5,
            font=("Arial", 10),
            bg=self.theme["card_bg"],
            fg=self.theme["text"],
            insertbackground=self.theme["accent"],
            relief=tk.FLAT,
            bd=2
        )
        self.goal_entry.pack(side=tk.LEFT, padx=5)
        self.goal_entry.insert(0, str(self.session_data['daily_goal'] // 60))
        
        set_goal_btn = tk.Button(
            goal_frame,
            text="Set Goal",
            command=self.set_daily_goal,
            font=("Arial", 9, "bold"),
            bg=self.theme["primary"],
            fg=self.theme["text"],
            padx=15,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"]
        )
        set_goal_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        btn_frame = tk.Frame(content, bg=self.theme["card_bg"])
        btn_frame.pack(fill=tk.X, pady=15)
        
        break_btn = tk.Button(
            btn_frame,
            text="☕ Take a Break",
            command=self.take_break,
            font=("Arial", 10, "bold"),
            bg=self.theme["success"],
            fg=self.theme["bg"],
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"]
        )
        break_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(
            btn_frame,
            text="🔄 Reset Daily Data",
            command=self.reset_daily_data,
            font=("Arial", 10, "bold"),
            bg=self.theme["warning"],
            fg=self.theme["bg"],
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground=self.theme["accent"]
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
        self.play_sound()
        messagebox.showinfo("✅ Success", f"Added {minutes} minutes of {activity}! 🎉")
    
    def add_custom_time(self):
        """Add custom time"""
        try:
            minutes = int(self.custom_entry.get())
            if minutes <= 0:
                messagebox.showerror("❌ Error", "Enter a positive number!")
                return
            self.add_screen_time(minutes)
            self.custom_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("❌ Error", "Enter a valid number!")
    
    def start_session(self):
        """Start session"""
        self.is_tracking = True
        self.session_timer = 0
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.play_sound()
        self.update_timer()
    
    def stop_session(self):
        """Stop session"""
        self.is_tracking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.play_sound()
        
        if self.session_timer > 0:
            minutes = self.session_timer // 60
            if minutes > 0:
                self.add_screen_time(minutes)
                messagebox.showinfo("✅ Session Ended", f"Added {minutes} minute(s)! 🎯")
            self.session_timer = 0
            self.timer_label.config(text="0h 0m 0s")
    
    def update_timer(self):
        """Update timer"""
        if self.is_tracking:
            self.session_timer += 1
            hours = self.session_timer // 3600
            minutes = (self.session_timer % 3600) // 60
            seconds = self.session_timer % 60
            self.timer_label.config(text=f"{hours}h {minutes}m {seconds}s")
            self.root.after(1000, self.update_timer)
    
    def set_daily_goal(self):
        """Set daily goal"""
        try:
            hours = float(self.goal_entry.get())
            if hours <= 0:
                messagebox.showerror("❌ Error", "Enter a positive number!")
                return
            self.session_data['daily_goal'] = int(hours * 60)
            self.save_data()
            self.update_dashboard()
            self.play_sound()
            messagebox.showinfo("✅ Goal Set", f"Daily goal set to {hours} hours! 🎯")
        except ValueError:
            messagebox.showerror("❌ Error", "Enter a valid number!")
    
    def take_break(self):
        """Take a break"""
        self.session_data['breaks_taken'] += 1
        self.save_data()
        self.update_dashboard()
        self.play_sound()
        
        import random
        message = random.choice(BREAK_MESSAGES)
        messagebox.showinfo("☕ Break Time", message)
    
    def reset_daily_data(self):
        """Reset daily data"""
        if messagebox.askyesno("⚠️ Confirm", "Reset today's data?"):
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
            self.play_sound()
            messagebox.showinfo("✅ Reset Complete", "Daily data cleared! 🔄")
    
    def update_dashboard(self):
        """Update dashboard"""
        total_time = self.session_data['total_screen_time']
        daily_goal = self.session_data['daily_goal']
        
        # Update display
        hours = total_time // 60
        minutes = total_time % 60
        self.screen_time_label.config(text=f"{hours}h {minutes}m")
        
        goal_hours = daily_goal // 60
        goal_minutes = daily_goal % 60
        self.goal_label.config(text=f"{goal_hours}h {goal_minutes}m")
        
        self.breaks_label.config(text=str(self.session_data['breaks_taken']))
        
        # Progress
        progress = (total_time / daily_goal * 100) if daily_goal > 0 else 0
        progress = min(progress, 100)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}% used")
        
        # Motivational message
        import random
        activity = self.current_activity.get()
        message = random.choice(MOTIVATIONAL_MESSAGES.get(activity, MOTIVATIONAL_MESSAGES["Other"]))
        self.motivational_label.config(text=message)
        
        # Stats
        for activity in ["Studying", "Gaming", "Entertainment", "Other"]:
            time_minutes = self.session_data['activity_time'][activity]
            hours = time_minutes // 60
            minutes = time_minutes % 60
            self.stats_labels[activity].config(text=f"{hours}h {minutes}m")
    
    def start_break_reminder(self):
        """Start break reminder"""
        def reminder_loop():
            while True:
                time.sleep(60)
                if self.is_tracking:
                    self.break_counter += 1
                    if self.break_counter >= 25:
                        self.show_break_reminder()
                        self.break_counter = 0
                else:
                    self.break_counter = 0
        
        self.break_reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
        self.break_reminder_thread.start()
    
    def show_break_reminder(self):
        """Show break reminder"""
        self.play_sound()
        activity = self.current_activity.get()
        
        if activity == "Studying":
            message = "You've been studying for 25 minutes!\nTime for a short break! 📚"
        else:
            message = "You've been at it for 25 minutes!\nTime to take a break! 🧘"
        
        if messagebox.askyesno("⏰ Break Reminder", message + "\n\nDid you take a break?"):
            self.take_break()


def main():
    root = tk.Tk()
    app = FocusBuddyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
