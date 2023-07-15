from rest_framework.routers import DefaultRouter

from django.urls import path, include

from api.views import TagViewset, IngredientViewset, RecipeViewset

app_name = 'api'

router = DefaultRouter()

router.register('tags', TagViewset, basename='tags')
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('recipes', RecipeViewset, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
