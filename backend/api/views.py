from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient,
)
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    FavoriteCartRecipeSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
)

User = get_user_model()


class TagViewset(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)


class FavoriteView(APIView):
    """Вью-класс для работы с избранными рецептами."""

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteCartRecipeSerializer(recipe, request.data)
        if serializer.is_valid():
            if not Favorite.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(APIView):
    """Вью-класс для работы с корзиной рецептов."""

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteCartRecipeSerializer(recipe, request.data)
        if serializer.is_valid():
            if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe,
        ).exists():
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewset(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


@api_view(['GET'])
def download_shopping_cart(request):
    """Вью-функция для списка покупок."""

    cart = []
    recipe_ingredients = (
        RecipeIngredient.objects.filter(
            recipe__recipe_in_cart__user=request.user,
        )
        .values(
            'ingredient.name',
            'ingredient.measurement_unit',
        )
        .annotate(amount=Sum('amount'))
    )
    for i in recipe_ingredients:
        cart.append(
            f'Ингредиент: {i.ingredient.name},'
            f'Количество: {i.amount},'
            f'Единица измерения: {i.ingredient.measurement_unit};',
        )
    response = HttpResponse(
        '\n'.join(cart).rstrip(';'),
        'Content-Type: application/pdf',
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename={"shopping_cart.pdf"}'
    return response
