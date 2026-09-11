from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import date, timedelta

app = Flask(__name__)

subjects = [
    {"name": "Mathematics", "difficulty": "Hard", "exam": "2026-10-25"},
    {"name": "DBMS", "difficulty": "Medium", "exam": "2026-10-25"},
    {"name": "Python", "difficulty": "Easy", "exam": "2026-10-25"},
    {"name": "Computer Networks", "difficulty": "Medium", "exam": "2026-10-25"},
]

tasks = [
    {"id": 1, "subject": "Mathematics", "topic": "Integration", "duration": 60, "done": True},
    {"id": 2, "subject": "DBMS", "topic": "Normalization", "duration": 60, "done": False},
    {"id": 3, "subject": "Python", "topic": "Functions", "duration": 45, "done": False},
    {"id": 4, "subject": "Computer Networks", "topic": "TCP/IP", "duration": 60, "done": False},
]

def priority(difficulty, exam):
    d = {"Hard": 3, "Medium": 2, "Easy": 1}.get(difficulty, 1)
    try:
        days = max((date.fromisoformat(exam) - date.today()).days, 1)
    except ValueError:
        days = 30
    urgency = max(1, 30 / days)
    return round(d * urgency, 2)

def generate_plan(hours=5):
    ranked = sorted(subjects, key=lambda s: priority(s["difficulty"], s["exam"]), reverse=True)
    topics = {
        "Mathematics": ["Integration", "Differential Equations", "Revision"],
        "DBMS": ["Normalization", "Transactions", "SQL"],
        "Python": ["Functions", "OOP", "Modules"],
        "Computer Networks": ["TCP/IP", "Routing", "Transport Layer"]
    }
    plan = []
    remaining = int(hours * 60)
    for i, s in enumerate(ranked):
        if remaining <= 0: break
        mins = min(120 if s["difficulty"] == "Hard" else 60, remaining)
        plan.append({"day": f"Day {i+1}", "subject": s["name"],
                     "topic": topics.get(s["name"], ["Core Topics"])[0],
                     "duration": mins})
        remaining -= mins
    return plan

@app.route("/")
def dashboard():
    total = len(tasks)
    completed = sum(t["done"] for t in tasks)
    progress = round(completed / total * 100) if total else 0
    return render_template("dashboard.html", tasks=tasks, progress=progress, subjects=subjects)

@app.route("/plan")
def plan():
    return render_template("plan.html", plan=generate_plan())

@app.route("/generate", methods=["POST"])
def generate():
    hours = float(request.form.get("hours", 5))
    return render_template("plan.html", plan=generate_plan(hours))

@app.post("/task/<int:task_id>/toggle")
def toggle(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            break
    return redirect(url_for("dashboard"))

@app.post("/replan")
def replan():
    # Agentic demonstration: missed tasks receive higher priority in the new plan.
    missed = [t for t in tasks if not t["done"]]
    updated = []
    for i, t in enumerate(missed[:5]):
        updated.append({
            "day": f"Day {i+1}",
            "subject": t["subject"],
            "topic": t["topic"],
            "duration": min(t["duration"] + 30, 120)
        })
    return render_template("plan.html", plan=updated, replanned=True)

@app.get("/api/assistant")
def assistant():
    q = request.args.get("q", "").lower()
    if "missed" in q or "replan" in q:
        return jsonify({"answer": "I found pending tasks and can prioritize them for the next available study sessions."})
    if "progress" in q:
        done = sum(t["done"] for t in tasks)
        return jsonify({"answer": f"Your current task completion is {done}/{len(tasks)}. Keep going!"})
    return jsonify({"answer": "Try asking about your progress, missed tasks, or replanning."})

if __name__ == "__main__":
    app.run(debug=True)
