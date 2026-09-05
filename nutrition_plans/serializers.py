from django.contrib.auth import get_user_model
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction

from .models import (
    Food,
    MealLibrary,
    MealLibraryItem,
    NutritionPlan,
    PlanMeal,
    PlanMealItem,
)

from .services import (
    calculate_food_nutrition,
    calculate_meal_nutrition,
    calculate_plan_nutrition,
)

User = get_user_model()


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            "id",
            "name",
            "category",
            "serving",
            "serving_amount",
            "serving_unit",
            "calories",
            "protein",
            "carbohydrates",
            "fat",
            "fiber",
        ]


class PlanMealItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(
        source="food.name",
        read_only=True,
    )

    nutrition = serializers.SerializerMethodField()

    class Meta:
        model = PlanMealItem
        fields = [
            "id",
            "food",
            "food_name",
            "quantity",
            "nutrition",
        ]

    def get_nutrition(self, obj):
        return calculate_food_nutrition(
            obj.food,
            obj.quantity,
        )


class PlanMealSerializer(serializers.ModelSerializer):
    items = PlanMealItemSerializer(
        many=True,
        read_only=True,
    )

    nutrition = serializers.SerializerMethodField()

    class Meta:
        model = PlanMeal
        fields = [
            "id",
            "name",
            "meal_type",
            "source",
            "order",
            "items",
            "nutrition",
        ]

    def get_nutrition(self, obj):
        return calculate_meal_nutrition(obj)


class NutritionPlanListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True,
    )

    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "client",
            "client_name",
            "plan_name",
            "goal",
            "start_date",
            "end_date",
            "status",
        ]


class NutritionPlanDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True,
    )

    nutritionist_name = serializers.CharField(
        source="nutritionist.full_name",
        read_only=True,
    )

    meals = PlanMealSerializer(
        many=True,
        read_only=True,
    )

    nutrition = serializers.SerializerMethodField()

    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "client",
            "client_name",
            "nutritionist",
            "nutritionist_name",
            "plan_name",
            "goal",
            "start_date",
            "end_date",
            "target_calories",
            "notes",
            "status",
            "meals",
            "nutrition",
            "created_at",
            "updated_at",
        ]

    def get_nutrition(self, obj):
        return calculate_plan_nutrition(obj)


class PlanMealItemWriteSerializer(serializers.Serializer):
    food = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.filter(is_active=True)
    )

    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )


class PlanMealWriteSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255
    )

    meal_type = serializers.ChoiceField(
        choices=[
            "Breakfast",
            "Snack",
            "Lunch",
            "Dinner",
        ]
    )

    source = serializers.ChoiceField(
        choices=[
            "library",
            "custom",
        ],
        default="custom",
    )

    items = PlanMealItemWriteSerializer(
        many=True,
    )


class NutritionPlanCreateSerializer(serializers.Serializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="user")
    )

    plan_name = serializers.CharField(
        max_length=255
    )

    goal = serializers.ChoiceField(
        choices=[
            "Weight Management",
            "Healthy Weight Gain",
            "Balanced Nutrition",
            "Diabetes Management",
            "Heart Health",
            "Improved Energy",
            "General Wellness",
        ]
    )

    start_date = serializers.DateField()
    end_date = serializers.DateField()

    target_calories = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    status = serializers.ChoiceField(
        choices=[
            "Draft",
            "Active",
            "Completed",
        ],
        required=False,
        default="Draft",
    )

    meal_options = serializers.DictField(
        child=serializers.ListField(
            child=PlanMealWriteSerializer()
        )
    )

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        meal_options = attrs.get(
            "meal_options",
            {}
        )

        allowed_types = {
            "Breakfast",
            "Snack",
            "Lunch",
            "Dinner",
        }

        for meal_type, meals in meal_options.items():

            if meal_type not in allowed_types:
                raise serializers.ValidationError({
                    "meal_options":
                        f"Invalid meal type: {meal_type}"
                })

            if not isinstance(meals, list):
                raise serializers.ValidationError({
                    "meal_options":
                        f"{meal_type} must be a list."
                })

            for meal in meals:

                if meal["meal_type"] != meal_type:
                    raise serializers.ValidationError({
                        "meal_options":
                            f"Meal '{meal['name']}' has meal_type "
                            f"'{meal['meal_type']}' but is under "
                            f"'{meal_type}'."
                    })

        return attrs
    @transaction.atomic
    def create(self, validated_data):

        meal_options = validated_data.pop(
            "meal_options"
        )

        nutritionist = self.context[
            "request"
        ].user

        plan = NutritionPlan.objects.create(
            nutritionist=nutritionist,
            **validated_data,
        )

        for meal_type, meals in meal_options.items():

            for index, meal_data in enumerate(meals):

                items = meal_data.pop(
                    "items",
                    []
                )

                meal = PlanMeal.objects.create(
                    nutrition_plan=plan,
                    name=meal_data["name"],
                    meal_type=meal_data["meal_type"],
                    source=meal_data.get(
                        "source",
                        "custom",
                    ),
                    order=index,
                )

                for item in items:

                    PlanMealItem.objects.create(
                        meal=meal,
                        food=item["food"],
                        quantity=item["quantity"],
                    )

        return plan


