import customtkinter as ctk
from PIL import Image
import requests
import os
import datetime
import json
import random

# ==========================================
# 1. GLOBAL STATE & CONFIG
# ==========================================
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
SCHEDULE_FILE = "schedule.json"
API_URL = "http://127.0.0.1:8000/api/top-workouts"

# COLOR PALETTE
BG_DARK_GREY = "#2A2B2E"
PANEL_GREY = "#35373B"
SOFT_BLUE = "#5C8EAD"
HOVER_BLUE = "#4A748F"

IMAGE_MAP = {
    "Upper Chest (Clavicular)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    "Middle Chest (Sternal Mid)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    "Lower Chest (Sternal Lower)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    "Lats": {"front": "Back_front.png", "back": "Back_back.png"},
    "Upper Back / Rhomboids / Middle Traps": {"front": "Back_front.png", "back": "Back_back.png"},
    "Lower Back": {"front": "Back_front.png", "back": "Back_back.png"},
    "Legs": {"front": "Legs_front.png", "back": "Legs_back.png"},
    "Quads": {"front": "Legs_front.png", "back": "Legs_back.png"},
    "Hamstrings": {"front": "Legs_front.png", "back": "Legs_back.png"},
    "Calves": {"front": "Legs_front.png", "back": "Legs_back.png"},
    "Glutes": {"front": "Legs_front.png", "back": "Legs_back.png"},
    "Default": {"front": "1canadite.png", "back": "2canadite.png"}
}

SPLIT_MAP = {
    "Push": ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lower Chest (Sternal Lower)", "Triceps", "Front Delts"],
    "Pull": ["Lats", "Upper Back / Rhomboids / Middle Traps", "Lower Back", "Biceps"],
    "Legs": ["Quads", "Hamstrings", "Calves", "Glutes"],
    "Upper": ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lats", "Upper Back / Rhomboids / Middle Traps", "Biceps", "Triceps"],
    "Lower": ["Quads", "Hamstrings", "Calves", "Glutes"],
    "Cardio": ["PLACEHOLDER_CARDIO"]
}

GOAL_MAP = {
    "Strength": {"sets": (3, 4), "reps": (3, 6), "weight": "Max Weight"},
    "Hypertrophy": {"sets": (3, 5), "reps": (6, 10), "weight": "Medium Weight"},
    "Endurance": {"sets": (4, 8), "reps": (12, 25), "weight": "Low / Body Weight"}
}

current_view = "Front"
current_selected_muscle = "Default"
weekly_schedule = {}

