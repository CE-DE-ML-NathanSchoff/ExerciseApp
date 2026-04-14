import csv
import json
import os

def build_master_database():
    master_db = []

    # ==========================================
    # 1. The Core 21-Exercise Master Data
    # ==========================================
    core_data = [
        # --- UPPER CHEST ---
        {
            "exercise_name": "Incline Dumbbell Press",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Upper Chest (Clavicular)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "Set bench to 30-45 degrees. Keep shoulders retracted and drive the dumbbells up and slightly inward."
        },
        {
            "exercise_name": "Decline Push-Up",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Upper Chest (Clavicular)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 7, "mechanics": "Compound"},
            "notes": "Elevate your feet on a bench or chair. The angle shifts the gravity to focus heavily on the upper chest fibers."
        },
        {
            "exercise_name": "Incline Smith Machine Press",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Upper Chest (Clavicular)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "The fixed bar path allows for maximum muscle isolation without worrying about stabilizing the weight."
        },
        # --- MIDDLE CHEST ---
        {
            "exercise_name": "Flat Barbell Bench Press",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Middle Chest (Sternal Mid)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 9, "mechanics": "Compound"},
            "notes": "The gold standard for chest mass. Keep a slight arch in your lower back and plant your feet firmly."
        },
        {
            "exercise_name": "Standard Flat Push-Up",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Middle Chest (Sternal Mid)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 6, "mechanics": "Compound"},
            "notes": "Keep a rigid core. Hands should be placed slightly wider than shoulder-width apart."
        },
        {
            "exercise_name": "Pec Deck Fly Machine",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Middle Chest (Sternal Mid)", "secondary_muscles": [] },
            "metrics": {"intensity_score": 7, "mechanics": "Isolation"},
            "notes": "Focus on squeezing the chest at the center of the movement. Keep a slight bend in the elbows."
        },
        # --- LOWER CHEST ---
        {
            "exercise_name": "Decline Dumbbell Press",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Lower Chest (Sternal Lower)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "Hook your legs securely into the decline bench. Lower the weights to the lower portion of your sternum."
        },
        {
            "exercise_name": "Chest Dips",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Lower Chest (Sternal Lower)", "secondary_muscles": ["Triceps"] },
            "metrics": {"intensity_score": 9, "mechanics": "Compound"},
            "notes": "Lean your torso forward about 30 degrees while dipping. Keeping your body perfectly straight shifts the load to the triceps instead."
        },
        {
            "exercise_name": "High-to-Low Cable Crossover",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Chest", "specific_muscle": "Lower Chest (Sternal Lower)", "secondary_muscles": [] },
            "metrics": {"intensity_score": 7, "mechanics": "Isolation"},
            "notes": "Set the pulleys above head height. Drive your hands downward and together toward your waist."
        },
        # --- LATS ---
        {
            "exercise_name": "Dumbbell Pullover",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lats", "secondary_muscles": [] },
            "metrics": {"intensity_score": 7, "mechanics": "Isolation"},
            "notes": "Lie perpendicular across a bench. Stretch the dumbbell behind your head to fully elongate the lats."
        },
        {
            "exercise_name": "Wide Grip Pull-Up",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lats", "secondary_muscles": ["Biceps"] },
            "metrics": {"intensity_score": 9, "mechanics": "Compound"},
            "notes": "Grip the bar significantly wider than your shoulders. Pull your chest to the bar to maximize lat spread."
        },
        {
            "exercise_name": "Wide Grip Lat Pulldown",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lats", "secondary_muscles": ["Biceps"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "Lean slightly back. Pull the bar to your upper chest, focusing on driving your elbows down toward the floor."
        },
        # --- UPPER BACK ---
        {
            "exercise_name": "Barbell Pendlay Row",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Upper Back / Rhomboids / Middle Traps", "secondary_muscles": ["Biceps"] },
            "metrics": {"intensity_score": 9, "mechanics": "Compound"},
            "notes": "Torso should be strictly parallel to the floor. The barbell returns to a dead stop on the ground after every single rep."
        },
        {
            "exercise_name": "Inverted Bodyweight Row",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Upper Back / Rhomboids / Middle Traps", "secondary_muscles": ["Biceps"] },
            "metrics": {"intensity_score": 6, "mechanics": "Compound"},
            "notes": "Set a barbell low on a squat rack. Hang underneath it and pull your chest to the bar, keeping your body perfectly straight."
        },
        {
            "exercise_name": "Seated Cable Row (Close Grip)",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Upper Back / Rhomboids / Middle Traps", "secondary_muscles": ["Biceps"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "Use the V-handle attachment. Keep your chest up and squeeze your shoulder blades together hard at the end of the pull."
        },
        # --- LOWER BACK ---
        {
            "exercise_name": "Barbell Deadlift",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lower Back", "secondary_muscles": ["Hamstrings", "Glutes"] },
            "metrics": {"intensity_score": 10, "mechanics": "Compound"},
            "notes": "Keep the bar scraping your shins. Drive through the floor with your legs rather than pulling with your spine."
        },
        {
            "exercise_name": "Superman Holds",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lower Back", "secondary_muscles": ["Glutes"] },
            "metrics": {"intensity_score": 5, "mechanics": "Isolation"},
            "notes": "Lie face down. Simultaneously lift your arms, chest, and legs off the floor and hold the contraction for 3-5 seconds."
        },
        {
            "exercise_name": "45-Degree Back Extension",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Back", "specific_muscle": "Lower Back", "secondary_muscles": ["Hamstrings"] },
            "metrics": {"intensity_score": 6, "mechanics": "Compound"},
            "notes": "Lock your heels in. Lower your torso until you feel a stretch in the hamstrings, then contract the lower back to return to a neutral spine."
        },
        # --- BICEPS ---
        {
            "exercise_name": "Alternating Dumbbell Curl",
            "equipment_type": "Free Weights",
            "targeting": { "primary_group": "Biceps", "specific_muscle": "Biceps", "secondary_muscles": [] },
            "metrics": {"intensity_score": 7, "mechanics": "Isolation"},
            "notes": "Supinate (twist) your wrist outward at the top of the movement to maximize the peak contraction of the bicep."
        },
        {
            "exercise_name": "Underhand Chin-Up",
            "equipment_type": "Body Weights",
            "targeting": { "primary_group": "Biceps", "specific_muscle": "Biceps", "secondary_muscles": ["Lats"] },
            "metrics": {"intensity_score": 8, "mechanics": "Compound"},
            "notes": "Take a shoulder-width, palms-facing-you grip on the pull-up bar. This shifts the primary leverage directly onto the biceps."
        },
        {
            "exercise_name": "Machine Preacher Curl",
            "equipment_type": "Machine Weights",
            "targeting": { "primary_group": "Biceps", "specific_muscle": "Biceps", "secondary_muscles": [] },
            "metrics": {"intensity_score": 7, "mechanics": "Isolation"},
            "notes": "Lock your triceps firmly into the pad. The machine prevents any swinging or cheating, forcing the biceps to do 100% of the work."
        }
    ]
    master_db.extend(core_data)

    # ==========================================
    # 2. Ingest and Format the Excel/CSV Data (Optional)
    # ==========================================
    if os.path.exists('back_biceps_exercises.csv'):
        with open('back_biceps_exercises.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                eq_type = row['Equipment Type']
                if eq_type == "Bodyweight": eq_type = "Body Weights"
                elif eq_type == "Machines": eq_type = "Machine Weights"

                exercise_doc = {
                    "exercise_name": row['Exercise'],
                    "equipment_type": eq_type,
                    "targeting": {
                        "primary_group": "Back & Biceps",
                        "specific_muscle": row['Muscle Group'],
                        "secondary_muscles": []
                    },
                    "metrics": { "intensity_score": 5, "mechanics": "Compound" },
                    "notes": "Imported from CSV."
                }
                master_db.append(exercise_doc)

    # ==========================================
    # 3. Export to a single Master JSON file
    # ==========================================
    with open('workout_database.json', 'w', encoding='utf-8') as json_file:
        json.dump(master_db, json_file, indent=4)
        
    print(f"Success! Conglomerated {len(master_db)} exercises into workout_database.json")

if __name__ == "__main__":
    build_master_database()
    