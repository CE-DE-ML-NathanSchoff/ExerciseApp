import sqlite3

# 1. Connect to the database (creates 'workout_data.db' in your current folder)
conn = sqlite3.connect('workout_data.db')
cursor = conn.cursor()

# 2. Write ALL your SQL in one giant string
# Note: I added "IF NOT EXISTS" and "OR IGNORE" so if you run this script 
# twice by accident, it won't crash or duplicate your data.
sql_script = """
-- Create the Categories Table
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);

-- Create the Exercises Table
CREATE TABLE IF NOT EXISTS Exercises (
    exercise_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    exercise_name VARCHAR(100) NOT NULL,
    target_area VARCHAR(100),
    secondary_muscles VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- Insert our three main categories
INSERT OR IGNORE INTO Categories (category_id, category_name) VALUES 
(1, 'Home Workout'),
(2, 'Body Workout'),
(3, 'Weight Workout');

-- Insert the Body Workout exercise
INSERT OR IGNORE INTO Exercises (exercise_id, category_id, exercise_name, target_area, secondary_muscles, notes) VALUES 
(1, 2, 'Chest-Focused Dips', 'Lower pectoralis major', 'Triceps, Anterior deltoids', 'Leaning forward increases chest involvement.');

-- Insert the Weight Workout exercises
INSERT OR IGNORE INTO Exercises (exercise_id, category_id, exercise_name, target_area, secondary_muscles, notes) VALUES 
(2, 3, 'Incline Barbell Bench Press', 'Upper pectoralis major', 'Anterior deltoids, Triceps', NULL),
(3, 3, 'Flat Dumbbell Press', 'Middle pectoralis major', 'Triceps, Shoulders', 'Offers a greater stretch at the bottom of the movement.'),
(4, 3, 'High‑to‑Low Cable Fly', 'Lower pectoralis major', 'Inner chest fibers', 'Downward cable path isolates the lower fibers effectively.');
"""

# 3. Execute the entire SQL script at once
cursor.executescript(sql_script)

# 4. Save the changes and close the connection
conn.commit()
conn.close()

print("Database built and populated successfully from a single script!")