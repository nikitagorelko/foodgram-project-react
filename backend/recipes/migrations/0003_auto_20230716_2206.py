# Generated by Django 3.2.3 on 2023-07-16 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230715_1803'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='user_shoppingcart_unique',
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='user_recipe_shoppingcart_unique'),
        ),
    ]
