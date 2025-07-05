Idea
Perfect — you’re describing a Wellness Memory Coach — a smart assistant that evolves with the user’s fitness, diet, medical needs, and lifestyle over time.

Let’s flesh it out clearly so your group can present and build it easily.

⸻

🏋️‍♂️🧠 Wellness Memory Coach

“Your body knows. I remember.”

⸻

🧩 Concept:

A persistent AI assistant that remembers and adapts to your diet, fitness, goals, injuries, and medical conditions.
It learns over time and helps you adjust your plans daily with context-aware support.

⸻

✅ Memory Categories & Examples

Category	Example Input	Stored As	Example Use
Diet goals	“I want to eat 1500 calories, high protein”	diet.goals.calories = 1500, diet.macros = {high protein}	Suggests recipes/snacks
Sleep	“I slept 5 hours”	logs.sleep[date] = 5	Alerts user they’re under-recovered
Workouts	“I lifted today: squats, 80kg x 5”	logs.lifting[date] = {...}	Tracks PRs or missed lifts
Injuries	“I rolled my ankle skateboarding”	injuries.ankle = {start: date}	Recommends avoiding plyometrics
Supplements	“Taking creatine and vitamin D”	supplements.active = [creatine, D]	Reminds on rest days
Medical history	“I have asthma and IBS”	medical = {asthma: true, ibs: true}	Filters recommendations
Purchases	“Need new shoes”	shopping_list += ["running shoes"]	Suggests brands or reminders


⸻

🧠 What It Remembers
	•	Your goals, failures, and successes
	•	Your daily log (sleep, lifts, injuries, calories)
	•	Your preferences (e.g., “no tofu”)
	•	Your adjustments (“I’m sick today” → light food & no gym)
	•	Your long-term plan (e.g. cutting to 72kg)

⸻

💬 Example Dialogues

User: “Add 40g pea protein and 100g oatmeal to my shake.”
→ Stored to diet.shake_recipe
→ Later: “What’s in my shake again?”

⸻

User: “I strained my shoulder lifting.”
→ Stored under injuries.shoulder = today
→ Next day: “Skip upper body lifts today. Want a light walk plan instead?”

⸻

User: “I slept only 4 hours last night.”
→ Stored to sleep_log[today] = 4
→ Coach: “Let’s reduce your calorie deficit today. Rest is more important.”

⸻

🔧 Tech Breakdown

Component	Tool
LLM agent	Gemini via Google API
Memory	Couchbase (bucket = raw or wellness)
App backend	FastAPI
CLI or frontend	Start with CLI, then explore Streamlit/Web
Env setup	.env with Gemini key + Couchbase creds


⸻

🧑‍💻 MVP Feature Suggestions (Split for Group Members)

Task Area	Description
Memory Schema	Design and create Couchbase data structure: goals, logs, injuries, etc.
LLM Agent	Setup Gemini API connection, parse intent, route to memory/actions
Daily Update Flow	“How did you sleep?” → logs → response
Food Tracker	Add/update meals, macros, reminders
Workout Logging	Input and recall of lifting history
Injury Protocols	Modify advice based on stored injuries
Shopping Assistant	Add/recommend based on needs or habits


⸻
