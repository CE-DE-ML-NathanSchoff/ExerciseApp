import customtkinter as ctk
from PIL import Image
import requests
import os

# ==========================================
# 1. GLOBAL STATE & CONFIG
# ==========================================
current_view = "Front"
current_mask_name = None
current_intensity = 0

# The URL of your local FastAPI server
API_URL = "http://127.0.0.1:8000/api/top-workouts"

# ==========================================
# 2. IMAGE PROCESSING ENGINE (Pillow)
# ==========================================
def generate_heatmap_image():
    """Layers the base body and the tinted muscle mask."""
    global current_view, current_mask_name, current_intensity
    
    # Select base image
    base_file = "body_front.png" if current_view == "Front" else "body_back.png"
    base_path = os.path.join("assets", base_file)
    
    try:
        base_image = Image.open(base_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find {base_path}. Please check your assets folder.")
        return None

    # If we have a mask selected, try to load and tint it
    if current_mask_name:
        mask_path = os.path.join("assets", current_mask_name)
        if os.path.exists(mask_path):
            # Determine color based on intensity
            if current_intensity >= 8: hex_color = "#bf3a3a"  # Red
            elif current_intensity >= 5: hex_color = "#e67300"  # Orange
            else: hex_color = "#2fa572"  # Green
                
            mask_image = Image.open(mask_path).convert("RGBA")
            color_block = Image.new("RGBA", mask_image.size, hex_color)
            
            # Tint the white mask
            tinted_mask = Image.composite(color_block, Image.new("RGBA", mask_image.size, (0,0,0,0)), mask_image)
            
            # Paste it onto the base body
            base_image.paste(tinted_mask, (0, 0), tinted_mask)
        else:
            print(f"Notice: Mask '{mask_path}' not found. Showing base body only.")

    # Convert to a format CustomTkinter can display
    # Resize to fit nicely on the left side of the screen
    base_image.thumbnail((400, 700), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=base_image, dark_image=base_image, size=base_image.size)

def update_display():
    """Forces the UI to redraw the image."""
    new_image = generate_heatmap_image()
    if new_image:
        image_label.configure(image=new_image, text="")
        
def on_toggle_change(value):
    """Fired when the user clicks Front or Back."""
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

image_label = ctk.CTkLabel(image_panel, text="Load an image to begin")
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
        mask_prefix = "mask_chest" 
    else:
        options = ["Lats", "Upper Back / Rhomboids / Middle Traps", "Lower Back", "Biceps"]
        mask_prefix = "mask_back" # You can make this more specific later!
        
    for option in options:
        # We pass the mask name so the image updates correctly
        ctk.CTkButton(menu_panel, text=option, width=300, height=40, 
                      command=lambda opt=option, prefix=mask_prefix: show_results(equipment, opt, f"{prefix}.png")).pack(pady=10)

    ctk.CTkButton(menu_panel, text="← Back", width=100, fg_color="#555555", 
                  command=lambda: show_muscle_groups(equipment)).pack(pady=(30, 0))

def show_results(equipment, muscle, mask_file):
    clear_menu()
    global current_mask_name, current_intensity
    
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
        # Update our Image Globals based on the top result!
        top_score = results[0]["metrics"]["intensity_score"]
        current_mask_name = mask_file
        current_intensity = top_score
        update_display() # Trigger the image redraw!
        
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
