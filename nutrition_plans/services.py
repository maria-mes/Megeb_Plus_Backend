from decimal import Decimal


def calculate_food_nutrition(food, quantity):
    quantity = Decimal(str(quantity))
    grams_per_unit = Decimal(str(food.grams_per_unit))

    if grams_per_unit <= 0 or quantity <= 0:
        return {
            "calories": Decimal("0.00"),
            "protein": Decimal("0.00"),
            "carbs": Decimal("0.00"),
            "fat": Decimal("0.00"),
            "fiber": Decimal("0.00"),
        }

    if food.unit_based:
        # Example:
        # Egg = 1 egg
        # grams_per_unit = 50g
        # quantity = 2
        #
        # Therefore:
        # 2 eggs = 2 × nutrition of 1 egg
        multiplier = quantity
    else:
        # Example:
        # Rice = nutrition per 100g
        # quantity = 200g
        #
        # Therefore:
        # 200g = 2 × nutrition of 100g
        multiplier = quantity / grams_per_unit

    return {
        "calories": (food.calories * multiplier).quantize(Decimal("0.01")),
        "protein": (food.protein * multiplier).quantize(Decimal("0.01")),
        "carbs": (food.carbs * multiplier).quantize(Decimal("0.01")),
        "fat": (food.fat * multiplier).quantize(Decimal("0.01")),
        "fiber": (food.fiber * multiplier).quantize(Decimal("0.01")),
    }

def calculate_meal_nutrition(meal):
    """
    Calculate total nutrition for all food items in a meal.
    """

    totals = {
        "calories": Decimal("0.00"),
        "protein": Decimal("0.00"),
        "carbs": Decimal("0.00"),
        "fat": Decimal("0.00"),
        "fiber": Decimal("0.00"),
    }

    for item in meal.items.all():
        nutrition = calculate_food_nutrition(
            item.food,
            item.quantity,
        )

        for key in totals:
            totals[key] += nutrition[key]

    return totals


def calculate_plan_nutrition(plan):
    """
    Calculate total nutrition for all meals in a nutrition plan.
    """

    totals = {
        "calories": Decimal("0.00"),
        "protein": Decimal("0.00"),
        "carbs": Decimal("0.00"),
        "fat": Decimal("0.00"),
        "fiber": Decimal("0.00"),
    }

    for meal in plan.meals.all():
        nutrition = calculate_meal_nutrition(meal)

        for key in totals:
            totals[key] += nutrition[key]

    return totals