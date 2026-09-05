from django.core.management.base import BaseCommand
from health.models import Food

# Matches services/food.ts FOOD_DATABASE on the mobile app,
# so switching from mock data to the real API is seamless.
FOODS = [
    {"name": "Injera", "category": "Ethiopian Food", "calories_per_100g": 170, "protein_g": 3.5, "carbs_g": 34, "fat_g": 1.5, "fiber_g": 2.5},
    {"name": "Shiro", "category": "Ethiopian Food", "calories_per_100g": 180, "protein_g": 7, "carbs_g": 25, "fat_g": 6, "fiber_g": 5},
    {"name": "Doro Wat", "category": "Ethiopian Food", "calories_per_100g": 210, "protein_g": 18, "carbs_g": 8, "fat_g": 12, "fiber_g": 2},
    {"name": "Rice", "category": "Grains", "calories_per_100g": 130, "protein_g": 2.7, "carbs_g": 28, "fat_g": 0.3, "fiber_g": 0.4},
    {"name": "Chicken", "category": "Protein", "calories_per_100g": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0},
    {"name": "Egg", "category": "Protein", "calories_per_100g": 155, "protein_g": 13, "carbs_g": 1.1, "fat_g": 11, "fiber_g": 0},
    {"name": "Banana", "category": "Fruit", "calories_per_100g": 89, "protein_g": 1.1, "carbs_g": 22.8, "fat_g": 0.3, "fiber_g": 2.6},
    {"name": "Apple", "category": "Fruit", "calories_per_100g": 52, "protein_g": 0.3, "carbs_g": 13.8, "fat_g": 0.2, "fiber_g": 2.4},
    {"name": "Bread", "category": "Grains", "calories_per_100g": 265, "protein_g": 9, "carbs_g": 49, "fat_g": 3.2, "fiber_g": 2.7},
    {"name": "Lentils", "category": "Legumes", "calories_per_100g": 116, "protein_g": 9, "carbs_g": 20, "fat_g": 0.4, "fiber_g": 7.9},
    {"name": "Beans", "category": "Legumes", "calories_per_100g": 127, "protein_g": 8.7, "carbs_g": 22.8, "fat_g": 0.5, "fiber_g": 6.4},
    {"name": "Potato", "category": "Vegetables", "calories_per_100g": 77, "protein_g": 2, "carbs_g": 17, "fat_g": 0.1, "fiber_g": 2.2},
]


class Command(BaseCommand):
    help = "Seed the Food catalog with starter Ethiopian + common foods"

    def handle(self, *args, **options):
        created = 0
        for item in FOODS:
            obj, was_created = Food.objects.get_or_create(
                name=item["name"], defaults=item
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new food(s). {len(FOODS)} total in seed list."
            )
        )