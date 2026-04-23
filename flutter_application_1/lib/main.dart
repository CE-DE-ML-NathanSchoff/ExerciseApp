import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:shared_preferences/shared_preferences.dart';

// ==========================================
// 1. GLOBAL STATE, CONFIG & NOTIFIERS
// ==========================================
const Color bgDarkGrey = Color(0xFF2A2B2E);
const Color panelGrey = Color(0xFF35373B);
const Color softBlue = Color(0xFF5C8EAD);
const Color hoverBlue = Color(0xFF4A748F);

// Global Notifiers for the Interactive Diagram
final ValueNotifier<String> activeMuscle = ValueNotifier<String>("Default");
final ValueNotifier<String> activeView = ValueNotifier<String>("Front");

// Smart Network Bridge
String get apiUrl {
  if (kIsWeb) return "http://127.0.0.1:8000/api/top-workouts";
  if (Platform.isAndroid) return "http://10.0.2.2:8000/api/top-workouts";
  return "http://127.0.0.1:8000/api/top-workouts";
}

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

// Image Map for Diagram Routing
const Map<String, Map<String, String>> imageMap = {
  "Upper Chest (Clavicular)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "Middle Chest (Sternal Mid)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "Lower Chest (Sternal Lower)": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "Lats": {"front": "Back_front.png", "back": "Back_back.png"},
  "Upper Back / Rhomboids / Middle Traps": {"front": "Back_front.png", "back": "Back_back.png"},
  "Lower Back": {"front": "Back_front.png", "back": "Back_back.png"},
  "Legs": {"front": "Legs_front.png", "back": "Legs_back.png"},
  "Quads": {"front": "Legs_front.png", "back": "Legs_back.png"},
  "Hamstrings": {"front": "Legs_front.png", "back": "Legs_back.png"},
  "Calves": {"front": "Legs_front.png", "back": "Legs_back.png"},
  "Glutes": {"front": "Legs_front.png", "back": "Legs_back.png"},
  "Default": {"front": "1canadite.png", "back": "2canadite.png"},
  "Triceps": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "Front Delts": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "Biceps": {"front": "Tricept_front.png", "back": "Tricepts_back.png"},
  "PLACEHOLDER_CARDIO": {"front": "1canadite.png", "back": "2canadite.png"}
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
      home: const MainAppShell(), 
    );
  }
}

// ==========================================
// 2. THE APP SHELL (CONSTANT DIAGRAM LAYOUT)
// ==========================================
class MainAppShell extends StatelessWidget {
  const MainAppShell({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          Container(
            width: 450,
            color: panelGrey,
            child: const AnatomyDiagramPanel(),
          ),
          Expanded(
            child: Navigator(
              onGenerateRoute: (settings) {
                return MaterialPageRoute(builder: (context) => const HomeScreen());
              },
            ),
          ),
        ],
      ),
    );
  }
}

class AnatomyDiagramPanel extends StatelessWidget {
  const AnatomyDiagramPanel({super.key});

  Widget buildRubricDot(Color color, String label) {
    return Row(
      children: [
        Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 5),
        Text(label, style: const TextStyle(color: Colors.white, fontSize: 11)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ValueListenableBuilder<String>(
              valueListenable: activeView,
              builder: (context, currentView, child) {
                return Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ChoiceChip(
                          label: const Text("Front"), selected: currentView == "Front",
                          selectedColor: softBlue, backgroundColor: bgDarkGrey, labelStyle: const TextStyle(color: Colors.white),
                          onSelected: (bool selected) { if (selected) activeView.value = "Front"; },
                        ),
                        const SizedBox(width: 10),
                        ChoiceChip(
                          label: const Text("Back"), selected: currentView == "Back",
                          selectedColor: softBlue, backgroundColor: bgDarkGrey, labelStyle: const TextStyle(color: Colors.white),
                          onSelected: (bool selected) { if (selected) activeView.value = "Back"; },
                        ),
                      ],
                    ),
                    const SizedBox(height: 15),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        buildRubricDot(Colors.white, "Resting"),
                        buildRubricDot(Colors.amber, "Secondary"),
                        buildRubricDot(Colors.redAccent, "Primary"),
                      ],
                    ),
                  ],
                );
              }
            ),
            const SizedBox(height: 30),
            ValueListenableBuilder<String>(
              valueListenable: activeMuscle,
              builder: (context, muscle, child) {
                return ValueListenableBuilder<String>(
                  valueListenable: activeView,
                  builder: (context, view, child) {
                    var muscleData = imageMap[muscle] ?? imageMap["Default"]!;
                    String filename = muscleData[view.toLowerCase()] ?? imageMap["Default"]![view.toLowerCase()]!;
                    return Image.asset(
                      'assets/$filename',
                      height: 400,
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) => const SizedBox(
                        height: 400, child: Center(child: Text("❌ Image Missing", style: TextStyle(color: Colors.red))),
                      ),
                    );
                  }
                );
              }
            ),
          ],
        ),
      ),
    );
  }
}

