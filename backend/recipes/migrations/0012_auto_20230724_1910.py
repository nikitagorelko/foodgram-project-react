# Generated by Django 3.2.3 on 2023-07-24 16:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20230723_2214'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ['user'], 'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ['recipe']},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'ordering': ['recipe']},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ['user'], 'verbose_name': 'Рецепт в списке покупок', 'verbose_name_plural': 'Рецепты в списке покупок'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(error_messages={'validators': 'Время приготовления не может быть менее минуты!'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(error_messages={'validators': 'Количество ингредиента не может быть менее 1!'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Количество'),
        ),
    ]