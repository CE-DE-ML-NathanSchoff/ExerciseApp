import json
import os
from pymongo import MongoClient
import certifi

# ==========================================
# 1. Connect to the Cloud
# ==========================================
# Replace 'password' with your actual database password. 
uri = "mongodb+srv://wolfismyfav_db_user:Nakedsnake@cluster0.b9qeiyo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print("Connecting to MongoDB Atlas...")
try:
    # Connect using certifi for SSL safety
    client = MongoClient(uri, tlsCAFile=certifi.where())
    # Send a quick ping to verify the connection works
    client.admin.command('ping')
    print("Ping successful! Connected to MongoDB.")
except Exception as e:
    print(f"Connection failed! Error: {e}")
    exit()

# ==========================================
# 2. Setup the Database and Collection
# ==========================================
db = client['fitness_app']           
collection = db['exercises']         

# ==========================================
# 3. Load the Local JSON Data
# ==========================================
print("Loading local JSON data...")

# Bulletproof absolute path - looks in the exact folder this script lives in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'workout_database.json')

try:
    with open(json_path, 'r', encoding='utf-8') as file:
        workout_data = json.load(file)
except FileNotFoundError:
    print(f"Error: Could not find workout_database.json at {json_path}")
    exit()

# ==========================================
# 4. Blast it to MongoDB
# ==========================================
print("Uploading to MongoDB Atlas...")

# Clear the old data so we don't create duplicates
collection.delete_many({}) 

# Insert the new 21 exercises
collection.insert_many(workout_data)

print(f"Success! {len(workout_data)} exercises are now live in the cloud!")