// ==========================================
// 3. REUSABLE UI COMPONENTS
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
// 4. API & SCHEDULE STORAGE LOGIC
// ==========================================
Future<List<Map<String, dynamic>>> generateWorkouts(String split, String goal) async {
  final random = Random();
  List<String> targetMuscles = List.from(splitMap[split] ?? []);
  targetMuscles.shuffle();
  List<String> selectedMuscles = targetMuscles.take(4).toList();
  List<Map<String, dynamic>> dailyRoutine = [];
  List<String> eqTypes = ["Free Weights", "Machine Weights", "Body Weights"];

  for (String m in selectedMuscles) {
    Map<String, dynamic> workoutData = {};
    if (m == "PLACEHOLDER_CARDIO" || split == "Cardio") {
      workoutData = {"exercise_name": "30 Min Treadmill / Cycling", "metrics": {"intensity_score": 5}, "notes": "Steady state cardio.", "sets": 1, "reps": "30 Mins", "weight_profile": "Body Weight"};
    } else {
      String eq = eqTypes[random.nextInt(eqTypes.length)];
      try {
        final uri = Uri.parse("$apiUrl?equipment=$eq&muscle=$m&k=3");
        final response = await http.get(uri);
        if (response.statusCode == 200) {
          List<dynamic> results = json.decode(response.body);
          if (results.isNotEmpty) workoutData = results[random.nextInt(results.length)]; 
        }
      } catch (e) { print("API Error: $e"); }
      if (workoutData.isEmpty) {
        workoutData = {"exercise_name": "Generic $m Exercise", "metrics": {"intensity_score": 0}, "notes": "Placeholder due to DB miss."};
      }
      var gData = goalMap[goal]!;
      workoutData["sets"] = gData["sets_min"] + random.nextInt(gData["sets_max"] - gData["sets_min"] + 1);
      workoutData["reps"] = gData["reps_min"] + random.nextInt(gData["reps_max"] - gData["reps_min"] + 1);
      workoutData["weight_profile"] = gData["weight"];
    }
    workoutData["target_muscle_tag"] = m;
    dailyRoutine.add(workoutData); 
  }
  return dailyRoutine;
}

Future<void> saveWorkoutToDay(String day, List<Map<String, dynamic>> routine) async {
  final prefs = await SharedPreferences.getInstance();
  String jsonString = json.encode(routine);
  await prefs.setString('schedule_$day', jsonString);
}

Future<List<dynamic>?> loadWorkoutForDay(String day) async {
  final prefs = await SharedPreferences.getInstance();
  String? jsonString = prefs.getString('schedule_$day');
  if (jsonString != null) return json.decode(jsonString);
  return null;
}

// ==========================================
// 5. NAVIGATION SCREENS
// ==========================================
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("Enterprise Fitness", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 40),
              PillButton(text: "Quick Daily Workout", onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const SplitSelectionScreen()))),
              PillButton(text: "Current Weekly Schedule", onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const WeeklyScheduleScreen())), isPrimary: false),
            ],
          ),
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
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("What are we hitting today?", style: TextStyle(fontSize: 20, color: Colors.white)),
              const SizedBox(height: 30),
              for (String split in ["Upper", "Lower", "Cardio"])
                PillButton(text: split, onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => GoalSelectionScreen(selectedSplit: split)))),
            ],
          ),
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
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text("Split: $selectedSplit", style: const TextStyle(fontSize: 18, color: softBlue, fontWeight: FontWeight.bold)),
              const SizedBox(height: 30),
              for (String goal in ["Strength", "Hypertrophy", "Endurance"])
                PillButton(text: goal, onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => WorkoutResultsScreen(split: selectedSplit, goal: goal)))),
            ],
          ),
        ),
      ),
    );
  }
}

