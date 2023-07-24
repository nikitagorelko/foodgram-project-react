from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

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
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.follower.filter(author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class FavoriteCartSubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для добавления в избранное и корзину и подписки."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if not 1 <= value <= 32000:
            raise serializers.ValidationError(
                'Проверьте количество ингредиента!',
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецепта."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
            'name',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        return obj.image.url

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.recipe_in_favorite.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.recipe_in_cart.filter(recipe=obj).exists()
        )

    def validate_cooking_time(self, value):
        if not 1 <= value <= 32000:
            raise serializers.ValidationError('Проверьте время готовки!')
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        return obj.image.url

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def validate_cooking_time(self, value):
        if not 1 <= value <= 32000:
            raise serializers.ValidationError('Проверьте время готовки!')
        return value


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор отображения подписки/подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.follower.filter(author=obj).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = FavoriteCartSubscribeRecipeSerializer(
            recipes,
            many=True,
            read_only=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
            ),
        ]

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(
            instance.author,
            context={
                'request': self.context.get('request'),
            },
        ).data
