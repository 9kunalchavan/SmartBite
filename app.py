"""SmartBite - Smart College Food Habit & Diet Planner (Flask backend).

Data is kept in memory for each browser (identified by a session cookie),
so no database is needed. Restarting the server clears the data.
"""
import os
import uuid
from flask import Flask, jsonify, render_template, request, session
from food_data import FOODS, MEALS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smartbite-dev-key")

USERS = {}  # session id -> that student's data

PREFERENCES = ["Vegetarian", "Non-Vegetarian"]
# Daily targets for each goal (sample values for a college student)
GOALS = {
    "Healthy Eating":   {"calories": 1800, "protein": 50},
    "Muscle Building":  {"calories": 2500, "protein": 90},
    "General Fitness":  {"calories": 2200, "protein": 65},
}
# Share of the daily budget given to each meal
BUDGET_SHARE = {"Breakfast": 0.25, "Lunch": 0.35, "Evening Snack": 0.15, "Dinner": 0.25}
WATER_TARGET = 8  # glasses


def get_user():
    uid = session.get("uid")
    if uid not in USERS:
        uid = uuid.uuid4().hex
        session["uid"] = uid
        USERS[uid] = {"profile": None, "log": [], "water": 0, "next_id": 1}
    return USERS[uid]


def error(message, code=400):
    return jsonify({"error": message}), code


def allowed_foods(profile):
    """Vegetarian students only see vegetarian food."""
    if profile and profile["preference"] == "Vegetarian":
        return [f for f in FOODS if f["veg"]]
    return FOODS


def score(food, goal):
    """Simple rule-based score: higher means a better match for the goal."""
    if goal == "Muscle Building":
        return food["protein"] * 2 - food["price"] * 0.05
    if goal == "Healthy Eating":
        return (15 if food["healthy"] else 0) - food["calories"] / 40 + food["protein"]
    return food["protein"] + (8 if food["healthy"] else 0) - food["price"] * 0.05  # General Fitness


REASONS = {
    "Muscle Building": "High in protein",
    "Healthy Eating": "Light and healthy",
    "General Fitness": "Balanced protein and energy",
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/profile", methods=["GET", "POST"])
def profile():
    user = get_user()
    if request.method == "GET":
        return jsonify({"profile": user["profile"]})

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    preference = data.get("preference")
    goal = data.get("goal")
    try:
        age = int(data.get("age"))
        budget = float(data.get("budget"))
    except (TypeError, ValueError):
        return error("Age and budget must be numbers.")

    if not name or len(name) > 40:
        return error("Please enter a name (up to 40 characters).")
    if not 15 <= age <= 60:
        return error("Age must be between 15 and 60.")
    if preference not in PREFERENCES:
        return error("Please choose a food preference.")
    if not 30 <= budget <= 2000:
        return error("Daily budget must be between 30 and 2000 rupees.")
    if goal not in GOALS:
        return error("Please choose a goal.")

    user["profile"] = {"name": name, "age": age, "preference": preference,
                       "budget": budget, "goal": goal}
    return jsonify({"profile": user["profile"]})


@app.get("/api/foods")
def foods():
    return jsonify({"foods": allowed_foods(get_user()["profile"])})


@app.get("/api/meal-plan")
def meal_plan():
    profile = get_user()["profile"]
    if not profile:
        return error("Save your student profile first.")

    foods_ok = allowed_foods(profile)
    plan = {}
    for meal in MEALS:
        limit = profile["budget"] * BUDGET_SHARE[meal]
        options = [f for f in foods_ok if meal in f["meals"]]
        affordable = [f for f in options if f["price"] <= limit]
        if affordable:
            affordable.sort(key=lambda f: score(f, profile["goal"]), reverse=True)
            picks = affordable[:2]
        else:  # nothing fits the budget: show the cheapest options
            picks = sorted(options, key=lambda f: f["price"])[:2]
        plan[meal] = {"budget": round(limit), "options": picks}
    return jsonify({"plan": plan, "reason": REASONS[profile["goal"]]})


def with_totals(entries):
    return {
        "calories": round(sum(e["calories"] for e in entries)),
        "protein": round(sum(e["protein"] for e in entries), 1),
        "cost": round(sum(e["cost"] for e in entries), 1),
    }


@app.route("/api/log", methods=["GET", "POST", "DELETE"])
def log():
    user = get_user()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        food = next((f for f in FOODS if f["id"] == data.get("food_id")), None)
        if not food:
            return error("Please choose a food from the list.")
        try:
            qty = float(data.get("quantity"))
        except (TypeError, ValueError):
            return error("Quantity must be a number.")
        if not 0.5 <= qty <= 20:
            return error("Quantity must be between 0.5 and 20.")
        user["log"].append({
            "id": user["next_id"], "name": food["name"], "emoji": food["emoji"],
            "unit": food["unit"], "quantity": qty,
            "calories": round(food["calories"] * qty),
            "protein": round(food["protein"] * qty, 1),
            "cost": round(food["price"] * qty, 1),
        })
        user["next_id"] += 1
    elif request.method == "DELETE":
        entry_id = request.args.get("id", type=int)
        if entry_id is None:
            user["log"] = []  # clear all
        else:
            user["log"] = [e for e in user["log"] if e["id"] != entry_id]
    return jsonify({"log": user["log"], "totals": with_totals(user["log"])})


@app.post("/api/water")
def water():
    user = get_user()
    action = (request.get_json(silent=True) or {}).get("action")
    if action == "add":
        user["water"] = min(user["water"] + 1, 20)
    elif action == "remove":
        user["water"] = max(user["water"] - 1, 0)
    else:
        return error("Action must be 'add' or 'remove'.")
    return jsonify({"water": user["water"], "target": WATER_TARGET})


@app.get("/api/dashboard")
def dashboard():
    user = get_user()
    profile = user["profile"]
    targets = GOALS[profile["goal"]] if profile else GOALS["General Fitness"]
    totals = with_totals(user["log"])

    tip = "Looking good! Keep your meals balanced."
    if not user["log"]:
        tip = "Add the food you eat in the Food Tracker to see your progress."
    elif totals["protein"] < targets["protein"] * 0.5:
        tip = "Protein is low. Try dal, soya, paneer, sprouts or eggs."
    elif totals["calories"] > targets["calories"]:
        tip = "You crossed your calorie target. Choose lighter meals next."
    elif user["water"] < WATER_TARGET / 2:
        tip = "Drink more water through the day."

    return jsonify({
        "name": profile["name"] if profile else None,
        "calories": totals["calories"], "calorie_target": targets["calories"],
        "protein": totals["protein"], "protein_target": targets["protein"],
        "expense": totals["cost"], "budget": profile["budget"] if profile else None,
        "water": user["water"], "water_target": WATER_TARGET, "tip": tip,
    })


if __name__ == "__main__":
    app.run(debug=True)
