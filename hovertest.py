import customtkinter as ctk

app = ctk.CTk()
app.geometry("500x300")
app.title("Hover Mechanic Test")

# 1. This simulates your left-side anatomy image panel
feedback_label = ctk.CTkLabel(app, text="Hover over a workout...", font=("Arial", 24, "bold"))
feedback_label.pack(pady=40)

# 2. The functions that fire when the mouse moves
def on_hover_enter(event, muscle_name):
    # In the real app, this will call update_display() with the new image!
    feedback_label.configure(text=f"Swapping image to: {muscle_name} 🔥", text_color="#bf3a3a")

def on_hover_leave(event):
    # Reverts back to the default image
    feedback_label.configure(text="Hover over a workout...", text_color="white")

# 3. Simulating your checklist of generated workouts
checklist_frame = ctk.CTkFrame(app)
checklist_frame.pack(pady=10, padx=20, fill="x")

# Mock Workout 1
workout_1 = ctk.CTkCheckBox(checklist_frame, text="Incline Dumbbell Press (Chest)")
workout_1.pack(pady=10, padx=20, anchor="w")

# THE MAGIC: Binding the mouse events to the checkbox
workout_1.bind("<Enter>", lambda event: on_hover_enter(event, "Upper Chest"))
workout_1.bind("<Leave>", on_hover_leave)

# Mock Workout 2
workout_2 = ctk.CTkCheckBox(checklist_frame, text="Barbell Squat (Quads)")
workout_2.pack(pady=10, padx=20, anchor="w")

workout_2.bind("<Enter>", lambda event: on_hover_enter(event, "Quads"))
workout_2.bind("<Leave>", on_hover_leave)

app.mainloop()