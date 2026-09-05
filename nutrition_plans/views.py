from django.db.models import Q 
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PlanMealSerializer
from django.utils import timezone

from .models import (
    Food,
    MealLibrary,
    MealLibraryItem,
    NutritionPlan,
)
from .permissions import IsNutritionist
from .serializers import (
    FoodSerializer,
    NutritionPlanCreateSerializer,
    NutritionPlanDetailSerializer,
    NutritionPlanListSerializer,
    NutritionPlanUpdateSerializer,
    MealLibrarySerializer,
    MealLibraryCreateSerializer,
)


class NutritionPlanListCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsNutritionist,
    ]

    def get(self, request):

        plans = (
            NutritionPlan.objects
            .filter(nutritionist=request.user)
            .select_related("client")
        )

        search = request.query_params.get(
            "search"
        )

        status_filter = request.query_params.get(
            "status"
        )

        if search:
            plans = plans.filter(
                Q(plan_name__icontains=search)
                | Q(goal__icontains=search)
                | Q(client__full_name__icontains=search)
            )

        if status_filter:
            plans = plans.filter(
                status=status_filter
            )

        serializer = NutritionPlanListSerializer(
            plans,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = NutritionPlanCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        plan = serializer.save()

        return Response(
            NutritionPlanDetailSerializer(
                plan
            ).data,
            status=status.HTTP_201_CREATED,
        )


class NutritionPlanDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, request, plan_id):

        try:
            return NutritionPlan.objects.get(
                id=plan_id,
                nutritionist=request.user,
            )
        except NutritionPlan.DoesNotExist:
            return None

    def get(self, request, plan_id):

        plan = self.get_object(
            request,
            plan_id,
        )

        if not plan:
            return Response(
                {"detail": "Nutrition plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NutritionPlanDetailSerializer(
            plan
        )

        return Response(
            serializer.data
        )

    def patch(self, request, plan_id):

        plan = self.get_object(
            request,
            plan_id,
        )

        if not plan:
            return Response(
                {"detail": "Nutrition plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NutritionPlanUpdateSerializer(
            plan,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        plan = serializer.save()

        return Response(
            NutritionPlanDetailSerializer(
                plan
            ).data
        )

    def delete(self, request, plan_id):

        plan = self.get_object(
            request,
            plan_id,
        )

        if not plan:
            return Response(
                {"detail": "Nutrition plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        plan.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class FoodListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        foods = Food.objects.filter(
            is_active=True
        )

        search = request.query_params.get("search")

        if search:
            foods = foods.filter(
                Q(name__icontains=search)
                | Q(category__icontains=search)
            )

        category = request.query_params.get(
            "category"
        )

        if category:
            foods = foods.filter(
                category__iexact=category
            )

        serializer = FoodSerializer(
            foods,
            many=True
        )

        return Response(serializer.data)

class ClientListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsNutritionist,
    ]

    def get(self, request):

        clients = request.user.__class__.objects.filter(
            role="user",
            is_active=True,
        ).order_by("full_name")

        search = request.query_params.get(
            "search"
        )

        if search:
            clients = clients.filter(
                full_name__icontains=search
            )

        data = [
            {
                "id": str(client.id),
                "name": client.full_name,
                "preferences": "",
                "allergies": "",
            }
            for client in clients
        ]

        return Response(data)
class MealLibraryView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsNutritionist,
    ]

    def get(self, request):
        meals = (
            MealLibrary.objects
            .filter(nutritionist=request.user)
            .prefetch_related("ingredients__food")
            .order_by("-created_at")
        )

        serializer = MealLibrarySerializer(
            meals,
            many=True
        )

        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = MealLibraryCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        meal = serializer.save()

        # Reload with ingredients + foods
        meal = (
            MealLibrary.objects
            .prefetch_related("ingredients__food")
            .get(pk=meal.pk)
        )

        response_serializer = MealLibrarySerializer(
            meal
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )        
class MealLibraryDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsNutritionist,
    ]

    def delete(self, request, meal_id):

        try:
            meal = MealLibrary.objects.get(
                id=meal_id,
                nutritionist=request.user
            )
        except MealLibrary.DoesNotExist:
            return Response(
                {"detail": "Meal not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        meal.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
class NutritionPlanApproveView(APIView):
    permission_classes = [IsAuthenticated, IsNutritionist]

    def post(self, request, plan_id):
        try:
            plan = NutritionPlan.objects.get(
                id=plan_id,
                nutritionist=request.user
            )
        except NutritionPlan.DoesNotExist:
            return Response(
                {"detail": "Nutrition plan not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if plan.status != "Draft":
            return Response(
                {
                    "detail": (
                        f"Only Draft plans can be approved. "
                        f"Current status: {plan.status}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        plan.status = "Active"
        plan.save(update_fields=["status", "updated_at"])

        return Response(
            NutritionPlanDetailSerializer(plan).data,
            status=status.HTTP_200_OK
        )