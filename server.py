from fastapi import FastAPI
from pymongo import MongoClient
import certifi

# Initialize the API
app = FastAPI(title="Fitness Generator API")

# Connect to MongoDB (Paste your Atlas connection string here!)
uri = "mongodb+srv://wolfismyfav:s0mOimlI7PbSox0h@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['fitness_app']
collection = db['exercises']

@app.get("/")
def health_check():
    return {"status": "API is online and connected to MongoDB!"}

# This is our new Endpoint! It replaces our old Python subsetting/heap algorithm.
@app.get("/api/top-workouts")
def get_top_workouts(equipment: str, muscle: str, k: int = 3):
    # 1. Subsetting: We tell MongoDB exactly what to look for
    query = {
        "equipment_type": equipment,
        "targeting.specific_muscle": muscle
    }
    
    # 2. Top K Elements: We tell MongoDB to sort by intensity (descending) and limit to 'k'
    # The {"_id": 0} tells Mongo to hide the messy internal database ID from our clean JSON output
    cursor = collection.find(query, {"_id": 0}).sort("metrics.intensity_score", -1).limit(k)
    
    # Return the results as a clean list
    return list(cursor)