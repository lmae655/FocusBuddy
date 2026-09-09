import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time
import winsound
import random

DATA_FILE = "focusbuddy_data.json"

MOTIVATIONAL_MESSAGES = {
    "Studying": ["Great focus session! Keep it up! 📚", "You're doing amazing! Stay focused! 💪", "Learning is a superpower! Keep going! 🚀", "Your future self will thank you! 📖", "Excellence is earned through dedication! ⭐"],
    "Gaming": ["Having fun? Don't forget to take breaks! 🎮", "Remember to rest your eyes soon! 👀", "Balance is key! Consider a study session next! 🎯", "Gaming is cool, but health comes first! 🏥"],
    "Entertainment": ["Enjoying yourself? That's great! 🎬", "Don't forget your daily goals! 🎯", "Time for a break? Your eyes need it! 👁️", "You deserve entertainment, but balance matters! ⚖️"],
    "Other": ["Keep up the good work! 💯", "You're making progress! 🌟", "Stay consistent! 🎯"]
}

BREAK_MESSAGES = ["Time for a break! Look away from the screen! 👀", "Your eyes need a rest! Take 5 minutes off! 🧘", "Stretch it out! Your body will thank you! 🤸", "Hydration break! Grab some water! 💧", "Time to move! Walk around for a bit! 🚶", "Rest your mind! Close your eyes for a moment! 😌"]

THEMES = {
    "Ocean": {
        "bg": "#0f1419",
        "primary": "#00b4d8",
        "secondary": "#0096c7",
        "accent": "#00d9ff",
        "card_bg": "#1a2332",
        "text": "#ffffff",
        "text_light": "#a8dadc",
        "success": "#06d6a0",
        "warning": "#fb5607",
        "header": "#0096c7",
        "stat_bg": "#164e63"
    },
    "Fire": {
        "bg": "#1a0f0a",
        "primary": "#ff6b35",
        "secondary": "#f7931e",
        "accent": "#ffa500",
        "card_bg": "#2d1810",
        "text": "#ffffff",
        "text_light": "#ffb84d",
        "success": "#ff9d00",
        "warning": "#d62828",
        "header": "#d62828",
        "stat_bg": "#3d2817"
    },
    "Sunset": {
        "bg": "#2a1810",
        "primary": "#ff6b6b",
        "secondary": "#ff8e3c",
        "accent": "#ffd93d",
        "card_bg": "#3f2d1d",
        "text": "#ffffff",
        "text_light": "#fed7aa",
        "success": "#6bcf7f",
        "warning": "#ff6348",
        "header": "#e63946",
        "stat_bg": "#4d3828"
    },
    "Nature": {
        "bg": "#0b1929",
        "primary": "#2ecc71",
        "secondary": "#27ae60",
        "accent": "#1abc9c",
        "card_bg": "#1a3a2a",
        "text": "#ecf0f1",
        "text_light": "#95a5a6",
        "success": "#f39c12",
        "warning": "#e74c3c",
        "header": "#27ae60",
        "stat_bg": "#0f4c27"
    },
    "Dark": {
        "bg": "#0d0221",
        "primary": "#3a86ff",
        "secondary": "#8338ec",
        "accent": "#fb5607",
        "card_bg": "#1a0033",
        "text": "#ffffff",
        "text_light": "#c0c0c0",
        "success": "#06ffa5",
        "warning": "#ff006e",
        "header": "#1f0047",
        "stat_bg": "#2d0052"
    }
}

class FocusBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ FocusBuddy - Smart Screen-Time Nudge App")
        self.root.geometry("1200x1000")
        self.root.resizable(True, True)
        
        self.current_theme = "Ocean"
        self.theme = THEMES[self.current_theme].copy()
        self.root.configure(bg=self.theme["bg"])
        
        self.setup_styles()
        
        self.current_activity = tk.StringVar(value="Studying")
        self.session_data = self.load_data()
        self.session_timer = 0
        self.is_tracking = False
        self.break_reminder_thread = None
        self.break_counter = 0
        self.daily_goal_thread = None
        self.daily_goal_reached = False
        self.alarm_playing = False
        self.music_playing = True
        
        self.create_ui()
        self.update_dashboard()
        self.start_break_reminder()
        self.start_daily_goal_monitor()
        self.play_background_music()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", background=self.theme["primary"], troughcolor=self.theme["card_bg"])
        style.configure("TCombobox", fieldbackground=self.theme["card_bg"], background=self.theme["primary"])
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == str(datetime.now().date()):
                        return data
            except:
                pass
        return {'date': str(datetime.now().date()), 'daily_goal': 480, 'total_screen_time': 0, 'breaks_taken': 0, 'sessions': [], 'activity_time': {'Studying': 0, 'Gaming': 0, 'Entertainment': 0, 'Other': 0}}
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.session_data, f, indent=4)
    
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme = THEMES[theme_name].copy()
        self.root.configure(bg=self.theme["bg"])
        self.setup_styles()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_ui()
        self.update_dashboard()
    
    def play_sound(self, frequency=1000, duration=200):
        try:
            winsound.Beep(frequency, duration)
        except:
            pass
    
    def play_alarm(self):
        if not self.alarm_playing:
            self.alarm_playing = True
            try:
                for i in range(5):
                    winsound.Beep(2000, 300)
                    time.sleep(0.1)
                    winsound.Beep(1500, 300)
                    time.sleep(0.1)
            except:
                pass
            self.alarm_playing = False
    
    def play_background_music(self):
        def music_loop():
            frequencies = [523, 587, 659, 784, 880, 987, 1047, 987, 880, 784, 659, 587]
            while self.music_playing:
                try:
                    for freq in frequencies:
                        if not self.alarm_playing and self.music_playing:
                            winsound.Beep(freq, 150)
                            time.sleep(0.1)
                    time.sleep(2)
                except:
                    break
        music_thread = threading.Thread(target=music_loop, daemon=True)
        music_thread.start()
    
    def create_ui(self):
        # Header with spacing
        header_frame = tk.Frame(self.root, bg=self.theme["header"], height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="⚡ FocusBuddy", font=("Arial", 32, "bold"), bg=self.theme["header"], fg=self.theme["text"])
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(header_frame, text="Smart Screen-Time Management for Students", font=("Arial", 11), bg=self.theme["header"], fg=self.theme["text_light"])
        subtitle_label.pack(pady=(0, 15))
        
        # Theme selector
        theme_selector_frame = tk.Frame(header_frame, bg=self.theme["header"])
        theme_selector_frame.pack(side=tk.RIGHT, padx=30, pady=15)
        
        tk.Label(theme_selector_frame, text="🎨 Theme:", font=("Arial", 10, "bold"), bg=self.theme["header"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=8)
        
        theme_combo = ttk.Combobox(theme_selector_frame, values=list(THEMES.keys()), state="readonly", width=12, font=("Arial", 10))
        theme_combo.set(self.current_theme)
        theme_combo.pack(side=tk.LEFT, padx=8)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_combo.get()))
        
        # Main content with scrollbar
        main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        canvas = tk.Canvas(main_frame, bg=self.theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme["bg"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_mega_dashboard(scrollable_frame)
        self.create_activity_section(scrollable_frame)
        self.create_tracking_section(scrollable_frame)
        self.create_stats_section(scrollable_frame)
        self.create_controls_section(scrollable_frame)
    
    def create_card(self, parent, title, icon=""):
        card = tk.Frame(parent, bg=self.theme["card_bg"], relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, padx=0, pady=15)
        
        header = tk.Frame(card, bg=self.theme["primary"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text=f"{icon} {title}", font=("Arial", 13, "bold"), bg=self.theme["primary"], fg=self.theme["text"])
        header_label.pack(side=tk.LEFT, pady=12, padx=20)
        
        content = tk.Frame(card, bg=self.theme["card_bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        return content
    
    def create_mega_dashboard(self, parent):
        dash = tk.Frame(parent, bg=self.theme["card_bg"], relief=tk.RAISED, bd=2)
        dash.pack(fill=tk.X, padx=0, pady=15)
        
        header = tk.Frame(dash, bg=self.theme["accent"], height=55)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text="🎯 TODAY'S PERFORMANCE", font=("Arial", 15, "bold"), bg=self.theme["accent"], fg=self.theme["bg"])
        header_label.pack(side=tk.LEFT, pady=12, padx=20)
        
        stats_frame = tk.Frame(dash, bg=self.theme["card_bg"])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Screen time stat
        st_frame = tk.Frame(stats_frame, bg=self.theme["stat_bg"], relief=tk.RAISED, bd=2)
        st_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        
        tk.Label(st_frame, text="⏱️", font=("Arial", 32), bg=self.theme["stat_bg"]).pack(pady=(15, 5))
        tk.Label(st_frame, text="Screen Time", font=("Arial", 10, "bold"), bg=self.theme["stat_bg"], fg=self.theme["text_light"]).pack()
        self.screen_time_label = tk.Label(st_frame, text="0h 0m", font=("Arial", 26, "bold"), bg=self.theme["stat_bg"], fg=self.theme["secondary"])
        self.screen_time_label.pack(pady=(5, 15))
        
        # Daily goal stat
        dg_frame = tk.Frame(stats_frame, bg=self.theme["stat_bg"], relief=tk.RAISED, bd=2)
        dg_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        
        tk.Label(dg_frame, text="🎯", font=("Arial", 32), bg=self.theme["stat_bg"]).pack(pady=(15, 5))
        tk.Label(dg_frame, text="Daily Goal", font=("Arial", 10, "bold"), bg=self.theme["stat_bg"], fg=self.theme["text_light"]).pack()
        self.goal_label = tk.Label(dg_frame, text="8h 0m", font=("Arial", 26, "bold"), bg=self.theme["stat_bg"], fg=self.theme["primary"])
        self.goal_label.pack(pady=(5, 15))
        
        # Breaks stat
        br_frame = tk.Frame(stats_frame, bg=self.theme["stat_bg"], relief=tk.RAISED, bd=2)
        br_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        
        tk.Label(br_frame, text="☕", font=("Arial", 32), bg=self.theme["stat_bg"]).pack(pady=(15, 5))
        tk.Label(br_frame, text="Breaks Taken", font=("Arial", 10, "bold"), bg=self.theme["stat_bg"], fg=self.theme["text_light"]).pack()
        self.breaks_label = tk.Label(br_frame, text="0", font=("Arial", 26, "bold"), bg=self.theme["stat_bg"], fg=self.theme["success"])
        self.breaks_label.pack(pady=(5, 15))
        
        # Progress section
        progress_frame = tk.Frame(dash, bg=self.theme["card_bg"])
        progress_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(progress_frame, text="Progress to Goal", font=("Arial", 12, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"]).pack(anchor=tk.W, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate', length=500)
        progress_bar.pack(fill=tk.X, pady=8)
        
        self.progress_label = tk.Label(progress_frame, text="0% used", font=("Arial", 10, "bold"), bg=self.theme["card_bg"], fg=self.theme["accent"])
        self.progress_label.pack(anchor=tk.W)
        
        # Motivational message
        self.motivational_label = tk.Label(dash, text="Keep crushing your goals! 💪", font=("Arial", 12, "italic"), bg=self.theme["card_bg"], fg=self.theme["accent"], wraplength=700)
        self.motivational_label.pack(pady=(0, 20), padx=20)
    
    def create_activity_section(self, parent):
        content = self.create_card(parent, "What Are You Doing?", "🎮")
        
        activities = ["Studying", "Gaming", "Entertainment", "Other"]
        activity_frame = tk.Frame(content, bg=self.theme["card_bg"])
        activity_frame.pack(fill=tk.X)
        
        for activity in activities:
            rb_frame = tk.Frame(activity_frame, bg=self.theme["card_bg"])
            rb_frame.pack(fill=tk.X, pady=12)
            
            rb = tk.Radiobutton(rb_frame, text=activity, variable=self.current_activity, value=activity, font=("Arial", 12, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"], activebackground=self.theme["card_bg"], activeforeground=self.theme["accent"], selectcolor=self.theme["primary"], command=self.update_dashboard)
            rb.pack(anchor=tk.W, padx=20)
    
    def create_tracking_section(self, parent):
        content = self.create_card(parent, "Screen-Time Tracking", "⏱️")
        
        # Quick add buttons
        quick_frame = tk.Frame(content, bg=self.theme["card_bg"])
        quick_frame.pack(fill=tk.X, pady=12)
        
        tk.Label(quick_frame, text="Quick Add:", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=8)
        
        for minutes in [15, 30, 60]:
            btn = tk.Button(quick_frame, text=f"+ {minutes}m", command=lambda m=minutes: self.add_screen_time(m), font=("Arial", 11, "bold"), bg=self.theme["secondary"], fg=self.theme["text"], padx=14, pady=8, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
            btn.pack(side=tk.LEFT, padx=8)
        
        # Custom input
        custom_frame = tk.Frame(content, bg=self.theme["card_bg"])
        custom_frame.pack(fill=tk.X, pady=12)
        
        tk.Label(custom_frame, text="Custom Time (min):", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=8)
        
        self.custom_entry = tk.Entry(custom_frame, width=10, font=("Arial", 11), bg=self.theme["card_bg"], fg=self.theme["text"], insertbackground=self.theme["accent"], relief=tk.FLAT, bd=2)
        self.custom_entry.pack(side=tk.LEFT, padx=8)
        
        add_btn = tk.Button(custom_frame, text="Add", command=self.add_custom_time, font=("Arial", 10, "bold"), bg=self.theme["primary"], fg=self.theme["text"], padx=16, pady=6, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
        add_btn.pack(side=tk.LEFT, padx=8)
        
        # Timer section
        timer_frame = tk.Frame(content, bg=self.theme["card_bg"])
        timer_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(timer_frame, text="Live Timer:", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=8)
        
        self.timer_label = tk.Label(timer_frame, text="0h 0m 0s", font=("Arial", 15, "bold"), bg=self.theme["card_bg"], fg=self.theme["accent"])
        self.timer_label.pack(side=tk.LEFT, padx=15)
        
        button_frame = tk.Frame(timer_frame, bg=self.theme["card_bg"])
        button_frame.pack(side=tk.LEFT, padx=8)
        
        self.start_btn = tk.Button(button_frame, text="▶ Start Session", command=self.start_session, font=("Arial", 10, "bold"), bg=self.theme["success"], fg=self.theme["bg"], padx=13, pady=7, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
        self.start_btn.pack(side=tk.LEFT, padx=3)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ Stop", command=self.stop_session, font=("Arial", 10, "bold"), bg=self.theme["warning"], fg=self.theme["bg"], padx=13, pady=7, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"], state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
    
    def create_stats_section(self, parent):
        content = self.create_card(parent, "Activity Statistics", "📊")
        
        self.stats_labels = {}
        colors = [self.theme["primary"], self.theme["secondary"], self.theme["accent"], self.theme["success"]]
        
        for idx, activity in enumerate(["Studying", "Gaming", "Entertainment", "Other"]):
            act_frame = tk.Frame(content, bg=self.theme["card_bg"])
            act_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(act_frame, text=f"{activity}:", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"], width=18, anchor=tk.W).pack(side=tk.LEFT, padx=8)
            
            self.stats_labels[activity] = tk.Label(act_frame, text="0h 0m", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=colors[idx])
            self.stats_labels[activity].pack(side=tk.LEFT, padx=8)
    
    def create_controls_section(self, parent):
        content = self.create_card(parent, "Settings & Actions", "⚙️")
        
        # Goal setting
        goal_frame = tk.Frame(content, bg=self.theme["card_bg"])
        goal_frame.pack(fill=tk.X, pady=12)
        
        tk.Label(goal_frame, text="Daily Goal (hours):", font=("Arial", 11, "bold"), bg=self.theme["card_bg"], fg=self.theme["text"]).pack(side=tk.LEFT, padx=8)
        
        self.goal_entry = tk.Entry(goal_frame, width=6, font=("Arial", 11), bg=self.theme["card_bg"], fg=self.theme["text"], insertbackground=self.theme["accent"], relief=tk.FLAT, bd=2)
        self.goal_entry.pack(side=tk.LEFT, padx=8)
        self.goal_entry.insert(0, str(self.session_data['daily_goal'] // 60))
        
        set_goal_btn = tk.Button(goal_frame, text="Set Goal", command=self.set_daily_goal, font=("Arial", 10, "bold"), bg=self.theme["primary"], fg=self.theme["text"], padx=16, pady=6, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
        set_goal_btn.pack(side=tk.LEFT, padx=8)
        
        # Action buttons
        btn_frame = tk.Frame(content, bg=self.theme["card_bg"])
        btn_frame.pack(fill=tk.X, pady=15)
        
        break_btn = tk.Button(btn_frame, text="☕ Take a Break", command=self.take_break, font=("Arial", 11, "bold"), bg=self.theme["success"], fg=self.theme["bg"], padx=22, pady=9, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
        break_btn.pack(side=tk.LEFT, padx=8)
        
        reset_btn = tk.Button(btn_frame, text="🔄 Reset Daily Data", command=self.reset_daily_data, font=("Arial", 11, "bold"), bg=self.theme["warning"], fg=self.theme["bg"], padx=22, pady=9, relief=tk.FLAT, cursor="hand2", activebackground=self.theme["accent"])
        reset_btn.pack(side=tk.RIGHT, padx=8)
    
    def add_screen_time(self, minutes):
        activity = self.current_activity.get()
        self.session_data['total_screen_time'] += minutes
        self.session_data['activity_time'][activity] += minutes
        self.session_data['sessions'].append({'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'activity': activity, 'duration': minutes})
        self.save_data()
        self.update_dashboard()
        self.play_sound()
        messagebox.showinfo("✅ Success", f"Added {minutes} minutes of {activity}! 🎉")
    
    def add_custom_time(self):
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
        self.is_tracking = True
        self.session_timer = 0
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.play_sound()
        self.update_timer()
    
    def stop_session(self):
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
        if self.is_tracking:
            self.session_timer += 1
            hours = self.session_timer // 3600
            minutes = (self.session_timer % 3600) // 60
            seconds = self.session_timer % 60
            self.timer_label.config(text=f"{hours}h {minutes}m {seconds}s")
            self.root.after(1000, self.update_timer)
    
    def set_daily_goal(self):
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
        self.session_data['breaks_taken'] += 1
        self.save_data()
        self.update_dashboard()
        self.play_sound()
        message = random.choice(BREAK_MESSAGES)
        messagebox.showinfo("☕ Break Time", message)
    
    def reset_daily_data(self):
        if messagebox.askyesno("⚠️ Confirm", "Reset today's data?"):
            self.session_data = {'date': str(datetime.now().date()), 'daily_goal': 480, 'total_screen_time': 0, 'breaks_taken': 0, 'sessions': [], 'activity_time': {'Studying': 0, 'Gaming': 0, 'Entertainment': 0, 'Other': 0}}
            self.save_data()
            self.update_dashboard()
            self.play_sound()
            messagebox.showinfo("✅ Reset Complete", "Daily data cleared! 🔄")
    
    def update_dashboard(self):
        total_time = self.session_data['total_screen_time']
        daily_goal = self.session_data['daily_goal']
        hours = total_time // 60
        minutes = total_time % 60
        self.screen_time_label.config(text=f"{hours}h {minutes}m")
        goal_hours = daily_goal // 60
        goal_minutes = daily_goal % 60
        self.goal_label.config(text=f"{goal_hours}h {goal_minutes}m")
        self.breaks_label.config(text=str(self.session_data['breaks_taken']))
        progress = (total_time / daily_goal * 100) if daily_goal > 0 else 0
        progress = min(progress, 100)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}% used")
        activity = self.current_activity.get()
        message = random.choice(MOTIVATIONAL_MESSAGES.get(activity, MOTIVATIONAL_MESSAGES["Other"]))
        self.motivational_label.config(text=message)
        for activity in ["Studying", "Gaming", "Entertainment", "Other"]:
            time_minutes = self.session_data['activity_time'][activity]
            hours = time_minutes // 60
            minutes = time_minutes % 60
            self.stats_labels[activity].config(text=f"{hours}h {minutes}m")
    
    def start_daily_goal_monitor(self):
        def goal_monitor_loop():
            while True:
                time.sleep(5)
                total_time = self.session_data['total_screen_time']
                daily_goal = self.session_data['daily_goal']
                if total_time >= daily_goal and not self.daily_goal_reached:
                    self.daily_goal_reached = True
                    self.trigger_goal_completion_alarm()
                elif total_time < daily_goal:
                    self.daily_goal_reached = False
        self.daily_goal_thread = threading.Thread(target=goal_monitor_loop, daemon=True)
        self.daily_goal_thread.start()
    
    def trigger_goal_completion_alarm(self):
        self.alarm_playing = True
        self.play_alarm()
        random_theme = random.choice(list(THEMES.keys()))
        self.change_theme(random_theme)
        messagebox.showwarning("🎉 DAILY GOAL COMPLETED! 🎉", f"🎊 Congratulations! 🎊\n\nYou have reached your daily screen-time goal!\nGreat work! Take a well-deserved break! ☕\n\nRemember to rest your eyes and stretch! 🧘")
        self.alarm_playing = False
    
    def start_break_reminder(self):
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
