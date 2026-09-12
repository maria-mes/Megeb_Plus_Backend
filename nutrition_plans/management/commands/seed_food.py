from django.core.management.base import BaseCommand
from nutrition_plans.models import Food


FOODS = [
    # ============================================================
    # GRAINS
    # ============================================================

    {
        "name": "Teff Grain",
        "category": "Grains",
        "calories": 367,
        "protein": 13.3,
        "carbs": 73.1,
        "fat": 2.4,
        "fiber": 8.0,
    },
    {
        "name": "Teff Flour",
        "category": "Grains",
        "calories": 366,
        "protein": 12.4,
        "carbs": 73.1,
        "fat": 3.0,
        "fiber": 8.0,
    },
    {
        "name": "Injera",
        "category": "Grains",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 100,
        "calories": 166,
        "protein": 5.0,
        "carbs": 33.0,
        "fat": 1.0,
        "fiber": 3.0,
    },
    {
        "name": "Barley",
        "category": "Grains",
        "calories": 354,
        "protein": 12.5,
        "carbs": 73.5,
        "fat": 2.3,
        "fiber": 17.3,
    },
    {
        "name": "Barley Flour",
        "category": "Grains",
        "calories": 345,
        "protein": 10.5,
        "carbs": 74.5,
        "fat": 1.6,
        "fiber": 10.0,
    },
    {
        "name": "Wheat",
        "category": "Grains",
        "calories": 340,
        "protein": 13.7,
        "carbs": 72.6,
        "fat": 2.5,
        "fiber": 12.2,
    },
    {
        "name": "Whole Wheat Flour",
        "category": "Grains",
        "calories": 340,
        "protein": 13.7,
        "carbs": 72.6,
        "fat": 2.5,
        "fiber": 10.7,
    },
    {
        "name": "Maize",
        "category": "Grains",
        "calories": 365,
        "protein": 9.4,
        "carbs": 74.3,
        "fat": 4.7,
        "fiber": 7.3,
    },
    {
        "name": "Corn Flour",
        "category": "Grains",
        "calories": 361,
        "protein": 6.9,
        "carbs": 76.9,
        "fat": 3.9,
        "fiber": 7.3,
    },
    {
        "name": "Sorghum",
        "category": "Grains",
        "calories": 329,
        "protein": 10.6,
        "carbs": 72.1,
        "fat": 3.5,
        "fiber": 6.7,
    },
    {
        "name": "Millet",
        "category": "Grains",
        "calories": 378,
        "protein": 11.0,
        "carbs": 72.9,
        "fat": 4.2,
        "fiber": 8.5,
    },
    {
        "name": "White Rice",
        "category": "Grains",
        "calories": 360,
        "protein": 7.1,
        "carbs": 79.9,
        "fat": 0.7,
        "fiber": 1.3,
    },
    {
        "name": "Brown Rice",
        "category": "Grains",
        "calories": 370,
        "protein": 7.9,
        "carbs": 77.2,
        "fat": 2.9,
        "fiber": 3.5,
    },
    {
        "name": "Oats",
        "category": "Grains",
        "calories": 389,
        "protein": 16.9,
        "carbs": 66.3,
        "fat": 6.9,
        "fiber": 10.6,
    },
    {
        "name": "Pasta",
        "category": "Grains",
        "calories": 371,
        "protein": 13.0,
        "carbs": 75.0,
        "fat": 1.5,
        "fiber": 3.2,
    },
    {
        "name": "Whole Wheat Pasta",
        "category": "Grains",
        "calories": 348,
        "protein": 14.0,
        "carbs": 74.0,
        "fat": 2.5,
        "fiber": 9.0,
    },
    {
        "name": "White Bread",
        "category": "Grains",
        "calories": 266,
        "protein": 8.9,
        "carbs": 49.4,
        "fat": 3.2,
        "fiber": 2.7,
    },
    {
        "name": "Whole Wheat Bread",
        "category": "Grains",
        "calories": 247,
        "protein": 13.0,
        "carbs": 41.0,
        "fat": 4.2,
        "fiber": 7.0,
    },

    # ============================================================
    # FRUITS
    # ============================================================

    {
        "name": "Banana",
        "category": "Fruits",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 118,
        "calories": 89,
        "protein": 1.1,
        "carbs": 22.8,
        "fat": 0.3,
        "fiber": 2.6,
    },
    {
        "name": "Apple",
        "category": "Fruits",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 182,
        "calories": 52,
        "protein": 0.3,
        "carbs": 13.8,
        "fat": 0.2,
        "fiber": 2.4,
    },
    {
        "name": "Mango",
        "category": "Fruits",
        "calories": 60,
        "protein": 0.8,
        "carbs": 15.0,
        "fat": 0.4,
        "fiber": 1.6,
    },
    {
        "name": "Papaya",
        "category": "Fruits",
        "calories": 43,
        "protein": 0.5,
        "carbs": 10.8,
        "fat": 0.3,
        "fiber": 1.7,
    },
    {
        "name": "Orange",
        "category": "Fruits",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 131,
        "calories": 47,
        "protein": 0.9,
        "carbs": 11.8,
        "fat": 0.1,
        "fiber": 2.4,
    },
    {
        "name": "Tangerine",
        "category": "Fruits",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 88,
        "calories": 53,
        "protein": 0.8,
        "carbs": 13.3,
        "fat": 0.3,
        "fiber": 1.8,
    },
    {
        "name": "Guava",
        "category": "Fruits",
        "calories": 68,
        "protein": 2.6,
        "carbs": 14.3,
        "fat": 1.0,
        "fiber": 5.4,
    },
    {
        "name": "Pineapple",
        "category": "Fruits",
        "calories": 50,
        "protein": 0.5,
        "carbs": 13.1,
        "fat": 0.1,
        "fiber": 1.4,
    },
    {
        "name": "Watermelon",
        "category": "Fruits",
        "calories": 30,
        "protein": 0.6,
        "carbs": 7.6,
        "fat": 0.2,
        "fiber": 0.4,
    },
    {
        "name": "Avocado",
        "category": "Fruits",
        "calories": 160,
        "protein": 2.0,
        "carbs": 8.5,
        "fat": 14.7,
        "fiber": 6.7,
    },
    {
        "name": "Passion Fruit",
        "category": "Fruits",
        "calories": 97,
        "protein": 2.2,
        "carbs": 23.4,
        "fat": 0.7,
        "fiber": 10.4,
    },
    {
        "name": "Pomegranate",
        "category": "Fruits",
        "calories": 83,
        "protein": 1.7,
        "carbs": 18.7,
        "fat": 1.2,
        "fiber": 4.0,
    },
    {
        "name": "Pear",
        "category": "Fruits",
        "calories": 57,
        "protein": 0.4,
        "carbs": 15.2,
        "fat": 0.1,
        "fiber": 3.1,
    },
    {
        "name": "Peach",
        "category": "Fruits",
        "calories": 39,
        "protein": 0.9,
        "carbs": 9.5,
        "fat": 0.3,
        "fiber": 1.5,
    },
    {
        "name": "Strawberry",
        "category": "Fruits",
        "calories": 32,
        "protein": 0.7,
        "carbs": 7.7,
        "fat": 0.3,
        "fiber": 2.0,
    },
    {
        "name": "Grapes",
        "category": "Fruits",
        "calories": 69,
        "protein": 0.7,
        "carbs": 18.1,
        "fat": 0.2,
        "fiber": 0.9,
    },
    {
        "name": "Dates",
        "category": "Fruits",
        "calories": 282,
        "protein": 2.5,
        "carbs": 75.0,
        "fat": 0.4,
        "fiber": 8.0,
    },
    {
        "name": "Lemon",
        "category": "Fruits",
        "calories": 29,
        "protein": 1.1,
        "carbs": 9.3,
        "fat": 0.3,
        "fiber": 2.8,
    },

    # ============================================================
    # LEGUMES
    # ============================================================

    {
        "name": "Red Lentils",
        "category": "Legumes",
        "calories": 352,
        "protein": 24.6,
        "carbs": 63.4,
        "fat": 1.1,
        "fiber": 10.7,
    },
    {
        "name": "Green Lentils",
        "category": "Legumes",
        "calories": 352,
        "protein": 24.6,
        "carbs": 63.4,
        "fat": 1.1,
        "fiber": 10.7,
    },
    {
        "name": "Chickpeas",
        "category": "Legumes",
        "calories": 364,
        "protein": 19.3,
        "carbs": 60.7,
        "fat": 6.0,
        "fiber": 17.4,
    },
    {
        "name": "Fava Beans",
        "category": "Legumes",
        "calories": 341,
        "protein": 26.1,
        "carbs": 58.3,
        "fat": 1.5,
        "fiber": 25.0,
    },
    {
        "name": "Kidney Beans",
        "category": "Legumes",
        "calories": 333,
        "protein": 23.6,
        "carbs": 60.0,
        "fat": 0.8,
        "fiber": 24.9,
    },
    {
        "name": "White Beans",
        "category": "Legumes",
        "calories": 333,
        "protein": 23.4,
        "carbs": 60.3,
        "fat": 0.8,
        "fiber": 15.2,
    },
    {
        "name": "Black Beans",
        "category": "Legumes",
        "calories": 341,
        "protein": 21.6,
        "carbs": 62.4,
        "fat": 1.4,
        "fiber": 15.5,
    },
    {
        "name": "Soybeans",
        "category": "Legumes",
        "calories": 446,
        "protein": 36.5,
        "carbs": 30.2,
        "fat": 19.9,
        "fiber": 9.3,
    },
    {
        "name": "Green Peas",
        "category": "Legumes",
        "calories": 81,
        "protein": 5.4,
        "carbs": 14.5,
        "fat": 0.4,
        "fiber": 5.7,
    },
    {
        "name": "Split Peas",
        "category": "Legumes",
        "calories": 341,
        "protein": 24.6,
        "carbs": 60.1,
        "fat": 1.2,
        "fiber": 25.5,
    },
    {
        "name": "Shiro Flour",
        "category": "Legumes",
        "calories": 360,
        "protein": 20.0,
        "carbs": 60.0,
        "fat": 5.0,
        "fiber": 10.0,
    },

    # ============================================================
    # VEGETABLES
    # ============================================================

    {
        "name": "Tomato",
        "category": "Vegetables",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 123,
        "calories": 18,
        "protein": 0.9,
        "carbs": 3.9,
        "fat": 0.2,
        "fiber": 1.2,
    },
    {
        "name": "Onion",
        "category": "Vegetables",
        "calories": 40,
        "protein": 1.1,
        "carbs": 9.3,
        "fat": 0.1,
        "fiber": 1.7,
    },
    {
        "name": "Garlic",
        "category": "Vegetables",
        "calories": 149,
        "protein": 6.4,
        "carbs": 33.1,
        "fat": 0.5,
        "fiber": 2.1,
    },
    {
        "name": "Carrot",
        "category": "Vegetables",
        "unit_based": True,
        "unit_name": "piece",
        "grams_per_unit": 61,
        "calories": 41,
        "protein": 0.9,
        "carbs": 9.6,
        "fat": 0.2,
        "fiber": 2.8,
    },
    {
        "name": "Cabbage",
        "category": "Vegetables",
        "calories": 25,
        "protein": 1.3,
        "carbs": 5.8,
        "fat": 0.1,
        "fiber": 2.5,
    },
    {
        "name": "Kale",
        "category": "Vegetables",
        "calories": 49,
        "protein": 4.3,
        "carbs": 8.8,
        "fat": 0.9,
        "fiber": 4.1,
    },
    {
        "name": "Spinach",
        "category": "Vegetables",
        "calories": 23,
        "protein": 2.9,
        "carbs": 3.6,
        "fat": 0.4,
        "fiber": 2.2,
    },
    {
        "name": "Lettuce",
        "category": "Vegetables",
        "calories": 15,
        "protein": 1.4,
        "carbs": 2.9,
        "fat": 0.2,
        "fiber": 1.3,
    },
    {
        "name": "Green Pepper",
        "category": "Vegetables",
        "calories": 20,
        "protein": 0.9,
        "carbs": 4.6,
        "fat": 0.2,
        "fiber": 1.7,
    },
    {
        "name": "Red Pepper",
        "category": "Vegetables",
        "calories": 31,
        "protein": 1.0,
        "carbs": 6.0,
        "fat": 0.3,
        "fiber": 2.1,
    },
    {
        "name": "Beetroot",
        "category": "Vegetables",
        "calories": 43,
        "protein": 1.6,
        "carbs": 9.6,
        "fat": 0.2,
        "fiber": 2.8,
    },
    {
        "name": "Potato",
        "category": "Vegetables",
        "calories": 77,
        "protein": 2.0,
        "carbs": 17.5,
        "fat": 0.1,
        "fiber": 2.2,
    },
    {
        "name": "Sweet Potato",
        "category": "Vegetables",
        "calories": 86,
        "protein": 1.6,
        "carbs": 20.1,
        "fat": 0.1,
        "fiber": 3.0,
    },
    {
        "name": "Broccoli",
        "category": "Vegetables",
        "calories": 34,
        "protein": 2.8,
        "carbs": 6.6,
        "fat": 0.4,
        "fiber": 2.6,
    },
    {
        "name": "Cauliflower",
        "category": "Vegetables",
        "calories": 25,
        "protein": 1.9,
        "carbs": 5.0,
        "fat": 0.3,
        "fiber": 2.0,
    },
    {
        "name": "Green Beans",
        "category": "Vegetables",
        "calories": 31,
        "protein": 1.8,
        "carbs": 7.0,
        "fat": 0.2,
        "fiber": 2.7,
    },
    {
        "name": "Eggplant",
        "category": "Vegetables",
        "calories": 25,
        "protein": 1.0,
        "carbs": 5.9,
        "fat": 0.2,
        "fiber": 3.0,
    },
    {
        "name": "Cucumber",
        "category": "Vegetables",
        "calories": 15,
        "protein": 0.7,
        "carbs": 3.6,
        "fat": 0.1,
        "fiber": 0.5,
    },
    {
        "name": "Pumpkin",
        "category": "Vegetables",
        "calories": 26,
        "protein": 1.0,
        "carbs": 6.5,
        "fat": 0.1,
        "fiber": 0.5,
    },

    # ============================================================
    # PROTEIN
    # ============================================================

    {
        "name": "Egg",
        "category": "Protein",
        "unit_based": True,
        "unit_name": "egg",
        "grams_per_unit": 50,
        "calories": 143,
        "protein": 12.6,
        "carbs": 0.7,
        "fat": 9.5,
        "fiber": 0,
    },
    {
        "name": "Chicken Breast",
        "category": "Protein",
        "calories": 165,
        "protein": 31.0,
        "carbs": 0,
        "fat": 3.6,
        "fiber": 0,
    },
    {
        "name": "Chicken Thigh",
        "category": "Protein",
        "calories": 209,
        "protein": 26.0,
        "carbs": 0,
        "fat": 10.9,
        "fiber": 0,
    },
    {
        "name": "Beef",
        "category": "Protein",
        "calories": 250,
        "protein": 26.0,
        "carbs": 0,
        "fat": 15.0,
        "fiber": 0,
    },
    {
        "name": "Lean Beef",
        "category": "Protein",
        "calories": 217,
        "protein": 26.1,
        "carbs": 0,
        "fat": 11.8,
        "fiber": 0,
    },
    {
        "name": "Goat Meat",
        "category": "Protein",
        "calories": 143,
        "protein": 27.1,
        "carbs": 0,
        "fat": 3.0,
        "fiber": 0,
    },
    {
        "name": "Lamb",
        "category": "Protein",
        "calories": 294,
        "protein": 25.6,
        "carbs": 0,
        "fat": 20.9,
        "fiber": 0,
    },
    {
        "name": "Tilapia",
        "category": "Protein",
        "calories": 128,
        "protein": 26.0,
        "carbs": 0,
        "fat": 2.7,
        "fiber": 0,
    },
    {
        "name": "Tuna",
        "category": "Protein",
        "calories": 132,
        "protein": 28.0,
        "carbs": 0,
        "fat": 1.3,
        "fiber": 0,
    },
    {
        "name": "Salmon",
        "category": "Protein",
        "calories": 208,
        "protein": 20.4,
        "carbs": 0,
        "fat": 13.4,
        "fiber": 0,
    },
    {
        "name": "Sardines",
        "category": "Protein",
        "calories": 208,
        "protein": 24.6,
        "carbs": 0,
        "fat": 11.5,
        "fiber": 0,
    },

    # ============================================================
    # DAIRY
    # ============================================================

    {
        "name": "Whole Milk",
        "category": "Dairy",
        "calories": 61,
        "protein": 3.2,
        "carbs": 4.8,
        "fat": 3.3,
        "fiber": 0,
    },
    {
        "name": "Low Fat Milk",
        "category": "Dairy",
        "calories": 42,
        "protein": 3.4,
        "carbs": 5.0,
        "fat": 1.0,
        "fiber": 0,
    },
    {
        "name": "Yogurt",
        "category": "Dairy",
        "calories": 61,
        "protein": 3.5,
        "carbs": 4.7,
        "fat": 3.3,
        "fiber": 0,
    },
    {
        "name": "Greek Yogurt",
        "category": "Dairy",
        "calories": 59,
        "protein": 10.0,
        "carbs": 3.6,
        "fat": 0.4,
        "fiber": 0,
    },
    {
        "name": "Cheese",
        "category": "Dairy",
        "calories": 402,
        "protein": 25.0,
        "carbs": 1.3,
        "fat": 33.0,
        "fiber": 0,
    },
    {
        "name": "Cottage Cheese",
        "category": "Dairy",
        "calories": 98,
        "protein": 11.1,
        "carbs": 3.4,
        "fat": 4.3,
        "fiber": 0,
    },
    # ============================================================
    # NUTS & SEEDS
    # ============================================================

    {
        "name": "Peanuts",
        "category": "Nuts & Seeds",
        "calories": 567,
        "protein": 25.8,
        "carbs": 16.1,
        "fat": 49.2,
        "fiber": 8.5,
    },
    {
        "name": "Almonds",
        "category": "Nuts & Seeds",
        "calories": 579,
        "protein": 21.2,
        "carbs": 21.6,
        "fat": 49.9,
        "fiber": 12.5,
    },
    {
        "name": "Cashews",
        "category": "Nuts & Seeds",
        "calories": 553,
        "protein": 18.2,
        "carbs": 30.2,
        "fat": 43.9,
        "fiber": 3.3,
    },
    {
        "name": "Walnuts",
        "category": "Nuts & Seeds",
        "calories": 654,
        "protein": 15.2,
        "carbs": 13.7,
        "fat": 65.2,
        "fiber": 6.7,
    },
    {
        "name": "Sesame Seeds",
        "category": "Nuts & Seeds",
        "calories": 573,
        "protein": 17.7,
        "carbs": 23.4,
        "fat": 49.7,
        "fiber": 11.8,
    },
    {
        "name": "Sunflower Seeds",
        "category": "Nuts & Seeds",
        "calories": 584,
        "protein": 20.8,
        "carbs": 20.0,
        "fat": 51.5,
        "fiber": 8.6,
    },
    {
        "name": "Pumpkin Seeds",
        "category": "Nuts & Seeds",
        "calories": 559,
        "protein": 30.2,
        "carbs": 10.7,
        "fat": 49.1,
        "fiber": 6.0,
    },
    {
        "name": "Flax Seeds",
        "category": "Nuts & Seeds",
        "calories": 534,
        "protein": 18.3,
        "carbs": 28.9,
        "fat": 42.2,
        "fiber": 27.3,
    },
    {
        "name": "Chia Seeds",
        "category": "Nuts & Seeds",
        "calories": 486,
        "protein": 16.5,
        "carbs": 42.1,
        "fat": 30.7,
        "fiber": 34.4,
    },
    {
        "name": "Pistachios",
        "category": "Nuts & Seeds",
        "calories": 562,
        "protein": 20.2,
        "carbs": 27.2,
        "fat": 45.3,
        "fiber": 10.6,
    },
    {
        "name": "Hazelnuts",
        "category": "Nuts & Seeds",
        "calories": 628,
        "protein": 14.9,
        "carbs": 16.7,
        "fat": 60.8,
        "fiber": 9.7,
    },


    # ============================================================
    # OTHER
    # ============================================================

    {
        "name": "Olive Oil",
        "category": "Other",
        "calories": 884,
        "protein": 0,
        "carbs": 0,
        "fat": 100,
        "fiber": 0,
    },
    {
        "name": "Vegetable Oil",
        "category": "Other",
        "calories": 884,
        "protein": 0,
        "carbs": 0,
        "fat": 100,
        "fiber": 0,
    },
    {
        "name": "Honey",
        "category": "Other",
        "calories": 304,
        "protein": 0.3,
        "carbs": 82.4,
        "fat": 0,
        "fiber": 0.2,
    },
    {
        "name": "Sugar",
        "category": "Other",
        "calories": 387,
        "protein": 0,
        "carbs": 100,
        "fat": 0,
        "fiber": 0,
    },
    {
        "name": "Coffee",
        "category": "Other",
        "calories": 2,
        "protein": 0.3,
        "carbs": 0,
        "fat": 0,
        "fiber": 0,
    },
    {
        "name": "Tea",
        "category": "Other",
        "calories": 1,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0,
    },
]

