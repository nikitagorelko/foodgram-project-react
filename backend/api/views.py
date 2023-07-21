import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteCartSubscribeRecipeSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription

registerFont(TTFont('times', 'times.ttf'))

User = get_user_model()


def recipe_post_view(request, id, serializer, model):
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


def recipe_delete_view(request, id, model):
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
    pagination_class = None


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class FavoriteView(APIView):
    """Вью-класс для работы с избранными рецептами."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        return recipe_post_view(
            request,
            id,
            FavoriteCartSubscribeRecipeSerializer,
            Favorite,
        )

    def delete(self, request, id):
        return recipe_delete_view(request, id, Favorite)


class ShoppingCartView(APIView):
    """Вью-класс для работы с корзиной рецептов."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        return recipe_post_view(
            request,
            id,
            FavoriteCartSubscribeRecipeSerializer,
            ShoppingCart,
        )

    def delete(self, request, id):
        return recipe_delete_view(request, id, ShoppingCart)


class RecipeViewset(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.prefetch_related(
        'tags',
        'ingredients',
        'author',
    ).all()
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class SubscribeView(APIView):
    """Вью-класс для подписки/отписки."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionsSerializer(
            author,
            request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            if (
                not Subscription.objects.select_related('user', 'author')
                .filter(
                    user=request.user,
                    author=author,
                )
                .exists()
            ):
                Subscription.objects.create(user=request.user, author=author)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if (
            Subscription.objects.select_related('user', 'author')
            .filter(
                user=request.user,
                author=author,
            )
            .exists()
        ):
            Subscription.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """Вью-класс для отображения подписок."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        serializer = SubscriptionsSerializer(
            queryset,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
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
        pdf_file.drawString(
            100,
            y,
            (
                f'Ингредиент: {i["ingredient__name"]}, '
                f'Количество: {i["amount"]}, '
                f'Единица измерения: {i["ingredient__measurement_unit"]}.'
            ),
        )
        y -= 20
    pdf_file.save()
    pdf_buffer.seek(0)
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename='shopping_cart.pdf',
    )
