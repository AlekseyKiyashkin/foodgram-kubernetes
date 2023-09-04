import csv

from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import PageLimitPagination
from api.serializers import (
    CartSerializer,
    CustomUserSerializer,
    IngredientSerilizer,
    RecipesPostUpdateSerializer,
    RecipesSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, SAFE_METHODS,
)
from .permissions import IsAuthorOrAdminOrReadOnly
from rest_framework.response import Response
from djoser.views import UserViewSet
from foodgram.settings import SHOPCART_FILENAME
from recipes.models import (
    Favorite, Ingredient, Recipes, ShoppingCart, Tag, AmountIngredient
)
from users.models import Subscribe, User

TEXT_CSV = "text/csv"


class UsersViewSet(UserViewSet):
    """Вьюсет для получения информации о пользователях."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    search_fields = ("username", "email")
    permission_classes = (AllowAny,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        id = self.kwargs.get("id")
        if id is not None:
            return User.objects.filter(pk=id)
        else:
            return User.objects.all()

    def get_subscription_queryset(self):
        return User.objects.filter(subscribing__user=self.request.user)

    @action(
        methods=("GET",),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def my(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=("GET",),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.subscriber.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        methods=(
            "POST",
            "DELETE",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {"error": "Нельзя подписатся на себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscribers = Subscribe.objects.filter(
            user=user,
            author=author
        )
        if self.request.method == "POST":
            if subscribers.exists():
                return Response(
                    {"error": "Уже подписан"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(user=request.user, author=author),
            serializer = SubscribeSerializer(
                author, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == "DELETE":
            if subscribers.exists():
                subscribers.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Такой подписки нет"}, status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет создания тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @action(detail=False)
    def get_tag(self, request):
        tag = Tag.objects.all()
        serializer = self.get_serializer(tag, many=True)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerilizer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = IngredientsFilter
    search_fields = ("name",)
    pagination_class = None

    @action(detail=False)
    def get_ingredients(self, request):
        ingredient = Ingredient.objects.all()
        serializer = self.get_serializer(ingredient, many=True)
        return Response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания рецептов"""

    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action == SAFE_METHODS:
            return RecipesSerializer
        return RecipesPostUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, partial=False)

    @action(detail=False, methods=("get",))
    def get_recipes(self, request):
        recipes = Recipes.objects.all()
        serializer = RecipesSerializer(recipes, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=(
            "post",
            "patch",
            "delete",
        ),
        permission_classes=(IsAuthenticated,),
    )
    def post_recipes(self, request):
        print(request.data)
        serializer = RecipesPostUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=(
            "post",
            "delete",
        ),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if self.request.method == "POST":
            if cart.exists():
                return Response(
                    {"error": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = CartSerializer(recipe, context={"request": request})
            return Response(serializer.data)

        if self.request.method == "DELETE":
            if cart.exists():
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Рецепта нет в корзине"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=(
            "post",
            "delete",
        ),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        chosen = Favorite.objects.filter(user=user, recipe=recipe)
        if self.request.method == "POST":
            if chosen.exists():
                return Response(
                    {"error": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = CartSerializer(recipe, context={"request": request})
            return Response(serializer.data)

        if self.request.method == "DELETE":
            if chosen.exists():
                chosen.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Рецепта нет в избранном"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        recipes = Recipes.objects.filter(shopping_cart__user=user)
        if not recipes:
            return Response(status=status.HTTP_204_NO_CONTENT)
        response = HttpResponse(content_type=TEXT_CSV)
        response["Content-Disposition"] = "attachment; filename=" + \
            SHOPCART_FILENAME
        ingredient_dict = {}
        for recipe in recipes:
            ingredient_data = AmountIngredient.objects.filter(recipe=recipe)
            for data in ingredient_data:
                ingredient = data.ingredient
                ingredient_name = ingredient.name
                ingredient_amount = data.amount
                ingredient_measurement_unit = ingredient.measurement_unit
                if ingredient_name in ingredient_dict:
                    ingredient_dict[ingredient_name]["amount"] += \
                        ingredient_amount
                else:
                    ingredient_dict[ingredient_name] = {
                        "amount": ingredient_amount,
                        "measurement_unit": ingredient_measurement_unit,
                    }

        writer = csv.writer(response)
        writer.writerow(
            (
                "Ingredient name",
                "Ingredient amount",
                "Measurement unit",
            )
        )
        for name, data in ingredient_dict.items():
            writer.writerow(
                (
                    name,
                    data["amount"],
                    data["measurement_unit"],
                )
            )
        return response
