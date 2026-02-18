import customtkinter as ctk

# 1. App Configuration
ctk.set_appearance_mode("dark")  # Force dark mode
ctk.set_default_color_theme("blue")  # Blue accents

app = ctk.CTk()
app.geometry("750x500")
app.title("Algorithm Toolkit")

# Configure the grid layout (1 row, 2 columns)
# Weight=1 allows the main content area to expand when you resize the window
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# 2. Build the Sidebar (Column 0)
sidebar_frame = ctk.CTkFrame(app, width=200, corner_radius=0)
sidebar_frame.grid(row=0, column=0, sticky="nsew")

# Sidebar Title
ctk.CTkLabel(sidebar_frame, text="Select Tool", font=("Arial", 20, "bold")).pack(pady=(20, 20))

# Sidebar Navigation Buttons
ctk.CTkButton(sidebar_frame, text="Dijkstra / A* Visualizer").pack(pady=10, padx=20)
ctk.CTkButton(sidebar_frame, text="Topological Sort").pack(pady=10, padx=20)
ctk.CTkButton(sidebar_frame, text="Sliding Window").pack(pady=10, padx=20)
ctk.CTkButton(sidebar_frame, text="Modified Binary Search").pack(pady=10, padx=20)

# 3. Build the Main Content Area (Column 1)
main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

# Default Main Screen Text
welcome_label = ctk.CTkLabel(main_frame, text="Welcome! Select a module from the left to begin.", font=("Arial", 16))
welcome_label.pack(pady=50)

# 4. Run the App
app.mainloop()