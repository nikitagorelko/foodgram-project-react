from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    FavoriteView,
    IngredientViewset,
    RecipeViewset,
    ShoppingCartView,
    ShowSubscriptionsView,
    SubscribeView,
    TagViewset,
    download_shopping_cart,
)

app_name = 'api'

router = DefaultRouter()

router.register('tags', TagViewset, basename='tags')
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('recipes', RecipeViewset, basename='recipes')

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe',
    ),
    path(
        'users/subscriptions/',
        ShowSubscriptionsView.as_view(),
        name='subscriptions',
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
