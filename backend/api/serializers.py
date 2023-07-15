from rest_framework import serializers

from djoser.serializers import UserSerializer

from recipes.models import Tag, Ingredient, Recipe
from users.models import User, Subscription


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта для добавления в избранное."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url



# class RecipeGetSerializer(serializers.ModelSerializer):
#     ingredients = 

#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'auhtor', 'ingredients', 'name',)
#         read_only = 

#     def





class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор модели пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj,
        ).exists()


class SubsriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'auhtor'),
            ),
        ]
