from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Tag, Ingredient, Recipe, Favorite
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    FavoriteRecipeSerializer,
)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteView(APIView):
    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteRecipeSerializer(data=recipe)
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
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class APIFollow(APIView):
    pass
