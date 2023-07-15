from rest_framework.routers import DefaultRouter

from django.urls import path, include

from api.views import TagViewset

app_name = 'api'

router = DefaultRouter()

router.register('tags', TagViewset, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
