from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цветовой HEX-код',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit',
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)],
        error_messages={
            'validators': 'Время приготовления не может быть менее минуты!',
        },
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Модель связи тега и рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class RecipeIngredient(models.Model):
    """Модель связи ингредиента и рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={
            'validators': 'Количество ингредиента не может быть менее 1!',
        },
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='uniqe_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='recipe_in_favorite',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель рецепта в списке покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_in_cart',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_recipe_shoppingcart_unique',
            ),
        ]