# ==========================================
# 2. JSON STATE MANAGER
# ==========================================
def load_schedule():
    global weekly_schedule
    weekly_schedule = {day: {"is_active": False, "split_type": None, "workouts": []} 
                       for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r") as f:
                saved_data = json.load(f)
                if saved_data and isinstance(saved_data, dict): 
                    weekly_schedule = saved_data
        except json.JSONDecodeError:
            print(f"⚠️ Warning: {SCHEDULE_FILE} was empty or corrupted. Starting fresh.")

def save_schedule():
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(weekly_schedule, f, indent=4)

# ==========================================
# 3. IMAGE SWAP ENGINE & HOVER MECHANICS
# ==========================================
def update_display():
    global current_selected_muscle, current_view
    image_data = IMAGE_MAP.get(current_selected_muscle, IMAGE_MAP["Default"])
    
    target_filename = image_data["front"] if current_view == "Front" else image_data["back"]
    img_path = os.path.join(ASSET_DIR, target_filename)
    
    try:
        pil_image = Image.open(img_path)
        ctk_img = ctk.CTkImage(light_image=pil_image, size=(320, 550))
        image_label.configure(image=ctk_img, text="")
    except FileNotFoundError:
        image_label.configure(image="", text=f"❌ Missing Image:\n{target_filename}")

def on_toggle_change(value):
    global current_view
    current_view = value
    update_display()

def on_hover_enter(event, muscle):
    global current_selected_muscle
    current_selected_muscle = muscle
    update_display()

def on_hover_leave(event):
    global current_selected_muscle
    current_selected_muscle = "Default"
    update_display()

# ==========================================
# 4. ALGORITHMIC GENERATOR
# ==========================================
def fetch_workout_for_muscle(muscle):
    if muscle == "PLACEHOLDER_CARDIO":
        return {"exercise_name": "30 Min Treadmill / Cycling", "metrics": {"intensity_score": 5}, "notes": "Steady state cardio."}
    
    eq = random.choice(["Free Weights", "Machine Weights", "Body Weights"])
    try:
        response = requests.get(API_URL, params={"equipment": eq, "muscle": muscle, "k": 3})
        if response.status_code == 200 and response.json():
            return random.choice(response.json())
    except:
        pass
    return {"exercise_name": f"Generic {muscle} Exercise", "metrics": {"intensity_score": 0}, "notes": "Placeholder due to DB miss."}

def generate_workouts_for_split(split_name, goal_name):
    target_muscles = SPLIT_MAP.get(split_name, [])
    selected_muscles = random.choices(target_muscles, k=4) 
    
    daily_routine = []
    for m in selected_muscles:
        workout = fetch_workout_for_muscle(m)
        workout["target_muscle_tag"] = m 
        
        if m == "PLACEHOLDER_CARDIO" or split_name == "Cardio":
            workout["sets"] = 1
            workout["reps"] = "30 Mins"
            workout["weight_profile"] = "Body Weight"
        else:
            s_min, s_max = GOAL_MAP[goal_name]["sets"]
            r_min, r_max = GOAL_MAP[goal_name]["reps"]
            workout["sets"] = random.randint(s_min, s_max)
            workout["reps"] = random.randint(r_min, r_max)
            workout["weight_profile"] = GOAL_MAP[goal_name]["weight"]
            
        daily_routine.append(workout)
    return daily_routine

# ==========================================
# 5. UI SETUP & SPLIT SCREEN
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1100x700")
app.title("Enterprise Fitness Generator")
app.configure(fg_color=BG_DARK_GREY) # Intense Grey Background

# --- LEFT PANEL: The Anatomy Diagram ---
image_panel = ctk.CTkFrame(app, width=450, fg_color=PANEL_GREY, corner_radius=0)
image_panel.pack(side="left", fill="y", padx=20, pady=20)

control_frame = ctk.CTkFrame(image_panel, fg_color="transparent")
control_frame.pack(side="top", fill="x", pady=(10, 0))

# Pill-shaped Toggle Switch using Soft Blue
view_toggle = ctk.CTkSegmentedButton(
    control_frame, values=["Front", "Back"], command=on_toggle_change,
    selected_color=SOFT_BLUE, selected_hover_color=HOVER_BLUE, 
    unselected_color=BG_DARK_GREY, corner_radius=25
)
view_toggle.set("Front")
view_toggle.pack(pady=(5, 10))

legend_container = ctk.CTkFrame(control_frame, fg_color="transparent")
legend_container.pack(pady=(0, 10))

w_frame = ctk.CTkFrame(legend_container, width=12, height=12, fg_color="#FFFFFF", corner_radius=6)
w_frame.grid(row=0, column=0, padx=(5, 5))
ctk.CTkLabel(legend_container, text="Resting", font=("Arial", 11)).grid(row=0, column=1, padx=(0, 15))

y_frame = ctk.CTkFrame(legend_container, width=12, height=12, fg_color="#FACC15", corner_radius=6) 
y_frame.grid(row=0, column=2, padx=(5, 5))
ctk.CTkLabel(legend_container, text="Secondary", font=("Arial", 11)).grid(row=0, column=3, padx=(0, 15))

r_frame = ctk.CTkFrame(legend_container, width=12, height=12, fg_color="#EF4444", corner_radius=6) 
r_frame.grid(row=0, column=4, padx=(5, 5))
ctk.CTkLabel(legend_container, text="Primary", font=("Arial", 11)).grid(row=0, column=5, padx=(0, 5))

image_label = ctk.CTkLabel(image_panel, text="Loading anatomy...")
image_label.pack(expand=True, pady=(0, 10))

# --- RIGHT PANEL: The Interactive Menu ---
menu_panel = ctk.CTkFrame(app, fg_color=PANEL_GREY, corner_radius=0)
menu_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

def clear_menu():
    for widget in menu_panel.winfo_children():
        widget.destroy()

# ==========================================
# 6. APP NAVIGATION & MENUS
# ==========================================
def create_pill_button(parent, text, command, width=250, is_primary=True):
    """Helper function to enforce the soft blue pill aesthetic."""
    bg_color = SOFT_BLUE if is_primary else "#555555"
    hov_color = HOVER_BLUE if is_primary else "#333333"
    return ctk.CTkButton(parent, text=text, width=width, height=50, 
                         fg_color=bg_color, hover_color=hov_color, 
                         corner_radius=25, font=("Arial", 15, "bold"), command=command)

def show_home_screen():
    clear_menu()
    on_hover_leave(None)
    
    today = datetime.date.today()
    date_str = today.strftime("%A, %B %d, %Y")

    ctk.CTkLabel(menu_panel, text="Enterprise Fitness", font=("Arial", 32, "bold")).pack(pady=(60, 5))
    ctk.CTkLabel(menu_panel, text=f"Today is {date_str}", text_color=SOFT_BLUE, font=("Arial", 16)).pack(pady=(0, 40))

    create_pill_button(menu_panel, "Quick Daily Workout", show_quick_daily_prompt, width=300).pack(pady=10)
    create_pill_button(menu_panel, "Current Weekly Schedule", show_weekly_grid, width=300).pack(pady=10)

# --- QUICK DAILY WORKOUT ---
def show_quick_daily_prompt():
    clear_menu()
    ctk.CTkLabel(menu_panel, text="Quick Daily Generator", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    ctk.CTkLabel(menu_panel, text="What are we hitting today?", font=("Arial", 16)).pack(pady=(0, 20))
    
    for split in ["Upper", "Lower", "Cardio"]:
        create_pill_button(menu_panel, split, lambda s=split: show_quick_daily_goal(s)).pack(pady=10)
                      
    create_pill_button(menu_panel, "← Home", show_home_screen, width=120, is_primary=False).pack(pady=(30, 0))

def show_quick_daily_goal(split_choice):
    clear_menu()
    ctk.CTkLabel(menu_panel, text="Training Goal", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    ctk.CTkLabel(menu_panel, text=f"Split: {split_choice}", text_color=SOFT_BLUE, font=("Arial", 16)).pack(pady=(0, 20))
    
    for goal in ["Strength", "Hypertrophy", "Endurance"]:
        create_pill_button(menu_panel, goal, lambda g=goal: process_quick_daily(split_choice, g)).pack(pady=10)
                      
    create_pill_button(menu_panel, "← Back", show_quick_daily_prompt, width=120, is_primary=False).pack(pady=(30, 0))

def process_quick_daily(split_choice, goal_choice):
    clear_menu()
    ctk.CTkLabel(menu_panel, text="Consulting Database...", font=("Arial", 24, "bold"), text_color=SOFT_BLUE).pack(pady=100)
    app.update() 
    
    routine = generate_workouts_for_split(split_choice, goal_choice)
    render_interactive_checklist(f"{split_choice} Day ({goal_choice})", routine, show_home_screen)

# --- WEEKLY SCHEDULE WIZARD ---
def show_weekly_wizard():
    clear_menu()
    ctk.CTkLabel(menu_panel, text="Schedule Architect", font=("Arial", 28, "bold")).pack(pady=(20, 20))
    
    ctk.CTkLabel(menu_panel, text="1. Select Weekly Flow:", font=("Arial", 16)).pack(anchor="w", padx=40)
    split_var = ctk.StringVar(value="Push, Pull, Legs")
    split_dropdown = ctk.CTkOptionMenu(
        menu_panel, variable=split_var, values=["Push, Pull, Legs", "Upper, Lower", "Upper, Lower, Cardio"],
        fg_color=SOFT_BLUE, button_color=HOVER_BLUE, button_hover_color=BG_DARK_GREY, corner_radius=25
    )
    split_dropdown.pack(pady=(5, 10), padx=40, fill="x")
    
    ctk.CTkLabel(menu_panel, text="2. Select Training Goal:", font=("Arial", 16)).pack(anchor="w", padx=40)
    goal_var = ctk.StringVar(value="Hypertrophy")
    goal_dropdown = ctk.CTkOptionMenu(
        menu_panel, variable=goal_var, values=["Strength", "Hypertrophy", "Endurance"],
        fg_color=SOFT_BLUE, button_color=HOVER_BLUE, button_hover_color=BG_DARK_GREY, corner_radius=25
    )
    goal_dropdown.pack(pady=(5, 15), padx=40, fill="x")

    ctk.CTkLabel(menu_panel, text="3. Set Active Training Days:", font=("Arial", 16)).pack(anchor="w", padx=40)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_switches = {}
    
    switches_frame = ctk.CTkFrame(menu_panel, fg_color="transparent")
    switches_frame.pack(pady=5, padx=40, fill="x")
    
    for day in days_of_week:
        var = ctk.BooleanVar(value=True if day not in ["Saturday", "Sunday"] else False)
        switch = ctk.CTkSwitch(switches_frame, text=day, variable=var, progress_color=SOFT_BLUE)
        switch.pack(pady=2, anchor="w")
        day_switches[day] = var

    def execute_build():
        clear_menu()
        ctk.CTkLabel(menu_panel, text="Generating Week...", font=("Arial", 24, "bold"), text_color=SOFT_BLUE).pack(pady=100)
        app.update()
        
        sequence_choice = split_var.get().split(", ")
        current_goal = goal_var.get()
        seq_idx = 0
        
        for d in days_of_week:
            if day_switches[d].get():
                current_split = sequence_choice[seq_idx % len(sequence_choice)]
                seq_idx += 1
                weekly_schedule[d] = {
                    "is_active": True, 
                    "split_type": current_split, 
                    "workouts": generate_workouts_for_split(current_split, current_goal)
                }
            else:
                weekly_schedule[d] = {"is_active": False, "split_type": None, "workouts": []}
                
        save_schedule()
        show_weekly_grid()

    create_pill_button(menu_panel, "Generate Schedule", execute_build, width=300).pack(pady=15)
    create_pill_button(menu_panel, "Cancel", show_weekly_grid, width=120, is_primary=False).pack(pady=5)

def show_weekly_grid():
    clear_menu()
    on_hover_leave(None)
    ctk.CTkLabel(menu_panel, text="Weekly Schedule", font=("Arial", 28, "bold")).pack(pady=(20, 10))

    grid_frame = ctk.CTkFrame(menu_panel, fg_color="transparent")
    grid_frame.pack(pady=5, fill="x", padx=10)

    for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
        day_data = weekly_schedule.get(day, {})
        is_active = day_data.get("is_active", False)
        
        text_color = "white" if is_active else "gray"
        split_text = day_data.get("split_type") if is_active else "Rest Day"
        
        ctk.CTkLabel(grid_frame, text=day, font=("Arial", 14, "bold"), text_color=text_color).grid(row=i, column=0, padx=15, pady=8, sticky="w")
        ctk.CTkLabel(grid_frame, text=split_text, font=("Arial", 14), text_color=text_color).grid(row=i, column=1, padx=15, pady=8, sticky="w")
        
        if is_active:
            # Brutalist sharp button for the data grid interaction
            ctk.CTkButton(
                grid_frame, text="View Workout", width=100, height=28, fg_color=SOFT_BLUE, hover_color=HOVER_BLUE, corner_radius=0,
                command=lambda r=day_data["workouts"], title=f"{day} - {split_text}": render_interactive_checklist(title, r, show_weekly_grid)
            ).grid(row=i, column=2, padx=15, pady=8)

    create_pill_button(menu_panel, "Regenerate Week", show_weekly_wizard, width=250).pack(pady=(20, 5))
    create_pill_button(menu_panel, "← Home", show_home_screen, width=120, is_primary=False).pack(pady=10)

# --- INTERACTIVE CHECKLIST RENDERER ---
def render_interactive_checklist(title, routine, back_command):
    clear_menu()
    ctk.CTkLabel(menu_panel, text=title, font=("Arial", 28, "bold")).pack(pady=(20, 5))
    ctk.CTkLabel(menu_panel, text="Hover over an exercise to see muscles targeted.", text_color="gray").pack(pady=(0, 15))
    
    scroll_frame = ctk.CTkScrollableFrame(menu_panel, width=450, height=400, fg_color="transparent")
    scroll_frame.pack(pady=5)
    
    for workout in routine:
        # Brutalist Data Card
        card = ctk.CTkFrame(scroll_frame, fg_color=BG_DARK_GREY, corner_radius=0)
        card.pack(pady=5, padx=10, fill="x")
        
        muscle_tag = workout.get("target_muscle_tag", "Default")
        
        cb = ctk.CTkCheckBox(card, text=workout["exercise_name"], font=("Arial", 16, "bold"), 
                             fg_color=SOFT_BLUE, hover_color=HOVER_BLUE, corner_radius=0)
        cb.pack(anchor="w", padx=10, pady=(10, 2))
        
        sets_reps_text = f"🎯 {workout.get('sets', '-')} Sets | 🔄 {workout.get('reps', '-')} Reps | ⚖️ {workout.get('weight_profile', '-')}"
        ctk.CTkLabel(card, text=sets_reps_text, font=("Arial", 13, "bold"), text_color=SOFT_BLUE).pack(anchor="w", padx=35)
        
        ctk.CTkLabel(card, text=f"Intensity: {workout['metrics']['intensity_score']}/10", font=("Arial", 12)).pack(anchor="w", padx=35, pady=(0,5))
        
        cb.bind("<Enter>", lambda event, m=muscle_tag: on_hover_enter(event, m))
        cb.bind("<Leave>", on_hover_leave)
        card.bind("<Enter>", lambda event, m=muscle_tag: on_hover_enter(event, m))
        card.bind("<Leave>", on_hover_leave)

    create_pill_button(menu_panel, "← Back", back_command, width=120, is_primary=False).pack(pady=(20, 0))

# Boot up!
load_schedule()
show_home_screen()
app.mainloop()