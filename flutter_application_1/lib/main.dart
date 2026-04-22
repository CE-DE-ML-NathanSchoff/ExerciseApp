import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';

// ==========================================
// 1. GLOBAL STATE & CONFIG
// ==========================================
const Color bgDarkGrey = Color(0xFF2A2B2E);
const Color panelGrey = Color(0xFF35373B);
const Color softBlue = Color(0xFF5C8EAD);
const Color hoverBlue = Color(0xFF4A748F);

const String apiUrl = "http://127.0.0.1:8000/api/top-workouts";

const Map<String, List<String>> splitMap = {
  "Push": ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lower Chest (Sternal Lower)", "Triceps", "Front Delts"],
  "Pull": ["Lats", "Upper Back / Rhomboids / Middle Traps", "Lower Back", "Biceps"],
  "Legs": ["Quads", "Hamstrings", "Calves", "Glutes"],
  "Upper": ["Upper Chest (Clavicular)", "Middle Chest (Sternal Mid)", "Lats", "Upper Back / Rhomboids / Middle Traps", "Biceps", "Triceps"],
  "Lower": ["Quads", "Hamstrings", "Calves", "Glutes"],
  "Cardio": ["PLACEHOLDER_CARDIO"]
};

const Map<String, Map<String, dynamic>> goalMap = {
  "Strength": {"sets_min": 3, "sets_max": 4, "reps_min": 3, "reps_max": 6, "weight": "Max Weight"},
  "Hypertrophy": {"sets_min": 3, "sets_max": 5, "reps_min": 6, "reps_max": 10, "weight": "Medium Weight"},
  "Endurance": {"sets_min": 4, "sets_max": 8, "reps_min": 12, "reps_max": 25, "weight": "Low / Body Weight"}
};

void main() {
  runApp(const EnterpriseFitnessApp());
}

class EnterpriseFitnessApp extends StatelessWidget {
  const EnterpriseFitnessApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Enterprise Fitness',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: bgDarkGrey,
        appBarTheme: const AppBarTheme(backgroundColor: bgDarkGrey, elevation: 0, iconTheme: IconThemeData(color: softBlue)),
      ),
      home: const HomeScreen(),
    );
  }
}

// ==========================================
// 2. REUSABLE UI COMPONENTS
// ==========================================
class PillButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final bool isPrimary;

  const PillButton({super.key, required this.text, required this.onPressed, this.isPrimary = true});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isPrimary ? softBlue : panelGrey,
          foregroundColor: Colors.white,
          minimumSize: const Size(280, 55),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        ),
        child: Text(text, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
      ),
    );
  }
}

// ==========================================
// 3. API LOGIC (Translated from Python)
// ==========================================
Future<List<Map<String, dynamic>>> generateWorkouts(String split, String goal) async {
  final random = Random();
  List<String> targetMuscles = List.from(splitMap[split] ?? []);
  
  // Randomly subset 4 muscles from the pool
  targetMuscles.shuffle();
  List<String> selectedMuscles = targetMuscles.take(4).toList();
  
  List<Map<String, dynamic>> dailyRoutine = [];
  List<String> eqTypes = ["Free Weights", "Machine Weights", "Body Weights"];

  for (String m in selectedMuscles) {
    Map<String, dynamic> workoutData = {};
    
    if (m == "PLACEHOLDER_CARDIO" || split == "Cardio") {
      workoutData = {
        "exercise_name": "30 Min Treadmill / Cycling",
        "metrics": {"intensity_score": 5},
        "notes": "Steady state cardio.",
        "sets": 1,
        "reps": "30 Mins",
        "weight_profile": "Body Weight"
      };
    } else {
      String eq = eqTypes[random.nextInt(eqTypes.length)];
      
      try {
        final uri = Uri.parse("$apiUrl?equipment=$eq&muscle=$m&k=3");
        final response = await http.get(uri);
        
        if (response.statusCode == 200) {
          List<dynamic> results = json.decode(response.body);
          if (results.isNotEmpty) {
            workoutData = results[random.nextInt(results.length)]; // Pick 1 randomly from top 3
          }
        }
      } catch (e) {
        print("API Error: $e");
      }
      
      // Fallback if DB misses
      if (workoutData.isEmpty) {
        workoutData = {
          "exercise_name": "Generic $m Exercise",
          "metrics": {"intensity_score": 0},
          "notes": "Placeholder due to DB miss."
        };
      }

      // Inject Goal Specs
      var gData = goalMap[goal]!;
      workoutData["sets"] = gData["sets_min"] + random.nextInt(gData["sets_max"] - gData["sets_min"] + 1);
      workoutData["reps"] = gData["reps_min"] + random.nextInt(gData["reps_max"] - gData["reps_min"] + 1);
      workoutData["weight_profile"] = gData["weight"];
    }
    
    workoutData["target_muscle_tag"] = m;
    dailyRoutine.append(workoutData); // Add to routine
  }
  
  return dailyRoutine;
}

