import customtkinter as ctk
import sqlite3

# ==========================================
# 1. DATABASE BACKEND (The Fetcher)
# ==========================================
def get_exercises_by_category(category_id):
    """Connects to the DB, fetches exercises for a specific category, and returns a list."""
    conn = sqlite3.connect('workout_data.db')
    cursor = conn.cursor()
    
    # The '?' safely injects the category_id into the query
    cursor.execute('''
        SELECT exercise_name, target_area, secondary_muscles, notes 
        FROM Exercises 
        WHERE category_id = ?
    ''', (category_id,))
    
    results = cursor.fetchall()
    conn.close()
    return results

# ==========================================
# 2. UI FRONTEND (The Visuals)
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x500")
app.title("Chest Workout Database")

# Set up the grid
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# --- The Magic Function: Updates the Main Screen ---
def show_exercises(category_id, category_name):
    # 1. Destroy everything currently sitting inside the main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
        
    # 2. Draw the new category title
    title = ctk.CTkLabel(main_frame, text=category_name, font=("Arial", 24, "bold"))
    title.pack(pady=(20, 10))
    
    # 3. Ask the database for the data
    exercises = get_exercises_by_category(category_id)
    
    # 4. Handle empty categories (like Home Workout right now)
    if not exercises:
        ctk.CTkLabel(main_frame, text="No exercises found in this category yet.", font=("Arial", 14, "italic")).pack(pady=20)
        return

    # 5. Loop through the database results and draw a "Card" for each one
    for ex in exercises:
        name, target, secondary, notes = ex
        
        # Create a visually distinct box (frame) for each exercise
        card = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#2b2b2b")
        card.pack(pady=10, padx=20, fill="x") # fill="x" makes it stretch horizontally
        
        # Populate the card with the database info
        ctk.CTkLabel(card, text=name, font=("Arial", 18, "bold"), text_color="#3a7ebf").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(card, text=f"Target: {target}", font=("Arial", 14)).pack(anchor="w", padx=15)
        ctk.CTkLabel(card, text=f"Secondary: {secondary}", font=("Arial", 12)).pack(anchor="w", padx=15)
        
        if notes:
            ctk.CTkLabel(card, text=f"Notes: {notes}", font=("Arial", 12, "italic")).pack(anchor="w", padx=15, pady=(0, 10))
        else:
            ctk.CTkLabel(card, text="").pack(anchor="w", padx=15, pady=(0, 5)) # Just padding if no notes

# --- Build the Sidebar (Column 0) ---
sidebar_frame = ctk.CTkFrame(app, width=200, corner_radius=0)
sidebar_frame.grid(row=0, column=0, sticky="nsew")

ctk.CTkLabel(sidebar_frame, text="Categories", font=("Arial", 20, "bold")).pack(pady=(20, 20))

# Notice the 'lambda:' - This stops the function from running immediately upon launch
# and instead waits for the user to actually click the button.
ctk.CTkButton(sidebar_frame, text="Home Workout", command=lambda: show_exercises(1, "Home Workout")).pack(pady=10, padx=20)
ctk.CTkButton(sidebar_frame, text="Body Workout", command=lambda: show_exercises(2, "Body Workout")).pack(pady=10, padx=20)
ctk.CTkButton(sidebar_frame, text="Weight Workout", command=lambda: show_exercises(3, "Weight Workout")).pack(pady=10, padx=20)

# --- Build the Main Content Area (Column 1) ---
main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

welcome_label = ctk.CTkLabel(main_frame, text="Welcome! Select a workout category from the left.", font=("Arial", 16))
welcome_label.pack(pady=50)

# Run the application
app.mainloop()