class NutritionPlanUpdateSerializer(serializers.Serializer):

    plan_name = serializers.CharField(
        max_length=255,
        required=False,
    )

    goal = serializers.ChoiceField(
        choices=[
            "Weight Management",
            "Healthy Weight Gain",
            "Balanced Nutrition",
            "Diabetes Management",
            "Heart Health",
            "Improved Energy",
            "General Wellness",
        ],
        required=False,
    )

    start_date = serializers.DateField(
        required=False
    )

    end_date = serializers.DateField(
        required=False
    )

    target_calories = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    status = serializers.ChoiceField(
        choices=[
            "Draft",
            "Active",
            "Completed",
        ],
        required=False,
    )

    meal_options = serializers.DictField(
        child=serializers.ListField(
            child=PlanMealWriteSerializer()
        ),
        required=False
    )

    def validate(self, attrs):

        start_date = attrs.get(
            "start_date",
            self.instance.start_date
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date
        )

        if end_date < start_date:
            raise serializers.ValidationError({
                "end_date":
                    "End date cannot be before start date."
            })

        return attrs
    @transaction.atomic
    def update(self, instance, validated_data):

        meal_options = validated_data.pop(
            "meal_options",
            None,
        )

        for field, value in validated_data.items():

            setattr(
                instance,
                field,
                value,
            )

        instance.save()

        if meal_options is not None:

            instance.meals.all().delete()

            for meal_type, meals in meal_options.items():

                for index, meal_data in enumerate(meals):

                    items = meal_data.pop(
                        "items",
                        []
                    )

                    meal = PlanMeal.objects.create(
                        nutrition_plan=instance,
                        name=meal_data["name"],
                        meal_type=meal_data["meal_type"],
                        source=meal_data.get(
                            "source",
                            "custom",
                        ),
                        order=index,
                    )

                    for item in items:

                        PlanMealItem.objects.create(
                            meal=meal,
                            food=item["food"],
                            quantity=item["quantity"],
                        )

        return instance


class MealLibraryIngredientCreateSerializer(
    serializers.Serializer
):

    food_id = serializers.IntegerField()

    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )


class MealLibraryCreateSerializer(
    serializers.Serializer
):

    name = serializers.CharField(
        max_length=255
    )

    meal_type = serializers.ChoiceField(
        choices=[
            "Breakfast",
            "Lunch",
            "Snack",
            "Dinner",
        ]
    )

    ingredients = MealLibraryIngredientCreateSerializer(
        many=True
    )

    def validate_ingredients(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one ingredient is required."
            )

        food_ids = [
            item["food_id"]
            for item in value
        ]

        foods = Food.objects.filter(
            id__in=food_ids,
            is_active=True
        )

        found_ids = set(
            foods.values_list(
                "id",
                flat=True
            )
        )

        missing_ids = set(food_ids) - found_ids

        if missing_ids:
            raise serializers.ValidationError(
                f"Invalid food IDs: {list(missing_ids)}"
            )

        return value

    def create(self, validated_data):

        ingredients = validated_data.pop(
            "ingredients"
        )

        nutritionist = self.context[
            "request"
        ].user

        meal = MealLibrary.objects.create(
            nutritionist=nutritionist,
            **validated_data
        )

        for ingredient in ingredients:

            food = Food.objects.get(
                id=ingredient["food_id"]
            )

            MealLibraryItem.objects.create(
                meal=meal,
                food=food,
                quantity=ingredient["quantity"]
            )

        return meal


class MealLibraryItemSerializer(
    serializers.ModelSerializer
):

    food_id = serializers.IntegerField(
        source="food.id",
        read_only=True,
    )

    class Meta:
        model = MealLibraryItem
        fields = [
            "id",
            "food_id",
            "quantity",
        ]


class MealLibrarySerializer(
    serializers.ModelSerializer
):

    ingredients = MealLibraryItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = MealLibrary
        fields = [
            "id",
            "name",
            "meal_type",
            "ingredients",
            "created_at",
            "updated_at",
        ]