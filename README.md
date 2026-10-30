# SmartBite – Smart College Food Habit & Diet Planner

Flask + HTML + CSS + JavaScript. Meal suggestions are rule-based (no AI).

## Run locally
    pip install -r requirements.txt
    python app.py        # open http://127.0.0.1:5000

## Deploy on Render
1. Push this folder to a GitHub repository.
2. On Render: New + > Web Service > select the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 1`  (one worker, because data is stored in memory)
5. Deploy. (`render.yaml` already contains these settings.)

## Files
- `app.py` – Flask routes (API) and the rule-based planner
- `food_data.py` – sample Indian foods with estimated calories, protein and price
- `templates/index.html` – the page structure
- `static/style.css` – green and white styling
- `static/script.js` – calls the API with fetch() and updates the page

## How the meal planner works
1. Vegetarian students only see vegetarian foods.
2. Each meal gets a share of the daily budget (Breakfast 25%, Lunch 35%, Snack 15%, Dinner 25%).
3. Foods that fit that share are scored by goal (protein for Muscle Building, light and healthy foods
   for Healthy Eating, balanced for General Fitness). The top two are shown.

Data is kept in server memory per browser and resets when the server restarts.
