import customtkinter as ctk
from PIL import Image
import requests
import os

# ==========================================
# 1. GLOBAL STATE & CONFIG
# ==========================================
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

IMAGE_MAP = {
    # CHEST
    "Upper Chest (Clavicular)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    "Middle Chest (Sternal Mid)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    "Lower Chest (Sternal Lower)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
    
    # BACK
    "Lats": {"front": "Back_front.png", "back": "Back_back.png"},
    "Upper Back / Rhomboids / Middle Traps": {"front": "Back_front.png", "back": "Back_back.png"},
    "Lower Back": {"front": "Back_front.png", "back": "Back_back.png"},
    
    # LEGS
    "Legs": {"front": "Legs_front.png", "back": "Legs_back.png"},
    
    # DEFAULT
    "Default": {"front": "1canadite.png", "back": "2canadite.png"}
}

# The state variables that control what the UI shows
current_view = "Front"
current_selected_muscle = "Default"

# The URL of your local FastAPI server
API_URL = "http://127.0.0.1:8000/api/top-workouts"

# ==========================================
# 2. THE NEW IMAGE SWAP ENGINE
# ==========================================
def update_display():
    """Instantly grabs the correct pre-colored image and pushes it to the UI."""
    global current_selected_muscle, current_view
    
    # 1. Find the images for the currently selected muscle
    image_data = IMAGE_MAP.get(current_selected_muscle, IMAGE_MAP["Default"])
    
    # 2. Pick the front or back file depending on the UI Toggle Switch
    if current_view == "Front":
        target_filename = image_data["front"]
    else:
        target_filename = image_data["back"]
        
    img_path = os.path.join(ASSET_DIR, target_filename)
    
    # 3. Load it into the UI
    try:
        pil_image = Image.open(img_path)
        # CustomTkinter sizes it perfectly for your left panel
        ctk_img = ctk.CTkImage(light_image=pil_image, size=(350, 600))
        image_label.configure(image=ctk_img, text="")
    except FileNotFoundError:
        image_label.configure(image="", text=f"❌ Missing Image:\n{target_filename}")

def on_toggle_change(value):
    """Fired when the user clicks Front or Back toggle."""
    global current_view
    current_view = value
    update_display()

# ==========================================
# 3. UI SETUP & SPLIT SCREEN
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1100x700")
app.title("Enterprise Fitness Generator")

# --- LEFT PANEL: The Anatomy Diagram ---
image_panel = ctk.CTkFrame(app, width=450)
image_panel.pack(side="left", fill="y", padx=20, pady=20)

view_toggle = ctk.CTkSegmentedButton(image_panel, values=["Front", "Back"], command=on_toggle_change)
view_toggle.set("Front")
view_toggle.pack(pady=(20, 10))

image_label = ctk.CTkLabel(image_panel, text="Loading anatomy...")
image_label.pack(expand=True, pady=10)

# --- RIGHT PANEL: The Interactive Menu ---
menu_panel = ctk.CTkFrame(app)
menu_panel.pack(side="right", fill="both", expand=True, padx=20, pady=20)

def clear_menu():
    for widget in menu_panel.winfo_children():
        widget.destroy()

# ==========================================
# 4. THE MENU STATE MACHINE
# ==========================================
def show_equipment_selection():
    clear_menu()
    # Reset image to default when starting over!
    global current_selected_muscle
    current_selected_muscle = "Default"
    update_display()
    
    ctk.CTkLabel(menu_panel, text="Step 1: Select Equipment", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    
    for eq in ["Free Weights", "Body Weights", "Machine Weights"]:
        ctk.CTkButton(menu_panel, text=eq, width=250, height=50, 
                      command=lambda e=eq: show_muscle_groups(e)).pack(pady=15)

def show_muscle_groups(equipment):
    clear_menu()
    ctk.CTkLabel(menu_panel, text=f"Equipment: {equipment}", text_color="gray").pack(pady=(20,0))
    ctk.CTkLabel(menu_panel, text="Step 2: Muscle Group", font=("Arial", 28, "bold")).pack(pady=(10, 30))
    
    ctk.CTkButton(menu_panel, text="Chest & Triceps", width=250, height=50, 
                  command=lambda: show_specific_muscles(equipment, "Chest")).pack(pady=10)
    ctk.CTkButton(menu_panel, text="Back & Biceps", width=250, height=50, 
                  command=lambda: show_specific_muscles(equipment, "Back")).pack(pady=10)

    ctk.CTkButton(menu_panel, text="← Back", width=100, fg_color="#555555", 
                  command=show_equipment_selection).pack(pady=(40, 0))
    
def show_specific_muscles(equipment, broad_group):
    clear_menu()
    ctk.CTkLabel(menu_panel, text="Step 3: Target Area", font=("Arial", 28, "bold")).pack(pady=(40, 30))
    
    if broad_group == "Chest":
        options = ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lower Chest (Sternal Lower)"]
    else:
        options = ["Lats", "Upper Back / Rhomboids / Middle Traps", "Lower Back", "Biceps"]
        
    for option in options:
        ctk.CTkButton(menu_panel, text=option, width=300, height=40, 
                      command=lambda opt=option: show_results(equipment, opt)).pack(pady=10)

    ctk.CTkButton(menu_panel, text="← Back", width=100, fg_color="#555555", 
                  command=lambda: show_muscle_groups(equipment)).pack(pady=(30, 0))

def show_results(equipment, muscle):
    clear_menu()
    global current_selected_muscle
    
    # THE MAGIC: We update the global state and immediately trigger the image swap!
    current_selected_muscle = muscle
    update_display()
    
    ctk.CTkLabel(menu_panel, text="Top Results", font=("Arial", 28, "bold")).pack(pady=(20, 10))
    
    # --- FETCH FROM FASTAPI SERVER ---
    try:
        response = requests.get(API_URL, params={"equipment": equipment, "muscle": muscle, "k": 3})
        results = response.json()
    except Exception as e:
        ctk.CTkLabel(menu_panel, text="Error connecting to server. Is FastAPI running?", text_color="red").pack(pady=20)
        results = []

    if not results:
        ctk.CTkLabel(menu_panel, text="No exercises found in the database.").pack(pady=30)
    else:
        # Display the text results
        scroll_frame = ctk.CTkScrollableFrame(menu_panel, width=450, height=350)
        scroll_frame.pack(pady=10)
        
        for index, ex in enumerate(results):
            color = "#2fa572" if index == 0 else "#2b2b2b"
            card = ctk.CTkFrame(scroll_frame, fg_color=color)
            card.pack(pady=5, padx=10, fill="x")
            
            name = ex["exercise_name"]
            score = ex["metrics"]["intensity_score"]
            notes = ex.get("notes", "No notes available.")
            
            ctk.CTkLabel(card, text=f"#{index + 1}: {name}", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(card, text=f"Intensity: {score}/10").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=notes, text_color="gray", wraplength=400, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

    ctk.CTkButton(menu_panel, text="Start Over", fg_color="#bf3a3a", hover_color="#8c2828", 
                  command=show_equipment_selection).pack(pady=(20, 0))

# Boot up!
update_display() # Load initial blank body
show_equipment_selection()
app.mainloop()