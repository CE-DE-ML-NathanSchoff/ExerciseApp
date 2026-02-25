import customtkinter as ctk
import json
import heapq

# ==========================================
# 1. DSA BACKEND (Algorithms & Data Structures)
# ==========================================
def load_data():
    """Loads the NoSQL Master JSON database into memory."""
    try:
        with open('workout_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_top_k_exercises(equipment, specific_muscle, k=3):
    """Uses subsetting and a priority queue to find the top workouts."""
    database = load_data()
    
    # 1. Subsetting: Filter the full dataset down to match the user's path
    subset = [
        ex for ex in database 
        if ex["equipment_type"] == equipment 
        and ex["targeting"]["specific_muscle"] == specific_muscle
    ]
    
    # 2. Top K Elements Pattern via Priority Queue (Heap)
    # heapq.nlargest automatically pushes our subset into a heap and pops the top 'k' 
    # elements based on the intensity_score. It's highly efficient.
    top_workouts = heapq.nlargest(
        k, 
        subset, 
        key=lambda x: x["metrics"]["intensity_score"]
    )
    
    return top_workouts

# ==========================================
# 2. UI FRONTEND (The State Machine)
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x600")
app.title("Algorithmic Workout Generator")

container = ctk.CTkFrame(app)
container.pack(fill="both", expand=True, padx=40, pady=40)

def clear_screen():
    for widget in container.winfo_children():
        widget.destroy()

# --- STATE 1: Equipment ---
def show_equipment_selection():
    clear_screen()
    ctk.CTkLabel(container, text="Step 1: Select Equipment", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    
    ctk.CTkButton(container, text="Free Weights", width=250, height=50, 
                  command=lambda: show_muscle_groups("Free Weights")).pack(pady=15)
    ctk.CTkButton(container, text="Body Weights", width=250, height=50, 
                  command=lambda: show_muscle_groups("Body Weights")).pack(pady=15)
    ctk.CTkButton(container, text="Machine Weights", width=250, height=50, 
                  command=lambda: show_muscle_groups("Machine Weights")).pack(pady=15)

# --- STATE 2: Muscle Group ---
def show_muscle_groups(equipment_choice):
    clear_screen()
    ctk.CTkLabel(container, text=f"Equipment: {equipment_choice}", font=("Arial", 16, "italic"), text_color="gray").pack()
    ctk.CTkLabel(container, text="Step 2: Select Muscle Group", font=("Arial", 28, "bold")).pack(pady=(20, 30))
    
    ctk.CTkButton(container, text="Chest & Triceps", width=250, height=50, 
                  command=lambda: show_specific_muscles(equipment_choice, "Chest")).pack(pady=10)
    ctk.CTkButton(container, text="Back & Biceps", width=250, height=50, 
                  command=lambda: show_specific_muscles(equipment_choice, "Back")).pack(pady=10)

    ctk.CTkButton(container, text="← Back", width=100, fg_color="#555555", hover_color="#333333", 
                  command=show_equipment_selection).pack(pady=(30, 0))

# --- STATE 3: Specific Muscle ---
def show_specific_muscles(equipment_choice, broad_group):
    clear_screen()
    ctk.CTkLabel(container, text="Step 3: Target Area", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    
    # Dynamically generate the specific muscle buttons based on the broad group
    if broad_group == "Chest":
        options = ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lower Chest (Sternal Lower)"]
    elif broad_group == "Back":
        # These match the exact strings from your CSV import
        options = ["Lats", "Upper Back / Rhomboids / Middle Traps", "Lower Back", "Biceps"]
        
    for option in options:
        ctk.CTkButton(container, text=option, width=300, height=40, 
                      command=lambda opt=option: show_results(equipment_choice, opt)).pack(pady=10)

    ctk.CTkButton(container, text="← Back", width=100, fg_color="#555555", hover_color="#333333", 
                  command=lambda: show_muscle_groups(equipment_choice)).pack(pady=(30, 0))

# --- STATE 4: Output / Process & Merge ---
def show_results(equipment_choice, specific_muscle):
    clear_screen()
    ctk.CTkLabel(container, text="Top Recommended Exercises", font=("Arial", 28, "bold")).pack(pady=(20, 10))
    
    # Run our algorithm to get the top 3 best workouts!
    results = get_top_k_exercises(equipment_choice, specific_muscle, k=3)
    
    if not results:
        ctk.CTkLabel(container, text="No exercises found for this combination.", font=("Arial", 16, "italic")).pack(pady=30)
    else:
        scroll_frame = ctk.CTkScrollableFrame(container, width=550, height=300)
        scroll_frame.pack(pady=10)
        
        for index, ex in enumerate(results):
            color = "#2fa572" if index == 0 else "#2b2b2b" # Highlight the #1 choice
            card = ctk.CTkFrame(scroll_frame, fg_color=color, corner_radius=8)
            card.pack(pady=5, padx=10, fill="x")
            
            # Extract data from the JSON document structure
            name = ex["exercise_name"]
            score = ex["metrics"]["intensity_score"]
            notes = ex.get("notes", "No notes available.")
            
            ctk.CTkLabel(card, text=f"#{index + 1}: {name}", font=("Arial", 18, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(card, text=f"Intensity: {score}/10", font=("Arial", 14)).pack(anchor="w", padx=15)
            ctk.CTkLabel(card, text=f"Notes: {notes}", font=("Arial", 12, "italic"), text_color="#cccccc", wraplength=480, justify="left").pack(anchor="w", padx=15, pady=(5, 10))

    ctk.CTkButton(container, text="Start Over", width=150, fg_color="#bf3a3a", hover_color="#8c2828", 
                  command=show_equipment_selection).pack(pady=(30, 0))

# Boot up the app
show_equipment_selection()
app.mainloop()