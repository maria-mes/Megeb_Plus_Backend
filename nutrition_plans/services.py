from decimal import Decimal


def calculate_food_nutrition(food, quantity):
    """
    Calculate nutrition for a given quantity of a food.

    The quantity represents the number of servings.
    Example:
        Egg serving_amount = 1
        quantity = 2
        => nutrition is multiplied by 2
    """

    quantity = Decimal(str(quantity))
    serving_amount = Decimal(str(food.serving_amount))

    if serving_amount <= 0:
        return {
            "calories": Decimal("0.00"),
            "protein": Decimal("0.00"),
            "carbs": Decimal("0.00"),
            "fat": Decimal("0.00"),
            "fiber": Decimal("0.00"),
        }

    multiplier = quantity / serving_amount

    return {
        "calories": food.calories * multiplier,
        "protein": food.protein * multiplier,
        "carbs": food.carbohydrates * multiplier,
        "fat": food.fat * multiplier,
        "fiber": food.fiber * multiplier,
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