// Extension to help append to list easily
extension AppendExtension<T> on List<T> {
  void append(T item) => add(item);
}


// ==========================================
// 4. SCREENS
// ==========================================
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text("Enterprise Fitness", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 40),
            PillButton(
              text: "Quick Daily Workout",
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const SplitSelectionScreen())),
            ),
            PillButton(text: "Current Weekly Schedule", onPressed: () {}),
          ],
        ),
      ),
    );
  }
}

class SplitSelectionScreen extends StatelessWidget {
  const SplitSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select Split", style: TextStyle(color: Colors.white))),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text("What are we hitting today?", style: TextStyle(fontSize: 20, color: Colors.white)),
            const SizedBox(height: 30),
            for (String split in ["Upper", "Lower", "Cardio"])
              PillButton(
                text: split,
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => GoalSelectionScreen(selectedSplit: split))),
              ),
          ],
        ),
      ),
    );
  }
}

class GoalSelectionScreen extends StatelessWidget {
  final String selectedSplit;
  const GoalSelectionScreen({super.key, required this.selectedSplit});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select Goal", style: TextStyle(color: Colors.white))),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Split: $selectedSplit", style: const TextStyle(fontSize: 18, color: softBlue, fontWeight: FontWeight.bold)),
            const SizedBox(height: 30),
            for (String goal in ["Strength", "Hypertrophy", "Endurance"])
              PillButton(
                text: goal,
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => WorkoutResultsScreen(split: selectedSplit, goal: goal))),
              ),
          ],
        ),
      ),
    );
  }
}

// ==========================================
// 5. WORKOUT RESULTS (THE BRUTALIST UI)
// ==========================================
class WorkoutResultsScreen extends StatelessWidget {
  final String split;
  final String goal;

  const WorkoutResultsScreen({super.key, required this.split, required this.goal});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("$split Day ($goal)", style: const TextStyle(color: Colors.white))),
      // FutureBuilder automatically handles Loading / Success / Error states!
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: generateWorkouts(split, goal),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: softBlue));
          } else if (snapshot.hasError) {
            return Center(child: Text("Error generating workout: ${snapshot.error}", style: const TextStyle(color: Colors.red)));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("No workouts generated.", style: TextStyle(color: Colors.white)));
          }

          List<Map<String, dynamic>> routine = snapshot.data!;

          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: routine.length,
            itemBuilder: (context, index) {
              var workout = routine[index];
              return Container(
                margin: const EdgeInsets.only(bottom: 15),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: panelGrey,
                  borderRadius: BorderRadius.circular(0), // Brutalist Sharp Corners
                  border: Border(left: BorderSide(color: softBlue, width: 4)), // Accent line
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(workout["exercise_name"], style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                    const SizedBox(height: 8),
                    Text(
                      "🎯 ${workout['sets']} Sets | 🔄 ${workout['reps']} Reps | ⚖️ ${workout['weight_profile']}",
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: softBlue),
                    ),
                    const SizedBox(height: 4),
                    Text("Intensity: ${workout['metrics']['intensity_score']}/10", style: const TextStyle(fontSize: 14, color: Colors.grey)),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}