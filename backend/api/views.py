import io

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont

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


registerFont(TTFont('times', 'times.ttf'))

User = get_user_model()


def RecipePostView(request, id, serializer, model):
    recipe = get_object_or_404(Recipe, id=id)
    serializer = serializer(recipe, request.data)
    if serializer.is_valid():
        if not model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).exists():
            model.objects.create(user=request.user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def RecipeDeleteView(request, id, model):
    recipe = get_object_or_404(Recipe, id=id)
    if model.objects.filter(
        user=request.user,
        recipe=recipe,
    ).exists():
        model.objects.get(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


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
        return RecipePostView(request, id, FavoriteCartRecipeSerializer, Favorite)

    def delete(self, request, id):
        return RecipeDeleteView(request, id, Favorite)


class ShoppingCartView(APIView):
    """Вью-класс для работы с корзиной рецептов."""

    def post(self, request, id):
        return RecipePostView(request, id, FavoriteCartRecipeSerializer, ShoppingCart)

    def delete(self, request, id):
        return RecipeDeleteView(request, id, ShoppingCart)


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
            'ingredient__name',
            'ingredient__measurement_unit',
        )
        .annotate(amount=Sum('amount'))
    )
    for i in recipe_ingredients:
        cart.append(
            f'Ingredient: {i["ingredient__name"]}, '
            f'Количество: {i["amount"]}, '
            f'Единица измерения: {i["ingredient__measurement_unit"]};',
        )
    pdf_buffer = io.BytesIO()
    pdf_file = canvas.Canvas(pdf_buffer, initialFontName='times')
    y = 800
    for i in recipe_ingredients:
        pdf_file.drawString(100, y, (
            f'Ингредиент: {i["ingredient__name"]}, '
            f'Количество: {i["amount"]}, '
            f'Единица измерения: {i["ingredient__measurement_unit"]}.'
        ))
        y -= 20
    pdf_file.save()
    pdf_buffer.seek(0)
    return FileResponse(pdf_buffer, as_attachment=True, filename='shopping_cart.pdf')
