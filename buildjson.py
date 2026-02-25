import csv
import json

def build_master_database():
    master_db = []

    # ==========================================
    # 1. Add our existing Chest Data
    # ==========================================
    chest_data = [
        {
          "exercise_name": "Incline Chest Press Machine",
          "equipment_type": "Machine Weights",
          "targeting": {
            "primary_group": "Chest & Triceps",
            "specific_muscle": "Upper Chest (Clavicular)",
            "secondary_muscles": ["Anterior Deltoids", "Triceps"]
          },
          "metrics": {"intensity_score": 10, "mechanics": "Compound"},
          "notes": "Only machine explicitly stated to target the upper pecs."
        },
        {
          "exercise_name": "Decline Chest Press Machine",
          "equipment_type": "Machine Weights",
          "targeting": {
            "primary_group": "Chest & Triceps",
            "specific_muscle": "Lower Chest (Sternal Lower)",
            "secondary_muscles": ["Triceps", "Anterior Deltoids"]
          },
          "metrics": {"intensity_score": 10, "mechanics": "Compound"},
          "notes": "Only machine explicitly defined as targeting lower pecs."
        },
        {
          "exercise_name": "Chest-Focused Dips",
          "equipment_type": "Body Weights",
          "targeting": {
            "primary_group": "Chest & Triceps",
            "specific_muscle": "Lower Chest (Sternal Lower)",
            "secondary_muscles": ["Triceps", "Anterior Deltoids"]
          },
          "metrics": {"intensity_score": 8, "mechanics": "Compound"},
          "notes": "Leaning forward increases chest involvement."
        }
    ]
    master_db.extend(chest_data)

    # ==========================================
    # 2. Ingest and Format the Excel/CSV Data
    # ==========================================
    with open('back_biceps_exercises.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Standardize equipment names to match our UI buttons exactly
            eq_type = row['Equipment Type']
            if eq_type == "Bodyweight": eq_type = "Body Weights"
            elif eq_type == "Machines": eq_type = "Machine Weights"

            # Transform the flat CSV row into our nested NoSQL schema
            exercise_doc = {
                "exercise_name": row['Exercise'],
                "equipment_type": eq_type,
                "targeting": {
                    "primary_group": "Back & Biceps", # Broad category
                    "specific_muscle": row['Muscle Group'], # Specific from CSV
                    "secondary_muscles": [] # Placeholder for you to fill later
                },
                "metrics": {
                    "intensity_score": 5, # Default placeholder score
                    "mechanics": "Compound" # Default placeholder
                },
                "notes": "Imported from CSV."
            }
            master_db.append(exercise_doc)

    # ==========================================
    # 3. Export to a single Master JSON file
    # ==========================================
    with open('workout_database.json', 'w', encoding='utf-8') as json_file:
        # indent=4 makes it beautifully formatted and human-readable!
        json.dump(master_db, json_file, indent=4)
        
    print(f"Success! Conglomerated {len(master_db)} exercises into workout_database.json")

# Run the function
build_master_database()