# Sample Indian food data (estimated values, per one serving).
# Prices are approximate college-canteen / home-cooked costs in rupees.
# meals: B = Breakfast, L = Lunch, S = Evening Snack, D = Dinner

MEALS = ["Breakfast", "Lunch", "Evening Snack", "Dinner"]
CODE = {"B": "Breakfast", "L": "Lunch", "S": "Evening Snack", "D": "Dinner"}

def f(name, emoji, unit, cal, protein, price, veg, meals, healthy=False):
    return {"name": name, "emoji": emoji, "unit": unit, "calories": cal,
            "protein": protein, "price": price, "veg": veg,
            "meals": [CODE[m] for m in meals], "healthy": healthy}

_RAW = [
    # Breakfast
    f("Poha", "🍚", "1 plate", 250, 5, 25, True, "B", True),
    f("Upma", "🥣", "1 bowl", 230, 6, 25, True, "B", True),
    f("Idli with Sambar", "⚪", "3 pieces", 180, 6, 30, True, "B", True),
    f("Masala Dosa", "🥞", "1 piece", 300, 7, 50, True, "B"),
    f("Aloo Paratha with Curd", "🫓", "1 paratha", 320, 9, 40, True, "B"),
    f("Besan Chilla", "🥞", "2 pieces", 220, 11, 25, True, "B", True),
    f("Oats with Milk", "🥛", "1 bowl", 220, 9, 30, True, "B", True),
    f("Vegetable Sandwich", "🥪", "2 slices", 250, 8, 35, True, "B"),
    f("Boiled Eggs", "🥚", "2 eggs", 155, 13, 14, False, "BS", True),
    f("Egg Bhurji with Bread", "🍳", "1 plate", 300, 16, 40, False, "B"),
    # Lunch and dinner
    f("Dal Rice", "🍛", "1 plate", 400, 12, 50, True, "L", True),
    f("Rajma Chawal", "🍛", "1 plate", 450, 15, 60, True, "L"),
    f("Chole Chawal", "🍛", "1 plate", 470, 14, 60, True, "L"),
    f("Veg Thali (2 roti, dal, sabzi, rice)", "🍽️", "1 thali", 600, 18, 80, True, "L"),
    f("Paneer Bhurji with 2 Roti", "🧀", "1 plate", 480, 22, 90, True, "LD"),
    f("Curd Rice", "🍚", "1 bowl", 300, 8, 35, True, "L", True),
    f("Vegetable Khichdi", "🥘", "1 plate", 350, 12, 40, True, "LD", True),
    f("Soya Chunks Pulao", "🍲", "1 plate", 420, 24, 55, True, "L", True),
    f("Egg Curry with Rice", "🍛", "1 plate", 520, 20, 70, False, "L"),
    f("Chicken Curry with 2 Roti", "🍗", "1 plate", 520, 32, 110, False, "LD"),
    f("Chicken Biryani", "🍗", "1 plate", 600, 28, 120, False, "L"),
    f("Roti with Mixed Sabzi", "🫓", "2 roti", 320, 9, 40, True, "D", True),
    f("Dal Tadka with 2 Roti", "🍲", "1 plate", 380, 14, 45, True, "D", True),
    f("Soya Curry with 2 Roti", "🍲", "1 plate", 400, 24, 55, True, "D", True),
    f("Vegetable Pulao", "🍚", "1 plate", 350, 8, 45, True, "D"),
    f("Egg Curry with 2 Roti", "🥚", "1 plate", 400, 18, 55, False, "D"),
    f("Egg Fried Rice", "🍳", "1 plate", 420, 14, 60, False, "D"),
    # Evening snacks
    f("Roasted Chana", "🥜", "50 g", 180, 10, 10, True, "S", True),
    f("Sprouts Chaat", "🥗", "1 bowl", 150, 10, 20, True, "S", True),
    f("Fruit Bowl", "🍎", "1 bowl", 100, 1, 30, True, "S", True),
    f("Banana", "🍌", "1 piece", 105, 1, 8, True, "S", True),
    f("Masala Buttermilk", "🥛", "1 glass", 40, 2, 10, True, "S", True),
    f("Peanuts", "🥜", "30 g", 170, 7, 10, True, "S"),
    f("Banana Milkshake", "🥤", "1 glass", 250, 8, 40, True, "S"),
    f("Boiled Sweet Corn", "🌽", "1 cup", 130, 4, 20, True, "S", True),
    f("Samosa", "🥟", "1 piece", 260, 4, 15, True, "S"),
]

FOODS = [dict(item, id=i + 1) for i, item in enumerate(_RAW)]