class WorkoutResultsScreen extends StatelessWidget {
  final String split;
  final String goal;
  const WorkoutResultsScreen({super.key, required this.split, required this.goal});

  void _showSaveDialog(BuildContext context, List<Map<String, dynamic>> routine) {
    List<String> days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    showDialog(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          backgroundColor: bgDarkGrey,
          title: const Text("Save to which day?", style: TextStyle(color: Colors.white)),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: days.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(days[index], style: const TextStyle(color: softBlue)),
                  onTap: () async {
                    await saveWorkoutToDay(days[index], routine);
                    if (context.mounted) {
                      Navigator.pop(dialogContext);
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Saved to ${days[index]}!", style: const TextStyle(color: Colors.white)), backgroundColor: softBlue));
                    }
                  },
                );
              },
            ),
          ),
        );
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("$split Day ($goal)", style: const TextStyle(color: Colors.white))),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: generateWorkouts(split, goal),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator(color: softBlue));
          if (snapshot.hasError) return Center(child: Text("Error: ${snapshot.error}", style: const TextStyle(color: Colors.red)));
          if (!snapshot.hasData || snapshot.data!.isEmpty) return const Center(child: Text("No workouts generated.", style: TextStyle(color: Colors.white)));

          List<Map<String, dynamic>> routine = snapshot.data!;
          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16.0),
                  itemCount: routine.length,
                  itemBuilder: (context, index) {
                    var workout = routine[index];
                    String muscleTag = workout["target_muscle_tag"] ?? "Default";
                    return MouseRegion(
                      onEnter: (_) => activeMuscle.value = muscleTag,
                      onExit: (_) => activeMuscle.value = "Default",
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 15),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(color: panelGrey, borderRadius: BorderRadius.circular(0), border: const Border(left: BorderSide(color: softBlue, width: 4))),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(workout["exercise_name"], style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                            const SizedBox(height: 8),
                            Text("🎯 ${workout['sets']} Sets | 🔄 ${workout['reps']} Reps | ⚖️ ${workout['weight_profile']}", style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: softBlue)),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: PillButton(text: "Save to Schedule", onPressed: () => _showSaveDialog(context, routine)),
              )
            ],
          );
        },
      ),
    );
  }
}

class WeeklyScheduleScreen extends StatelessWidget {
  const WeeklyScheduleScreen({super.key});
  final List<String> daysOfWeek = const ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Weekly Schedule", style: TextStyle(color: Colors.white))),
      body: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: daysOfWeek.length,
        itemBuilder: (context, index) {
          String day = daysOfWeek[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 15),
            child: InkWell(
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => DayScheduleScreen(day: day))),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(color: panelGrey, borderRadius: BorderRadius.circular(10), border: const Border(left: BorderSide(color: softBlue, width: 4))),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(day, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                    const Icon(Icons.arrow_forward_ios, color: softBlue, size: 16),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class DayScheduleScreen extends StatelessWidget {
  final String day;
  const DayScheduleScreen({super.key, required this.day});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("$day's Routine", style: const TextStyle(color: Colors.white))),
      body: FutureBuilder<List<dynamic>?>(
        future: loadWorkoutForDay(day),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator(color: softBlue));
          if (!snapshot.hasData || snapshot.data == null || snapshot.data!.isEmpty) return const Center(child: Text("Rest Day. No workout scheduled.", style: TextStyle(color: Colors.grey, fontSize: 18)));

          List<dynamic> routine = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: routine.length,
            itemBuilder: (context, index) {
              var workout = routine[index];
              return Container(
                margin: const EdgeInsets.only(bottom: 15),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: panelGrey, borderRadius: BorderRadius.circular(0), border: const Border(left: BorderSide(color: softBlue, width: 4))),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(workout["exercise_name"], style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                    const SizedBox(height: 8),
                    Text("🎯 ${workout['sets']} Sets | 🔄 ${workout['reps']} Reps | ⚖️ ${workout['weight_profile']}", style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: softBlue)),
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