FOOD_DETAILS = {

    # ============================================================
    # GRAINS
    # ============================================================

    "Teff Grain": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry teff (about 45 g)",
    },
    "Teff Flour": {
        "preparation": "Dry",
        "serving_description": "1/4 cup teff flour (about 30 g)",
    },
    "Injera": {
        "preparation": "Prepared",
        "serving_description": "1 piece (about 100 g)",
    },
    "Barley": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry barley (about 45 g)",
    },
    "Barley Flour": {
        "preparation": "Dry",
        "serving_description": "1/4 cup barley flour (about 30 g)",
    },
    "Wheat": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry wheat (about 45 g)",
    },
    "Whole Wheat Flour": {
        "preparation": "Dry",
        "serving_description": "1/4 cup whole wheat flour (about 30 g)",
    },
    "Maize": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry maize (about 40 g)",
    },
    "Corn Flour": {
        "preparation": "Dry",
        "serving_description": "1/4 cup corn flour (about 30 g)",
    },
    "Sorghum": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry sorghum (about 40 g)",
    },
    "Millet": {
        "preparation": "Dry",
        "serving_description": "1/4 cup dry millet (about 45 g)",
    },
    "White Rice": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked rice (about 160 g)",
    },
    "Brown Rice": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked rice (about 195 g)",
    },
    "Oats": {
        "preparation": "Dry",
        "serving_description": "1/2 cup dry oats (about 40 g)",
    },
    "Pasta": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked pasta (about 140 g)",
    },
    "Whole Wheat Pasta": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked pasta (about 140 g)",
    },
    "White Bread": {
        "preparation": "Ready to eat",
        "serving_description": "1 slice (about 25 g)",
    },
    "Whole Wheat Bread": {
        "preparation": "Ready to eat",
        "serving_description": "1 slice (about 30 g)",
    },


    # ============================================================
    # FRUITS
    # ============================================================

    "Banana": {
        "preparation": "Raw",
        "serving_description": "1 medium banana (about 118 g)",
    },
    "Apple": {
        "preparation": "Raw",
        "serving_description": "1 medium apple (about 182 g)",
    },
    "Mango": {
        "preparation": "Raw",
        "serving_description": "1 cup sliced mango (about 165 g)",
    },
    "Papaya": {
        "preparation": "Raw",
        "serving_description": "1 cup cubed papaya (about 145 g)",
    },
    "Orange": {
        "preparation": "Raw",
        "serving_description": "1 medium orange (about 131 g)",
    },
    "Tangerine": {
        "preparation": "Raw",
        "serving_description": "1 medium tangerine (about 88 g)",
    },
    "Guava": {
        "preparation": "Raw",
        "serving_description": "1 medium guava (about 100 g)",
    },
    "Pineapple": {
        "preparation": "Raw",
        "serving_description": "1 cup chunks (about 165 g)",
    },
    "Watermelon": {
        "preparation": "Raw",
        "serving_description": "1 cup diced watermelon (about 152 g)",
    },
    "Avocado": {
        "preparation": "Raw",
        "serving_description": "1/2 medium avocado (about 75 g)",
    },
    "Passion Fruit": {
        "preparation": "Raw",
        "serving_description": "2 medium passion fruits (about 36 g)",
    },
    "Pomegranate": {
        "preparation": "Raw",
        "serving_description": "1/2 cup arils (about 87 g)",
    },
    "Pear": {
        "preparation": "Raw",
        "serving_description": "1 medium pear (about 178 g)",
    },
    "Peach": {
        "preparation": "Raw",
        "serving_description": "1 medium peach (about 150 g)",
    },
    "Strawberry": {
        "preparation": "Raw",
        "serving_description": "1 cup whole strawberries (about 152 g)",
    },
    "Grapes": {
        "preparation": "Raw",
        "serving_description": "1 cup grapes (about 151 g)",
    },
    "Dates": {
        "preparation": "Raw",
        "serving_description": "3 dates (about 24 g)",
    },
    "Lemon": {
        "preparation": "Raw",
        "serving_description": "1 medium lemon (about 58 g)",
    },


    # ============================================================
    # LEGUMES
    # ============================================================

    "Red Lentils": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked lentils (about 198 g)",
    },
    "Green Lentils": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked lentils (about 198 g)",
    },
    "Chickpeas": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked chickpeas (about 164 g)",
    },
    "Fava Beans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked fava beans (about 170 g)",
    },
    "Kidney Beans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked kidney beans (about 177 g)",
    },
    "White Beans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked white beans (about 179 g)",
    },
    "Black Beans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked black beans (about 172 g)",
    },
    "Soybeans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked soybeans (about 172 g)",
    },
    "Green Peas": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked peas (about 160 g)",
    },
    "Split Peas": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked split peas (about 196 g)",
    },
    "Shiro Flour": {
        "preparation": "Dry",
        "serving_description": "1/4 cup shiro flour (about 30 g)",
    },


    # ============================================================
    # VEGETABLES
    # ============================================================

    "Tomato": {
        "preparation": "Raw",
        "serving_description": "1 medium tomato (about 123 g)",
    },
    "Onion": {
        "preparation": "Raw",
        "serving_description": "1/2 medium onion (about 55 g)",
    },
    "Garlic": {
        "preparation": "Raw",
        "serving_description": "1 clove (about 3 g)",
    },
    "Carrot": {
        "preparation": "Raw",
        "serving_description": "1 medium carrot (about 61 g)",
    },
    "Cabbage": {
        "preparation": "Raw",
        "serving_description": "1 cup shredded cabbage (about 89 g)",
    },
    "Kale": {
        "preparation": "Raw",
        "serving_description": "1 cup chopped kale (about 67 g)",
    },
    "Spinach": {
        "preparation": "Raw",
        "serving_description": "1 cup raw spinach (about 30 g)",
    },
    "Lettuce": {
        "preparation": "Raw",
        "serving_description": "1 cup chopped lettuce (about 47 g)",
    },
    "Green Pepper": {
        "preparation": "Raw",
        "serving_description": "1 medium green pepper (about 119 g)",
    },
    "Red Pepper": {
        "preparation": "Raw",
        "serving_description": "1 medium red pepper (about 119 g)",
    },
    "Beetroot": {
        "preparation": "Raw",
        "serving_description": "1 medium beetroot (about 82 g)",
    },
    "Potato": {
        "preparation": "Boiled",
        "serving_description": "1 medium potato (about 150 g)",
    },
    "Sweet Potato": {
        "preparation": "Boiled",
        "serving_description": "1 medium sweet potato (about 130 g)",
    },
    "Broccoli": {
        "preparation": "Steamed",
        "serving_description": "1 cup chopped broccoli (about 156 g)",
    },
    "Cauliflower": {
        "preparation": "Steamed",
        "serving_description": "1 cup chopped cauliflower (about 107 g)",
    },
    "Green Beans": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked green beans (about 125 g)",
    },
    "Eggplant": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked eggplant (about 99 g)",
    },
    "Cucumber": {
        "preparation": "Raw",
        "serving_description": "1/2 medium cucumber (about 100 g)",
    },
    "Pumpkin": {
        "preparation": "Cooked",
        "serving_description": "1 cup cooked pumpkin (about 245 g)",
    },


    # ============================================================
    # PROTEIN
    # ============================================================

    "Egg": {
        "preparation": "Boiled",
        "serving_description": "1 large egg (about 50 g)",
    },
    "Chicken Breast": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked chicken breast",
    },
    "Chicken Thigh": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked chicken thigh",
    },
    "Beef": {
        "preparation": "Cooked",
        "serving_description": "100 g cooked beef",
    },
    "Lean Beef": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked lean beef",
    },
    "Goat Meat": {
        "preparation": "Cooked",
        "serving_description": "100 g cooked goat meat",
    },
    "Lamb": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked lamb",
    },
    "Tilapia": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked tilapia",
    },
    "Tuna": {
        "preparation": "Canned, drained",
        "serving_description": "100 g drained tuna",
    },
    "Salmon": {
        "preparation": "Grilled",
        "serving_description": "100 g cooked salmon",
    },
    "Sardines": {
        "preparation": "Canned, drained",
        "serving_description": "100 g drained sardines",
    },


    # ============================================================
    # DAIRY
    # ============================================================

    "Whole Milk": {
        "preparation": "Ready to drink",
        "serving_description": "1 cup (240 ml)",
    },
    "Low Fat Milk": {
        "preparation": "Ready to drink",
        "serving_description": "1 cup (240 ml)",
    },
    "Yogurt": {
        "preparation": "Ready to eat",
        "serving_description": "1 cup (245 g)",
    },
    "Greek Yogurt": {
        "preparation": "Ready to eat",
        "serving_description": "1 cup (170 g)",
    },
    "Cheese": {
        "preparation": "Ready to eat",
        "serving_description": "1 oz (about 28 g)",
    },
    "Cottage Cheese": {
        "preparation": "Ready to eat",
        "serving_description": "1/2 cup (about 113 g)",
    },


    # ============================================================
    # NUTS & SEEDS
    # ============================================================

    "Peanuts": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 28 g)",
    },
    "Almonds": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 23 almonds)",
    },
    "Cashews": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 18 cashews)",
    },
    "Walnuts": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 14 halves)",
    },
    "Sesame Seeds": {
        "preparation": "Raw",
        "serving_description": "1 tablespoon (about 9 g)",
    },
    "Sunflower Seeds": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 28 g)",
    },
    "Pumpkin Seeds": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 28 g)",
    },
    "Flax Seeds": {
        "preparation": "Raw",
        "serving_description": "1 tablespoon (about 10 g)",
    },
    "Chia Seeds": {
        "preparation": "Raw",
        "serving_description": "1 tablespoon (about 12 g)",
    },
    "Pistachios": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 49 pistachios)",
    },
    "Hazelnuts": {
        "preparation": "Raw",
        "serving_description": "1 oz (about 21 hazelnuts)",
    },


    # ============================================================
    # OTHER
    # ============================================================

    "Olive Oil": {
        "preparation": "Ready to use",
        "serving_description": "1 tablespoon (15 ml)",
    },
    "Vegetable Oil": {
        "preparation": "Ready to use",
        "serving_description": "1 tablespoon (15 ml)",
    },
    "Honey": {
        "preparation": "Ready to use",
        "serving_description": "1 tablespoon (21 g)",
    },
    "Sugar": {
        "preparation": "Ready to use",
        "serving_description": "1 tablespoon (about 12.5 g)",
    },
    "Coffee": {
        "preparation": "Brewed",
        "serving_description": "1 cup brewed coffee (240 ml)",
    },
    "Tea": {
        "preparation": "Brewed",
        "serving_description": "1 cup brewed tea (240 ml)",
    },
}


class Command(BaseCommand):
    help = "Populate the food database with common Ethiopian and international foods"

    def handle(self, *args, **kwargs):
       created = 0
       updated = 0

       for food_data in FOODS:
         name = food_data["name"]

         food, was_created = Food.objects.update_or_create(
            name=name,
            defaults=food_data,
        )

         if was_created:
            created += 1
         else:
            updated += 1

    # Add serving/preparation information
       details_updated = 0

       for name, details in FOOD_DETAILS.items():
        details_updated += Food.objects.filter(name=name).update(**details)

       self.stdout.write(
        self.style.SUCCESS(
            f"Food database seeded successfully. "
            f"Created: {created}, Updated: {updated}, "
            f"Serving details updated: {details_updated}, "
            f"Total seed foods: {len(FOODS)}"
        )
    )